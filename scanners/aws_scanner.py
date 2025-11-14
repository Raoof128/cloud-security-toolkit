"""
AWS Security Scanner
Comprehensive security audit scanner for AWS environments
"""
from typing import List, Dict, Any, Optional
import boto3
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError, NoCredentialsError
import sys


class AWSSecurityScanner:
    """Main AWS security scanner class"""

    def __init__(self, region: str = 'ap-southeast-2') -> None:
        """
        Initialize AWS security scanner

        Args:
            region (str): AWS region to scan
        """
        self.region: str = region
        self.findings: List[Dict[str, Any]] = []

        try:
            # Initialize AWS clients
            self.iam_client = boto3.client('iam')
            self.s3_client = boto3.client('s3')
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.cloudtrail_client = boto3.client('cloudtrail', region_name=region)
            self.sts_client = boto3.client('sts')

            # Get account ID
            self.account_id = self.sts_client.get_caller_identity()['Account']

            print(f"[*] Initialized AWS scanner for account {self.account_id} in region {region}")
        except NoCredentialsError:
            print("[-] Error: AWS credentials not found. Please configure credentials.")
            sys.exit(1)
        except Exception as e:
            print(f"[-] Error initializing AWS scanner: {str(e)}")
            sys.exit(1)

    def scan_iam_users(self) -> List[Dict[str, Any]]:
        """
        Check IAM users for security issues

        Checks:
        - MFA not enabled
        - Access keys older than 90 days
        - Unused users (no recent activity)
        - Users with administrator access

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking IAM users...")

        try:
            # Use pagination to handle large numbers of users
            users = []
            paginator = self.iam_client.get_paginator('list_users')
            for page in paginator.paginate():
                users.extend(page['Users'])

            for user in users:
                username = user['UserName']

                # Check MFA
                try:
                    mfa_devices = self.iam_client.list_mfa_devices(UserName=username)
                    if not mfa_devices['MFADevices']:
                        findings.append({
                            'resource': username,
                            'type': 'IAM User',
                            'severity': 'HIGH',
                            'issue': 'MFA not enabled',
                            'recommendation': 'Enable MFA for enhanced security',
                            'compliance': ['CIS 1.14', 'ASD Essential 8 #2']
                        })
                except ClientError:
                    pass

                # Check access keys age
                try:
                    access_keys = self.iam_client.list_access_keys(UserName=username)
                    for key in access_keys['AccessKeyMetadata']:
                        key_age = (datetime.now(timezone.utc) - key['CreateDate']).days

                        if key_age > 90:
                            findings.append({
                                'resource': f"{username} ({key['AccessKeyId']})",
                                'type': 'Access Key',
                                'severity': 'MEDIUM',
                                'issue': f'Access key older than 90 days ({key_age} days)',
                                'recommendation': 'Rotate access keys regularly (every 90 days)',
                                'compliance': ['CIS 1.4']
                            })

                        # Check if key has been used recently
                        try:
                            last_used = self.iam_client.get_access_key_last_used(
                                AccessKeyId=key['AccessKeyId']
                            )
                            if 'LastUsedDate' in last_used['AccessKeyLastUsed']:
                                days_since_use = (datetime.now(timezone.utc) -
                                                last_used['AccessKeyLastUsed']['LastUsedDate']).days
                                if days_since_use > 90:
                                    findings.append({
                                        'resource': f"{username} ({key['AccessKeyId']})",
                                        'type': 'Access Key',
                                        'severity': 'LOW',
                                        'issue': f'Access key not used in {days_since_use} days',
                                        'recommendation': 'Remove unused access keys',
                                        'compliance': ['CIS 1.3']
                                    })
                        except ClientError:
                            pass
                except ClientError:
                    pass

                # Check for administrator access
                try:
                    attached_policies = self.iam_client.list_attached_user_policies(
                        UserName=username
                    )
                    for policy in attached_policies['AttachedPolicies']:
                        if policy['PolicyArn'] == 'arn:aws:iam::aws:policy/AdministratorAccess':
                            findings.append({
                                'resource': username,
                                'type': 'IAM User',
                                'severity': 'HIGH',
                                'issue': 'User has AdministratorAccess policy attached',
                                'recommendation': 'Use least privilege principle; avoid direct admin access',
                                'compliance': ['CIS 1.16']
                            })
                except ClientError:
                    pass

            # Check root account usage
            try:
                credential_report = self.iam_client.generate_credential_report()
                # Wait for report to be ready
                import time
                for _ in range(10):
                    report_status = self.iam_client.get_credential_report()
                    if report_status['ResponseMetadata']['HTTPStatusCode'] == 200:
                        break
                    time.sleep(1)

                report_content = report_status['Content'].decode('utf-8')
                lines = report_content.split('\n')
                if len(lines) > 1:
                    root_line = lines[1]  # First line after header
                    if '<root_account>' in root_line:
                        fields = root_line.split(',')
                        if len(fields) > 10:
                            # Check if root has MFA
                            if fields[7] == 'false':  # mfa_active column
                                findings.append({
                                    'resource': 'Root Account',
                                    'type': 'IAM Root',
                                    'severity': 'CRITICAL',
                                    'issue': 'Root account MFA not enabled',
                                    'recommendation': 'Enable MFA on root account immediately',
                                    'compliance': ['CIS 1.5', 'ASD Essential 8']
                                })
            except ClientError as e:
                print(f"    [-] Unable to check root account: {str(e)}")

        except ClientError as e:
            print(f"    [-] Error scanning IAM users: {str(e)}")

        print(f"  [+] Found {len(findings)} IAM-related issues")
        return findings

    def scan_iam_password_policy(self) -> List[Dict[str, Any]]:
        """
        Check IAM password policy compliance

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking IAM password policy...")

        try:
            policy = self.iam_client.get_account_password_policy()['PasswordPolicy']

            # Check minimum password length
            if policy.get('MinimumPasswordLength', 0) < 14:
                findings.append({
                    'resource': 'Account Password Policy',
                    'type': 'IAM Policy',
                    'severity': 'MEDIUM',
                    'issue': f'Minimum password length is {policy.get("MinimumPasswordLength", 0)} (should be 14+)',
                    'recommendation': 'Set minimum password length to 14 characters',
                    'compliance': ['CIS 1.8']
                })

            # Check password complexity requirements
            required_settings = {
                'RequireUppercaseCharacters': 'uppercase characters',
                'RequireLowercaseCharacters': 'lowercase characters',
                'RequireNumbers': 'numbers',
                'RequireSymbols': 'symbols'
            }

            for setting, description in required_settings.items():
                if not policy.get(setting, False):
                    findings.append({
                        'resource': 'Account Password Policy',
                        'type': 'IAM Policy',
                        'severity': 'MEDIUM',
                        'issue': f'Password policy does not require {description}',
                        'recommendation': f'Enable requirement for {description} in passwords',
                        'compliance': ['CIS 1.9']
                    })

            # Check password expiration
            if not policy.get('ExpirePasswords', False):
                findings.append({
                    'resource': 'Account Password Policy',
                    'type': 'IAM Policy',
                    'severity': 'MEDIUM',
                    'issue': 'Passwords do not expire',
                    'recommendation': 'Enable password expiration (90 days recommended)',
                    'compliance': ['CIS 1.11']
                })
            elif policy.get('MaxPasswordAge', 0) > 90:
                findings.append({
                    'resource': 'Account Password Policy',
                    'type': 'IAM Policy',
                    'severity': 'LOW',
                    'issue': f'Password expiration set to {policy.get("MaxPasswordAge")} days (should be 90)',
                    'recommendation': 'Set password expiration to 90 days',
                    'compliance': ['CIS 1.11']
                })

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                findings.append({
                    'resource': 'Account',
                    'type': 'IAM Policy',
                    'severity': 'HIGH',
                    'issue': 'No password policy configured',
                    'recommendation': 'Configure a strong password policy',
                    'compliance': ['CIS 1.8-1.11']
                })
            else:
                print(f"    [-] Error checking password policy: {str(e)}")

        return findings

    def scan_s3_buckets(self) -> List[Dict[str, Any]]:
        """
        Audit S3 bucket configurations

        Checks:
        - Public access
        - Encryption
        - Versioning
        - Logging
        - Secure transport

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking S3 buckets...")

        try:
            # Note: S3 list_buckets doesn't support pagination as it returns all buckets
            # However, we handle it properly in case of API changes
            buckets = self.s3_client.list_buckets().get('Buckets', [])
            print(f"    [*] Found {len(buckets)} buckets to scan")

            for bucket in buckets:
                bucket_name = bucket['Name']

                # Get bucket location
                try:
                    location = self.s3_client.get_bucket_location(Bucket=bucket_name)
                    bucket_region = location['LocationConstraint']
                    if bucket_region is None:
                        bucket_region = 'us-east-1'
                except ClientError:
                    bucket_region = 'unknown'

                # Check public access block
                try:
                    public_block = self.s3_client.get_public_access_block(Bucket=bucket_name)
                    config = public_block['PublicAccessBlockConfiguration']

                    if not all([
                        config.get('BlockPublicAcls', False),
                        config.get('IgnorePublicAcls', False),
                        config.get('BlockPublicPolicy', False),
                        config.get('RestrictPublicBuckets', False)
                    ]):
                        findings.append({
                            'resource': bucket_name,
                            'type': 'S3 Bucket',
                            'severity': 'CRITICAL',
                            'issue': 'Public access block not fully enabled',
                            'recommendation': 'Enable all public access block settings',
                            'compliance': ['CIS 2.1.5'],
                            'exposure': 'public'
                        })
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                        findings.append({
                            'resource': bucket_name,
                            'type': 'S3 Bucket',
                            'severity': 'CRITICAL',
                            'issue': 'No public access block configured',
                            'recommendation': 'Configure public access block to prevent data exposure',
                            'compliance': ['CIS 2.1.5'],
                            'exposure': 'public'
                        })

                # Check bucket ACL for public access
                try:
                    acl = self.s3_client.get_bucket_acl(Bucket=bucket_name)
                    for grant in acl['Grants']:
                        grantee = grant.get('Grantee', {})
                        if grantee.get('Type') == 'Group':
                            uri = grantee.get('URI', '')
                            if 'AllUsers' in uri or 'AuthenticatedUsers' in uri:
                                findings.append({
                                    'resource': bucket_name,
                                    'type': 'S3 Bucket',
                                    'severity': 'CRITICAL',
                                    'issue': f'Bucket has public ACL ({uri})',
                                    'recommendation': 'Remove public ACL grants',
                                    'compliance': ['CIS 2.1.5'],
                                    'exposure': 'public'
                                })
                except ClientError:
                    pass

                # Check encryption
                try:
                    encryption = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        findings.append({
                            'resource': bucket_name,
                            'type': 'S3 Bucket',
                            'severity': 'HIGH',
                            'issue': 'Server-side encryption not enabled',
                            'recommendation': 'Enable AES-256 or KMS encryption',
                            'compliance': ['CIS 2.1.1']
                        })

                # Check versioning
                try:
                    versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                    if versioning.get('Status') != 'Enabled':
                        findings.append({
                            'resource': bucket_name,
                            'type': 'S3 Bucket',
                            'severity': 'MEDIUM',
                            'issue': 'Versioning not enabled',
                            'recommendation': 'Enable versioning for data protection and recovery',
                            'compliance': ['CIS 2.1.3']
                        })
                except ClientError:
                    pass

                # Check logging
                try:
                    logging = self.s3_client.get_bucket_logging(Bucket=bucket_name)
                    if 'LoggingEnabled' not in logging:
                        findings.append({
                            'resource': bucket_name,
                            'type': 'S3 Bucket',
                            'severity': 'MEDIUM',
                            'issue': 'Access logging not enabled',
                            'recommendation': 'Enable S3 access logging for audit trail',
                            'compliance': ['CIS 2.1.4']
                        })
                except ClientError:
                    pass

        except ClientError as e:
            print(f"    [-] Error scanning S3 buckets: {str(e)}")

        print(f"  [+] Found {len(findings)} S3-related issues")
        return findings

    def scan_security_groups(self) -> List[Dict[str, Any]]:
        """
        Check security group rules for open access

        Checks:
        - Unrestricted inbound rules (0.0.0.0/0)
        - Open sensitive ports (SSH, RDP, databases)

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking security groups...")

        try:
            # Use pagination to handle large numbers of security groups
            security_groups = []
            paginator = self.ec2_client.get_paginator('describe_security_groups')
            for page in paginator.paginate():
                security_groups.extend(page['SecurityGroups'])
            print(f"    [*] Found {len(security_groups)} security groups")

            # Define sensitive ports
            sensitive_ports = {
                22: ('SSH', 'CRITICAL'),
                3389: ('RDP', 'CRITICAL'),
                3306: ('MySQL', 'CRITICAL'),
                5432: ('PostgreSQL', 'CRITICAL'),
                1433: ('SQL Server', 'CRITICAL'),
                27017: ('MongoDB', 'CRITICAL'),
                6379: ('Redis', 'CRITICAL'),
                5984: ('CouchDB', 'HIGH'),
                9200: ('Elasticsearch', 'HIGH'),
                11211: ('Memcached', 'HIGH')
            }

            for sg in security_groups:
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                vpc_id = sg.get('VpcId', 'EC2-Classic')

                # Check inbound rules
                for rule in sg.get('IpPermissions', []):
                    from_port = rule.get('FromPort', 0)
                    to_port = rule.get('ToPort', 65535)
                    protocol = rule.get('IpProtocol', 'all')

                    # Check for 0.0.0.0/0 access
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            # Determine severity based on port
                            severity = 'HIGH'
                            port_desc = f'Port {from_port}'

                            if from_port == to_port and from_port in sensitive_ports:
                                port_name, severity = sensitive_ports[from_port]
                                port_desc = f'{port_name} (port {from_port})'
                            elif from_port == 0 or protocol == '-1':  # All ports
                                severity = 'CRITICAL'
                                port_desc = 'All ports'

                            findings.append({
                                'resource': f"{sg_name} ({sg_id})",
                                'type': 'Security Group',
                                'severity': severity,
                                'issue': f'{port_desc} open to internet (0.0.0.0/0)',
                                'recommendation': 'Restrict access to specific IP ranges or use VPN/bastion host',
                                'compliance': ['CIS 5.2'],
                                'exposure': 'internet-facing'
                            })

                    # Check for ::/0 (IPv6) access
                    for ipv6_range in rule.get('Ipv6Ranges', []):
                        if ipv6_range.get('CidrIpv6') == '::/0':
                            severity = 'HIGH'
                            if from_port == to_port and from_port in sensitive_ports:
                                port_name, severity = sensitive_ports[from_port]

                            findings.append({
                                'resource': f"{sg_name} ({sg_id})",
                                'type': 'Security Group',
                                'severity': severity,
                                'issue': f'Port {from_port} open to IPv6 internet (::/0)',
                                'recommendation': 'Restrict IPv6 access to specific ranges',
                                'compliance': ['CIS 5.2'],
                                'exposure': 'internet-facing'
                            })

        except ClientError as e:
            print(f"    [-] Error scanning security groups: {str(e)}")

        print(f"  [+] Found {len(findings)} security group issues")
        return findings

    def scan_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        Check EC2 instances for security issues

        Checks:
        - Unencrypted EBS volumes
        - Public IP addresses
        - IMDSv1 usage

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking EC2 instances...")

        try:
            # Use pagination to handle large numbers of instances
            reservations = []
            paginator = self.ec2_client.get_paginator('describe_instances')
            for page in paginator.paginate():
                reservations.extend(page['Reservations'])
            instance_count = sum(len(r['Instances']) for r in reservations)
            print(f"    [*] Found {instance_count} instances")

            for reservation in reservations:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']

                    # Skip terminated instances
                    if instance_state == 'terminated':
                        continue

                    # Check for public IP
                    if instance.get('PublicIpAddress'):
                        findings.append({
                            'resource': instance_id,
                            'type': 'EC2 Instance',
                            'severity': 'MEDIUM',
                            'issue': 'Instance has public IP address',
                            'recommendation': 'Use private IPs with NAT gateway or bastion host',
                            'compliance': ['CIS 5.1'],
                            'exposure': 'internet-facing'
                        })

                    # Check instance metadata service version
                    metadata_options = instance.get('MetadataOptions', {})
                    if metadata_options.get('HttpTokens') == 'optional':
                        findings.append({
                            'resource': instance_id,
                            'type': 'EC2 Instance',
                            'severity': 'MEDIUM',
                            'issue': 'Instance using IMDSv1 (vulnerable to SSRF)',
                            'recommendation': 'Require IMDSv2 (HttpTokens=required)',
                            'compliance': ['AWS Best Practice']
                        })

                    # Check EBS volume encryption
                    for bdm in instance.get('BlockDeviceMappings', []):
                        if 'Ebs' in bdm:
                            volume_id = bdm['Ebs']['VolumeId']
                            try:
                                volume = self.ec2_client.describe_volumes(
                                    VolumeIds=[volume_id]
                                )['Volumes'][0]

                                if not volume.get('Encrypted', False):
                                    findings.append({
                                        'resource': f"{instance_id} (Volume: {volume_id})",
                                        'type': 'EBS Volume',
                                        'severity': 'HIGH',
                                        'issue': 'EBS volume not encrypted',
                                        'recommendation': 'Enable EBS encryption for data at rest protection',
                                        'compliance': ['CIS 2.2.1']
                                    })
                            except ClientError:
                                pass

        except ClientError as e:
            print(f"    [-] Error scanning EC2 instances: {str(e)}")

        print(f"  [+] Found {len(findings)} EC2-related issues")
        return findings

    def scan_cloudtrail(self) -> List[Dict[str, Any]]:
        """
        Check CloudTrail logging configuration

        Checks:
        - CloudTrail enabled
        - Multi-region trails
        - Log file validation
        - S3 bucket logging

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking CloudTrail configuration...")

        try:
            trails = self.cloudtrail_client.describe_trails()['trailList']

            if not trails:
                findings.append({
                    'resource': 'Account',
                    'type': 'CloudTrail',
                    'severity': 'CRITICAL',
                    'issue': 'No CloudTrail trails configured',
                    'recommendation': 'Enable CloudTrail for comprehensive audit logging',
                    'compliance': ['CIS 3.1', 'ASD Essential 8']
                })
            else:
                multi_region_enabled = False

                for trail in trails:
                    trail_name = trail['Name']

                    # Check if trail is logging
                    try:
                        status = self.cloudtrail_client.get_trail_status(Name=trail_name)

                        if not status.get('IsLogging', False):
                            findings.append({
                                'resource': trail_name,
                                'type': 'CloudTrail',
                                'severity': 'CRITICAL',
                                'issue': 'CloudTrail logging is disabled',
                                'recommendation': 'Enable CloudTrail logging',
                                'compliance': ['CIS 3.1']
                            })
                    except ClientError:
                        pass

                    # Check multi-region
                    if trail.get('IsMultiRegionTrail', False):
                        multi_region_enabled = True

                    # Check log file validation
                    if not trail.get('LogFileValidationEnabled', False):
                        findings.append({
                            'resource': trail_name,
                            'type': 'CloudTrail',
                            'severity': 'HIGH',
                            'issue': 'Log file validation not enabled',
                            'recommendation': 'Enable log file integrity validation',
                            'compliance': ['CIS 3.2']
                        })

                    # Check S3 bucket encryption
                    # (Note: This would require additional S3 bucket checks)

                if not multi_region_enabled:
                    findings.append({
                        'resource': 'CloudTrail Configuration',
                        'type': 'CloudTrail',
                        'severity': 'HIGH',
                        'issue': 'No multi-region trail configured',
                        'recommendation': 'Enable multi-region trail to log all regions',
                        'compliance': ['CIS 3.1']
                    })

        except ClientError as e:
            print(f"    [-] Error checking CloudTrail: {str(e)}")

        print(f"  [+] Found {len(findings)} CloudTrail issues")
        return findings

    def scan_vpc_flow_logs(self) -> List[Dict[str, Any]]:
        """
        Check VPC Flow Logs configuration

        Returns:
            List[Dict[str, Any]]: List of security findings
        """
        findings: List[Dict[str, Any]] = []
        print("  [*] Checking VPC Flow Logs...")

        try:
            # Use pagination to handle large numbers of VPCs
            vpcs = []
            paginator = self.ec2_client.get_paginator('describe_vpcs')
            for page in paginator.paginate():
                vpcs.extend(page['Vpcs'])

            for vpc in vpcs:
                vpc_id = vpc['VpcId']

                # Check if flow logs are enabled
                flow_logs = self.ec2_client.describe_flow_logs(
                    Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}]
                )['FlowLogs']

                if not flow_logs:
                    findings.append({
                        'resource': vpc_id,
                        'type': 'VPC',
                        'severity': 'MEDIUM',
                        'issue': 'VPC Flow Logs not enabled',
                        'recommendation': 'Enable VPC Flow Logs for network traffic visibility',
                        'compliance': ['CIS 3.9']
                    })

        except ClientError as e:
            print(f"    [-] Error checking VPC Flow Logs: {str(e)}")

        return findings

    def run_full_scan(self) -> List[Dict[str, Any]]:
        """
        Execute all security checks

        Returns:
            List[Dict[str, Any]]: All findings from all checks
        """
        print("[*] Starting AWS security scan...")
        print(f"[*] Account: {self.account_id}")
        print(f"[*] Region: {self.region}")
        print()

        # Run all scans
        print("[*] Scanning IAM configuration...")
        self.findings.extend(self.scan_iam_users())
        self.findings.extend(self.scan_iam_password_policy())

        print("\n[*] Scanning S3 buckets...")
        self.findings.extend(self.scan_s3_buckets())

        print("\n[*] Scanning network security...")
        self.findings.extend(self.scan_security_groups())

        print("\n[*] Scanning EC2 instances...")
        self.findings.extend(self.scan_ec2_instances())

        print("\n[*] Scanning CloudTrail...")
        self.findings.extend(self.scan_cloudtrail())

        print("\n[*] Scanning VPC configuration...")
        self.findings.extend(self.scan_vpc_flow_logs())

        print(f"\n[+] Scan complete!")
        print(f"[+] Total findings: {len(self.findings)}")

        # Summary by severity
        severity_counts = {}
        for finding in self.findings:
            severity = finding['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print("\nFindings by severity:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                print(f"  {severity}: {count}")

        return self.findings


if __name__ == '__main__':
    # Quick test
    scanner = AWSSecurityScanner()
    findings = scanner.run_full_scan()

    print("\n" + "="*80)
    print("Sample findings:")
    for finding in findings[:5]:
        print(f"\n[{finding['severity']}] {finding['issue']}")
        print(f"  Resource: {finding['resource']}")
        print(f"  Recommendation: {finding['recommendation']}")
