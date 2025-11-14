"""
Unit tests for input validators
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import (
    validate_s3_bucket_name, validate_cidr_block, validate_port_number,
    validate_port_range, validate_security_group_id, validate_vpc_id,
    validate_instance_id, validate_aws_region, validate_cloudtrail_name,
    sanitize_resource_name
)


class TestS3BucketNameValidation:
    """Tests for S3 bucket name validation"""

    def test_valid_bucket_names(self):
        """Test valid S3 bucket names"""
        assert validate_s3_bucket_name('my-bucket')
        assert validate_s3_bucket_name('my-bucket-123')
        assert validate_s3_bucket_name('my.bucket.name')
        assert validate_s3_bucket_name('abc')  # minimum 3 chars

    def test_invalid_bucket_names(self):
        """Test invalid S3 bucket names"""
        assert not validate_s3_bucket_name('My-Bucket')  # uppercase
        assert not validate_s3_bucket_name('my_bucket')  # underscore
        assert not validate_s3_bucket_name('ab')  # too short
        assert not validate_s3_bucket_name('a' * 64)  # too long
        assert not validate_s3_bucket_name('192.168.1.1')  # IP format
        assert not validate_s3_bucket_name('bucket..name')  # double period
        assert not validate_s3_bucket_name('-bucket')  # starts with hyphen
        assert not validate_s3_bucket_name('bucket-')  # ends with hyphen
        assert not validate_s3_bucket_name('')  # empty
        assert not validate_s3_bucket_name(None)  # None


class TestCIDRBlockValidation:
    """Tests for CIDR block validation"""

    def test_valid_cidr_blocks(self):
        """Test valid CIDR blocks"""
        assert validate_cidr_block('192.168.1.0/24')
        assert validate_cidr_block('10.0.0.0/8')
        assert validate_cidr_block('172.16.0.0/12')
        assert validate_cidr_block('0.0.0.0/0')
        assert validate_cidr_block('192.168.1.1/32')

    def test_invalid_cidr_blocks(self):
        """Test invalid CIDR blocks"""
        assert not validate_cidr_block('256.1.1.1/24')  # invalid octet
        assert not validate_cidr_block('192.168.1.0/33')  # invalid prefix
        assert not validate_cidr_block('192.168.1.0')  # missing prefix
        assert not validate_cidr_block('192.168.1.0/-1')  # negative prefix
        assert not validate_cidr_block('192.168/24')  # incomplete IP
        assert not validate_cidr_block('192.168.1.1.1/24')  # too many octets
        assert not validate_cidr_block('')  # empty
        assert not validate_cidr_block(None)  # None


class TestPortNumberValidation:
    """Tests for port number validation"""

    def test_valid_port_numbers(self):
        """Test valid port numbers"""
        assert validate_port_number(0)
        assert validate_port_number(80)
        assert validate_port_number(443)
        assert validate_port_number(65535)

    def test_invalid_port_numbers(self):
        """Test invalid port numbers"""
        assert not validate_port_number(-1)
        assert not validate_port_number(65536)
        assert not validate_port_number('80')  # string
        assert not validate_port_number(None)  # None
        assert not validate_port_number(100000)


class TestPortRangeValidation:
    """Tests for port range validation"""

    def test_valid_port_ranges(self):
        """Test valid port ranges"""
        assert validate_port_range(80, 80)
        assert validate_port_range(80, 443)
        assert validate_port_range(0, 65535)

    def test_invalid_port_ranges(self):
        """Test invalid port ranges"""
        assert not validate_port_range(443, 80)  # reversed
        assert not validate_port_range(-1, 80)  # invalid from_port
        assert not validate_port_range(80, 65536)  # invalid to_port


class TestSecurityGroupIDValidation:
    """Tests for security group ID validation"""

    def test_valid_security_group_ids(self):
        """Test valid security group IDs"""
        assert validate_security_group_id('sg-12345678')
        assert validate_security_group_id('sg-1234567890abcdef0')

    def test_invalid_security_group_ids(self):
        """Test invalid security group IDs"""
        assert not validate_security_group_id('sg-123')  # too short
        assert not validate_security_group_id('sg-12345')  # wrong length
        assert not validate_security_group_id('sg-123456789')  # wrong length
        assert not validate_security_group_id('invalid')
        assert not validate_security_group_id('i-12345678')  # instance ID
        assert not validate_security_group_id('')
        assert not validate_security_group_id(None)


class TestVPCIDValidation:
    """Tests for VPC ID validation"""

    def test_valid_vpc_ids(self):
        """Test valid VPC IDs"""
        assert validate_vpc_id('vpc-12345678')
        assert validate_vpc_id('vpc-1234567890abcdef0')

    def test_invalid_vpc_ids(self):
        """Test invalid VPC IDs"""
        assert not validate_vpc_id('vpc-123')
        assert not validate_vpc_id('sg-12345678')  # security group ID
        assert not validate_vpc_id('')
        assert not validate_vpc_id(None)


class TestInstanceIDValidation:
    """Tests for instance ID validation"""

    def test_valid_instance_ids(self):
        """Test valid instance IDs"""
        assert validate_instance_id('i-12345678')
        assert validate_instance_id('i-1234567890abcdef0')

    def test_invalid_instance_ids(self):
        """Test invalid instance IDs"""
        assert not validate_instance_id('i-123')
        assert not validate_instance_id('sg-12345678')
        assert not validate_instance_id('')
        assert not validate_instance_id(None)


class TestAWSRegionValidation:
    """Tests for AWS region validation"""

    def test_valid_regions(self):
        """Test valid AWS regions"""
        assert validate_aws_region('us-east-1')
        assert validate_aws_region('us-west-2')
        assert validate_aws_region('eu-west-1')
        assert validate_aws_region('ap-southeast-2')

    def test_invalid_regions(self):
        """Test invalid AWS regions"""
        assert not validate_aws_region('invalid-region')
        assert not validate_aws_region('us-east-99')
        assert not validate_aws_region('')
        assert not validate_aws_region(None)


class TestCloudTrailNameValidation:
    """Tests for CloudTrail name validation"""

    def test_valid_cloudtrail_names(self):
        """Test valid CloudTrail names"""
        assert validate_cloudtrail_name('my-trail')
        assert validate_cloudtrail_name('my_trail_123')
        assert validate_cloudtrail_name('MyTrail.Name')

    def test_invalid_cloudtrail_names(self):
        """Test invalid CloudTrail names"""
        assert not validate_cloudtrail_name('my trail')  # space
        assert not validate_cloudtrail_name('my@trail')  # special char
        assert not validate_cloudtrail_name('a' * 129)  # too long
        assert not validate_cloudtrail_name('')
        assert not validate_cloudtrail_name(None)


class TestResourceNameSanitization:
    """Tests for resource name sanitization"""

    def test_sanitize_valid_names(self):
        """Test sanitizing valid names"""
        assert sanitize_resource_name('my-resource') == 'my-resource'
        assert sanitize_resource_name('my_resource') == 'my_resource'
        assert sanitize_resource_name('MyResource123') == 'MyResource123'

    def test_sanitize_dangerous_characters(self):
        """Test removal of dangerous characters"""
        assert sanitize_resource_name('my<script>alert()</script>') == 'myscriptalertscript'
        assert sanitize_resource_name('name@#$%') == 'name'
        assert sanitize_resource_name('path/to/file') == 'pathtofile'

    def test_sanitize_length_limit(self):
        """Test length limiting"""
        long_name = 'a' * 300
        result = sanitize_resource_name(long_name, max_length=50)
        assert len(result) == 50

    def test_sanitize_edge_cases(self):
        """Test edge cases"""
        assert sanitize_resource_name('') is None
        assert sanitize_resource_name(None) is None
        assert sanitize_resource_name('   ') is None  # whitespace only
        assert sanitize_resource_name('  name  ') == 'name'  # trimmed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
