"""
Report Generator Module
Generate security audit reports in multiple formats (HTML, JSON, CSV)
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import json
import csv
import os


class SecurityReportGenerator:
    """Security report generator with multiple output formats"""

    def __init__(self, template_dir='reporting/templates'):
        """
        Initialize report generator

        Args:
            template_dir (str): Directory containing Jinja2 templates
        """
        # Get absolute path to templates
        if not os.path.isabs(template_dir):
            # Assume relative to project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(script_dir, 'templates')

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_html_report(self, findings, stats, output_path, account_id='', region=''):
        """
        Generate comprehensive HTML report

        Args:
            findings (list): Security findings
            stats (dict): Summary statistics
            output_path (str): Output file path
            account_id (str): AWS account ID
            region (str): AWS region
        """
        try:
            template = self.env.get_template('security_report.html')

            html = template.render(
                scan_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                findings=findings,
                stats=stats,
                score=stats['security_score'],
                grade=stats['security_grade'],
                account_id=account_id,
                region=region
            )

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"[+] HTML report generated: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error generating HTML report: {str(e)}")
            return False

    def export_to_json(self, findings, stats, output_path):
        """
        Export findings to JSON format

        Args:
            findings (list): Security findings
            stats (dict): Summary statistics
            output_path (str): Output file path
        """
        try:
            report_data = {
                'metadata': {
                    'scan_date': datetime.now().isoformat(),
                    'total_findings': len(findings),
                    'security_score': stats['security_score'],
                    'security_grade': stats['security_grade']
                },
                'summary': {
                    'critical': stats['critical'],
                    'high': stats['high'],
                    'medium': stats['medium'],
                    'low': stats['low'],
                    'immediate_action_required': stats['immediate_action_required'],
                    'average_risk_score': stats['average_risk_score']
                },
                'findings_by_type': stats['findings_by_type'],
                'compliance_violations': stats['compliance_violations'],
                'top_risks': stats['top_risks'][:10],
                'all_findings': findings
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)

            print(f"[+] JSON export complete: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error exporting JSON: {str(e)}")
            return False

    def export_to_csv(self, findings, output_path):
        """
        Export findings to CSV format

        Args:
            findings (list): Security findings
            output_path (str): Output file path
        """
        try:
            if not findings:
                print("[-] No findings to export")
                return False

            # Define CSV columns
            fieldnames = [
                'severity',
                'resource',
                'type',
                'issue',
                'recommendation',
                'risk_score',
                'exposure',
                'compliance'
            ]

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for finding in findings:
                    # Convert compliance list to string
                    if 'compliance' in finding and isinstance(finding['compliance'], list):
                        finding['compliance'] = ', '.join(finding['compliance'])

                    writer.writerow(finding)

            print(f"[+] CSV export complete: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error exporting CSV: {str(e)}")
            return False

    def generate_executive_summary(self, stats):
        """
        Generate executive summary text

        Args:
            stats (dict): Summary statistics

        Returns:
            str: Executive summary text
        """
        summary = f"""
{'='*80}
CLOUD SECURITY AUDIT - EXECUTIVE SUMMARY
{'='*80}

Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SECURITY SCORE: {stats['security_score']}/100 (Grade: {stats['security_grade']})

FINDINGS SUMMARY:
  Critical Issues:       {stats['critical']}
  High Severity:         {stats['high']}
  Medium Severity:       {stats['medium']}
  Low Severity:          {stats['low']}
  ─────────────────────────────
  Total Findings:        {stats['total_findings']}
  Immediate Action:      {stats['immediate_action_required']} findings

AVERAGE RISK SCORE: {stats['average_risk_score']}/100

