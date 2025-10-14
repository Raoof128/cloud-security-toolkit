"""
AWS Remediation Module
Automated remediation scripts for common AWS security issues
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import json


class AWSRemediation:
    """AWS security remediation engine"""

    def __init__(self, region='ap-southeast-2', dry_run=True):
        """
        Initialize AWS remediation engine

        Args:
            region (str): AWS region
            dry_run (bool): If True, only simulate changes without applying them
        """
        self.region = region
        self.dry_run = dry_run
        self.remediation_log = []

        # Initialize AWS clients
        self.iam_client = boto3.client('iam')
        self.s3_client = boto3.client('s3')
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.cloudtrail_client = boto3.client('cloudtrail', region_name=region)

        mode = "DRY RUN" if dry_run else "LIVE"
        print(f"[*] AWS Remediation initialized in {mode} mode")

    def log_action(self, action, resource, status, details=''):
        """Log remediation action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'resource': resource,
            'status': status,
            'details': details,
            'dry_run': self.dry_run
        }
        self.remediation_log.append(log_entry)

    # ========== S3 Remediations ==========

    def enable_s3_encryption(self, bucket_name):
        """
        Enable server-side encryption on S3 bucket

        Args:
            bucket_name (str): Name of the S3 bucket
        """
        if self.dry_run:
            print(f"[DRY RUN] Would enable AES256 encryption on bucket: {bucket_name}")
            self.log_action('enable_s3_encryption', bucket_name, 'simulated')
            return True

        try:
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }]
                }
            )
            print(f"[+] Enabled AES256 encryption on bucket: {bucket_name}")
            self.log_action('enable_s3_encryption', bucket_name, 'success')
            return True
        except ClientError as e:
            print(f"[-] Error enabling encryption on {bucket_name}: {str(e)}")
            self.log_action('enable_s3_encryption', bucket_name, 'failed', str(e))
            return False

    def enable_s3_versioning(self, bucket_name):
        """
        Enable versioning on S3 bucket

        Args:
            bucket_name (str): Name of the S3 bucket
        """
        if self.dry_run:
            print(f"[DRY RUN] Would enable versioning on bucket: {bucket_name}")
            self.log_action('enable_s3_versioning', bucket_name, 'simulated')
            return True

        try:
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"[+] Enabled versioning on bucket: {bucket_name}")
            self.log_action('enable_s3_versioning', bucket_name, 'success')
            return True
        except ClientError as e:
            print(f"[-] Error enabling versioning on {bucket_name}: {str(e)}")
            self.log_action('enable_s3_versioning', bucket_name, 'failed', str(e))
            return False

    def block_s3_public_access(self, bucket_name):
        """
        Block all public access to S3 bucket

        Args:
            bucket_name (str): Name of the S3 bucket
        """
        if self.dry_run:
            print(f"[DRY RUN] Would block public access on bucket: {bucket_name}")
            self.log_action('block_s3_public_access', bucket_name, 'simulated')
            return True

        try:
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            print(f"[+] Blocked public access on bucket: {bucket_name}")
            self.log_action('block_s3_public_access', bucket_name, 'success')
            return True
        except ClientError as e:
            print(f"[-] Error blocking public access on {bucket_name}: {str(e)}")
            self.log_action('block_s3_public_access', bucket_name, 'failed', str(e))
            return False

    def enable_s3_logging(self, bucket_name, log_bucket_name=None):
        """
        Enable access logging for S3 bucket

        Args:
            bucket_name (str): Name of the S3 bucket
            log_bucket_name (str): Name of bucket to store logs (optional)
        """
        if log_bucket_name is None:
            log_bucket_name = f"{bucket_name}-logs"

        if self.dry_run:
            print(f"[DRY RUN] Would enable logging on {bucket_name} -> {log_bucket_name}")
            self.log_action('enable_s3_logging', bucket_name, 'simulated')
            return True

        try:
            # Check if log bucket exists, create if not
            try:
                self.s3_client.head_bucket(Bucket=log_bucket_name)
            except ClientError:
                print(f"[*] Creating log bucket: {log_bucket_name}")
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=log_bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=log_bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )

            # Enable logging
            self.s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': log_bucket_name,
                        'TargetPrefix': f'{bucket_name}/'
                    }
                }
            )
            print(f"[+] Enabled logging on bucket: {bucket_name}")
            self.log_action('enable_s3_logging', bucket_name, 'success', f'Logs to {log_bucket_name}')
            return True
        except ClientError as e:
            print(f"[-] Error enabling logging on {bucket_name}: {str(e)}")
            self.log_action('enable_s3_logging', bucket_name, 'failed', str(e))
            return False

    # ========== Security Group Remediations ==========

    def restrict_security_group_rule(self, sg_id, port, protocol='tcp', new_cidr='10.0.0.0/8'):
        """
        Restrict security group rule from 0.0.0.0/0 to specific CIDR

        Args:
            sg_id (str): Security group ID
            port (int): Port number
            protocol (str): Protocol (tcp/udp/icmp)
            new_cidr (str): New CIDR range to allow
        """
        if self.dry_run:
            print(f"[DRY RUN] Would restrict SG {sg_id} port {port} from 0.0.0.0/0 to {new_cidr}")
            self.log_action('restrict_security_group', sg_id, 'simulated')
            return True

        try:
            # Revoke 0.0.0.0/0 rule
            self.ec2_client.revoke_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[{
                    'IpProtocol': protocol,
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
            )
            print(f"[+] Revoked 0.0.0.0/0 access on port {port}")

            # Add restricted rule
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[{
                    'IpProtocol': protocol,
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': new_cidr, 'Description': 'Auto-restricted by security audit'}]
                }]
            )
            print(f"[+] Added restricted rule: {new_cidr} on port {port}")
            self.log_action('restrict_security_group', sg_id, 'success',
                          f'Port {port}: 0.0.0.0/0 -> {new_cidr}')
            return True
        except ClientError as e:
            print(f"[-] Error restricting SG {sg_id}: {str(e)}")
            self.log_action('restrict_security_group', sg_id, 'failed', str(e))
            return False

    def remove_security_group_rule(self, sg_id, port, protocol='tcp'):
        """
        Remove a security group rule completely

        Args:
            sg_id (str): Security group ID
            port (int): Port number
            protocol (str): Protocol (tcp/udp/icmp)
        """
        if self.dry_run:
            print(f"[DRY RUN] Would remove SG {sg_id} rule for port {port}")
            self.log_action('remove_security_group_rule', sg_id, 'simulated')
            return True

        try:
            self.ec2_client.revoke_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[{
                    'IpProtocol': protocol,
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
            )
            print(f"[+] Removed open rule from SG {sg_id} port {port}")
            self.log_action('remove_security_group_rule', sg_id, 'success', f'Removed port {port}')
            return True
        except ClientError as e:
            print(f"[-] Error removing rule from {sg_id}: {str(e)}")
            self.log_action('remove_security_group_rule', sg_id, 'failed', str(e))
            return False

    # ========== EC2 Remediations ==========

    def enable_ebs_encryption(self, volume_id):
        """
        Enable encryption on EBS volume (requires snapshot and recreate)

        Args:
            volume_id (str): Volume ID
        """
        if self.dry_run:
            print(f"[DRY RUN] Would encrypt EBS volume: {volume_id}")
            print(f"  Note: This requires creating encrypted snapshot and new volume")
            self.log_action('enable_ebs_encryption', volume_id, 'simulated')
            return True

        try:
            print(f"[*] Creating encrypted snapshot of volume {volume_id}")
            # This is a complex operation that requires:
            # 1. Create snapshot
            # 2. Copy snapshot with encryption
            # 3. Create new volume from encrypted snapshot
            # 4. Replace volume (requires instance stop)

            print(f"[!] EBS encryption requires instance downtime and manual volume replacement")
            print(f"[!] Recommended: Use AWS console or implement full automation with approval")
            self.log_action('enable_ebs_encryption', volume_id, 'manual_required',
                          'Requires snapshot and volume replacement')
            return False
        except ClientError as e:
            print(f"[-] Error encrypting volume {volume_id}: {str(e)}")
            self.log_action('enable_ebs_encryption', volume_id, 'failed', str(e))
            return False

    def enforce_imdsv2(self, instance_id):
        """
        Enforce IMDSv2 on EC2 instance

        Args:
            instance_id (str): EC2 instance ID
        """
        if self.dry_run:
            print(f"[DRY RUN] Would enforce IMDSv2 on instance: {instance_id}")
            self.log_action('enforce_imdsv2', instance_id, 'simulated')
            return True

        try:
            self.ec2_client.modify_instance_metadata_options(
                InstanceId=instance_id,
                HttpTokens='required',  # Require IMDSv2
                HttpPutResponseHopLimit=1
            )
            print(f"[+] Enforced IMDSv2 on instance: {instance_id}")
            self.log_action('enforce_imdsv2', instance_id, 'success')
            return True
        except ClientError as e:
            print(f"[-] Error enforcing IMDSv2 on {instance_id}: {str(e)}")
            self.log_action('enforce_imdsv2', instance_id, 'failed', str(e))
            return False

    # ========== CloudTrail Remediations ==========

    def enable_cloudtrail(self, trail_name='default-security-trail', s3_bucket_name=None):
        """
        Enable CloudTrail logging

        Args:
            trail_name (str): Name for the trail
            s3_bucket_name (str): S3 bucket for logs
        """
        if s3_bucket_name is None:
            # Generate bucket name
            account_id = boto3.client('sts').get_caller_identity()['Account']
            s3_bucket_name = f"cloudtrail-logs-{account_id}"

        if self.dry_run:
            print(f"[DRY RUN] Would create CloudTrail: {trail_name}")
            print(f"  Bucket: {s3_bucket_name}")
            self.log_action('enable_cloudtrail', trail_name, 'simulated')
            return True

        try:
            # Create S3 bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=s3_bucket_name)
            except ClientError:
                print(f"[*] Creating CloudTrail S3 bucket: {s3_bucket_name}")
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=s3_bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=s3_bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )

                # Apply bucket policy for CloudTrail
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AWSCloudTrailAclCheck",
                            "Effect": "Allow",
                            "Principal": {"Service": "cloudtrail.amazonaws.com"},
                            "Action": "s3:GetBucketAcl",
                            "Resource": f"arn:aws:s3:::{s3_bucket_name}"
                        },
                        {
                            "Sid": "AWSCloudTrailWrite",
                            "Effect": "Allow",
                            "Principal": {"Service": "cloudtrail.amazonaws.com"},
                            "Action": "s3:PutObject",
                            "Resource": f"arn:aws:s3:::{s3_bucket_name}/*",
                            "Condition": {
                                "StringEquals": {
                                    "s3:x-amz-acl": "bucket-owner-full-control"
                                }
                            }
                        }
                    ]
                }
                self.s3_client.put_bucket_policy(
                    Bucket=s3_bucket_name,
                    Policy=json.dumps(bucket_policy)
                )

            # Create trail
            self.cloudtrail_client.create_trail(
                Name=trail_name,
                S3BucketName=s3_bucket_name,
                IsMultiRegionTrail=True,
                EnableLogFileValidation=True
            )
            print(f"[+] Created CloudTrail: {trail_name}")

            # Start logging
            self.cloudtrail_client.start_logging(Name=trail_name)
            print(f"[+] Started CloudTrail logging")

            self.log_action('enable_cloudtrail', trail_name, 'success', f'Bucket: {s3_bucket_name}')
            return True
        except ClientError as e:
            print(f"[-] Error enabling CloudTrail: {str(e)}")
            self.log_action('enable_cloudtrail', trail_name, 'failed', str(e))
            return False

    def enable_log_file_validation(self, trail_name):
        """
        Enable log file validation for CloudTrail

        Args:
            trail_name (str): Trail name
        """
        if self.dry_run:
            print(f"[DRY RUN] Would enable log file validation for: {trail_name}")
            self.log_action('enable_log_validation', trail_name, 'simulated')
            return True

        try:
            self.cloudtrail_client.update_trail(
                Name=trail_name,
                EnableLogFileValidation=True
            )
            print(f"[+] Enabled log file validation for: {trail_name}")
            self.log_action('enable_log_validation', trail_name, 'success')
            return True
        except ClientError as e:
            print(f"[-] Error enabling log validation: {str(e)}")
            self.log_action('enable_log_validation', trail_name, 'failed', str(e))
            return False

    # ========== VPC Remediations ==========

    def enable_vpc_flow_logs(self, vpc_id, log_group_name=None):
        """
        Enable VPC Flow Logs

        Args:
            vpc_id (str): VPC ID
            log_group_name (str): CloudWatch log group name
        """
        if log_group_name is None:
            log_group_name = f"/aws/vpc/flowlogs/{vpc_id}"

        if self.dry_run:
            print(f"[DRY RUN] Would enable flow logs for VPC: {vpc_id}")
            self.log_action('enable_vpc_flow_logs', vpc_id, 'simulated')
            return True

        try:
            # Create IAM role for VPC Flow Logs if needed
            # (Simplified - in production, check if role exists first)

            self.ec2_client.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType='VPC',
                TrafficType='ALL',
                LogDestinationType='cloud-watch-logs',
                LogGroupName=log_group_name
            )
            print(f"[+] Enabled VPC Flow Logs for: {vpc_id}")
            self.log_action('enable_vpc_flow_logs', vpc_id, 'success', f'Log group: {log_group_name}')
            return True
        except ClientError as e:
            print(f"[-] Error enabling VPC Flow Logs: {str(e)}")
            self.log_action('enable_vpc_flow_logs', vpc_id, 'failed', str(e))
            return False

    # ========== Automated Remediation ==========

    def remediate_findings(self, findings, auto_fix_types=None):
        """
        Automatically remediate findings based on type

        Args:
            findings (list): List of security findings
            auto_fix_types (list): List of finding types to auto-remediate

        Returns:
            dict: Remediation results
        """
        if auto_fix_types is None:
            # Default safe remediations
            auto_fix_types = [
                'enable_s3_encryption',
                'enable_s3_versioning',
                'block_s3_public_access',
                'enable_s3_logging'
            ]

        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        print(f"\n[*] Starting automated remediation...")
        print(f"[*] Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"[*] Processing {len(findings)} findings\n")

        for finding in findings:
            resource = finding['resource']
            finding_type = finding['type']
            issue = finding['issue']

            # S3 Bucket remediations
            if finding_type == 'S3 Bucket':
                if 'encryption' in issue.lower() and 'enable_s3_encryption' in auto_fix_types:
                    results['attempted'] += 1
                    if self.enable_s3_encryption(resource):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1

                elif 'public' in issue.lower() and 'block_s3_public_access' in auto_fix_types:
                    results['attempted'] += 1
                    if self.block_s3_public_access(resource):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1

                elif 'versioning' in issue.lower() and 'enable_s3_versioning' in auto_fix_types:
                    results['attempted'] += 1
                    if self.enable_s3_versioning(resource):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1

                elif 'logging' in issue.lower() and 'enable_s3_logging' in auto_fix_types:
                    results['attempted'] += 1
                    if self.enable_s3_logging(resource):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                else:
                    results['skipped'] += 1

            # EC2 Instance remediations
            elif finding_type == 'EC2 Instance':
                if 'IMDSv1' in issue or 'metadata' in issue.lower():
                    results['attempted'] += 1
                    if self.enforce_imdsv2(resource):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                else:
                    results['skipped'] += 1

            else:
                results['skipped'] += 1

        print(f"\n[+] Remediation complete!")
        print(f"  Attempted: {results['attempted']}")
        print(f"  Successful: {results['successful']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Skipped: {results['skipped']}")

        results['details'] = self.remediation_log
        return results

    def export_remediation_log(self, filename='remediation_log.json'):
        """Export remediation log to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.remediation_log, f, indent=2)
        print(f"[+] Remediation log exported to: {filename}")


if __name__ == '__main__':
    # Test remediation (dry run)
    remediator = AWSRemediation(dry_run=True)

    # Test S3 remediations
    print("Testing S3 remediations:")
    remediator.enable_s3_encryption('test-bucket')
    remediator.enable_s3_versioning('test-bucket')
    remediator.block_s3_public_access('test-bucket')

    # Test security group remediation
    print("\nTesting Security Group remediations:")
    remediator.restrict_security_group_rule('sg-12345', 22)

    # Test EC2 remediation
    print("\nTesting EC2 remediations:")
    remediator.enforce_imdsv2('i-12345')

    print("\nRemediation log:")
    for entry in remediator.remediation_log:
        print(f"  {entry['action']}: {entry['resource']} - {entry['status']}")
