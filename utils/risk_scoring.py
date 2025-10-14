"""
Risk Scoring Module
Calculates risk scores and prioritizes security findings
"""


class RiskScorer:
    """Risk scoring and prioritization engine"""

    # Base severity scores (0-10 scale)
    SEVERITY_SCORES = {
        'CRITICAL': 10,
        'HIGH': 7,
        'MEDIUM': 4,
        'LOW': 2,
        'INFO': 1
    }

    # Exposure multipliers
    EXPOSURE_MULTIPLIERS = {
        'public': 2.0,              # Publicly accessible
        'internet-facing': 1.8,     # Internet-facing
        'internal': 1.0,            # Internal only
        'isolated': 0.5,            # Isolated/private
        'unknown': 1.0
    }

    # Resource type risk factors
    RESOURCE_TYPE_MULTIPLIERS = {
        'IAM Root': 1.5,
        'S3 Bucket': 1.3,
        'IAM User': 1.2,
        'Security Group': 1.2,
        'CloudTrail': 1.4,
        'EC2 Instance': 1.1,
        'EBS Volume': 1.0,
        'VPC': 1.0
    }

    def __init__(self):
        """Initialize risk scorer"""
        self.total_risk_score = 0
        self.finding_count = 0

    def calculate_finding_score(self, finding):
        """
        Calculate risk score for individual finding

        Args:
            finding (dict): Security finding with severity, type, exposure, etc.

        Returns:
            float: Risk score (0-100 scale)
        """
        # Get base severity score
        severity = finding.get('severity', 'MEDIUM')
        base_score = self.SEVERITY_SCORES.get(severity, 4)

        # Apply exposure multiplier
        exposure = finding.get('exposure', 'internal')
        exposure_mult = self.EXPOSURE_MULTIPLIERS.get(exposure, 1.0)

        # Apply resource type multiplier
        resource_type = finding.get('type', 'Unknown')
        type_mult = self.RESOURCE_TYPE_MULTIPLIERS.get(resource_type, 1.0)

        # Additional risk factors
        risk_factors = 1.0

        # Check if contains sensitive data
        if finding.get('contains_pii', False):
            risk_factors *= 1.5

        # Check if compliance-related
        if finding.get('compliance'):
            risk_factors *= 1.2

        # Check if affects authentication/authorization
        if 'IAM' in resource_type or 'authentication' in finding.get('issue', '').lower():
            risk_factors *= 1.3

        # Calculate final score
        final_score = base_score * exposure_mult * type_mult * risk_factors

        # Cap at 100
        return min(round(final_score, 2), 100.0)

    def calculate_account_score(self, findings):
        """
        Calculate overall account security score (0-100)
        Higher score = better security

        Args:
            findings (list): List of all security findings

        Returns:
            float: Security score (0-100, higher is better)
        """
        if not findings:
            return 100.0

        # Calculate total risk
        total_risk = sum(self.calculate_finding_score(f) for f in findings)

        # Calculate maximum possible risk (if all findings were CRITICAL+public)
        max_possible_risk = len(findings) * 100.0

        # Calculate security score (inverse of risk percentage)
        risk_percentage = (total_risk / max_possible_risk) * 100
        security_score = max(0, 100 - risk_percentage)

        return round(security_score, 2)

    def get_security_grade(self, score):
        """
        Convert security score to letter grade

        Args:
            score (float): Security score (0-100)

        Returns:
            str: Letter grade (A+ to F)
        """
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D+'
        elif score >= 45:
            return 'D'
        elif score >= 40:
            return 'D-'
        else:
            return 'F'

    def prioritize_findings(self, findings):
        """
        Sort findings by risk score (highest first)

        Args:
            findings (list): List of security findings

        Returns:
            list: Sorted findings with risk_score added
        """
        scored_findings = []

        for finding in findings:
            score = self.calculate_finding_score(finding)
            finding['risk_score'] = score
            scored_findings.append(finding)

        # Sort by risk score (descending)
        return sorted(scored_findings, key=lambda x: x['risk_score'], reverse=True)

    def generate_summary_stats(self, findings):
        """
        Generate executive summary statistics

        Args:
            findings (list): List of security findings

        Returns:
            dict: Summary statistics
        """
        # Count by severity
        severity_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'INFO': 0
        }

        for finding in findings:
            severity = finding.get('severity', 'MEDIUM')
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Count by resource type
        type_counts = {}
        for finding in findings:
            resource_type = finding.get('type', 'Unknown')
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1

        # Get top compliance violations
        compliance_violations = {}
        for finding in findings:
            for compliance in finding.get('compliance', []):
                compliance_violations[compliance] = compliance_violations.get(compliance, 0) + 1

        # Prioritize findings
        prioritized = self.prioritize_findings(findings.copy())

        # Calculate security score
        security_score = self.calculate_account_score(findings)
        security_grade = self.get_security_grade(security_score)

        # Calculate average risk score
        if findings:
            avg_risk_score = sum(f.get('risk_score', 0) for f in prioritized) / len(findings)
        else:
            avg_risk_score = 0

        stats = {
            'total_findings': len(findings),
            'critical': severity_counts['CRITICAL'],
            'high': severity_counts['HIGH'],
            'medium': severity_counts['MEDIUM'],
            'low': severity_counts['LOW'],
            'info': severity_counts['INFO'],
            'security_score': security_score,
            'security_grade': security_grade,
            'average_risk_score': round(avg_risk_score, 2),
            'top_risks': prioritized[:10],  # Top 10 highest risk findings
            'findings_by_type': type_counts,
            'compliance_violations': compliance_violations,
            'immediate_action_required': severity_counts['CRITICAL'] + severity_counts['HIGH']
        }

        return stats

    def get_risk_trend(self, current_findings, previous_findings):
        """
        Calculate risk trend between two scans

        Args:
            current_findings (list): Current scan findings
            previous_findings (list): Previous scan findings

        Returns:
            dict: Trend analysis
        """
        current_score = self.calculate_account_score(current_findings)
        previous_score = self.calculate_account_score(previous_findings)

        score_change = current_score - previous_score
        percent_change = (score_change / previous_score * 100) if previous_score > 0 else 0

        trend = {
            'current_score': current_score,
            'previous_score': previous_score,
            'score_change': round(score_change, 2),
            'percent_change': round(percent_change, 2),
            'improving': score_change > 0,
            'new_findings': len(current_findings) - len(previous_findings),
            'current_critical': sum(1 for f in current_findings if f.get('severity') == 'CRITICAL'),
            'previous_critical': sum(1 for f in previous_findings if f.get('severity') == 'CRITICAL')
        }

        return trend

    def export_metrics(self, findings):
        """
        Export key metrics for dashboards/monitoring

        Args:
            findings (list): Security findings

        Returns:
            dict: Key metrics
        """
        stats = self.generate_summary_stats(findings)

        metrics = {
            'security_score': stats['security_score'],
            'security_grade': stats['security_grade'],
            'total_findings': stats['total_findings'],
            'critical_count': stats['critical'],
            'high_count': stats['high'],
            'medium_count': stats['medium'],
            'low_count': stats['low'],
            'immediate_action_count': stats['immediate_action_required'],
            'average_risk_score': stats['average_risk_score'],
            'top_resource_type': max(stats['findings_by_type'].items(),
                                   key=lambda x: x[1])[0] if stats['findings_by_type'] else 'None',
            'most_violated_control': max(stats['compliance_violations'].items(),
                                        key=lambda x: x[1])[0] if stats['compliance_violations'] else 'None'
        }

        return metrics


