#!/bin/bash
# Pre-Upload Security Check Script
# Run this before pushing to GitHub to ensure no sensitive data is included

set -e

echo "======================================================================"
echo "  AgentOps Safety Ecosystem - Pre-Upload Security Check"
echo "======================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Check 1: Search for hardcoded API keys
echo "🔍 Checking for hardcoded API keys..."
if git diff --cached | grep -qE "sk-proj-|sk-ant-api03-"; then
    echo -e "${RED}❌ FAIL: Found potential API keys in staged changes${NC}"
    echo "   Run: git diff --cached | grep -E 'sk-proj-|sk-ant-api03-'"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ PASS: No API keys found in staged changes${NC}"
fi

# Check 2: Ensure .env is not staged
echo ""
echo "🔍 Checking if .env is excluded..."
if git status --porcelain | grep -q "^[MARC]. \.env$"; then
    echo -e "${RED}❌ FAIL: .env file is staged for commit${NC}"
    echo "   Run: git reset HEAD .env"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ PASS: .env file is not staged${NC}"
fi

# Check 3: Ensure database files are not staged
echo ""
echo "🔍 Checking for database files..."
if git status --porcelain | grep -qE "\.db$|\.sqlite"; then
    echo -e "${YELLOW}⚠️  WARNING: Database files found in staged changes${NC}"
    echo "   These files should be excluded via .gitignore"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ PASS: No database files staged${NC}"
fi

# Check 4: Check for large files
echo ""
echo "🔍 Checking for large files (>10MB)..."
LARGE_FILES=$(git diff --cached --name-only | xargs -I {} du -m {} 2>/dev/null | awk '$1 > 10 {print $2}' || true)
if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Large files found:${NC}"
    echo "$LARGE_FILES"
    echo "   Consider using Git LFS or excluding these files"
else
    echo -e "${GREEN}✅ PASS: No large files detected${NC}"
fi

# Check 5: Verify .env.example exists
echo ""
echo "🔍 Checking for .env.example..."
if [ ! -f ".env.example" ]; then
    echo -e "${RED}❌ FAIL: .env.example not found${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ PASS: .env.example exists${NC}"
fi

# Check 6: Search for common secret patterns
echo ""
echo "🔍 Checking for other secret patterns..."
SECRET_PATTERNS="password|secret|token|private.*key"
if git diff --cached | grep -qiE "$SECRET_PATTERNS"; then
    echo -e "${YELLOW}⚠️  WARNING: Found potential secrets in staged changes${NC}"
    echo "   Review carefully: git diff --cached | grep -iE '$SECRET_PATTERNS'"
else
    echo -e "${GREEN}✅ PASS: No obvious secrets found${NC}"
fi

# Check 7: Verify documentation exists
echo ""
echo "🔍 Checking documentation files..."
MISSING_DOCS=0
[ ! -f "GITHUB_PREPARATION.md" ] && echo -e "${YELLOW}⚠️  Missing: GITHUB_PREPARATION.md${NC}" && MISSING_DOCS=1
[ ! -f "CLEANUP_SUMMARY.md" ] && echo -e "${YELLOW}⚠️  Missing: CLEANUP_SUMMARY.md${NC}" && MISSING_DOCS=1
[ ! -f "training/QUICKSTART.md" ] && echo -e "${YELLOW}⚠️  Missing: training/QUICKSTART.md${NC}" && MISSING_DOCS=1

if [ $MISSING_DOCS -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: All documentation files present${NC}"
fi

# Summary
echo ""
echo "======================================================================"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - Safe to upload to GitHub${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Commit: git commit -m 'Add agent safety ecosystem'"
    echo "  3. Push: git push origin main"
    echo ""
else
    echo -e "${RED}❌ $ISSUES_FOUND ISSUE(S) FOUND - Please fix before uploading${NC}"
    echo ""
    echo "Review the issues above and fix them before pushing to GitHub."
    echo ""
fi
echo "======================================================================"

exit $ISSUES_FOUND
