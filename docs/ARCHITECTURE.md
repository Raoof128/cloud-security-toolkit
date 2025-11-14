# Architecture Documentation

## Overview

The Cloud Security Toolkit is designed as a modular, extensible security auditing framework for cloud infrastructure. The architecture follows clean separation of concerns and SOLID principles.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                  (cloud_security_audit.py)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼─────────┐           ┌────────▼─────────┐
│    Scanners      │           │   Remediation    │
│  - aws_scanner   │           │ - aws_remediation│
│  - azure_scanner │           │ - azure_remediation
│  - gcp_scanner   │           │ - gcp_remediation│
└────────┬─────────┘           └────────┬─────────┘
         │                               │
         │         ┌─────────────────────┤
         │         │                     │
┌────────▼─────────▼──┐         ┌───────▼──────────┐
│   Risk Scoring      │         │    Reporting     │
│  - calculate_risk   │         │  - HTML reports  │
│  - prioritize       │         │  - JSON export   │
│  - compliance_score │         │  - CSV export    │
└────────┬────────────┘         └───────┬──────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                ┌────────▼─────────┐
                │   Utilities      │
                │  - validators    │
                │  - config        │
                │  - credentials   │
                └──────────────────┘
```

## Module Architecture

### 1. Scanners Module (`scanners/`)

**Purpose**: Discover and audit cloud resources for security issues

**Components**:
- `aws_scanner.py` - AWS security scanner
  - IAM scanning
  - S3 bucket auditing
  - Security group analysis
  - EC2 instance checks
  - CloudTrail validation
  - VPC configuration review

**Design Pattern**: Strategy Pattern
- Each scanner implements a common interface
- Scanners are independent and can be run individually
- Findings follow a standardized format

**Key Features**:
- API pagination for large accounts
- Parallel scanning (planned)
- Incremental scanning support (planned)
- Multi-region support

**Data Flow**:
```
Scanner → Cloud API → Parse Response → Validate → Generate Finding
```

### 2. Risk Scoring Module (`utils/risk_scoring.py`)

**Purpose**: Calculate risk scores and prioritize findings

**Algorithm**:
```python
Risk Score = (Base Severity × Exposure Multiplier ×
              Resource Type Multiplier × Risk Factors)

Where:
- Base Severity: CRITICAL=10, HIGH=7, MEDIUM=4, LOW=2
- Exposure Multiplier: public=2.0, internet-facing=1.8, internal=1.0
- Resource Type Multiplier: IAM Root=1.5, S3=1.3, etc.
- Risk Factors: Compliance violations, PII data, authentication issues
```

**Security Score**:
```python
Security Score = 100 - (Total Risk / Max Possible Risk × 100)

Grade Scale:
- 95-100: A+
- 90-94:  A
- 80-89:  B
- 60-79:  C
- <60:    D-F
```

### 3. Remediation Module (`remediation/`)

**Purpose**: Automatically fix security issues

**Safety Architecture**:
```
User Request → Validate Input → Check Dry-Run Mode
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                    Dry-Run                      Live Mode
                        │                           │
                   Simulate → Log               Execute → Log
                        │                           │
                   Return Status              Return Status
