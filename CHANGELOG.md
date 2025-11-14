# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-14

### Added
- **Type hints** throughout entire codebase (PEP 484 compliance)
- **Input validation module** (`utils/validators.py`) with comprehensive security checks
- **Professional HTML report template** with responsive design and charts
- **Comprehensive test suite** with pytest (validators, risk scoring)
- **API pagination** for all AWS resource scanners
- **Module docstrings** for all packages
- **pytest.ini** configuration with coverage reporting
- **CHANGELOG.md** for version tracking
- **CONTRIBUTING.md** with contribution guidelines
- **SECURITY.md** with security policy
- **CI/CD workflows** for automated testing
- **Issue and PR templates** for better collaboration

### Changed
- **Cleaned dependencies** - Removed unused Azure/GCP SDKs, reportlab, python-dotenv, cryptography, tqdm
- **Improved error handling** throughout codebase
- **Enhanced documentation** in README with v2.0 improvements section
- **Better code organization** with proper module exports

### Fixed
- **API pagination** - Fixed missing resources in large AWS accounts (IAM users, security groups, EC2 instances, VPCs)
- **Missing HTML template** - Added professional responsive template
- **Silent exception handling** - Improved error reporting
- **Input validation** - Prevents injection attacks in remediation functions

### Security
- Input validation for S3 bucket names, CIDR blocks, ports
- Validation for AWS resource IDs (security groups, VPCs, instances)
- Resource name sanitization to prevent injection
- Type safety improvements reduce runtime vulnerabilities

## [1.0.0] - 2024-11-13

### Added
- Initial release with AWS security scanning
- IAM, S3, EC2, CloudTrail, VPC, Security Group scanning
- Risk scoring and prioritization engine
- Automated remediation capabilities
- Multiple report formats (HTML, JSON, CSV, Markdown, Text)
- Demo mode for testing without AWS credentials
- CIS Benchmarks and ASD Essential Eight compliance mapping
- Dry-run mode for safe remediation testing

[2.0.0]: https://github.com/Raoof128/cloud-security-toolkit/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/Raoof128/cloud-security-toolkit/releases/tag/v1.0.0
