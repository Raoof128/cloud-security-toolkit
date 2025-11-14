#!/usr/bin/env python3
"""
Remediation Example
Demonstrates how to use automated remediation features safely
"""
from remediation.aws_remediation import AWSRemediation


def main():
    """Example of safe remediation workflow"""
    print("AWS Security Remediation Example")
    print("=" * 80)

    # STEP 1: Always start with dry-run mode
    print("\n[STEP 1] Running in DRY-RUN mode (safe, no changes made)")
    print("-" * 80)

    remediator = AWSRemediation(region='us-east-1', dry_run=True)

    # Example: Enable S3 bucket encryption
    bucket_name = 'my-test-bucket'
    print(f"\nTesting encryption enablement on bucket: {bucket_name}")
    remediator.enable_s3_encryption(bucket_name)

    # Example: Enable S3 versioning
    print(f"\nTesting versioning enablement on bucket: {bucket_name}")
    remediator.enable_s3_versioning(bucket_name)

    # Example: Block public access
    print(f"\nTesting public access block on bucket: {bucket_name}")
    remediator.block_s3_public_access(bucket_name)

    # Review dry-run results
    print("\n" + "=" * 80)
    print("DRY-RUN SUMMARY")
    print("=" * 80)
    print(f"Actions simulated: {len(remediator.remediation_log)}")

    for action in remediator.remediation_log:
        print(f"  [{action['status'].upper()}] {action['action']} on {action['resource']}")

    # STEP 2: Review and confirm
    print("\n" + "=" * 80)
    print("[STEP 2] Review Results")
    print("=" * 80)
    print("\nIn a real scenario, you would:")
    print("1. Review the dry-run output above")
    print("2. Verify the changes are safe")
    print("3. Get approval if required")
    print("4. Create a backup/snapshot if needed")
    print("5. Run with dry_run=False to apply changes")

    # STEP 3: Live mode (commented out for safety)
    print("\n" + "=" * 80)
    print("[STEP 3] Live Mode (EXAMPLE - NOT EXECUTED)")
    print("=" * 80)
    print("""
# To run in live mode:
remediator_live = AWSRemediation(region='us-east-1', dry_run=False)
remediator_live.enable_s3_encryption('my-test-bucket')

# Always save the remediation log for audit purposes:
import json
with open('remediation_audit.json', 'w') as f:
    json.dump(remediator_live.remediation_log, f, indent=2)
    """)

    print("\n✅ Remediation example completed (dry-run only, no changes made)")
    print("=" * 80)


if __name__ == '__main__':
    main()
