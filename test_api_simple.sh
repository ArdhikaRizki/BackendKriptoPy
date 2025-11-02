#!/bin/bash

# Simple API Test Script
# Usage: ./test_api_simple.sh [server_url]

SERVER_URL="${1:-http://localhost:5000}"

echo "Testing: $SERVER_URL"
echo ""

# Test Homepage
echo "=== Test 1: Homepage ==="
curl -i "$SERVER_URL/"
echo ""
echo ""

# Test Debug
echo "=== Test 2: Debug Endpoint ==="
curl -i -X POST "$SERVER_URL/api/debug" \
  -H "Content-Type: application/json" \
  -d '{"test":"hello"}'
echo ""
echo ""

# Test Register
echo "=== Test 3: Register ==="
curl -i -X POST "$SERVER_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"testuser"}'
echo ""
echo ""

# Test Login
echo "=== Test 4: Login ==="
curl -i -X POST "$SERVER_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
echo ""
