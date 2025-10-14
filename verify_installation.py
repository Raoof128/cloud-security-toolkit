#!/usr/bin/env python3
"""
Installation Verification Script
Checks all dependencies and configurations
"""
import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        print("✅ Python version is compatible (3.10+)")
        return True
    else:
        print("❌ Python 3.10+ required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

def check_dependencies():
    """Check required Python packages"""
    print_header("Dependency Check")

    required_packages = [
        'boto3',
        'jinja2',
        'pandas',
        'pyyaml',
        'colorama'
    ]

    all_installed = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package:20s} installed")
        except ImportError:
            print(f"❌ {package:20s} NOT installed")
            all_installed = False

    if not all_installed:
        print("\n⚠️  Some dependencies are missing. Install them with:")
        print("   pip install -r requirements.txt")

    return all_installed

def check_aws_credentials():
    """Check AWS credentials"""
    print_header("AWS Credentials Check")

    # Check environment variables
    has_env_creds = all([
        os.getenv('AWS_ACCESS_KEY_ID'),
        os.getenv('AWS_SECRET_ACCESS_KEY')
    ])

    if has_env_creds:
        print("✅ AWS credentials found in environment variables")
        return True

    # Check AWS credentials file
    aws_creds_file = os.path.expanduser('~/.aws/credentials')
    if os.path.exists(aws_creds_file):
        print(f"✅ AWS credentials file found: {aws_creds_file}")
        return True

    print("❌ AWS credentials not found")
    print("\n   Configure credentials using one of these methods:")
    print("   1. Run: aws configure")
    print("   2. Set environment variables:")
    print("      export AWS_ACCESS_KEY_ID='your-key'")
    print("      export AWS_SECRET_ACCESS_KEY='your-secret'")
    print("   3. Create ~/.aws/credentials file")

    return False

def check_aws_connectivity():
    """Test AWS connection"""
    print_header("AWS Connectivity Check")

    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()

            print(f"✅ Successfully connected to AWS")
            print(f"   Account ID: {identity['Account']}")
            print(f"   User ARN: {identity['Arn']}")
            return True

        except NoCredentialsError:
            print("❌ AWS credentials not configured")
            return False
        except ClientError as e:
            print(f"❌ AWS connection error: {e}")
            return False

    except ImportError:
        print("⚠️  boto3 not installed - skipping AWS connectivity test")
        return False

def check_file_structure():
    """Check project file structure"""
    print_header("File Structure Check")

    required_files = [
        'cloud_security_audit.py',
        'requirements.txt',
        'README.md',
        'scanners/__init__.py',
        'scanners/aws_scanner.py',
        'utils/__init__.py',
        'utils/risk_scoring.py',
        'remediation/__init__.py',
        'remediation/aws_remediation.py',
        'reporting/__init__.py',
        'reporting/report_generator.py',
        'reporting/templates/security_report.html',
        'config/aws_config.yaml'
    ]

    all_exist = True

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False

    return all_exist

def check_modules():
    """Check if modules can be imported"""
    print_header("Module Import Check")

    modules_to_test = [
        ('utils.risk_scoring', 'RiskScorer'),
        ('reporting.report_generator', 'SecurityReportGenerator')
    ]

    all_imported = True

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {str(e)}")
            all_imported = False

    # Test boto3-dependent modules
    try:
        import boto3

        try:
            from scanners.aws_scanner import AWSSecurityScanner
            print(f"✅ scanners.aws_scanner.AWSSecurityScanner")
        except Exception as e:
            print(f"❌ scanners.aws_scanner.AWSSecurityScanner - {str(e)}")
            all_imported = False

        try:
            from remediation.aws_remediation import AWSRemediation
            print(f"✅ remediation.aws_remediation.AWSRemediation")
        except Exception as e:
            print(f"❌ remediation.aws_remediation.AWSRemediation - {str(e)}")
            all_imported = False

    except ImportError:
        print(f"⚠️  boto3-dependent modules - skipped (boto3 not installed)")

    return all_imported

def run_quick_test():
    """Run a quick functionality test"""
    print_header("Quick Functionality Test")

    try:
        # Test risk scoring
        from utils.risk_scoring import RiskScorer
        scorer = RiskScorer()

        test_finding = {
            'resource': 'test-bucket',
            'type': 'S3 Bucket',
            'severity': 'HIGH',
            'issue': 'Test finding',
            'recommendation': 'Test recommendation',
            'compliance': ['CIS 2.1.1']
        }

        score = scorer.calculate_finding_score(test_finding)
        print(f"✅ Risk scoring works - test score: {score}")

        # Test report generation
        from reporting.report_generator import SecurityReportGenerator
        reporter = SecurityReportGenerator()
        summary = reporter.generate_executive_summary({
            'security_score': 75.0,
            'security_grade': 'B',
            'total_findings': 10,
            'critical': 1,
            'high': 3,
            'medium': 4,
            'low': 2,
            'immediate_action_required': 4,
            'average_risk_score': 25.5,
            'top_risks': [test_finding],
            'findings_by_type': {'S3 Bucket': 5, 'IAM User': 3, 'Security Group': 2},
            'compliance_violations': {'CIS 2.1.1': 5}
        })

        if len(summary) > 100:
            print(f"✅ Report generation works - summary length: {len(summary)} chars")
        else:
            print(f"⚠️  Report generation may have issues - summary too short")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   Cloud Security Toolkit - Installation Verification             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'File Structure': check_file_structure(),
        'Module Imports': check_modules(),
        'AWS Credentials': check_aws_credentials(),
        'AWS Connectivity': check_aws_connectivity(),
        'Functionality Test': run_quick_test()
    }

    # Summary
    print_header("Verification Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {check}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! You're ready to use the toolkit.")
        print("\nQuick start:")
        print("  python cloud_security_audit.py --provider aws --output report.html")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure AWS: aws configure")
        print("  3. Check file structure")

    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
