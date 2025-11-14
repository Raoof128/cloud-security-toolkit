"""
Input Validation Module
Validates inputs for security and correctness
"""
import re
from typing import Optional


def validate_s3_bucket_name(bucket_name: str) -> bool:
    """
    Validate S3 bucket name according to AWS rules

    Args:
        bucket_name (str): S3 bucket name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not bucket_name or not isinstance(bucket_name, str):
        return False

    # S3 bucket name rules:
    # - Between 3 and 63 characters
    # - Only lowercase letters, numbers, hyphens, and periods
    # - Must start and end with lowercase letter or number
    # - Cannot be formatted as an IP address
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        return False

    if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket_name):
        return False

    # Check if it looks like an IP address
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', bucket_name):
        return False

    # Cannot contain two adjacent periods
    if '..' in bucket_name:
        return False

    return True


def validate_cidr_block(cidr: str) -> bool:
    """
    Validate CIDR block format

    Args:
        cidr (str): CIDR block to validate (e.g., "192.168.1.0/24")

    Returns:
        bool: True if valid, False otherwise
    """
    if not cidr or not isinstance(cidr, str):
        return False

    try:
        # Split CIDR into IP and prefix
        parts = cidr.split('/')
        if len(parts) != 2:
            return False

        ip_part, prefix_part = parts

        # Validate IP address
        octets = ip_part.split('.')
        if len(octets) != 4:
            return False

        for octet in octets:
            num = int(octet)
            if num < 0 or num > 255:
                return False

        # Validate prefix length
        prefix = int(prefix_part)
        if prefix < 0 or prefix > 32:
            return False

        return True
    except (ValueError, AttributeError):
        return False


def validate_port_number(port: int) -> bool:
    """
    Validate port number

    Args:
        port (int): Port number to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(port, int):
        return False

    return 0 <= port <= 65535


def validate_port_range(from_port: int, to_port: int) -> bool:
    """
    Validate port range

    Args:
        from_port (int): Starting port number
        to_port (int): Ending port number

    Returns:
        bool: True if valid, False otherwise
    """
    if not validate_port_number(from_port) or not validate_port_number(to_port):
        return False

    return from_port <= to_port


def validate_security_group_id(sg_id: str) -> bool:
    """
    Validate AWS security group ID format

    Args:
        sg_id (str): Security group ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not sg_id or not isinstance(sg_id, str):
        return False

    # Security group IDs start with 'sg-' followed by 8 or 17 hex characters
    return bool(re.match(r'^sg-[0-9a-f]{8}$|^sg-[0-9a-f]{17}$', sg_id))


def validate_vpc_id(vpc_id: str) -> bool:
    """
    Validate AWS VPC ID format

    Args:
        vpc_id (str): VPC ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not vpc_id or not isinstance(vpc_id, str):
        return False

    # VPC IDs start with 'vpc-' followed by 8 or 17 hex characters
    return bool(re.match(r'^vpc-[0-9a-f]{8}$|^vpc-[0-9a-f]{17}$', vpc_id))


def validate_instance_id(instance_id: str) -> bool:
    """
    Validate AWS EC2 instance ID format

    Args:
        instance_id (str): Instance ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not instance_id or not isinstance(instance_id, str):
        return False

    # Instance IDs start with 'i-' followed by 8 or 17 hex characters
    return bool(re.match(r'^i-[0-9a-f]{8}$|^i-[0-9a-f]{17}$', instance_id))


def validate_aws_region(region: str) -> bool:
    """
    Validate AWS region name

    Args:
        region (str): AWS region name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not region or not isinstance(region, str):
        return False

    # AWS region format: us-east-1, eu-west-2, ap-southeast-1, etc.
    valid_regions = [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
        'ap-south-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
        'ap-southeast-1', 'ap-southeast-2', 'ap-east-1',
        'ca-central-1', 'sa-east-1', 'me-south-1', 'af-south-1'
    ]

    return region in valid_regions


def validate_cloudtrail_name(trail_name: str) -> bool:
    """
    Validate CloudTrail trail name

    Args:
        trail_name (str): CloudTrail trail name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not trail_name or not isinstance(trail_name, str):
        return False

    # CloudTrail names: 1-128 characters, alphanumeric, periods, underscores, hyphens
    if len(trail_name) < 1 or len(trail_name) > 128:
        return False

    return bool(re.match(r'^[a-zA-Z0-9._-]+$', trail_name))


def sanitize_resource_name(name: str, max_length: int = 255) -> Optional[str]:
    """
    Sanitize resource name by removing dangerous characters

    Args:
        name (str): Resource name to sanitize
        max_length (int): Maximum allowed length

    Returns:
        Optional[str]: Sanitized name or None if invalid
    """
    if not name or not isinstance(name, str):
        return None

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\s.-]', '', name)

    # Trim to max length
    sanitized = sanitized[:max_length]

    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized if sanitized else None


if __name__ == '__main__':
    # Test validation functions
    print("Testing validators...")

    # Test S3 bucket names
    assert validate_s3_bucket_name('my-bucket-123') == True
    assert validate_s3_bucket_name('My-Bucket') == False  # uppercase
    assert validate_s3_bucket_name('ab') == False  # too short
    assert validate_s3_bucket_name('192.168.1.1') == False  # IP address format

    # Test CIDR blocks
    assert validate_cidr_block('192.168.1.0/24') == True
    assert validate_cidr_block('10.0.0.0/8') == True
    assert validate_cidr_block('256.1.1.1/24') == False  # invalid IP
    assert validate_cidr_block('192.168.1.0/33') == False  # invalid prefix

    # Test port numbers
    assert validate_port_number(80) == True
    assert validate_port_number(65535) == True
    assert validate_port_number(-1) == False
    assert validate_port_number(65536) == False

    # Test security group IDs
    assert validate_security_group_id('sg-12345678') == True
    assert validate_security_group_id('sg-12345') == False  # too short
    assert validate_security_group_id('invalid') == False

    # Test VPC IDs
    assert validate_vpc_id('vpc-12345678') == True
    assert validate_vpc_id('vpc-123') == False

    # Test AWS regions
    assert validate_aws_region('us-east-1') == True
    assert validate_aws_region('invalid-region') == False

    print("All validator tests passed!")
