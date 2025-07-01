# KOS Backend Engineer Work Trial - Data Package

This package contains all the data, configurations, and tools you need for the KOS Backend Engineer Work Trial. 

## Package Contents

### Data Files
- **`glucose_readings.json`** - Sample glucose monitoring data with various scenarios including normal readings, alerts, and edge cases
- **`user_profiles.json`** - User demographics and alert threshold configurations
- **`device_data.json`** - ARGUS device information, battery status, and sensor calibration data

### Configuration Files
- **`database_schema.sql`** - Complete PostgreSQL schema with tables, indexes, constraints, and sample data
- **`docker-compose.yml`** - Full development environment with PostgreSQL, Redis, and optional tools
- **`api_tests.postman_collection.json`** - Comprehensive Postman collection for API testing

### Documentation
- **`README.md`** - This file with setup instructions and usage guidelines

## Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed:
- **Docker & Docker Compose** (latest version)
- **Git** for version control
- **Your preferred code editor** (VS Code, IntelliJ, etc.)
- **Postman** or **curl** for API testing

### 2. Environment Setup

#### Start the Database and Cache
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Check database connection
docker-compose exec postgres psql -U glucose_user -d glucose_db -c "SELECT version();"

# Check Redis connection
docker-compose exec redis redis-cli -a redis_pass ping
```

#### Optional: Start Database Management Tools
```bash
# Start pgAdmin for database management
docker-compose --profile tools up -d postgres redis pgadmin

# Access pgAdmin at http://localhost:8081
# Email: admin@kos-ai.com, Password: admin_pass
```

### 3. Database Setup

The database schema and sample data are automatically loaded when you start the PostgreSQL container for the first time. The schema includes:

- **Users table** with demographic information
- **Devices table** with ARGUS device details
- **Glucose readings table** (main data table)
- **Alert configurations** and history
- **Analytics summaries** for performance
- **API audit logs** for compliance

### 4. Sample Data Overview

#### Users
- `user_5678` - 45F, medium skin tone, HbA1c 7.2
- `user_9012` - 67M, light skin tone, HbA1c 8.1  
- `user_3456` - 29F, dark skin tone, HbA1c 9.5
- `user_7890` - 38M, medium skin tone, HbA1c 6.8
- `user_1357` - 52F, light skin tone, HbA1c 10.1

#### Devices
- `ARGUS_001234` - Active device with good battery
- `ARGUS_002468` - Active device with fair battery
- `ARGUS_003691` - Active device, high-frequency sampling
- `ARGUS_004815` - New device with excellent battery
- `ARGUS_005927` - Device needing attention (low battery, poor readings)

#### Glucose Data Scenarios
- **Normal readings** - Typical glucose values with good confidence
- **Rapid changes** - Glucose spikes for alert testing
- **Low glucose** - Hypoglycemic readings for safety alerts
- **High glucose** - Hyperglycemic readings for management alerts
- **Poor signal quality** - Readings with motion artifacts and low confidence
- **Edge cases** - Extreme values for validation testing

### 5. API Testing

#### Import Postman Collection
1. Open Postman
2. Import `api_tests.postman_collection.json`
3. Collection includes:
   - All required API endpoints
   - Sample requests with realistic data
   - Validation tests for error handling
   - Authentication tests

#### API Endpoints to Implement
```
POST /api/v1/devices/{deviceId}/readings       # Submit glucose readings
GET  /api/v1/devices/{deviceId}/readings       # Get device readings
GET  /api/v1/users/{userId}/glucose/current    # Get current glucose
GET  /api/v1/users/{userId}/glucose/history    # Get glucose history
POST /api/v1/users/{userId}/alerts/configure   # Configure alerts
GET  /api/v1/users/{userId}/analytics/summary  # Get analytics
```

#### Test with curl
```bash
# Health check
curl http://localhost:8080/health

# Submit glucose reading (replace with your API)
curl -X POST http://localhost:8080/api/v1/devices/ARGUS_001234/readings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d @glucose_sample.json
```

### 6. Development Environment

#### Environment Variables
The docker-compose file sets up these environment variables for your application:

```bash
# Database
DATABASE_URL=postgresql://glucose_user:glucose_pass@postgres:5432/glucose_db
DB_HOST=postgres
DB_PORT=5432
DB_NAME=glucose_db
DB_USER=glucose_user
DB_PASSWORD=glucose_pass