"""

        # Risk assessment
        if stats['security_score'] >= 80:
            summary += "RISK ASSESSMENT: LOW - Excellent security posture\n"
        elif stats['security_score'] >= 60:
            summary += "RISK ASSESSMENT: MODERATE - Good security with room for improvement\n"
        elif stats['security_score'] >= 40:
            summary += "RISK ASSESSMENT: HIGH - Address critical issues promptly\n"
        else:
            summary += "RISK ASSESSMENT: CRITICAL - Immediate action required!\n"

        summary += "\nTOP 5 CRITICAL RISKS:\n"
        summary += "─" * 80 + "\n"

        for i, finding in enumerate(stats['top_risks'][:5], 1):
            summary += f"\n{i}. [{finding['severity']}] {finding['issue']}\n"
            summary += f"   Resource: {finding['resource']}\n"
            summary += f"   Type: {finding['type']}\n"
            summary += f"   Risk Score: {finding.get('risk_score', 'N/A')}/100\n"
            summary += f"   Recommendation: {finding['recommendation']}\n"

        # Compliance violations
        if stats['compliance_violations']:
            summary += f"\n{'─'*80}\n"
            summary += "COMPLIANCE VIOLATIONS:\n"
            for control, count in sorted(stats['compliance_violations'].items(),
                                        key=lambda x: x[1], reverse=True)[:5]:
                summary += f"  {control}: {count} violations\n"

        # Findings by type
        summary += f"\n{'─'*80}\n"
        summary += "FINDINGS BY RESOURCE TYPE:\n"
        for resource_type, count in sorted(stats['findings_by_type'].items(),
                                          key=lambda x: x[1], reverse=True):
            summary += f"  {resource_type}: {count} findings\n"

        summary += f"\n{'='*80}\n"
        summary += "RECOMMENDATIONS:\n"
        summary += f"{'='*80}\n\n"

        if stats['critical'] > 0:
            summary += f"1. IMMEDIATE: Address {stats['critical']} CRITICAL findings\n"
        if stats['high'] > 0:
            summary += f"2. URGENT: Remediate {stats['high']} HIGH severity findings\n"
        if stats['medium'] > 0:
            summary += f"3. IMPORTANT: Review {stats['medium']} MEDIUM severity findings\n"

        summary += "\n"
        summary += "For detailed findings and remediation steps, please refer to the HTML report.\n"
        summary += f"{'='*80}\n"

        return summary

    def generate_markdown_summary(self, stats):
        """
        Generate markdown-formatted summary

        Args:
            stats (dict): Summary statistics

        Returns:
            str: Markdown summary
        """
        md = f"""# Cloud Security Audit Summary

**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Security Score

**{stats['security_score']}/100** (Grade: **{stats['security_grade']}**)

## Findings Overview

| Severity | Count |
|----------|-------|
| Critical | {stats['critical']} |
| High     | {stats['high']} |
| Medium   | {stats['medium']} |
| Low      | {stats['low']} |
| **Total** | **{stats['total_findings']}** |

**Immediate Action Required:** {stats['immediate_action_required']} findings

## Top 5 Risks

"""
        for i, finding in enumerate(stats['top_risks'][:5], 1):
            md += f"""
### {i}. {finding['issue']}

