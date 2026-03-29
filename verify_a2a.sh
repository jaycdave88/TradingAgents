#!/bin/bash
# Verification script for TradingAgents A2A server

echo "=== TradingAgents A2A Server Verification ==="
echo

# Check if server is running
echo "1. Checking if server is running on port 8100..."
if lsof -i:8100 > /dev/null 2>&1; then
    echo "   ✅ Server is running"
    PID=$(lsof -ti:8100)
    echo "   PID: $PID"
else
    echo "   ❌ Server is NOT running"
    exit 1
fi
echo

# Check agent card endpoint
echo "2. Testing agent card endpoint..."
AGENT_CARD=$(curl -s http://localhost:8100/.well-known/agent.json)
if [ $? -eq 0 ]; then
    echo "   ✅ Agent card endpoint responding"
    echo "$AGENT_CARD" | python3 -m json.tool | head -5
else
    echo "   ❌ Agent card endpoint failed"
    exit 1
fi
echo

# Test A2A endpoint (quick test)
echo "3. Testing A2A endpoint (this may take a few minutes)..."
echo "   Sending test request for AAPL analysis..."
START_TIME=$(date +%s)

RESULT=$(curl -s -X POST http://localhost:8100/a2a \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc": "2.0", "id": "verify-test", "method": "tasks/send", "params": {"message": {"parts": [{"type": "text", "text": "Quick analysis for AAPL"}]}}}')

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $? -eq 0 ]; then
    echo "   ✅ A2A endpoint responding"
    echo "   Duration: ${DURATION}s"
    
    # Check if we got a valid response
    STATE=$(echo "$RESULT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('result', {}).get('status', {}).get('state', 'unknown'))" 2>/dev/null)
    echo "   Task state: $STATE"
    
    if [ "$STATE" = "completed" ]; then
        echo "   ✅ Analysis completed successfully"
        # Show first 200 chars of response
        echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
artifacts = d.get('result', {}).get('artifacts', [])
if artifacts:
    text = artifacts[0]['parts'][0]['text']
    print('   Response preview:')
    print('   ' + text[:200] + '...')
" 2>/dev/null
    else
        echo "   ⚠️  Analysis state: $STATE"
    fi
else
    echo "   ❌ A2A endpoint failed"
    exit 1
fi
echo

echo "=== Verification Complete ==="
echo "Server is ready to receive stock analysis requests from MOMO via iMessage!"

