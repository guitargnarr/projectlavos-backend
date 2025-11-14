package com.matthewscott.textanalysis.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.TimeUnit;

/**
 * Cache Service for Sentinel Platform
 * Provides Redis caching with consistent key generation and TTL management
 *
 * @author Matthew David Scott
 */
@Service
public class CacheService {

    private static final Logger logger = LoggerFactory.getLogger(CacheService.class);

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get cached value
     *
     * @param service Service name (sentiment, leads, phishing)
     * @param input   Input data to hash
     * @param clazz   Class to deserialize to
     * @return Cached object or null if not found
     */
    public <T> T get(String service, String input, Class<T> clazz) {
        try {
            String key = generateKey(service, input);
            String cached = redisTemplate.opsForValue().get(key);

            if (cached != null) {
                logger.info("[CACHE HIT] {}:{}", service, input.substring(0, Math.min(30, input.length())));
                return objectMapper.readValue(cached, clazz);
            } else {
                logger.info("[CACHE MISS] {}:{}", service, input.substring(0, Math.min(30, input.length())));
                return null;
            }
        } catch (JsonProcessingException e) {
            logger.error("Cache deserialization error: {}", e.getMessage());
            return null;
        } catch (Exception e) {
            logger.warn("Cache get error: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Cache value with TTL
     *
     * @param service Service name
     * @param input   Input data to hash
     * @param value   Value to cache
     * @param ttlSeconds TTL in seconds
     */
    public void set(String service, String input, Object value, long ttlSeconds) {
        try {
            String key = generateKey(service, input);
            String json = objectMapper.writeValueAsString(value);

            redisTemplate.opsForValue().set(key, json, ttlSeconds, TimeUnit.SECONDS);
            logger.debug("[CACHED] {}:{} (TTL: {}s)", service, input.substring(0, Math.min(30, input.length())), ttlSeconds);
        } catch (JsonProcessingException e) {
            logger.error("Cache serialization error: {}", e.getMessage());
        } catch (Exception e) {
            logger.warn("Cache set error: {}", e.getMessage());
        }
    }

    /**
     * Generate consistent cache key from service + input
     */
    private String generateKey(String service, String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(input.getBytes());
            StringBuilder hexString = new StringBuilder();

            for (int i = 0; i < Math.min(8, hash.length); i++) {
                String hex = Integer.toHexString(0xff & hash[i]);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }

            return service + ":" + hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            // Fallback to simple hash if SHA-256 unavailable
            return service + ":" + Math.abs(input.hashCode());
        }
    }
}