- **Severity:** {finding['severity']}
- **Resource:** {finding['resource']}
- **Type:** {finding['type']}
- **Risk Score:** {finding.get('risk_score', 'N/A')}/100
- **Recommendation:** {finding['recommendation']}
"""

        if stats['compliance_violations']:
            md += "\n## Compliance Violations\n\n"
            md += "| Control | Violations |\n"
            md += "|---------|------------|\n"
            for control, count in sorted(stats['compliance_violations'].items(),
                                        key=lambda x: x[1], reverse=True)[:10]:
                md += f"| {control} | {count} |\n"

        md += "\n## Findings by Resource Type\n\n"
        md += "| Resource Type | Count |\n"
        md += "|---------------|-------|\n"
        for resource_type, count in sorted(stats['findings_by_type'].items(),
                                          key=lambda x: x[1], reverse=True):
            md += f"| {resource_type} | {count} |\n"

        return md

    def save_summary_to_file(self, stats, output_path):
        """
        Save text summary to file

        Args:
            stats (dict): Summary statistics
            output_path (str): Output file path
        """
        try:
            summary = self.generate_executive_summary(stats)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)

            print(f"[+] Summary saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error saving summary: {str(e)}")
            return False

    def save_markdown_summary(self, stats, output_path):
        """
        Save markdown summary to file

        Args:
            stats (dict): Summary statistics
            output_path (str): Output file path
        """
        try:
            markdown = self.generate_markdown_summary(stats)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"[+] Markdown summary saved to: {output_path}")
            return True
        except Exception as e:
            print(f"[-] Error saving markdown: {str(e)}")
            return False

    def generate_all_reports(self, findings, stats, base_filename='security_audit',
                           account_id='', region=''):
        """
        Generate all report formats at once

        Args:
            findings (list): Security findings
            stats (dict): Summary statistics
            base_filename (str): Base filename (without extension)
            account_id (str): AWS account ID
            region (str): AWS region

        Returns:
            dict: Generated report paths
        """
        report_paths = {}

        # Create reports directory if it doesn't exist
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)

        # Add timestamp to filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{base_filename}_{timestamp}"

        # Generate HTML report
        html_path = os.path.join(reports_dir, f"{base_name}.html")
        if self.generate_html_report(findings, stats, html_path, account_id, region):
            report_paths['html'] = html_path

        # Generate JSON export
        json_path = os.path.join(reports_dir, f"{base_name}.json")
        if self.export_to_json(findings, stats, json_path):
            report_paths['json'] = json_path

        # Generate CSV export
        csv_path = os.path.join(reports_dir, f"{base_name}.csv")
        if self.export_to_csv(findings, csv_path):
            report_paths['csv'] = csv_path

        # Generate text summary
        summary_path = os.path.join(reports_dir, f"{base_name}_summary.txt")
        if self.save_summary_to_file(stats, summary_path):
            report_paths['summary'] = summary_path

        # Generate markdown summary
        md_path = os.path.join(reports_dir, f"{base_name}_summary.md")
        if self.save_markdown_summary(stats, md_path):
            report_paths['markdown'] = md_path

        print(f"\n[+] All reports generated successfully!")
        print(f"[+] Reports saved to: {reports_dir}/")

        return report_paths


if __name__ == '__main__':
    # Test with sample data
    from utils.risk_scoring import RiskScorer

    sample_findings = [
        {
            'resource': 'my-public-bucket',
            'type': 'S3 Bucket',
            'severity': 'CRITICAL',
            'issue': 'Bucket is publicly accessible',
            'recommendation': 'Enable public access block',
            'exposure': 'public',
            'compliance': ['CIS 2.1.5']
        },
        {
            'resource': 'web-sg',
            'type': 'Security Group',
            'severity': 'HIGH',
            'issue': 'SSH open to internet (0.0.0.0/0)',
            'recommendation': 'Restrict SSH access to specific IPs',
            'exposure': 'internet-facing',
            'compliance': ['CIS 5.2']
        },
        {
            'resource': 'admin-user',
            'type': 'IAM User',
            'severity': 'HIGH',
            'issue': 'MFA not enabled',
            'recommendation': 'Enable MFA for all IAM users',
            'compliance': ['CIS 1.14', 'ASD Essential 8']
        },
        {
            'resource': 'db-bucket',
            'type': 'S3 Bucket',
            'severity': 'MEDIUM',
            'issue': 'Versioning not enabled',
            'recommendation': 'Enable versioning for data protection',
            'compliance': ['CIS 2.1.3']
        }
    ]

    # Generate stats
    scorer = RiskScorer()
    findings_with_scores = scorer.prioritize_findings(sample_findings)
    stats = scorer.generate_summary_stats(findings_with_scores)

    # Generate reports
    reporter = SecurityReportGenerator()

    # Print executive summary
    print(reporter.generate_executive_summary(stats))

    # Generate all reports
    report_paths = reporter.generate_all_reports(
        findings_with_scores,
        stats,
        account_id='123456789012',
        region='ap-southeast-2'
    )

    print("\nGenerated Reports:")
    for format_type, path in report_paths.items():
        print(f"  {format_type.upper()}: {path}")
