#!/bin/bash

echo "🚨 Testing Rapid Glucose Change Alerts"
echo "======================================="

# Base timestamp - 2 minutes ago
BASE_TIME=$(date -u -v-2M +"%Y-%m-%dT%H:%M:%S.000Z")
# Current timestamp  
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

echo "📊 Submitting baseline reading (100 mg/dL)..."

curl -s -X POST "http://localhost:8000/api/v1/devices/ARGUS_001234/readings" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d "{
    \"deviceId\": \"ARGUS_001234\",
    \"userId\": \"user_5678\",
    \"timestamp\": \"$BASE_TIME\",
    \"glucoseValue\": 100,
    \"confidence\": 0.95,
    \"sensorData\": {
      \"red\": 1234.5, \"infrared\": 2345.6, \"green\": 3456.7,
      \"temperature\": 36.5, \"motionArtifact\": false
    },
    \"batteryLevel\": 85,
    \"signalQuality\": \"good\"
  }" | jq '.'

echo ""
echo "⏱️ Waiting 35 seconds for rate limit reset..."
sleep 35

echo ""
echo "🚨 Submitting rapid change reading (110 mg/dL in 2 minutes = 5 mg/dL/min)..."
echo "👀 WATCH THE API LOGS FOR: 'RAPID GLUCOSE CHANGE ALERT'"

curl -s -X POST "http://localhost:8000/api/v1/devices/ARGUS_001234/readings" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d "{
    \"deviceId\": \"ARGUS_001234\",
    \"userId\": \"user_5678\",
    \"timestamp\": \"$CURRENT_TIME\",
    \"glucoseValue\": 110,
    \"confidence\": 0.95,
    \"sensorData\": {
      \"red\": 1234.5, \"infrared\": 2345.6, \"green\": 3456.7,
      \"temperature\": 36.5, \"motionArtifact\": false
    },
    \"batteryLevel\": 85,
    \"signalQuality\": \"good\"
  }" | jq '.'

echo ""
echo "✅ Test complete! Check your API server logs for the alert message."
echo "Expected: 'RAPID GLUCOSE CHANGE ALERT for user_5678: change of 10.0 mg/dL over 2.0 minutes'" 