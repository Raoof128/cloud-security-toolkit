# Cloud Security Audit & Hardening Toolkit

<div align="center">

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/Raoof128/cloud-security-toolkit)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub issues](https://img.shields.io/github/issues/Raoof128/cloud-security-toolkit)](https://github.com/Raoof128/cloud-security-toolkit/issues)
[![GitHub stars](https://img.shields.io/github/stars/Raoof128/cloud-security-toolkit)](https://github.com/Raoof128/cloud-security-toolkit/stargazers)

[![Tests](https://github.com/Raoof128/cloud-security-toolkit/workflows/Tests/badge.svg)](https://github.com/Raoof128/cloud-security-toolkit/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Raoof128/cloud-security-toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/Raoof128/cloud-security-toolkit)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://github.com/Raoof128/cloud-security-toolkit/tree/main/docs)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://github.com/Raoof128/cloud-security-toolkit/blob/main/Dockerfile)

</div>

A comprehensive automated cloud security auditing and hardening toolkit that scans AWS, Azure, and GCP environments for misconfigurations, security vulnerabilities, and compliance violations.

**🎯 Portfolio-Ready | 🔒 Defensive Security | 🇦🇺 Australian Compliance | ✅ Production-Tested**

## Features

- **Comprehensive Security Scanning**: Audit IAM, S3, EC2, Security Groups, CloudTrail, VPC, and more
- **Risk Scoring & Prioritization**: Intelligent risk assessment with 0-100 security scores
- **Compliance Frameworks**: CIS Benchmarks, ASD Essential Eight, NIST alignment
- **Automated Remediation**: Fix common security issues automatically with dry-run support
- **Multiple Report Formats**: HTML, JSON, CSV, Markdown, and text summaries
- **Lightweight**: No VMs required, runs on standard laptops (8GB+ RAM)
- **Cloud-Native**: Leverages cloud provider APIs and SDKs

## Quick Start

### Demo Mode (No AWS Required!)

Try the toolkit without AWS credentials:

```bash
# Clone the repository
git clone https://github.com/Raoof128/cloud-security-toolkit.git
cd cloud-security-toolkit

# Install basic dependencies (no AWS SDK required for demo)
pip install jinja2 pandas pyyaml colorama

# Run demo mode with sample data
python cloud_security_audit.py --demo --output demo_report.html

# View the report
open demo_report.html  # macOS
xdg-open demo_report.html  # Linux
```

### Full Installation with AWS

```bash
# Install all dependencies including AWS SDK
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# Enter your Access Key, Secret Key, and preferred region (e.g., ap-southeast-2)

# Scan your AWS account
python cloud_security_audit.py --provider aws --output report.html
```

## Usage Examples

### Demo Mode

```bash
# Generate sample report (no AWS account needed)
python cloud_security_audit.py --demo

# Generate all report formats in demo mode
python cloud_security_audit.py --demo --format all --output demo_audit

# Verbose demo mode with executive summary
python cloud_security_audit.py --demo --verbose
```

### Scanning

```bash
# Scan with all report formats
python cloud_security_audit.py --provider aws --format all --output audit

# Scan specific region
python cloud_security_audit.py --provider aws --region us-east-1

# Verbose output with executive summary
python cloud_security_audit.py --provider aws --verbose
```

### Remediation

```bash
# Test remediation (dry-run, no changes)
python cloud_security_audit.py --provider aws --remediate --dry-run

# Apply automated fixes (requires confirmation)
python cloud_security_audit.py --provider aws --remediate

# Scan and remediate in one command
python cloud_security_audit.py --provider aws --remediate --dry-run --output report.html
```

### Export Formats

```bash
# Export to JSON
python cloud_security_audit.py --provider aws --format json --output findings.json

# Export to CSV for Excel/spreadsheets
python cloud_security_audit.py --provider aws --format csv --output findings.csv

# Generate all formats at once
python cloud_security_audit.py --provider aws --format all --output security_audit
```

## What Gets Scanned

### AWS Security Checks

#### IAM (Identity & Access Management)
- ✅ MFA enabled on all users
- ✅ Root account MFA
- ✅ Access key rotation (90 days)
- ✅ Unused access keys
- ✅ Password policy compliance
- ✅ Administrator access usage

#### S3 (Storage)
- ✅ Public access blocked
- ✅ Encryption enabled
- ✅ Versioning enabled
- ✅ Access logging configured
- ✅ Bucket policies reviewed

#### Security Groups
- ✅ No unrestricted inbound rules (0.0.0.0/0)
- ✅ SSH/RDP restricted
- ✅ Database ports not exposed
- ✅ Unused security groups

#### EC2 (Compute)
- ✅ EBS volumes encrypted
- ✅ IMDSv2 enforced
- ✅ Public IP usage reviewed
- ✅ Security group compliance

#### CloudTrail (Logging)
- ✅ CloudTrail enabled
- ✅ Multi-region trails
- ✅ Log file validation
- ✅ S3 logging configured

#### VPC (Network)
- ✅ Flow logs enabled
- ✅ Network ACLs reviewed
- ✅ Subnet configurations

## Compliance Frameworks

The toolkit checks against industry-standard compliance frameworks:

- **CIS AWS Foundations Benchmark v1.4**
- **ASD Essential Eight** (Australian Signals Directorate)
- **NIST Cybersecurity Framework** (alignment)

Each finding includes relevant compliance control mappings.

## Risk Scoring

Findings are scored using a multi-factor risk model:

- **Severity**: CRITICAL (10), HIGH (7), MEDIUM (4), LOW (2)
- **Exposure**: Public (2.0x), Internet-facing (1.8x), Internal (1.0x)
- **Resource Type**: IAM Root (1.5x), S3 Bucket (1.3x), CloudTrail (1.4x)
- **Compliance Impact**: +20% for compliance violations
- **Data Sensitivity**: +50% for PII/sensitive data

**Security Score**: 0-100 scale (higher is better)
- 80-100: Excellent (Grade A)
- 60-79: Good (Grade B)
- 40-59: Fair (Grade C)
- 0-39: Poor (Grade D-F)

## Automated Remediation

The toolkit can automatically fix common security issues:

### S3 Remediations
- Enable AES256 encryption
- Enable versioning
- Block public access
- Enable access logging

### Security Group Remediations
- Restrict 0.0.0.0/0 rules to specific CIDRs
- Remove dangerous open ports

### EC2 Remediations
- Enforce IMDSv2

### CloudTrail Remediations
- Enable CloudTrail
- Enable log file validation
- Configure multi-region trails

### VPC Remediations
- Enable VPC Flow Logs

**Safety Features**:
- **Dry-run mode** (default): Test changes without applying
- **Confirmation prompts** for live mode
- **Detailed audit logging** of all changes
- **Rollback guidance** in documentation

## Project Structure

```
cloud-security-toolkit/
├── cloud_security_audit.py      # Main CLI interface
├── requirements.txt              # Python dependencies
├── config/                       # Configuration files
│   ├── aws_config.yaml
│   ├── azure_config.yaml
│   ├── gcp_config.yaml
│   └── .env.template
├── scanners/                     # Security scanners
│   ├── aws_scanner.py
│   ├── azure_scanner.py
│   └── gcp_scanner.py
├── compliance/                   # Compliance frameworks
│   ├── cis_benchmarks.py
│   └── asd_essential_eight.py
├── remediation/                  # Automated fixes
│   ├── aws_remediation.py
│   ├── azure_remediation.py
│   └── gcp_remediation.py
├── reporting/                    # Report generation
│   ├── report_generator.py
│   └── templates/
│       └── security_report.html
├── utils/                        # Utilities
│   ├── risk_scoring.py
│   └── credential_manager.py
├── tests/                        # Unit tests
├── docs/                         # Documentation
└── reports/                      # Generated reports
```

## Requirements

- **Python**: 3.10+
- **AWS CLI**: Configured with credentials
- **RAM**: 8GB+ recommended
- **Permissions**: Read access to AWS services (see IAM policy below)

### Required AWS Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:List*",
        "iam:Get*",
        "s3:List*",
        "s3:Get*",
        "ec2:Describe*",
        "cloudtrail:Describe*",
        "cloudtrail:Get*",
        "cloudtrail:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

For remediation, additional write permissions are required (see docs/permissions.md).

## Configuration

### AWS Credentials

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-southeast-2"

# Option 3: .env file
cp config/.env.template .env
# Edit .env with your credentials
```

### Customization

Edit configuration files in `config/` to customize:
- Services to scan
- Compliance frameworks
- Risk scoring weights
- Remediation policies

## Security Considerations

- **Credentials**: Never commit credentials to version control
- **Permissions**: Use least-privilege IAM policies
- **Audit Logs**: All actions are logged for compliance
- **Read-Only**: Scanning requires only read permissions
- **Dry-Run First**: Always test remediations in dry-run mode

## Troubleshooting

### No credentials found
```bash
# Configure AWS CLI
aws configure

# Test connectivity
aws sts get-caller-identity
```

### Permission errors
- Ensure IAM user has required permissions
- Check AWS CloudTrail for denied API calls

### Module not found
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import boto3; print(boto3.__version__)"
```

## Recent Improvements

### Version 2.0 - Major Quality & Security Update

**Code Quality:**
- ✅ Added type hints throughout codebase (PEP 484)
- ✅ Comprehensive input validation for all remediation functions
- ✅ Professional HTML report template with responsive design
- ✅ Module docstrings and improved documentation

**Security Enhancements:**
- ✅ Input validation prevents injection attacks
- ✅ Secure validators for S3 buckets, CIDR blocks, ports, AWS resource IDs
- ✅ Sanitization of resource names
- ✅ Type safety reduces runtime errors

**Bug Fixes:**
- ✅ Fixed API pagination (prevents missing resources in large AWS accounts)
- ✅ Fixed missing HTML template issue
- ✅ Improved error handling

**Testing:**
- ✅ Comprehensive test suite with pytest
- ✅ Unit tests for validators and risk scoring
- ✅ Test coverage reporting configured

**Dependencies:**
- ✅ Removed unused Azure/GCP SDKs (commented for future use)
- ✅ Cleaner dependency tree
- ✅ Faster installation

## Roadmap

- [x] AWS scanning (IAM, S3, EC2, CloudTrail)
- [x] Risk scoring and prioritization
- [x] Automated remediation
- [x] Multiple report formats
- [x] Type hints and input validation
- [x] Comprehensive test suite
- [ ] Azure scanning (planned)
- [ ] GCP scanning (planned)
- [ ] CI/CD integration
- [ ] Scheduled scanning
- [ ] Dashboard UI
- [ ] Email notifications

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_validators.py -v
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for security assessment and hardening purposes only. Always:
- Test in non-production environments first
- Review all findings and remediations
- Follow your organization's change management processes
- Maintain backups before applying changes

## Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Questions**: Discussions tab

## Author

Built for cloud security professionals and DevSecOps engineers.

## Acknowledgments

- CIS Benchmarks for security best practices
- AWS Security Best Practices documentation
- ASD Essential Eight framework
- Open source security community
