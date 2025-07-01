# KOS Glucose Monitoring API

A high-performance FastAPI backend service for glucose monitoring with ARGUS devices. Built with Python, PostgreSQL, and Redis for real-time glucose data processing and analytics.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (latest version)
- **Python 3.9+** 
- **Git**

### 1. Setup Database Services

You'll need the Docker services from the work trial data package:

```bash
# Navigate to the backend_work_trial_data directory and start services
cd ../backend_work_trial_data
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps
```

### 2. Install Dependencies

```bash
# In the kos-glucose-api directory
pip install -r requirements.txt
```

### 3. Start the API Server

```bash
python3 -m app.main
```

The API will be available at:
- **API Base**: http://localhost:8080
- **Interactive Docs**: http://localhost:8080/docs
- **Alternative Docs**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

## 📋 API Endpoints

### Health & Status
- `GET /health` - Health check with service status

### Glucose Readings
- `POST /api/v1/devices/{deviceId}/readings` - Submit glucose reading
- `GET /api/v1/users/{userId}/glucose/current` - Get latest glucose reading
- `GET /api/v1/devices/{deviceId}/readings` - Get device readings (coming soon)
- `GET /api/v1/users/{userId}/glucose/history` - Get glucose history (coming soon)

### Alert Management (Coming Soon)
- `POST /api/v1/users/{userId}/alerts/configure` - Configure alerts
- `GET /api/v1/users/{userId}/analytics/summary` - Get analytics

## 🧪 Testing

### Manual Testing with curl

#### 1. Health Check
```bash
curl http://localhost:8080/health
```

#### 2. Submit Glucose Reading
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d @sample_reading.json \
     http://localhost:8080/api/v1/devices/ARGUS_001234/readings
```

#### 3. Get Current Glucose
```bash
curl http://localhost:8080/api/v1/users/user_5678/glucose/current
```

### Sample Data

Use `sample_reading.json` for testing:

```json
{
  "deviceId": "ARGUS_001234",
  "userId": "user_5678", 
  "timestamp": "2025-01-08T10:00:00Z",
  "glucoseValue": 115,
  "confidence": 0.95,
  "sensorData": {
    "red": 2.40,
    "infrared": 1.85,
    "green": 3.05,
    "temperature": 36.2,
    "motionArtifact": false
  },
  "batteryLevel": 80,
  "signalQuality": "good"
}
```

### Database Verification

```bash
# From the backend_work_trial_data directory
docker-compose exec postgres psql -U glucose_user -d glucose_db -c \
  "SELECT glucose_value, confidence, device_id FROM glucose_readings WHERE glucose_value = 115;"
```

## 🏗️ Architecture

### Technology Stack
- **FastAPI** - Modern, high-performance web framework
- **PostgreSQL 15** - Primary database with JSONB support
- **Redis 7** - Caching and session management
- **asyncpg** - Async PostgreSQL driver
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server with auto-reload

### Project Structure
```
kos-glucose-api/
├── app/
│   ├── api/           # API route handlers
│   │   ├── __init__.py
│   │   └── glucose.py # Glucose readings endpoints
│   ├── core/          # Configuration and database
│   │   ├── config.py  # Settings management
│   │   ├── database.py # PostgreSQL connection
│   │   └── redis_client.py # Redis connection
│   ├── schemas/       # Pydantic models
│   │   ├── __init__.py
│   │   └── glucose.py # Glucose data models
│   ├── main.py        # FastAPI application
│   └── __init__.py
├── requirements.txt   # Python dependencies
├── config.env        # Environment configuration
├── sample_reading.json # Test data
└── README.md         # This file
```

## 🔧 Development

### Running in Development Mode

```bash
# With auto-reload
python3 -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Environment Configuration

The application uses `config.env` for configuration:

```bash
# Database Configuration (connects to Docker services)
DATABASE_URL=postgresql://glucose_user:glucose_pass@localhost:5432/glucose_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=glucose_db
DB_USER=glucose_user
DB_PASSWORD=glucose_pass

# Redis Configuration  
REDIS_URL=redis://:redis_pass@localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass

# Application Configuration
PORT=8080
HOST=0.0.0.0
DEBUG=true

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
API_KEY_SECRET=dev-api-key-12345

# Medical Device Specific
MAX_GLUCOSE_READING_RATE=30
GLUCOSE_MIN_VALUE=40
GLUCOSE_MAX_VALUE=400
```

## 📊 Data Validation

### Glucose Value Constraints
- **Range**: 40-400 mg/dL
- **Type**: Integer
- **Required**: Yes

### Sensor Data Validation
- **Temperature**: 30-45°C (body temperature range)
- **Confidence**: 0.0-1.0 (percentage as decimal)
- **Signal Quality**: "excellent" | "good" | "fair" | "poor"

### Rate Limiting
- Maximum 1 reading per 30 seconds per device
- Prevents data spam and ensures data quality

## 🚨 Error Handling

The API returns structured error responses:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created (new reading)
- `400` - Bad Request (validation error)
- `404` - Not Found (user/device not found)
- `422` - Unprocessable Entity (invalid JSON)
- `500` - Internal Server Error

## 🔒 Security Considerations

### Current Implementation (Development)
- Basic API key authentication
- CORS enabled for all origins
- Input validation with Pydantic

### Production Recommendations
- Implement JWT authentication
- Add rate limiting middleware
- Enable HTTPS/TLS
- Restrict CORS origins
- Add API versioning
- Implement proper logging
- Add monitoring and alerting

## 🧪 Medical Domain Features

### Alert Thresholds
- **Low glucose**: <70 mg/dL (urgent)
- **High glucose**: >180 mg/dL (concerning) 
- **Rapid change**: >4 mg/dL/min (requires attention)

### Compliance Features
- Audit logging for all data access
- Data retention policies
- HIPAA-ready architecture (with proper configuration)

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8080
lsof -i :8080

# Kill process if needed
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check PostgreSQL status (from backend_work_trial_data directory)
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### Dependencies Issues
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is part of the KOS Backend Engineer Work Trial.

---

**Built with ❤️ using FastAPI and modern Python async patterns** 