def calculate_compliance_score(findings, framework='CIS'):
    """
    Calculate compliance score for specific framework

    Args:
        findings (list): Security findings
        framework (str): Compliance framework (CIS, ASD, NIST)

    Returns:
        dict: Compliance score details
    """
    # Get all findings related to the framework
    framework_findings = [
        f for f in findings
        if any(framework in str(c) for c in f.get('compliance', []))
    ]

    total_checks = len(framework_findings) if framework_findings else 1
    failed_checks = len(framework_findings)
    passed_checks = max(0, total_checks - failed_checks)

    compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 100

    return {
        'framework': framework,
        'compliance_percentage': round(compliance_percentage, 2),
        'passed_checks': passed_checks,
        'failed_checks': failed_checks,
        'total_checks': total_checks,
        'findings': framework_findings
    }


if __name__ == '__main__':
    # Test with sample findings
    sample_findings = [
        {
            'resource': 'my-public-bucket',
            'type': 'S3 Bucket',
            'severity': 'CRITICAL',
            'issue': 'Bucket is publicly accessible',
            'exposure': 'public',
            'compliance': ['CIS 2.1.5']
        },
        {
            'resource': 'web-server-sg',
            'type': 'Security Group',
            'severity': 'HIGH',
            'issue': 'SSH open to internet',
            'exposure': 'internet-facing',
            'compliance': ['CIS 5.2']
        },
        {
            'resource': 'admin-user',
            'type': 'IAM User',
            'severity': 'HIGH',
            'issue': 'MFA not enabled',
            'compliance': ['CIS 1.14']
        }
    ]

    scorer = RiskScorer()

    # Test individual scoring
    print("Individual Finding Scores:")
    for finding in sample_findings:
        score = scorer.calculate_finding_score(finding)
        print(f"  {finding['resource']}: {score}")

    # Test summary stats
    print("\nSummary Statistics:")
    stats = scorer.generate_summary_stats(sample_findings)
    print(f"  Security Score: {stats['security_score']}/100 (Grade: {stats['security_grade']})")
    print(f"  Total Findings: {stats['total_findings']}")
    print(f"  Critical: {stats['critical']}, High: {stats['high']}, Medium: {stats['medium']}")
    print(f"  Immediate Action Required: {stats['immediate_action_required']}")

    # Test compliance scoring
    print("\nCIS Compliance:")
    cis_score = calculate_compliance_score(sample_findings, 'CIS')
    print(f"  Compliance: {cis_score['compliance_percentage']}%")
    print(f"  Failed Checks: {cis_score['failed_checks']}/{cis_score['total_checks']}")
