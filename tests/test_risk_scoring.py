"""
Unit tests for risk scoring module
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.risk_scoring import RiskScorer, calculate_compliance_score


class TestRiskScorer:
    """Tests for RiskScorer class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.scorer = RiskScorer()
        self.sample_finding = {
            'resource': 'test-bucket',
            'type': 'S3 Bucket',
            'severity': 'CRITICAL',
            'issue': 'Bucket is publicly accessible',
            'exposure': 'public',
            'compliance': ['CIS 2.1.5']
        }

    def test_calculate_finding_score_critical(self):
        """Test calculating risk score for critical finding"""
        score = self.scorer.calculate_finding_score(self.sample_finding)
        assert isinstance(score, float)
        assert 0 <= score <= 100
        # Critical + public + S3 should result in high score
        assert score > 20

    def test_calculate_finding_score_low(self):
        """Test calculating risk score for low severity finding"""
        finding = {
            'resource': 'test-resource',
            'type': 'VPC',
            'severity': 'LOW',
            'issue': 'Minor issue',
            'exposure': 'internal'
        }
        score = self.scorer.calculate_finding_score(finding)
        assert score < 20  # Low severity should have lower score

    def test_calculate_account_score_no_findings(self):
        """Test account score with no findings"""
        score = self.scorer.calculate_account_score([])
        assert score == 100.0

    def test_calculate_account_score_with_findings(self):
        """Test account score with findings"""
        findings = [self.sample_finding] * 5
        score = self.scorer.calculate_account_score(findings)
        assert 0 <= score <= 100
        assert score < 100  # Should be less than perfect

    def test_get_security_grade(self):
        """Test security grade assignment"""
        assert self.scorer.get_security_grade(95) == 'A+'
        assert self.scorer.get_security_grade(90) == 'A'
        assert self.scorer.get_security_grade(85) == 'A-'
        assert self.scorer.get_security_grade(80) == 'B+'
        assert self.scorer.get_security_grade(60) == 'C'
        assert self.scorer.get_security_grade(30) == 'F'

    def test_prioritize_findings(self):
        """Test finding prioritization"""
        findings = [
            {'severity': 'LOW', 'type': 'VPC', 'exposure': 'internal'},
            {'severity': 'CRITICAL', 'type': 'S3 Bucket', 'exposure': 'public'},
            {'severity': 'MEDIUM', 'type': 'EC2 Instance', 'exposure': 'internal'}
        ]
        prioritized = self.scorer.prioritize_findings(findings)

        # Check that all findings have risk_score
        assert all('risk_score' in f for f in prioritized)

        # Check that findings are sorted by risk score
        scores = [f['risk_score'] for f in prioritized]
        assert scores == sorted(scores, reverse=True)

        # Critical should be first
        assert prioritized[0]['severity'] == 'CRITICAL'

    def test_generate_summary_stats(self):
        """Test summary statistics generation"""
        findings = [
            {'severity': 'CRITICAL', 'type': 'S3 Bucket', 'compliance': ['CIS 2.1.5']},
            {'severity': 'HIGH', 'type': 'IAM User', 'compliance': ['CIS 1.14']},
            {'severity': 'MEDIUM', 'type': 'Security Group', 'compliance': ['CIS 5.2']},
            {'severity': 'LOW', 'type': 'VPC', 'compliance': []},
        ]

        stats = self.scorer.generate_summary_stats(findings)

        # Check required fields
        assert 'total_findings' in stats
        assert 'critical' in stats
        assert 'high' in stats
        assert 'medium' in stats
        assert 'low' in stats
        assert 'security_score' in stats
        assert 'security_grade' in stats
        assert 'top_risks' in stats
        assert 'findings_by_type' in stats
        assert 'compliance_violations' in stats

        # Check counts
        assert stats['total_findings'] == 4
        assert stats['critical'] == 1
        assert stats['high'] == 1
        assert stats['medium'] == 1
        assert stats['low'] == 1

    def test_get_risk_trend(self):
        """Test risk trend calculation"""
        current_findings = [
            {'severity': 'CRITICAL', 'type': 'S3 Bucket'},
            {'severity': 'HIGH', 'type': 'IAM User'}
        ]
        previous_findings = [
            {'severity': 'MEDIUM', 'type': 'Security Group'}
        ]

        trend = self.scorer.get_risk_trend(current_findings, previous_findings)

        # Check required fields
        assert 'current_score' in trend
        assert 'previous_score' in trend
        assert 'score_change' in trend
        assert 'percent_change' in trend
        assert 'improving' in trend
        assert 'new_findings' in trend
        assert 'current_critical' in trend
        assert 'previous_critical' in trend

        # More critical findings should mean lower score (worse security)
        assert trend['current_score'] < trend['previous_score']
        assert not trend['improving']

    def test_export_metrics(self):
        """Test metrics export"""
        findings = [
            {'severity': 'CRITICAL', 'type': 'S3 Bucket', 'compliance': ['CIS 2.1.5']},
            {'severity': 'HIGH', 'type': 'IAM User', 'compliance': ['CIS 1.14']}
        ]

        metrics = self.scorer.export_metrics(findings)

        # Check required metrics
        assert 'security_score' in metrics
        assert 'security_grade' in metrics
        assert 'total_findings' in metrics
        assert 'critical_count' in metrics
        assert 'high_count' in metrics
        assert 'immediate_action_count' in metrics
        assert 'top_resource_type' in metrics
        assert 'most_violated_control' in metrics

        assert metrics['total_findings'] == 2
        assert metrics['critical_count'] == 1
        assert metrics['high_count'] == 1


class TestComplianceScoring:
    """Tests for compliance score calculation"""

    def test_calculate_compliance_score_cis(self):
        """Test CIS compliance scoring"""
        findings = [
            {'compliance': ['CIS 2.1.5', 'ASD Essential 8']},
            {'compliance': ['CIS 1.14']},
            {'compliance': ['ASD Essential 8']}
        ]

        cis_score = calculate_compliance_score(findings, 'CIS')

        assert 'framework' in cis_score
        assert 'compliance_percentage' in cis_score
        assert 'failed_checks' in cis_score
        assert 'total_checks' in cis_score

        assert cis_score['framework'] == 'CIS'
        assert cis_score['failed_checks'] == 2  # 2 findings with CIS

    def test_calculate_compliance_score_empty(self):
        """Test compliance scoring with no findings"""
        score = calculate_compliance_score([], 'CIS')

        assert score['compliance_percentage'] == 100.0
        assert score['failed_checks'] == 0

    def test_calculate_compliance_score_no_matches(self):
        """Test compliance scoring with no matching framework"""
        findings = [
            {'compliance': ['ASD Essential 8']},
            {'compliance': ['NIST']}
        ]

        cis_score = calculate_compliance_score(findings, 'CIS')

        # No CIS findings means 100% compliance
        assert cis_score['failed_checks'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