# Redis
REDIS_URL=redis://:redis_pass@redis:6379
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass

# Application
PORT=8080
NODE_ENV=development
LOG_LEVEL=debug

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
API_KEY_SECRET=your-api-key-secret-change-this

# Medical device specific
MAX_GLUCOSE_READING_RATE=30  # seconds between readings
GLUCOSE_MIN_VALUE=40
GLUCOSE_MAX_VALUE=400
```

#### Your Application Integration
Once you've built your application:

1. Create a `Dockerfile` in the data directory
2. Update the `app` service in `docker-compose.yml`
3. Run: `docker-compose --profile app up`

### 7. Data Validation Requirements

Your implementation should validate:

#### Glucose Values
- Range: 40-400 mg/dL
- Required field: cannot be null
- Integer type

#### Rate Limiting
- Maximum 1 reading per 30 seconds per device
- Implement sliding window or token bucket

#### Sensor Data
- Validate sensor readings are within reasonable ranges
- Check for motion artifacts
- Validate signal quality enum values

#### Timestamps
- Must be valid ISO 8601 format
- Cannot be in the future
- Cannot be too far in the past (>24 hours)

### 8. Medical Domain Considerations

#### Alert Thresholds
- **Low glucose**: Typically <70 mg/dL (urgent)
- **High glucose**: Typically >180 mg/dL (concerning)
- **Rapid change**: >4 mg/dL/min (requires attention)

#### Safety Requirements
- Critical alerts must be delivered reliably
- Data integrity is paramount
- System should fail safely
- Audit all access for compliance

#### Compliance Awareness
- HIPAA: Protect patient health information
- FDA: Medical device software requirements
- Data retention: Legal requirements for medical records

### 9. Performance Considerations

#### Database Optimization
- Use provided indexes for time-series queries
- Consider connection pooling
- Implement proper error handling
- Use transactions for data consistency

#### Caching Strategy
- Cache frequently accessed user data in Redis
- Cache analytics summaries
- Implement cache invalidation strategy

#### Real-time Processing
- Process glucose readings quickly (<180ms target)
- Generate alerts in near real-time
- Handle high-frequency data ingestion

### 10. Troubleshooting

#### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Restart services
docker-compose restart postgres
```

**Redis Connection Failed**
```bash
# Check Redis status
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli -a redis_pass ping
```

**Port Conflicts**
```bash
# Check what's using port 5432/6379/8080
lsof -i :5432
lsof -i :6379
lsof -i :8080

# Modify ports in docker-compose.yml if needed
```

**Data Issues**
```bash
# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d postgres redis

# View database logs
docker-compose logs -f postgres
```

#### Useful Database Queries

```sql
-- Check sample data loaded correctly
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM devices;
SELECT COUNT(*) FROM glucose_readings;

-- View recent glucose readings
SELECT gr.timestamp, gr.glucose_value, gr.confidence, u.user_id, d.device_id
FROM glucose_readings gr
JOIN users u ON gr.user_id = u.user_id
JOIN devices d ON gr.device_id = d.device_id
ORDER BY gr.timestamp DESC
LIMIT 10;

-- Check alert configurations
SELECT ac.user_id, ac.low_glucose, ac.high_glucose, ac.rapid_change
FROM alert_configs ac
JOIN users u ON ac.user_id = u.user_id;
```

### 11. Security Notes

**WARNING**: This configuration is for development only!

For production, you should:
1. Change all default passwords
2. Use secrets management instead of environment variables
3. Enable SSL/TLS for all connections
4. Implement proper network segmentation
5. Use read-only database users for application queries
6. Enable database and Redis authentication
7. Configure proper firewall rules

### 12. Getting Help

#### Documentation
- Review the main work trial PDF for complete requirements
- Check the database schema comments for field explanations
- Use the Postman collection examples as reference

#### Testing Your Implementation
1. Start with the health check endpoint
2. Implement glucose reading submission
3. Add data validation and error handling
4. Implement user endpoints with authentication
5. Add real-time processing and alerts
6. Test with the provided Postman collection

#### Time Management Tips
- **Hour 1**: Get basic API working with database connection
- **Hour 2**: Implement core endpoints and validation
- **Hour 3**: Add security, testing, and documentation

---

**Good luck with your implementation!** Focus on building a robust, well-tested system that demonstrates your backend engineering skills and understanding of medical device requirements.
