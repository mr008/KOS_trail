# KOS Glucose Monitoring API - Demo Script

## 🎯 **Demo Overview**
This script provides a complete, professional demonstration of the KOS Glucose Monitoring API using terminal-based tools. The demo showcases enterprise-grade features including authentication, validation, rate limiting, and database integration.

## 🖥️ **Terminal Setup**
**Recommended Layout**: 3 terminal windows side-by-side

1. **Terminal 1 (Logs)**: `docker-compose up` - Shows real-time application logs
2. **Terminal 2 (Commands)**: Main command center for curl requests and testing  
3. **Terminal 3 (Database)**: PostgreSQL queries to verify data persistence

---

## 📋 **Demo Script**

### **Phase 1: System Startup & Health Check**

#### Terminal 1 - Start the Stack
```bash
# Start all services with real-time logs
docker-compose up

# Look for these success indicators:
# ✅ Database connected successfully
# ✅ Redis connected successfully  
# ✅ All services connected successfully
# INFO: Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2 - Verify Health
```bash
# 1. Basic health check
curl -i http://localhost:8000/health

# Expected: HTTP/1.1 200 OK
# {
#   "status": "OK",
#   "timestamp": "2025-07-01T23:XX:XX.XXXXXX",
#   "service": "KOS Glucose Monitoring API",
#   "version": "1.0.0"
# }
```

**🗣️ Talking Point**: "The health endpoint confirms all services are running. Notice the clean JSON response with timestamp - this is what monitoring systems use."

### **Phase 2: Security Demonstration**

#### Terminal 2 - Authentication Testing
```bash
# 2. Test missing authentication (should fail)
curl -i -X POST \
  -H "Content-Type: application/json" \
  -d @tests/valid_reading.json \
  http://localhost:8000/api/v1/devices/ARGUS_001234/readings

# Expected: HTTP/1.1 401 Unauthorized
# {"detail":"Missing API key. Please include X-API-Key header."}
```

**🗣️ Talking Point**: "Security is enforced at the endpoint level. Without proper authentication, requests are immediately rejected."

### **Phase 3: Successful Data Ingestion**

#### Terminal 2 - Valid Glucose Reading
```bash
# 4. Submit valid glucose reading with authentication
curl -i -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d @tests/valid_reading.json \
  http://localhost:8000/api/v1/devices/ARGUS_001234/readings

# Expected: HTTP/1.1 201 Created
# {
#   "status": "processed",
#   "id": "uuid-here",
#   "message": "Glucose reading saved successfully"
# }
```

**🗣️ Talking Point**: "Success! Look at Terminal 1 - you'll see the request logged in real-time. The API returns a unique ID for tracking this reading."

---

## 🔧 **Technical Highlights**

### **1. Enterprise Architecture**
- Async/await for high concurrency
- Connection pooling for database efficiency
- Health checks and graceful shutdown
- Comprehensive error handling

### **2. Security Implementation**
- Multi-layer authentication (API keys + JWT)
- Rate limiting per device
- Input validation with Pydantic
- SQL injection prevention with parameterized queries

### **3. Production Readiness**
- Docker containerization
- Health check endpoints
- Structured logging
- Configuration management
- Comprehensive testing

---

## 📝 **Demo Notes**
- **Duration**: ~10-15 minutes
- **Preparation**: Ensure Docker is running, test files are in place
- **Extensions**: Can show API documentation at http://localhost:8000/docs
