#!/usr/bin/env python3
"""
Basic AWS Security Scan Example
Demonstrates how to use the toolkit programmatically
"""
from scanners.aws_scanner import AWSSecurityScanner
from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator


def main():
    """Run a basic AWS security scan"""
    print("Starting AWS Security Scan...")
    print("=" * 80)

    # Initialize scanner (uses AWS credential chain)
    scanner = AWSSecurityScanner(region='us-east-1')

    # Run full security scan
    findings = scanner.run_full_scan()

    # Calculate risk scores and prioritize
    scorer = RiskScorer()
    prioritized_findings = scorer.prioritize_findings(findings)
    stats = scorer.generate_summary_stats(prioritized_findings)

    # Display summary
    print("\n" + "=" * 80)
    print("SCAN SUMMARY")
    print("=" * 80)
    print(f"Total Findings: {stats['total_findings']}")
    print(f"Security Score: {stats['security_score']}/100 (Grade: {stats['security_grade']})")
    print(f"\nFindings by Severity:")
    print(f"  CRITICAL: {stats['critical']}")
    print(f"  HIGH: {stats['high']}")
    print(f"  MEDIUM: {stats['medium']}")
    print(f"  LOW: {stats['low']}")

    # Generate HTML report
    reporter = SecurityReportGenerator()
    reporter.generate_html_report(
        findings=prioritized_findings,
        stats=stats,
        output_path='security_report.html',
        account_id=scanner.account_id,
        region=scanner.region
    )

    print(f"\n✅ Report generated: security_report.html")
    print("=" * 80)


if __name__ == '__main__':
    main()
