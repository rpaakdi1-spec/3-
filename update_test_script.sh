#!/bin/bash

# Quick Fix: Update test script on production server
# Issue: Authentication endpoint expects form data, not JSON
# Solution: Pull latest changes with fixed test script

echo "🔧 Updating Phase 9 test script with authentication fix..."
echo ""

cd /root/uvis

# Pull latest changes
echo "📥 Pulling latest changes..."
git fetch origin phase8-verification
git pull origin phase8-verification

echo ""
echo "✅ Test script updated!"
echo ""
echo "🚀 Now run the test:"
echo "   ./test_phase9_reports.sh"
echo ""
