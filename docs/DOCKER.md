# Docker Deployment Guide

This guide covers running the Cloud Security Toolkit using Docker for consistent, isolated execution.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Installation](#docker-installation)
- [Building the Image](#building-the-image)
- [Running Containers](#running-containers)
- [Docker Compose](#docker-compose)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Run Demo Mode (No AWS Required)

```bash
# Pull and run demo
docker run --rm cloud-security-toolkit:latest --demo

# Or with docker-compose
docker-compose up scanner
```

### Run AWS Scan with Credentials

```bash
# Using host AWS credentials
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --output /app/reports/scan.html

# Using environment variables
docker run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --output /app/reports/scan.html
```

---

## Docker Installation

### Install Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
```bash
brew install --cask docker
# Or download Docker Desktop from docker.com
```

#### Windows
Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## Building the Image

### Build from Dockerfile

```bash
# Clone the repository
git clone https://github.com/Raoof128/cloud-security-toolkit.git
cd cloud-security-toolkit

# Build the image
docker build -t cloud-security-toolkit:latest .

# Build with specific version
docker build -t cloud-security-toolkit:2.0.0 .

# Build with custom tag
docker build -t myorg/cloud-security-toolkit:latest .
```

### Build with Docker Compose

```bash
docker-compose build scanner
```

### Multi-platform Build (Optional)

```bash
# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t cloud-security-toolkit:latest \
  .
```

---

## Running Containers

### Basic Usage

```bash
# Show help
docker run --rm cloud-security-toolkit:latest --help

# Run demo mode
docker run --rm cloud-security-toolkit:latest --demo

# Check version
docker run --rm cloud-security-toolkit:latest --version
```

### With AWS Credentials

#### Method 1: Mount AWS Credentials (Recommended)

```bash
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --region us-east-1 --output /app/reports/report.html
```

**Advantages**:
- Uses existing AWS configuration
- Supports AWS profiles
- No credential exposure in environment

#### Method 2: Environment Variables

```bash
docker run --rm \
  -e AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  -e AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --output /app/reports/report.html
```

**Note**: Never commit credentials. Use `.env` files or secrets management.

#### Method 3: IAM Role (When Running on EC2)

```bash
# No credentials needed - uses instance role
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --output /app/reports/report.html
```

### Volume Mounts

```bash
# Mount reports directory
-v $(pwd)/reports:/app/reports

# Mount custom configuration
-v $(pwd)/custom_config:/app/config:ro

# Mount AWS credentials (read-only)
-v ~/.aws:/home/scanner/.aws:ro
```

### Interactive Mode

```bash
# Run with shell access
docker run --rm -it \
  -v ~/.aws:/home/scanner/.aws:ro \
  cloud-security-toolkit:latest \
  /bin/bash

# Then run commands inside container
python cloud_security_audit.py --demo
```

---

## Docker Compose

### Using docker-compose.yml

The included `docker-compose.yml` provides pre-configured services.

#### Start Services

```bash
# Run default scanner (demo mode)
docker-compose up scanner

# Run in background
docker-compose up -d scanner

# View logs
docker-compose logs -f scanner
```

#### Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  scanner:
    volumes:
      - ~/.aws:/home/scanner/.aws:ro  # AWS credentials
      - ./reports:/app/reports         # Output directory
      - ./config:/app/config:ro        # Custom config

    environment:
      - AWS_DEFAULT_REGION=us-east-1  # AWS region

    command: ["--provider", "aws", "--output", "/app/reports/scan.html"]
```

#### Stop Services

```bash
docker-compose down
```

### Scheduled Scanning

Enable scheduled scanning service:

```bash
# Start scheduled scanner
docker-compose --profile scheduled up -d scanner-scheduled

# Check logs
docker-compose logs -f scanner-scheduled
```

---

## Configuration

### Environment Variables

Set via `-e` flag or `.env` file:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=production

# Application Configuration
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### Custom Configuration Files

Mount custom configuration:

```bash
docker run --rm \
  -v $(pwd)/custom_config:/app/config:ro \
  -v ~/.aws:/home/scanner/.aws:ro \
  cloud-security-toolkit:latest \
  --provider aws
```

### Resource Limits

```bash
# Limit CPU and memory
docker run --rm \
  --cpus="2" \
  --memory="2g" \
  cloud-security-toolkit:latest \
  --provider aws
```

Or in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

---

## Advanced Usage

### CI/CD Integration

#### GitHub Actions

```yaml
name: Security Scan
on: [push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run security scan
        run: |
          docker run --rm \
            -e AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }} \
            -e AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
            -v $(pwd)/reports:/app/reports \
            cloud-security-toolkit:latest \
            --provider aws --output /app/reports/scan.html

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: reports/
```

#### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh '''
                    docker run --rm \
                      -v $PWD/reports:/app/reports \
                      -e AWS_ACCESS_KEY_ID \
                      -e AWS_SECRET_ACCESS_KEY \
                      cloud-security-toolkit:latest \
                      --provider aws --output /app/reports/scan.html
                '''
                archiveArtifacts artifacts: 'reports/*.html'
            }
        }
    }
}
```

### Scheduled Scans with Cron

```bash
# Add to crontab
0 2 * * * docker run --rm -v ~/.aws:/home/scanner/.aws:ro cloud-security-toolkit:latest --provider aws
```

### Lambda Deployment (Future)

```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . ${LAMBDA_TASK_ROOT}
CMD ["cloud_security_audit.handler"]
```

### Multi-Account Scanning

```bash
# Scan multiple AWS accounts
for account in account1 account2 account3; do
  docker run --rm \
    -v ~/.aws:/home/scanner/.aws:ro \
    -e AWS_PROFILE=$account \
    -v $(pwd)/reports:/app/reports \
    cloud-security-toolkit:latest \
    --provider aws --output /app/reports/${account}_scan.html
done
```

---

## Troubleshooting

### Common Issues

#### Permission Denied

```bash
# Error: permission denied
# Solution: Check volume mount permissions
docker run --rm -v $(pwd)/reports:/app/reports cloud-security-toolkit:latest --demo

# Fix: Ensure directory exists and is writable
mkdir -p reports
chmod 755 reports
```

#### AWS Credentials Not Found

```bash
# Error: NoCredentialsError
# Solution: Verify credential mount
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  cloud-security-toolkit:latest \
  sh -c "ls -la /home/scanner/.aws"

# Should show credentials file
```

#### Network Issues

```bash
# Error: Cannot connect to AWS
# Solution: Check network mode
docker run --rm --network host cloud-security-toolkit:latest --provider aws
```

#### Memory Issues

```bash
# Error: Out of memory
# Solution: Increase memory limit
docker run --rm --memory="4g" cloud-security-toolkit:latest --provider aws
```

### Debugging

#### Check Container Logs

```bash
# Run with verbose output
docker run --rm cloud-security-toolkit:latest --provider aws --verbose

# Access container shell
docker run --rm -it cloud-security-toolkit:latest /bin/bash
```

#### Inspect Container

```bash
# View container details
docker inspect cloud-security-toolkit:latest

# View environment variables
docker run --rm cloud-security-toolkit:latest env
```

#### Test AWS Connectivity

```bash
# Test AWS credentials
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  cloud-security-toolkit:latest \
  python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

---

## Best Practices

### Security

1. **Use Read-Only Mounts**
   ```bash
   -v ~/.aws:/home/scanner/.aws:ro
   ```

2. **Don't Store Credentials in Images**
   - Never `COPY` credentials into Docker images
   - Use runtime secrets injection

3. **Run as Non-Root**
   - Image already uses non-root user `scanner`
   - Verify: `docker run --rm cloud-security-toolkit:latest whoami`

4. **Limit Resources**
   ```bash
   --cpus="2" --memory="2g" --memory-swap="2g"
   ```

### Performance

1. **Use Layer Caching**
   - Requirements layer cached separately
   - Rebuild only when dependencies change

2. **Multi-Stage Builds**
   - Already implemented in Dockerfile
   - Reduces final image size

3. **Clean Up**
   ```bash
   # Remove stopped containers
   docker container prune

   # Remove unused images
   docker image prune
   ```

### Maintenance

1. **Regular Updates**
   ```bash
   docker pull cloud-security-toolkit:latest
   ```

2. **Version Tagging**
   ```bash
   docker tag cloud-security-toolkit:latest cloud-security-toolkit:2.0.0
   ```

3. **Backup Reports**
   ```bash
   docker run --rm \
     -v $(pwd)/reports:/app/reports \
     cloud-security-toolkit:latest \
     --provider aws --output /app/reports/$(date +%Y%m%d)_scan.html
   ```

---

## Examples

### Complete Workflow

```bash
# 1. Build image
docker build -t cloud-security-toolkit:latest .

# 2. Test with demo
docker run --rm cloud-security-toolkit:latest --demo

# 3. Run AWS scan
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --region us-east-1 --output /app/reports/scan.html

# 4. Generate all report formats
docker run --rm \
  -v ~/.aws:/home/scanner/.aws:ro \
  -v $(pwd)/reports:/app/reports \
  cloud-security-toolkit:latest \
  --provider aws --format all --output /app/reports/scan

# 5. View report
open reports/scan.html  # macOS
xdg-open reports/scan.html  # Linux
```

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

**Last Updated**: 2025-11-14
**Version**: 2.0.0
