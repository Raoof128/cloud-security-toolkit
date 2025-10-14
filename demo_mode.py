#!/usr/bin/env python3
"""
Demo Mode for Cloud Security Toolkit
Generates sample findings without requiring AWS credentials
Useful for testing, demos, and development
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator


def generate_sample_findings():
    """Generate realistic sample security findings"""

    findings = [
        # CRITICAL Findings
        {
            'resource': 'Root Account',
            'type': 'IAM Root',
            'severity': 'CRITICAL',
            'issue': 'Root account MFA not enabled',
            'recommendation': 'Enable MFA on root account immediately',
            'compliance': ['CIS 1.5', 'ASD Essential 8'],
            'exposure': 'internal'
        },
        {
            'resource': 'public-data-bucket',
            'type': 'S3 Bucket',
            'severity': 'CRITICAL',
            'issue': 'Bucket is publicly accessible',
            'recommendation': 'Enable public access block and review bucket policy',
            'compliance': ['CIS 2.1.5'],
            'exposure': 'public',
            'contains_pii': True
        },
        {
            'resource': 'web-server-sg (sg-12345abc)',
            'type': 'Security Group',
            'severity': 'CRITICAL',
            'issue': 'SSH (port 22) open to internet (0.0.0.0/0)',
            'recommendation': 'Restrict SSH access to specific IP ranges or use VPN/bastion host',
            'compliance': ['CIS 5.2'],
            'exposure': 'internet-facing'
        },

        # HIGH Severity Findings
        {
            'resource': 'admin-user',
            'type': 'IAM User',
            'severity': 'HIGH',
            'issue': 'MFA not enabled',
            'recommendation': 'Enable MFA for enhanced security',
            'compliance': ['CIS 1.14', 'ASD Essential 8 #2']
        },
        {
            'resource': 'backup-bucket',
            'type': 'S3 Bucket',
            'severity': 'HIGH',
            'issue': 'Server-side encryption not enabled',
            'recommendation': 'Enable AES-256 or KMS encryption',
            'compliance': ['CIS 2.1.1']
        },
        {
            'resource': 'db-server-sg (sg-67890def)',
            'type': 'Security Group',
            'severity': 'HIGH',
            'issue': 'PostgreSQL (port 5432) open to internet (0.0.0.0/0)',
            'recommendation': 'Restrict database access to application security groups only',
            'compliance': ['CIS 5.2'],
            'exposure': 'internet-facing'
        },
        {
            'resource': 'i-0abc123def456789 (Volume: vol-0123456789abcdef)',
            'type': 'EBS Volume',
            'severity': 'HIGH',
            'issue': 'EBS volume not encrypted',
            'recommendation': 'Enable EBS encryption for data at rest protection',
            'compliance': ['CIS 2.2.1']
        },
        {
            'resource': 'security-audit-trail',
            'type': 'CloudTrail',
            'severity': 'HIGH',
            'issue': 'Log file validation not enabled',
            'recommendation': 'Enable log file integrity validation',
            'compliance': ['CIS 3.2']
        },

        # MEDIUM Severity Findings
        {
            'resource': 'developer-user (AKIAIOSFODNN7EXAMPLE)',
            'type': 'Access Key',
            'severity': 'MEDIUM',
            'issue': 'Access key older than 90 days (127 days)',
            'recommendation': 'Rotate access keys regularly (every 90 days)',
            'compliance': ['CIS 1.4']
        },
        {
            'resource': 'logs-bucket',
            'type': 'S3 Bucket',
            'severity': 'MEDIUM',
            'issue': 'Versioning not enabled',
            'recommendation': 'Enable versioning for data protection and recovery',
            'compliance': ['CIS 2.1.3']
        },
        {
            'resource': 'application-bucket',
            'type': 'S3 Bucket',
            'severity': 'MEDIUM',
            'issue': 'Access logging not enabled',
            'recommendation': 'Enable S3 access logging for audit trail',
            'compliance': ['CIS 2.1.4']
        },
        {
            'resource': 'i-0987654321fedcba',
            'type': 'EC2 Instance',
            'severity': 'MEDIUM',
            'issue': 'Instance has public IP address',
            'recommendation': 'Use private IPs with NAT gateway or bastion host',
            'compliance': ['CIS 5.1'],
            'exposure': 'internet-facing'
        },
        {
            'resource': 'i-0abcdef123456789',
            'type': 'EC2 Instance',
            'severity': 'MEDIUM',
            'issue': 'Instance using IMDSv1 (vulnerable to SSRF)',
            'recommendation': 'Require IMDSv2 (HttpTokens=required)',
            'compliance': ['AWS Best Practice']
        },
        {
            'resource': 'vpc-0123456789abcdef0',
            'type': 'VPC',
            'severity': 'MEDIUM',
            'issue': 'VPC Flow Logs not enabled',
            'recommendation': 'Enable VPC Flow Logs for network traffic visibility',
            'compliance': ['CIS 3.9']
        },
        {
            'resource': 'Account Password Policy',
            'type': 'IAM Policy',
            'severity': 'MEDIUM',
            'issue': 'Minimum password length is 8 (should be 14+)',
            'recommendation': 'Set minimum password length to 14 characters',
            'compliance': ['CIS 1.8']
        },

        # LOW Severity Findings
        {
            'resource': 'test-user (AKIAI44QH8DHBEXAMPLE)',
            'type': 'Access Key',
            'severity': 'LOW',
            'issue': 'Access key not used in 120 days',
            'recommendation': 'Remove unused access keys',
            'compliance': ['CIS 1.3']
        },
        {
            'resource': 'Account Password Policy',
            'type': 'IAM Policy',
            'severity': 'LOW',
            'issue': 'Password expiration set to 120 days (should be 90)',
            'recommendation': 'Set password expiration to 90 days',
            'compliance': ['CIS 1.11']
        }
    ]

    return findings


def run_demo(output_file='demo_report.html', format_type='html', verbose=False):
    """
    Run demo mode and generate reports

    Args:
        output_file (str): Output file path
        format_type (str): Report format (html, json, csv, all)
        verbose (bool): Verbose output
    """

    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      Cloud Security Audit & Hardening Toolkit - DEMO MODE                ║
║      Generating sample findings without AWS connection                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    print("[*] Generating sample security findings...")
    findings = generate_sample_findings()

    print(f"[+] Generated {len(findings)} sample findings")

    # Score and prioritize
    print("\n[*] Analyzing findings and calculating risk scores...")
    scorer = RiskScorer()
    findings = scorer.prioritize_findings(findings)
    stats = scorer.generate_summary_stats(findings)

    # Print console summary
    print("\n" + "="*80)
    print("DEMO SCAN RESULTS SUMMARY")
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

    if format_type == 'html':
        reporter.generate_html_report(
            findings, stats, output_file,
            account_id='123456789012 (DEMO)',
            region='ap-southeast-2 (DEMO)'
        )
    elif format_type == 'json':
        reporter.export_to_json(findings, stats, output_file)
    elif format_type == 'csv':
        reporter.export_to_csv(findings, output_file)
    elif format_type == 'all':
        base_name = output_file.rsplit('.', 1)[0] if '.' in output_file else output_file
        reporter.generate_all_reports(
            findings, stats, base_name,
            account_id='123456789012 (DEMO)',
            region='ap-southeast-2 (DEMO)'
        )

    # Print executive summary if verbose
    if verbose:
        print("\n" + reporter.generate_executive_summary(stats))

    print("\n[+] Demo complete!")
    print(f"[+] This is sample data for demonstration purposes")
    print(f"[+] To scan a real AWS account, configure credentials and run:")
    print(f"    python cloud_security_audit.py --provider aws")

    return findings, stats


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Demo Mode - Generate sample security audit reports'
    )

    parser.add_argument(
        '--output', '-o',
        default='demo_report.html',
        help='Output file path (default: demo_report.html)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['html', 'json', 'csv', 'all'],
        default='html',
        help='Report format (default: html)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    try:
        run_demo(args.output, args.format, args.verbose)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n[!] Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
