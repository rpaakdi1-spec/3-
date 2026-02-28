#!/bin/bash

# Script to fix multiple migration heads issue

echo "=========================================="
echo "Migration Heads Fix Script"
echo "=========================================="
echo ""

# Step 1: Check current migration heads
echo "📋 Step 1: Checking current migration heads..."
docker-compose run --rm backend alembic heads

echo ""
echo "📋 Step 2: Checking migration history..."
docker-compose run --rm backend alembic history | head -20

echo ""
echo "=========================================="
echo "To fix this, we need to:"
echo "1. Identify all head revisions"
echo "2. Create a merge migration that combines them"
echo "3. Or specify which head to use"
echo "=========================================="
