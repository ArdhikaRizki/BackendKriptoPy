#!/bin/bash

# Test API Script
# Untuk testing endpoint di server

SERVER_URL="${1:-http://localhost:5000}"

echo "=========================================="
echo "Testing Backend Kriptografi API"
echo "Server: $SERVER_URL"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Homepage
echo -e "${YELLOW}1. Testing Homepage (GET /)${NC}"
curl -s "$SERVER_URL/" | jq .
echo ""
echo "---"
echo ""

# Test 2: Debug endpoint GET
echo -e "${YELLOW}2. Testing Debug Endpoint (GET /api/debug)${NC}"
curl -s "$SERVER_URL/api/debug" | jq .
echo ""
echo "---"
echo ""

# Test 3: Debug endpoint POST
echo -e "${YELLOW}3. Testing Debug Endpoint (POST /api/debug)${NC}"
curl -s -X POST "$SERVER_URL/api/debug" \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}' | jq .
echo ""
echo "---"
echo ""

# Test 4: Test Database
echo -e "${YELLOW}4. Testing Database Connection (GET /api/test-db)${NC}"
curl -s "$SERVER_URL/api/test-db" | jq .
echo ""
echo "---"
echo ""

# Test 5: Hash Password
echo -e "${YELLOW}5. Testing Hash Password (POST /api/hash-password)${NC}"
curl -s -X POST "$SERVER_URL/api/hash-password" \
  -H "Content-Type: application/json" \
  -d '{"password":"password123"}' | jq .
echo ""
echo "---"
echo ""

# Test 6: Register User
echo -e "${YELLOW}6. Testing Register (POST /api/register)${NC}"
TIMESTAMP=$(date +%s)
curl -s -X POST "$SERVER_URL/api/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test${TIMESTAMP}@example.com\",\"password\":\"password123\",\"username\":\"testuser${TIMESTAMP}\"}" | jq .
echo ""
echo "---"
echo ""

# Test 7: Login User
echo -e "${YELLOW}7. Testing Login (POST /api/login)${NC}"
curl -s -X POST "$SERVER_URL/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test${TIMESTAMP}@example.com\",\"password\":\"password123\"}" | jq .
echo ""
echo "---"
echo ""

# Test 8: Get All Users
echo -e "${YELLOW}8. Testing Get Users (GET /api/users)${NC}"
curl -s "$SERVER_URL/api/users" | jq .
echo ""
echo "---"
echo ""

echo -e "${GREEN}=========================================="
echo "Testing Complete!"
echo "==========================================${NC}"
