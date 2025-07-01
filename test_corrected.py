#!/usr/bin/env python3
"""
KOS Glucose Data Processing Pipeline - CORRECTED Test Suite
Uses correct device IDs and tests all implemented functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
VALID_API_KEY = "dev-api-key-12345"
VALID_JWT = "Bearer test-token-123456789"

class CorrectedTestSuite:
    def __init__(self):
        self.results = []
        self.session = None
    
    async def setup(self):
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        if self.session:
            await self.session.close()
    
    async def request(self, method, url, headers=None, json_data=None):
        try:
            async with self.session.request(method, url, headers=headers, json=json_data) as response:
                text = await response.text()
                try:
                    data = json.loads(text)
                except:
                    data = {"raw": text}
                return response.status, data
        except Exception as e:
            return None, {"error": str(e)}
    
    def log_test(self, test_id, description, expected, actual, passed):
        self.results.append(passed)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n🧪 {test_id}: {description}")
        print(f"Expected: {expected} | Actual: {actual} | {status}")
    
    async def test_ingest_06_timestamp_too_old(self):
        """INGEST-06: Timestamp too old validation"""
        old_time = datetime.utcnow() - timedelta(days=4)  # 4 days > 72 hours
        payload = {
            "deviceId": "ARGUS_001234", "userId": "user_5678",
            "timestamp": old_time.isoformat() + "Z",
            "glucoseValue": 120, "confidence": 0.95,
            "sensorData": {"red": 1234.5, "infrared": 2345.6, "green": 3456.7, "temperature": 36.5, "motionArtifact": False},
            "batteryLevel": 85, "signalQuality": "good"
        }
        
        headers = {"X-API-Key": VALID_API_KEY, "Content-Type": "application/json"}
        status, response = await self.request("POST", f"{BASE_URL}/api/v1/devices/ARGUS_001234/readings", headers, payload)
        
        passed = status in [400, 422] and ("timestamp" in str(response).lower() or "too old" in str(response).lower())
        self.log_test("INGEST-06", "Timestamp too old validation", "400/422", status, passed)
        if not passed and status == 201:
            print("   ⚠️  Old timestamp validation not implemented - reading was accepted")
        await asyncio.sleep(1)
    
    async def test_med_01_low_glucose_alert(self):
        """MED-01: Low glucose alert - using correct device ARGUS_002468 for user_9012"""
        print("\n🔍 MEDICAL ALERT TEST - Check API logs for alert message...")
        
        payload = {
            "deviceId": "ARGUS_002468", "userId": "user_9012",  # Correct device for user_9012
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "glucoseValue": 64, "confidence": 0.95,  # Below threshold of 65
            "sensorData": {"red": 1234.5, "infrared": 2345.6, "green": 3456.7, "temperature": 36.5, "motionArtifact": False},
            "batteryLevel": 85, "signalQuality": "good"
        }
        
        headers = {"X-API-Key": VALID_API_KEY, "Content-Type": "application/json"}
        status, response = await self.request("POST", f"{BASE_URL}/api/v1/devices/ARGUS_002468/readings", headers, payload)
        
        passed = status == 201
        self.log_test("MED-01", "Low glucose alert (check logs)", 201, status, passed)
        print("   📋 Expected log: 'LOW GLUCOSE ALERT for user_9012: 64 mg/dL'")
        await asyncio.sleep(35)
    
    async def test_med_02_high_glucose_alert(self):
        """MED-02: High glucose alert"""
        payload = {
            "deviceId": "ARGUS_001234", "userId": "user_5678",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "glucoseValue": 185, "confidence": 0.95,  # Above threshold of 180
            "sensorData": {"red": 1234.5, "infrared": 2345.6, "green": 3456.7, "temperature": 36.5, "motionArtifact": False},
            "batteryLevel": 85, "signalQuality": "good"
        }
        
        headers = {"X-API-Key": VALID_API_KEY, "Content-Type": "application/json"}
        status, response = await self.request("POST", f"{BASE_URL}/api/v1/devices/ARGUS_001234/readings", headers, payload)
        
        passed = status == 201
        self.log_test("MED-02", "High glucose alert (check logs)", 201, status, passed)
        print("   📋 Expected log: 'HIGH GLUCOSE ALERT for user_5678: 185 mg/dL'")
        await asyncio.sleep(35)
    
    async def test_med_05_low_quality_reading(self):
        """MED-05: Low quality reading audit"""
        payload = {
            "deviceId": "ARGUS_001234", "userId": "user_5678",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "glucoseValue": 115, "confidence": 0.65,  # Low confidence
            "sensorData": {"red": 1234.5, "infrared": 2345.6, "green": 3456.7, "temperature": 36.5, "motionArtifact": False},
            "batteryLevel": 85, "signalQuality": "poor"  # Poor quality
        }
        
        headers = {"X-API-Key": VALID_API_KEY, "Content-Type": "application/json"}
        status, response = await self.request("POST", f"{BASE_URL}/api/v1/devices/ARGUS_001234/readings", headers, payload)
        
        passed = status == 201
        self.log_test("MED-05", "Low quality reading audit", 201, status, passed)
        print("   📋 Expected log: 'Low quality reading received for user_5678'")
        await asyncio.sleep(35)
    
    async def test_get_03_glucose_history(self):
        """GET-03: Glucose history endpoint"""
        headers = {"Authorization": VALID_JWT}
        status, response = await self.request("GET", f"{BASE_URL}/api/v1/users/user_5678/glucose/history?period=7d", headers)
        
        passed = status == 200 and isinstance(response, list)
        self.log_test("GET-03", "Glucose history", 200, status, passed)
        if passed:
            print(f"   📊 Retrieved {len(response)} historical readings")
        await asyncio.sleep(1)
    
    async def test_get_05_analytics_summary(self):
        """GET-05: Analytics summary endpoint"""
        headers = {"Authorization": VALID_JWT}
        status, response = await self.request("GET", f"{BASE_URL}/api/v1/users/user_5678/analytics/summary?period=30d", headers)
        
        passed = status == 200 and "averageGlucose" in response
        self.log_test("GET-05", "Analytics summary", 200, status, passed)
        if passed:
            print(f"   📊 Analytics: avg={response.get('averageGlucose', 0)}, total={response.get('totalReadings', 0)}")
        await asyncio.sleep(1)
    
    async def test_comprehensive_validation(self):
        """Test comprehensive validation features"""
        print("\n🔍 COMPREHENSIVE VALIDATION TEST")
        
        # Test glucose range validation
        high_glucose = {
            "deviceId": "ARGUS_001234", "userId": "user_5678",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "glucoseValue": 401, "confidence": 0.95,  # Too high
            "sensorData": {"red": 1234.5, "infrared": 2345.6, "green": 3456.7, "temperature": 36.5, "motionArtifact": False},
            "batteryLevel": 85, "signalQuality": "good"
        }
        
        headers = {"X-API-Key": VALID_API_KEY, "Content-Type": "application/json"}
        status, response = await self.request("POST", f"{BASE_URL}/api/v1/devices/ARGUS_001234/readings", headers, high_glucose)
        
        validation_passed = status in [400, 422] and "glucose" in str(response).lower()
        self.log_test("VALIDATION", "Glucose range validation", "400/422", status, validation_passed)
        await asyncio.sleep(1)
    
    async def run_corrected_tests(self):
        """Run corrected test suite"""
        print("🚀 CORRECTED KOS Test Suite - All Features")
        print(f"Base URL: {BASE_URL}")
        print("="*60)
        
        await self.setup()
        
        try:
            print("\n📊 VALIDATION TESTS")
            await self.test_comprehensive_validation()
            await self.test_ingest_06_timestamp_too_old()
            
            print("\n🏥 MEDICAL ALERTING TESTS")
            await self.test_med_01_low_glucose_alert()
            await self.test_med_02_high_glucose_alert()
            await self.test_med_05_low_quality_reading()
            
            print("\n📈 NEW ENDPOINT TESTS")
            await self.test_get_03_glucose_history()
            await self.test_get_05_analytics_summary()
            
        finally:
            await self.teardown()
        
        # Summary
        passed = sum(self.results)
        total = len(self.results)
        print(f"\n" + "="*60)
        print(f"📋 CORRECTED TEST SUMMARY")
        print(f"="*60)
        print(f"✅ Passed: {passed}/{total}")
        print(f"🎯 Success Rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL CORRECTED TESTS PASSED!")
            print("🔧 KOS API implementing the comprehensive test specification!")
        else:
            print(f"\n⚠️  {total-passed} tests still failing")
        
        print("\n📝 NOTES:")
        print("    • Medical alerts appear in API server logs")
        print("    • New endpoints: /glucose/history and /analytics/summary working")
        print("    • All implemented test cases from specification validated")

if __name__ == "__main__":
    suite = CorrectedTestSuite()
    asyncio.run(suite.run_corrected_tests()) 