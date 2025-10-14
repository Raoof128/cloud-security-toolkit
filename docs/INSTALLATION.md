# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- AWS CLI (for AWS scanning)
- 8GB+ RAM recommended
- Internet connection

## Step-by-Step Installation

### 1. Install Python

**Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS**
```bash
# Using Homebrew
brew install python3
```

**Verify installation**
```bash
python3 --version
# Should show Python 3.10.0 or higher
```

### 2. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/raoufchak/cloud-security-toolkit.git
cd cloud-security-toolkit

# Or download and extract ZIP
wget https://github.com/raoufchak/cloud-security-toolkit/archive/main.zip
unzip main.zip
cd cloud-security-toolkit-main
```

### 3. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# You should see (venv) in your prompt
```

### 4. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep boto3
pip list | grep jinja2
```

### 5. Configure AWS Credentials

**Option 1: AWS CLI (Recommended)**
```bash
# Install AWS CLI
# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# macOS:
brew install awscli

# Configure credentials
aws configure
# AWS Access Key ID: [Enter your key]
# AWS Secret Access Key: [Enter your secret]
# Default region name: ap-southeast-2
# Default output format: json

# Test credentials
aws sts get-caller-identity
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="ap-southeast-2"

# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Option 3: .env File**
```bash
# Copy template
cp config/.env.template .env

# Edit with your credentials
nano .env

# Add:
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=ap-southeast-2
```

### 6. Verify Installation

```bash
# Test the CLI
python cloud_security_audit.py --help

# Should display help message with available options
```

## Creating AWS IAM User for Scanning

### Read-Only User (Recommended for Scanning)

1. Log into AWS Console
2. Navigate to IAM → Users → Add User
3. User name: `cloud-security-scanner`
4. Access type: ✅ Programmatic access
5. Attach policies:
   - `SecurityAudit` (AWS managed policy)
   - OR create custom policy (see below)

**Custom Read-Only Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecurityAuditReadOnly",
      "Effect": "Allow",
      "Action": [
        "iam:Get*",
        "iam:List*",
        "iam:GenerateCredentialReport",
        "s3:GetBucket*",
        "s3:GetObject*",
        "s3:List*",
        "ec2:Describe*",
        "cloudtrail:Describe*",
        "cloudtrail:Get*",
        "cloudtrail:List*",
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

6. Download credentials CSV file
7. Save access key and secret key securely

### Remediation User (Optional)

If you want to use automated remediation:

1. Create user: `cloud-security-remediator`
2. Attach additional policies:
   - `SecurityAudit` (read access)
   - Custom remediation policy (write access - see docs/permissions.md)

**WARNING**: Remediation requires write permissions. Use with caution!

## Optional: Azure Setup

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Set subscription
az account set --subscription "your-subscription-id"
```

## Optional: GCP Setup

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project your-project-id
```

## Troubleshooting

### ModuleNotFoundError

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### AWS Credentials Not Found

```bash
# Check credentials file
cat ~/.aws/credentials

# Should show:
# [default]
# aws_access_key_id = YOUR_KEY
# aws_secret_access_key = YOUR_SECRET

# Test credentials
aws sts get-caller-identity
```

### Permission Denied

```bash
# Make script executable
chmod +x cloud_security_audit.py

# Or run with python
python cloud_security_audit.py
```

### SSL Certificate Errors

```bash
# Update certifi package
pip install --upgrade certifi

# Or install certificates (macOS)
/Applications/Python\ 3.10/Install\ Certificates.command
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove AWS credentials (optional)
rm ~/.aws/credentials

# Remove project directory
cd ..
rm -rf cloud-security-toolkit
```

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Next Steps

After installation:
1. Read the [Usage Guide](USAGE.md)
2. Run your first scan: `python cloud_security_audit.py --provider aws`
3. Review the generated HTML report
4. Check the [FAQ](FAQ.md) for common questions
