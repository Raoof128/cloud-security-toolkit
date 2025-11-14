#!/usr/bin/env python3
"""
Custom Scan Example
Demonstrates how to create custom scans and filters
"""
from scanners.aws_scanner import AWSSecurityScanner
from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator


def filter_critical_findings(findings):
    """Filter only critical findings"""
    return [f for f in findings if f.get('severity') == 'CRITICAL']


def filter_s3_findings(findings):
    """Filter only S3-related findings"""
    return [f for f in findings if f.get('type') == 'S3 Bucket']


def filter_high_risk_findings(findings, threshold=70):
    """Filter findings with risk score above threshold"""
    return [f for f in findings if f.get('risk_score', 0) >= threshold]


def custom_summary(findings, title="Custom Report"):
    """Generate custom summary"""
    print("\n" + "=" * 80)
    print(title.upper())
    print("=" * 80)

    if not findings:
        print("No findings match the filter criteria.")
        return

    # Group by resource type
    by_type = {}
    for finding in findings:
        resource_type = finding.get('type', 'Unknown')
        by_type[resource_type] = by_type.get(resource_type, 0) + 1

    print(f"\nTotal Findings: {len(findings)}")
    print("\nBy Resource Type:")
    for resource_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"  {resource_type}: {count}")

    # Show top 5
    print("\nTop 5 Findings:")
    for i, finding in enumerate(findings[:5], 1):
        print(f"\n{i}. [{finding.get('severity')}] {finding.get('issue')}")
        print(f"   Resource: {finding.get('resource')}")
        print(f"   Risk Score: {finding.get('risk_score', 'N/A')}")


def main():
    """Run custom AWS security scan with filters"""
    print("Custom AWS Security Scan Example")
    print("=" * 80)

    # Initialize scanner
    print("\nInitializing AWS scanner...")
    scanner = AWSSecurityScanner(region='us-east-1')

    # EXAMPLE 1: Scan only specific services
    print("\n[EXAMPLE 1] Scanning specific services only")
    print("-" * 80)

    # Scan only S3 buckets
    s3_findings = scanner.scan_s3_buckets()

    # Scan only IAM users
    iam_findings = scanner.scan_iam_users()

    combined_findings = s3_findings + iam_findings

    # Score and prioritize
    scorer = RiskScorer()
    prioritized = scorer.prioritize_findings(combined_findings)

    print(f"\nFound {len(s3_findings)} S3 issues")
    print(f"Found {len(iam_findings)} IAM issues")
    print(f"Total: {len(prioritized)} findings")

    # EXAMPLE 2: Filter critical findings only
    print("\n[EXAMPLE 2] Filtering CRITICAL findings only")
    print("-" * 80)

    critical = filter_critical_findings(prioritized)
    custom_summary(critical, "Critical Findings Report")

    # EXAMPLE 3: Filter high-risk findings
    print("\n[EXAMPLE 3] Filtering high-risk findings (score >= 70)")
    print("-" * 80)

    high_risk = filter_high_risk_findings(prioritized, threshold=70)
    custom_summary(high_risk, "High Risk Findings")

    # EXAMPLE 4: Generate filtered report
    print("\n[EXAMPLE 4] Generating custom report for S3 issues only")
    print("-" * 80)

    s3_only = filter_s3_findings(prioritized)

    if s3_only:
        stats = scorer.generate_summary_stats(s3_only)

        reporter = SecurityReportGenerator()
        reporter.generate_html_report(
            findings=s3_only,
            stats=stats,
            output_path='s3_security_report.html',
            account_id=scanner.account_id,
            region=scanner.region
        )

        print(f"✅ S3-specific report generated: s3_security_report.html")

    # EXAMPLE 5: Export findings to JSON for external tools
    print("\n[EXAMPLE 5] Exporting findings for external analysis")
    print("-" * 80)

    import json

    # Export critical findings
    export_data = {
        'scan_date': '2025-11-14',
        'account': scanner.account_id,
        'region': scanner.region,
        'critical_count': len(critical),
        'high_risk_count': len(high_risk),
        'findings': [
            {
                'severity': f.get('severity'),
                'resource': f.get('resource'),
                'type': f.get('type'),
                'issue': f.get('issue'),
                'risk_score': f.get('risk_score'),
                'recommendation': f.get('recommendation')
            }
            for f in critical
        ]
    }

    with open('critical_findings.json', 'w') as f:
        json.dump(export_data, f, indent=2)

    print("✅ Critical findings exported to: critical_findings.json")

    # EXAMPLE 6: Compliance-focused scan
    print("\n[EXAMPLE 6] Filtering CIS compliance violations")
    print("-" * 80)

    cis_findings = [
        f for f in prioritized
        if any('CIS' in str(c) for c in f.get('compliance', []))
    ]

    custom_summary(cis_findings, "CIS Compliance Violations")

    print("\n" + "=" * 80)
    print("✅ Custom scan examples completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
