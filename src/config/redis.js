const { createClient } = require('redis');
require('dotenv').config({ path: './config.env' });

const redisClient = createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  password: process.env.REDIS_PASSWORD,
});

redisClient.on('error', (err) => {
  console.error('❌ Redis Client Error:', err);
});

redisClient.on('connect', () => {
  console.log('✅ Redis connected successfully');
});

const connectRedis = async () => {
  try {
    await redisClient.connect();
    return true;
  } catch (err) {
    console.error('❌ Redis connection failed:', err);
    return false;
  }
};

module.exports = {
  redisClient,
  connectRedis
}; 