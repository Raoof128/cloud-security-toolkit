#!/bin/bash
# Comprehensive Test Script for Cloud Security Toolkit
# Tests all major components and features

set -e  # Exit on error

echo "========================================="
echo "Cloud Security Toolkit - Test Suite"
echo "========================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

passed=0
failed=0

# Test function
run_test() {
    local test_name="$1"
    local command="$2"

    echo -n "Testing: $test_name... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((failed++))
        return 1
    fi
}

# Test 1: Python syntax
echo "=== Syntax Tests ==="
run_test "Main CLI syntax" "python3 -m py_compile cloud_security_audit.py"
run_test "AWS scanner syntax" "python3 -m py_compile scanners/aws_scanner.py"
run_test "Risk scoring syntax" "python3 -m py_compile utils/risk_scoring.py"
run_test "Remediation syntax" "python3 -m py_compile remediation/aws_remediation.py"
run_test "Report generator syntax" "python3 -m py_compile reporting/report_generator.py"
run_test "Demo mode syntax" "python3 -m py_compile demo_mode.py"
run_test "Verify script syntax" "python3 -m py_compile verify_installation.py"
echo

# Test 2: Module imports (non-AWS)
echo "=== Module Import Tests ==="
run_test "Risk scoring import" "python3 -c 'from utils.risk_scoring import RiskScorer'"
run_test "Report generator import" "python3 -c 'from reporting.report_generator import SecurityReportGenerator'"
echo

# Test 3: CLI tests
echo "=== CLI Tests ==="
run_test "CLI help" "python3 cloud_security_audit.py --help"
run_test "Demo mode help" "python3 demo_mode.py --help"
run_test "Verify script help" "python3 verify_installation.py"
echo

# Test 4: Demo mode tests
echo "=== Demo Mode Tests ==="
run_test "Demo mode HTML" "python3 cloud_security_audit.py --demo --output test_demo.html --quiet"
run_test "Demo mode JSON" "python3 demo_mode.py --format json --output test_demo.json"
run_test "Demo mode CSV" "python3 demo_mode.py --format csv --output test_demo.csv"
echo

# Test 5: File checks
echo "=== File Structure Tests ==="
required_files=(
    "cloud_security_audit.py"
    "demo_mode.py"
    "verify_installation.py"
    "requirements.txt"
    "README.md"
    "QUICKSTART.md"
    "LICENSE"
    ".gitignore"
    "scanners/__init__.py"
    "scanners/aws_scanner.py"
    "utils/__init__.py"
    "utils/risk_scoring.py"
    "remediation/__init__.py"
    "remediation/aws_remediation.py"
    "reporting/__init__.py"
    "reporting/report_generator.py"
    "reporting/templates/security_report.html"
    "config/aws_config.yaml"
    "docs/INSTALLATION.md"
    "docs/USAGE.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        ((passed++))
    else
        echo -e "${RED}✗ Missing: $file${NC}"
        ((failed++))
    fi
done
echo -e "${GREEN}✓ ${#required_files[@]} required files checked${NC}"
echo

# Test 6: Generated reports
echo "=== Report Validation Tests ==="
if [ -f "test_demo.html" ]; then
    size=$(stat -f%z "test_demo.html" 2>/dev/null || stat -c%s "test_demo.html" 2>/dev/null)
    if [ "$size" -gt 10000 ]; then
        echo -e "${GREEN}✓ HTML report generated (${size} bytes)${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ HTML report too small${NC}"
        ((failed++))
    fi
else
    echo -e "${YELLOW}⚠ No HTML report found (run demo first)${NC}"
fi

if [ -f "test_demo.json" ]; then
    if python3 -c "import json; json.load(open('test_demo.json'))" 2>/dev/null; then
        echo -e "${GREEN}✓ JSON report is valid${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ JSON report is invalid${NC}"
        ((failed++))
    fi
else
    echo -e "${YELLOW}⚠ No JSON report found${NC}"
fi

if [ -f "test_demo.csv" ]; then
    lines=$(wc -l < "test_demo.csv")
    if [ "$lines" -gt 5 ]; then
        echo -e "${GREEN}✓ CSV report generated (${lines} lines)${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ CSV report too small${NC}"
        ((failed++))
    fi
else
    echo -e "${YELLOW}⚠ No CSV report found${NC}"
fi
echo

# Test 7: Functionality tests
echo "=== Functionality Tests ==="
run_test "Risk scoring calculation" "python3 -c 'from utils.risk_scoring import RiskScorer; rs = RiskScorer(); score = rs.calculate_finding_score({\"severity\": \"HIGH\", \"type\": \"S3 Bucket\", \"exposure\": \"public\"}); assert score > 0'"
run_test "Security grade calculation" "python3 -c 'from utils.risk_scoring import RiskScorer; rs = RiskScorer(); grade = rs.get_security_grade(85); assert grade in [\"A+\", \"A\", \"A-\", \"B+\"]'"
echo

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "Passed: ${GREEN}${passed}${NC}"
echo -e "Failed: ${RED}${failed}${NC}"
total=$((passed + failed))
echo "Total:  ${total}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