```

**Safety Features**:
- Input validation for all parameters
- Dry-run mode by default
- Audit logging of all actions
- Rollback guidance in logs
- Confirmation prompts for dangerous operations

### 4. Reporting Module (`reporting/`)

**Purpose**: Generate security reports in multiple formats

**Report Types**:
- **HTML**: Interactive, styled reports with charts
- **JSON**: Machine-readable for automation
- **CSV**: Spreadsheet-compatible exports
- **Markdown**: Documentation-friendly summaries
- **Text**: Plain-text summaries

**Template Engine**: Jinja2
- Responsive design
- Chart visualizations
- Severity color coding
- Compliance mapping display

### 5. Validation Module (`utils/validators.py`)

**Purpose**: Validate inputs to prevent injection and errors

**Validators**:
- S3 bucket name validation (AWS rules)
- CIDR block validation (IPv4)
- Port number validation (0-65535)
- AWS resource ID validation (format checking)
- Region name validation (known regions)
- Input sanitization

**Security Benefits**:
- Prevents command injection
- Validates before API calls
- Reduces error rate
- Type-safe operations

## Data Models

### Finding Object

```python
Finding = {
    'resource': str,          # Resource name/ID
    'type': str,              # Resource type (e.g., 'S3 Bucket')
    'severity': str,          # CRITICAL, HIGH, MEDIUM, LOW
    'issue': str,             # Description of the issue
    'recommendation': str,    # How to fix it
    'compliance': List[str],  # Compliance frameworks affected
    'exposure': str,          # public, internet-facing, internal
    'risk_score': float       # Calculated risk score (0-100)
}
```

### Statistics Object

```python
Stats = {
    'total_findings': int,
    'critical': int,
    'high': int,
    'medium': int,
    'low': int,
    'security_score': float,
    'security_grade': str,
    'average_risk_score': float,
    'top_risks': List[Finding],
    'findings_by_type': Dict[str, int],
    'compliance_violations': Dict[str, int],
    'immediate_action_required': int
}
```

## Design Patterns Used

### 1. Strategy Pattern
**Where**: Scanner implementations
**Why**: Easy to add new cloud providers without modifying existing code

### 2. Factory Pattern
**Where**: Report generation
**Why**: Create different report types based on format parameter

### 3. Template Method Pattern
**Where**: Base scanner logic
**Why**: Define skeleton of scanning algorithm, let subclasses override steps

### 4. Singleton Pattern
**Where**: Configuration loading (planned)
**Why**: Single instance of configuration throughout application

## Configuration Architecture

### Configuration Hierarchy

```
1. Environment Variables (highest priority)
2. .env file
3. config/*.yaml files
4. Default values (lowest priority)
```

### Configuration Files

- `config/aws_config.yaml` - AWS-specific settings
- `config/azure_config.yaml` - Azure-specific settings (planned)
- `config/gcp_config.yaml` - GCP-specific settings (planned)
- `.env` - Sensitive credentials (not in repo)

## Security Architecture

### Credential Management

```
Priority Order:
1. Environment variables
2. AWS credential file (~/.aws/credentials)
3. IAM role (when running on EC2/ECS/Lambda)
4. Instance profile

Never:
- Hardcoded credentials
- Credentials in version control
- Credentials in logs
```

### Input Validation

All external inputs are validated before use:
- User command-line arguments
- Configuration file values
- API responses
- File paths

### Secure Defaults

- Read-only mode by default
- Dry-run for remediation by default
- TLS for all API communication
- Minimal IAM permissions required

## Performance Considerations

### Optimization Strategies

1. **API Pagination**
   - Handles accounts with >1000 resources
   - Prevents timeouts
   - Memory efficient

2. **Parallel Scanning** (Planned)
   - Thread pool for independent checks
   - Rate limiting to avoid throttling
   - Graceful failure handling

3. **Caching** (Planned)
   - Cache IAM credential reports
   - Cache bucket locations
   - TTL-based invalidation

4. **Incremental Scanning** (Planned)
   - Track last scan timestamp
   - Only scan changed resources
   - Faster re-scans

## Extensibility

### Adding a New Cloud Provider

1. Create scanner: `scanners/<provider>_scanner.py`
2. Implement required methods:
   - `scan_<service>()`
   - `run_full_scan()`
3. Create remediation: `remediation/<provider>_remediation.py`
4. Add configuration: `config/<provider>_config.yaml`
5. Update CLI to support new provider

### Adding a New Security Check

1. Add method to appropriate scanner
2. Generate finding in standard format
3. Include compliance mappings
4. Add test cases
5. Document in README

### Adding a New Report Format

1. Add method to `SecurityReportGenerator`
2. Create template (if needed)
3. Handle data serialization
4. Add CLI option
5. Update documentation

## Testing Architecture

### Test Layers

1. **Unit Tests** (`tests/test_*.py`)
   - Test individual functions
   - Mock AWS API calls
   - Fast execution

2. **Integration Tests** (Planned)
   - Test full workflows
   - Use moto for AWS mocking
   - Test multiple components together

3. **End-to-End Tests** (Planned)
   - Test complete scan workflows
   - Use test AWS account
   - Validate reports

### Test Coverage Goals

- Core modules: >90%
- Validators: 100%
- Risk scoring: >85%
- Overall: >80%

## Deployment Architecture

### Supported Deployment Models

1. **Local CLI**
   - Direct Python execution
   - Installed via pip
   - Manual credential configuration

2. **Docker Container** (Planned)
   - Containerized execution
   - Portable across environments
   - Credential injection via env vars

3. **Lambda Function** (Planned)
   - Serverless execution
   - Scheduled scans
   - CloudWatch integration

4. **CI/CD Pipeline**
   - GitHub Actions integration
   - Jenkins plugin (planned)
   - GitLab CI support (planned)

## Error Handling Strategy

### Error Hierarchy

```
BaseException
└── Exception
    ├── ValueError (invalid inputs)
    ├── ClientError (AWS API errors)
    ├── ConfigurationError (config issues)
    └── ValidationError (validation failures)
```

### Error Response Pattern

```python
try:
    # Operation
    result = perform_operation()
    log_action('operation', 'success')
    return result
except SpecificError as e:
    log_action('operation', 'failed', str(e))
    # Attempt recovery or fail gracefully
    return None
```

## Logging Architecture

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (operation failures)
- **CRITICAL**: Critical errors (system failures)

### Log Outputs

1. Console (stdout) - User-facing messages
2. File (optional) - Persistent audit trail
3. Syslog (planned) - System integration

## Future Architectural Improvements

1. **Plugin System**
   - Dynamic scanner loading
   - Third-party extensions
   - Custom compliance frameworks

2. **Database Backend**
   - Store scan history
   - Track trends over time
   - Compare scans

3. **API Server**
   - RESTful API
   - Web dashboard
   - Multi-user support

4. **Distributed Scanning**
   - Multi-region parallel scans
   - Load balancing
   - Result aggregation

## Dependencies

### Core Dependencies
- `boto3` - AWS SDK
- `botocore` - AWS SDK core
- `jinja2` - Template engine
- `pandas` - Data manipulation
- `pyyaml` - Configuration parsing

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `moto` - AWS mocking

## Version History

- **v2.0.0** - Type hints, validation, testing, professional infrastructure
- **v1.0.0** - Initial release with AWS scanning

## References

- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [ASD Essential Eight](https://www.cyber.gov.au/acsc/view-all-content/essential-eight)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Last Updated**: 2025-11-14
**Version**: 2.0.0
