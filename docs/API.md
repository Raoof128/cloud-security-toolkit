# API Documentation

This document provides detailed API documentation for programmatic use of the Cloud Security Toolkit.

## Table of Contents

- [Scanners API](#scanners-api)
- [Risk Scoring API](#risk-scoring-api)
- [Remediation API](#remediation-api)
- [Reporting API](#reporting-api)
- [Validators API](#validators-api)
- [Usage Examples](#usage-examples)

---

## Scanners API

### AWSSecurityScanner

Main class for scanning AWS resources for security issues.

#### Constructor

```python
from scanners.aws_scanner import AWSSecurityScanner

scanner = AWSSecurityScanner(region: str = 'ap-southeast-2')
```

**Parameters**:
- `region` (str): AWS region to scan. Defaults to 'ap-southeast-2'

**Returns**: AWSSecurityScanner instance

**Raises**:
- `NoCredentialsError`: If AWS credentials are not configured
- `Exception`: If initialization fails

#### Methods

##### `scan_iam_users() -> List[Dict[str, Any]]`

Scans IAM users for security issues.

**Returns**: List of finding dictionaries

**Checks**:
- MFA not enabled
- Access keys older than 90 days
- Unused access keys
- Administrator access usage

**Example**:
```python
findings = scanner.scan_iam_users()
for finding in findings:
    print(f"{finding['severity']}: {finding['issue']}")
```

##### `scan_iam_password_policy() -> List[Dict[str, Any]]`

Checks IAM password policy compliance.

**Returns**: List of finding dictionaries

**Checks**:
- Minimum password length (14+ chars)
- Password complexity requirements
- Password expiration settings

##### `scan_s3_buckets() -> List[Dict[str, Any]]`

Audits S3 bucket configurations.

**Returns**: List of finding dictionaries

**Checks**:
- Public access block configuration
- Encryption settings
- Versioning enabled
- Access logging configured

**Example**:
```python
s3_findings = scanner.scan_s3_buckets()
critical = [f for f in s3_findings if f['severity'] == 'CRITICAL']
print(f"Found {len(critical)} critical S3 issues")
```

##### `scan_security_groups() -> List[Dict[str, Any]]`

Checks security group rules for open access.

**Returns**: List of finding dictionaries

**Checks**:
- Unrestricted inbound rules (0.0.0.0/0)
- Open sensitive ports (SSH, RDP, databases)

##### `scan_ec2_instances() -> List[Dict[str, Any]]`

Checks EC2 instances for security issues.

**Returns**: List of finding dictionaries

**Checks**:
- Unencrypted EBS volumes
- Public IP addresses
- IMDSv1 usage

##### `scan_cloudtrail() -> List[Dict[str, Any]]`

Checks CloudTrail logging configuration.

**Returns**: List of finding dictionaries

**Checks**:
- CloudTrail enabled
- Multi-region trails
- Log file validation
- S3 bucket logging

##### `scan_vpc_flow_logs() -> List[Dict[str, Any]]`

Checks VPC Flow Logs configuration.

**Returns**: List of finding dictionaries

**Checks**:
- Flow logs enabled for each VPC

##### `run_full_scan() -> List[Dict[str, Any]]`

Executes all security checks.

**Returns**: Combined list of all findings

**Example**:
```python
scanner = AWSSecurityScanner(region='us-east-1')
all_findings = scanner.run_full_scan()
print(f"Total findings: {len(all_findings)}")
```

---

## Risk Scoring API

### RiskScorer

Calculate risk scores and prioritize findings.

#### Constructor

```python
from utils.risk_scoring import RiskScorer

scorer = RiskScorer()
```

#### Methods

##### `calculate_finding_score(finding: Dict[str, Any]) -> float`

Calculate risk score for an individual finding.

**Parameters**:
- `finding` (dict): Security finding with severity, type, exposure, etc.

**Returns**: Risk score (0-100 scale)

**Algorithm**:
```
Risk Score = Base Severity × Exposure Multiplier ×
             Resource Type Multiplier × Risk Factors
```

**Example**:
```python
finding = {
    'severity': 'CRITICAL',
    'type': 'S3 Bucket',
    'exposure': 'public',
    'compliance': ['CIS 2.1.5']
}
risk_score = scorer.calculate_finding_score(finding)
print(f"Risk score: {risk_score}/100")
```

##### `calculate_account_score(findings: List[Dict[str, Any]]) -> float`

Calculate overall account security score.

**Parameters**:
- `findings` (list): List of all security findings

**Returns**: Security score (0-100, higher is better)

**Example**:
```python
security_score = scorer.calculate_account_score(all_findings)
print(f"Account security score: {security_score}/100")
```

##### `get_security_grade(score: float) -> str`

Convert security score to letter grade.

**Parameters**:
- `score` (float): Security score (0-100)

**Returns**: Letter grade (A+ to F)

**Grade Scale**:
- 95-100: A+
- 90-94:  A
- 85-89:  A-
- 80-84:  B+
- 75-79:  B
- 70-74:  B-
- 60-69:  C
- 40-59:  D
- <40:    F

##### `prioritize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Sort findings by risk score (highest first).

**Parameters**:
- `findings` (list): List of security findings

**Returns**: Sorted findings with risk_score added

**Example**:
```python
prioritized = scorer.prioritize_findings(findings)
top_10 = prioritized[:10]  # Get top 10 riskiest findings
```

##### `generate_summary_stats(findings: List[Dict[str, Any]]) -> Dict[str, Any]`

Generate executive summary statistics.

**Parameters**:
- `findings` (list): List of security findings

**Returns**: Dictionary with summary statistics

**Returned Fields**:
- `total_findings`: Total number of findings
- `critical`, `high`, `medium`, `low`: Counts by severity
- `security_score`: Overall security score
- `security_grade`: Letter grade
- `average_risk_score`: Average risk across findings
- `top_risks`: List of top 10 highest risk findings
- `findings_by_type`: Count by resource type
- `compliance_violations`: Count by compliance control
- `immediate_action_required`: Count of critical+high

---

## Remediation API

### AWSRemediation

Automated remediation for AWS security issues.

#### Constructor

```python
from remediation.aws_remediation import AWSRemediation

remediator = AWSRemediation(
    region: str = 'ap-southeast-2',
    dry_run: bool = True
)
```

**Parameters**:
- `region` (str): AWS region
- `dry_run` (bool): If True, only simulates changes (default: True)

**Safety**: Always starts in dry-run mode for safety

#### Methods

##### `enable_s3_encryption(bucket_name: str) -> bool`

Enable server-side encryption on S3 bucket.

**Parameters**:
- `bucket_name` (str): Name of the S3 bucket

**Returns**: True if successful, False otherwise

**Validation**: Validates bucket name format

**Example**:
```python
# Dry-run mode (safe)
remediator = AWSRemediation(dry_run=True)
remediator.enable_s3_encryption('my-bucket')

# Live mode (requires confirmation)
remediator_live = AWSRemediation(dry_run=False)
remediator_live.enable_s3_encryption('my-bucket')
```

##### `enable_s3_versioning(bucket_name: str) -> bool`

Enable versioning on S3 bucket.

**Parameters**:
- `bucket_name` (str): Name of the S3 bucket

**Returns**: True if successful, False otherwise

##### `block_s3_public_access(bucket_name: str) -> bool`

Block all public access to S3 bucket.

**Parameters**:
- `bucket_name` (str): Name of the S3 bucket

**Returns**: True if successful, False otherwise

##### `enable_s3_logging(bucket_name: str, target_bucket: str) -> bool`

Enable S3 access logging.

**Parameters**:
- `bucket_name` (str): Bucket to enable logging on
- `target_bucket` (str): Bucket to store logs

**Returns**: True if successful, False otherwise

##### `restrict_security_group_rule(sg_id: str, port: int, protocol: str = 'tcp', new_cidr: str = '10.0.0.0/8') -> bool`

Restrict security group rule from 0.0.0.0/0 to specific CIDR.

**Parameters**:
- `sg_id` (str): Security group ID
- `port` (int): Port number
- `protocol` (str): Protocol (tcp/udp/icmp)
- `new_cidr` (str): New CIDR range to allow

**Returns**: True if successful, False otherwise

**Validation**: Validates SG ID, port number, and CIDR format

##### `log_action(action: str, resource: str, status: str, details: str = '')`

Log remediation action for audit trail.

**Parameters**:
- `action` (str): Action performed
- `resource` (str): Resource affected
- `status` (str): Status (success/failed/simulated)
- `details` (str): Additional details

---

## Reporting API

### SecurityReportGenerator

Generate security reports in multiple formats.

#### Constructor

```python
from reporting.report_generator import SecurityReportGenerator

reporter = SecurityReportGenerator(
    template_dir: str = 'reporting/templates'
)
```

**Parameters**:
- `template_dir` (str): Directory containing Jinja2 templates

#### Methods

##### `generate_html_report(findings: List, stats: Dict, output_path: str, account_id: str = '', region: str = '') -> bool`

Generate comprehensive HTML report.

**Parameters**:
- `findings` (list): Security findings
- `stats` (dict): Summary statistics
- `output_path` (str): Output file path
- `account_id` (str): AWS account ID (optional)
- `region` (str): AWS region (optional)

**Returns**: True if successful, False otherwise

**Example**:
```python
reporter = SecurityReportGenerator()
success = reporter.generate_html_report(
    findings=all_findings,
    stats=summary_stats,
    output_path='security_report.html',
    account_id='123456789012',
    region='us-east-1'
)
```

##### `export_to_json(findings: List, stats: Dict, output_path: str) -> bool`

Export findings to JSON format.

**Parameters**:
- `findings` (list): Security findings
- `stats` (dict): Summary statistics
- `output_path` (str): Output file path

**Returns**: True if successful, False otherwise

##### `export_to_csv(findings: List, output_path: str) -> bool`

Export findings to CSV format.

**Parameters**:
- `findings` (list): Security findings
- `output_path` (str): Output file path

**Returns**: True if successful, False otherwise

##### `generate_all_reports(findings: List, stats: Dict, base_filename: str = 'security_audit', account_id: str = '', region: str = '') -> Dict`

Generate all report formats at once.

**Parameters**:
- `findings` (list): Security findings
- `stats` (dict): Summary statistics
- `base_filename` (str): Base filename (without extension)
- `account_id` (str): AWS account ID (optional)
- `region` (str): AWS region (optional)

**Returns**: Dictionary mapping format names to file paths

**Example**:
```python
report_paths = reporter.generate_all_reports(
    findings=all_findings,
    stats=summary_stats,
    base_filename='aws_audit_2025_11_14'
)
print(f"HTML: {report_paths['html']}")
print(f"JSON: {report_paths['json']}")
print(f"CSV: {report_paths['csv']}")
```

---

## Validators API

### Validation Functions

Input validation functions to ensure data integrity and security.

```python
from utils.validators import *
```

#### `validate_s3_bucket_name(bucket_name: str) -> bool`

Validate S3 bucket name according to AWS rules.

**Rules**:
- 3-63 characters
- Lowercase letters, numbers, hyphens, periods
- Must start/end with lowercase letter or number
- Cannot be formatted as IP address

**Example**:
```python
is_valid = validate_s3_bucket_name('my-bucket-123')  # True
is_valid = validate_s3_bucket_name('My-Bucket')  # False (uppercase)
```

#### `validate_cidr_block(cidr: str) -> bool`

Validate CIDR block format.

**Example**:
```python
is_valid = validate_cidr_block('192.168.1.0/24')  # True
is_valid = validate_cidr_block('256.1.1.1/24')  # False (invalid IP)
```

#### `validate_port_number(port: int) -> bool`

Validate port number (0-65535).

#### `validate_port_range(from_port: int, to_port: int) -> bool`

Validate port range.

#### `validate_security_group_id(sg_id: str) -> bool`

Validate AWS security group ID format.

**Example**:
```python
is_valid = validate_security_group_id('sg-12345678')  # True
```

#### `validate_vpc_id(vpc_id: str) -> bool`

Validate AWS VPC ID format.

#### `validate_instance_id(instance_id: str) -> bool`

Validate AWS EC2 instance ID format.

#### `validate_aws_region(region: str) -> bool`

Validate AWS region name.

#### `sanitize_resource_name(name: str, max_length: int = 255) -> Optional[str]`

Sanitize resource name by removing dangerous characters.

**Returns**: Sanitized name or None if invalid

---

## Usage Examples

### Complete Scanning Workflow

```python
from scanners.aws_scanner import AWSSecurityScanner
from utils.risk_scoring import RiskScorer
from reporting.report_generator import SecurityReportGenerator

# 1. Initialize scanner
scanner = AWSSecurityScanner(region='us-east-1')

# 2. Run scan
findings = scanner.run_full_scan()

# 3. Calculate risk scores
scorer = RiskScorer()
prioritized = scorer.prioritize_findings(findings)
stats = scorer.generate_summary_stats(prioritized)

# 4. Generate report
reporter = SecurityReportGenerator()
reporter.generate_html_report(
    findings=prioritized,
    stats=stats,
    output_path='report.html',
    account_id=scanner.account_id,
    region=scanner.region
)

print(f"Security Score: {stats['security_score']}/100 ({stats['security_grade']})")
```

### Custom Filtering

```python
# Filter critical findings only
critical = [f for f in findings if f['severity'] == 'CRITICAL']

# Filter S3-specific issues
s3_issues = [f for f in findings if f['type'] == 'S3 Bucket']

# Filter high-risk findings
high_risk = [f for f in findings if f.get('risk_score', 0) >= 70]

# Filter compliance violations
cis_violations = [
    f for f in findings
    if any('CIS' in str(c) for c in f.get('compliance', []))
]
```

### Safe Remediation Workflow

```python
from remediation.aws_remediation import AWSRemediation

# Step 1: Test with dry-run
remediator = AWSRemediation(dry_run=True)
remediator.enable_s3_encryption('my-bucket')
remediator.enable_s3_versioning('my-bucket')

# Step 2: Review logs
for action in remediator.remediation_log:
    print(f"{action['action']} on {action['resource']}: {action['status']}")

# Step 3: Apply if safe (requires explicit confirmation)
remediator_live = AWSRemediation(dry_run=False)
# ... apply changes
```

### Export to Multiple Formats

```python
reporter = SecurityReportGenerator()

# HTML report
reporter.generate_html_report(findings, stats, 'report.html')

# JSON export (for automation)
reporter.export_to_json(findings, stats, 'findings.json')

# CSV export (for spreadsheets)
reporter.export_to_csv(findings, 'findings.csv')

# All formats at once
report_paths = reporter.generate_all_reports(findings, stats, 'audit')
```

---

## Error Handling

All API methods handle errors gracefully and return appropriate values:

```python
try:
    findings = scanner.scan_s3_buckets()
except NoCredentialsError:
    print("AWS credentials not configured")
except ClientError as e:
    print(f"AWS API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Type Safety

All modules include type hints for better IDE support:

```python
from typing import List, Dict, Any

def process_findings(findings: List[Dict[str, Any]]) -> int:
    return len(findings)
```

---

**Last Updated**: 2025-11-14
**Version**: 2.0.0
