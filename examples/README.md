# Examples

This directory contains example scripts demonstrating how to use the Cloud Security Toolkit programmatically.

## Available Examples

### 1. `basic_scan.py` - Basic AWS Security Scan

Demonstrates:
- Initializing the AWS scanner
- Running a full security scan
- Calculating risk scores
- Generating HTML reports

**Usage:**
```bash
python examples/basic_scan.py
```

**Prerequisites:**
- AWS credentials configured
- Required permissions for scanning

### 2. `remediation_example.py` - Safe Remediation Workflow

Demonstrates:
- Using dry-run mode safely
- Testing remediations before applying
- Reviewing remediation logs
- Best practices for live remediation

**Usage:**
```bash
python examples/remediation_example.py
```

**Prerequisites:**
- AWS credentials configured
- Remediation permissions (for live mode)

### 3. `custom_scan.py` - Custom Scanning Logic

Demonstrates:
- Scanning specific AWS services
- Custom filtering of findings
- Generating custom reports
- Integrating with external systems

**Usage:**
```bash
python examples/custom_scan.py
```

## Running Examples

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # or set environment variables:
   export AWS_ACCESS_KEY_ID="your-key"
   export AWS_SECRET_ACCESS_KEY="your-secret"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

3. **Run an example:**
   ```bash
   python examples/basic_scan.py
   ```

### Using as Templates

These examples can be used as templates for:

- **CI/CD Integration**: Integrate into your pipeline
- **Scheduled Scans**: Run via cron or scheduled tasks
- **Custom Workflows**: Adapt to your specific needs
- **Automation Scripts**: Build on these foundations

## Integration Examples

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh 'python examples/basic_scan.py'
                archiveArtifacts artifacts: 'security_report.html'
            }
        }
    }
}
```

### GitHub Actions

```yaml
name: Security Scan
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security scan
        run: python examples/basic_scan.py
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security_report.html
```

### Cron Job

```bash
# Add to crontab -e
# Run security scan daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/examples/basic_scan.py
```

## Best Practices

1. **Always Test First**: Use dry-run mode for remediation
2. **Review Findings**: Don't blindly trust automated results
3. **Secure Credentials**: Never hardcode AWS credentials
4. **Log Everything**: Keep audit trails of all scans
5. **Regular Scans**: Schedule periodic security audits

## Support

For questions or issues:
- Check the main [README](../README.md)
- Review [CONTRIBUTING](../CONTRIBUTING.md) guidelines
- Open an [issue](https://github.com/Raoof128/cloud-security-toolkit/issues)

## License

These examples are provided under the same MIT License as the main project.
