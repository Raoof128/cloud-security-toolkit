#!/usr/bin/env python3
"""
Cloud Security Audit & Hardening Toolkit
Main CLI interface for security scanning and remediation
"""
import argparse
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import non-AWS-dependent modules
from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator

# AWS-dependent modules imported conditionally to allow demo mode without boto3


def print_banner():
    """Print tool banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      Cloud Security Audit & Hardening Toolkit                            ║
║      Comprehensive security scanning for AWS, Azure, and GCP             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def scan_aws(args):
    """
    Execute AWS security scan

    Args:
        args: Command-line arguments
    """
    # Import AWS-dependent modules
    try:
        from scanners.aws_scanner import AWSSecurityScanner
        from remediation.aws_remediation import AWSRemediation
    except ImportError as e:
        print(f"\n[-] Error importing AWS modules: {str(e)}")
        print("[!] AWS scanning requires boto3. Install dependencies:")
        print("    pip install -r requirements.txt")
        print("\n[*] Alternatively, try demo mode:")
        print("    python cloud_security_audit.py --demo")
        return 1

    print(f"\n[*] Starting AWS security scan...")
    print(f"[*] Region: {args.region}")

    # Initialize scanner
    try:
        scanner = AWSSecurityScanner(region=args.region)
    except Exception as e:
        print(f"\n[-] Failed to initialize AWS scanner: {str(e)}")
        print("[!] Please ensure AWS credentials are configured:")
        print("    - Run 'aws configure' to set up credentials")
        print("    - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        return 1

    # Run scan
    findings = scanner.run_full_scan()

    if not findings:
        print("\n[+] No security issues found! Your environment is secure.")
        return 0

    # Score and prioritize findings
    print("\n[*] Analyzing findings and calculating risk scores...")
    scorer = RiskScorer()
    findings = scorer.prioritize_findings(findings)
    stats = scorer.generate_summary_stats(findings)

    # Print console summary
    print("\n" + "="*80)
    print("SCAN RESULTS SUMMARY")
    print("="*80)
    print(f"Security Score: {stats['security_score']}/100 (Grade: {stats['security_grade']})")
    print(f"Total Findings: {stats['total_findings']}")
    print(f"  Critical: {stats['critical']}")
    print(f"  High:     {stats['high']}")
    print(f"  Medium:   {stats['medium']}")
    print(f"  Low:      {stats['low']}")
    print(f"\nImmediate Action Required: {stats['immediate_action_required']} findings")
    print("="*80)

    # Generate reports
    print("\n[*] Generating reports...")
    reporter = SecurityReportGenerator()

    if args.format == 'html':
        reporter.generate_html_report(
            findings, stats, args.output,
            account_id=scanner.account_id,
            region=args.region
        )
    elif args.format == 'json':
        reporter.export_to_json(findings, stats, args.output)
    elif args.format == 'csv':
        reporter.export_to_csv(findings, args.output)
    elif args.format == 'all':
        # Generate all formats
        base_name = args.output.rsplit('.', 1)[0]
        reporter.generate_all_reports(
            findings, stats, base_name,
            account_id=scanner.account_id,
            region=args.region
        )

    # Print executive summary
    if args.verbose:
        print("\n" + reporter.generate_executive_summary(stats))

    # Remediation
    if args.remediate:
        print("\n" + "="*80)
        print("AUTOMATED REMEDIATION")
        print("="*80)

        remediator = AWSRemediation(region=args.region, dry_run=args.dry_run)

        if args.dry_run:
            print("\n[*] Running in DRY RUN mode - no changes will be made")
        else:
            print("\n[!] WARNING: Running in LIVE mode - changes will be applied!")
            response = input("Are you sure you want to proceed? (yes/no): ")
            if response.lower() != 'yes':
                print("[*] Remediation cancelled")
                return 0

        results = remediator.remediate_findings(findings)

        print(f"\n[+] Remediation Summary:")
        print(f"    Attempted:  {results['attempted']}")
        print(f"    Successful: {results['successful']}")
        print(f"    Failed:     {results['failed']}")
        print(f"    Skipped:    {results['skipped']}")

        # Save remediation log
        log_file = f"remediation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        remediator.export_remediation_log(log_file)

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Cloud Security Audit & Hardening Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo mode (no AWS credentials required)
  python cloud_security_audit.py --demo --output demo_report.html

  # Scan AWS account and generate HTML report
  python cloud_security_audit.py --provider aws --output report.html

  # Scan and export to JSON
  python cloud_security_audit.py --provider aws --format json --output findings.json

  # Scan and auto-remediate (dry-run)
  python cloud_security_audit.py --provider aws --remediate --dry-run

  # Scan and apply fixes (live mode)
  python cloud_security_audit.py --provider aws --remediate

  # Generate all report formats
  python cloud_security_audit.py --provider aws --format all --output audit

For more information, visit: https://github.com/raoufchak/cloud-security-toolkit
        """
    )

    # Provider selection
    parser.add_argument(
        '--provider',
        choices=['aws', 'azure', 'gcp'],
        default='aws',
        help='Cloud provider to scan (default: aws)'
    )

    # Region
    parser.add_argument(
        '--region',
        default='ap-southeast-2',
        help='Cloud region (default: ap-southeast-2 for AWS)'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        default='security_audit_report.html',
        help='Output report path (default: security_audit_report.html)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['html', 'json', 'csv', 'all'],
        default='html',
        help='Report format (default: html)'
    )

    # Remediation options
    parser.add_argument(
        '--remediate',
        action='store_true',
        help='Auto-remediate findings'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate remediation without making changes'
    )

    # Verbosity
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output (print executive summary)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (minimal output)'
    )

    # Scan scope
    parser.add_argument(
        '--services',
        nargs='+',
        help='Specific services to scan (e.g., iam s3 ec2)'
    )

    parser.add_argument(
        '--compliance',
        choices=['cis', 'asd', 'nist', 'all'],
        help='Check specific compliance framework'
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with sample data (no AWS credentials required)'
    )

    args = parser.parse_args()

    # Print banner unless quiet mode
    if not args.quiet:
        print_banner()

    # Handle demo mode
    if args.demo:
        print("\n[*] Running in DEMO MODE with sample data")
        print("[*] No AWS credentials required\n")
        from demo_mode import run_demo
        run_demo(args.output, args.format, args.verbose)
        return 0

    # Execute scan based on provider
    if args.provider == 'aws':
        return scan_aws(args)
    elif args.provider == 'azure':
        print("[-] Azure scanning not yet implemented")
        print("[*] Coming soon! Focus is currently on AWS.")
        return 1
    elif args.provider == 'gcp':
        print("[-] GCP scanning not yet implemented")
        print("[*] Coming soon! Focus is currently on AWS.")
        return 1
    else:
        print(f"[-] Unknown provider: {args.provider}")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
