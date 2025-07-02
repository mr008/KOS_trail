# KOS Rapid Glucose Change Alert Test (Windows PowerShell Version)
# Run this in PowerShell after starting docker-compose up -d

Write-Host "🚨 Testing Rapid Glucose Change Alerts" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

# Base timestamp - 2 minutes ago
$BaseTime = (Get-Date).AddMinutes(-2).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
# Current timestamp  
$CurrentTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")

Write-Host "📊 Submitting baseline reading (100 mg/dL)..." -ForegroundColor Cyan

$BaselineBody = @{
    deviceId = "ARGUS_001234"
    userId = "user_5678"
    timestamp = $BaseTime
    glucoseValue = 100
    confidence = 0.95
    sensorData = @{
        red = 1234.5
        infrared = 2345.6
        green = 3456.7
        temperature = 36.5
        motionArtifact = $false
    }
    batteryLevel = 85
    signalQuality = "good"
} | ConvertTo-Json -Depth 3

$Headers = @{
    "X-API-Key" = "dev-api-key-12345"
    "Content-Type" = "application/json"
}

try {
    $Response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/devices/ARGUS_001234/readings" -Method POST -Body $BaselineBody -Headers $Headers
    Write-Host "✅ Baseline reading submitted: $($Response1.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error submitting baseline reading: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "⏱️ Waiting 35 seconds for rate limit reset..." -ForegroundColor Yellow
Start-Sleep -Seconds 35

Write-Host ""
Write-Host "🚨 Submitting rapid change reading (110 mg/dL in 2 minutes = 5 mg/dL/min)..." -ForegroundColor Yellow
Write-Host "👀 WATCH THE API LOGS FOR: 'RAPID GLUCOSE CHANGE ALERT'" -ForegroundColor Magenta

$RapidChangeBody = @{
    deviceId = "ARGUS_001234"
    userId = "user_5678"
    timestamp = $CurrentTime
    glucoseValue = 110
    confidence = 0.95
    sensorData = @{
        red = 1234.5
        infrared = 2345.6
        green = 3456.7
        temperature = 36.5
        motionArtifact = $false
    }
    batteryLevel = 85
    signalQuality = "good"
} | ConvertTo-Json -Depth 3

try {
    $Response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/devices/ARGUS_001234/readings" -Method POST -Body $RapidChangeBody -Headers $Headers
    Write-Host "✅ Rapid change reading submitted: $($Response2.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error submitting rapid change reading: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Test complete! Check your API server logs for the alert message." -ForegroundColor Green
Write-Host "Expected: 'RAPID GLUCOSE CHANGE ALERT for user_5678: change of 10.0 mg/dL over 2.0 minutes'" -ForegroundColor White

Write-Host ""
Write-Host "📋 To check Docker logs:" -ForegroundColor Cyan
Write-Host "docker logs kos_app --tail 10" -ForegroundColor Gray 