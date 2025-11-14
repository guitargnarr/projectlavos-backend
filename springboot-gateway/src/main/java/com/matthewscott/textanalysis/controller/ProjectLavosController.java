package com.matthewscott.textanalysis.controller;

import com.matthewscott.textanalysis.service.CacheService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;

/**
 * Project Lavos Gateway Controller
 * Routes to C++ (fast demos) or FastAPI (Claude demos)
 *
 * @author Matthew David Scott
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class ProjectLavosController {

    private final WebClient cppClient;
    private final WebClient fastApiClient;
    private final WebClient mlEnsembleClient;
    private final CacheService cacheService;

    @Autowired
    public ProjectLavosController(CacheService cacheService) {
        this.cacheService = cacheService;
        // C++ processor (fast text analysis)
        this.cppClient = WebClient.builder()
                .baseUrl("http://localhost:9000")
                .build();

        // FastAPI backend (Claude API demos)
        this.fastApiClient = WebClient.builder()
                .baseUrl("http://localhost:8000")
                .build();

        // Python ML Ensemble (PhishGuard)
        this.mlEnsembleClient = WebClient.builder()
                .baseUrl("http://localhost:9001")
                .build();
    }

    // =========================================================================
    // FAST DEMOS (Route to C++)
    // =========================================================================

    @PostMapping("/sentiment")
    public ResponseEntity<Map<String, Object>> sentimentAnalysis(@RequestBody Map<String, String> request) {
        try {
            String text = request.get("text");

            // Check cache first
            Map<String, Object> cachedResult = cacheService.get("sentiment", text, Map.class);
            if (cachedResult != null) {
                return ResponseEntity.ok(cachedResult);
            }

            // Route to C++ for ultra-fast sentiment
            Map<String, Object> cppResult = cppClient.post()
                    .uri("/analyze")
                    .bodyValue(Map.of("text", text))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(2))
                    .block();

            // Transform to FastAPI contract
            Number sentimentNumber = (Number) cppResult.get("sentiment");
            double sentimentScore = sentimentNumber.doubleValue();
            String sentiment;
            String explanation;

            if (sentimentScore > 0.6) {
                sentiment = "positive";
                explanation = "Text expresses satisfaction and positive sentiment.";
            } else if (sentimentScore < 0.4) {
                sentiment = "negative";
                explanation = "Text expresses dissatisfaction and negative sentiment.";
            } else {
                sentiment = "neutral";
                explanation = "Text is balanced with no strong sentiment.";
            }

            Map<String, Object> result = Map.of(
                    "sentiment", sentiment,
                    "confidence", Math.round(sentimentScore * 100) / 100.0,
                    "explanation", explanation
            );

            // Cache result (1 hour)
            cacheService.set("sentiment", text, result, 3600);

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of("error", "C++ processor unavailable"));
        }
    }

    @PostMapping("/leads")
    public ResponseEntity<Map<String, Object>> leadScoring(@RequestBody Map<String, String> request) {
        try {
            String cacheKey = request.get("email") + ":" + request.get("company");

            // Check cache first
            Map<String, Object> cachedResult = cacheService.get("leads", cacheKey, Map.class);
            if (cachedResult != null) {
                return ResponseEntity.ok(cachedResult);
            }

            // Route to C++ for fast lead scoring
            Map<String, Object> result = cppClient.post()
                    .uri("/score-lead")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(2))
                    .block();

            // Cache result (24 hours)
            cacheService.set("leads", cacheKey, result, 86400);

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of("error", "C++ processor unavailable"));
        }
    }

    @PostMapping("/phishing")
    public ResponseEntity<Map<String, Object>> phishingDetection(@RequestBody Map<String, String> request) {
        try {
            String cacheKey = request.get("sender") + ":" + request.get("subject");

            // Check cache first
            Map<String, Object> cachedResult = cacheService.get("phishing", cacheKey, Map.class);
            if (cachedResult != null) {
                return ResponseEntity.ok(cachedResult);
            }

            // Route to C++ for fast phishing detection
            Map<String, Object> result = cppClient.post()
                    .uri("/detect-phishing")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(2))
                    .block();

            // Cache result (24 hours)
            cacheService.set("phishing", cacheKey, result, 86400);

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of("error", "C++ processor unavailable"));
        }
    }

    @PostMapping("/phishing/ensemble")
    public Mono<ResponseEntity<Map>> phishingEnsemble(@RequestBody Map<String, String> request) {
        // Step 1: Extract features with C++ processor
        return cppClient.post()
                .uri("/extract-phishing-features")
                .bodyValue(Map.of("text", request.getOrDefault("text", "")))
                .retrieve()
                .bodyToMono(Map.class)
                .flatMap(features -> {
                    // Step 2: Send features to ML ensemble
                    return mlEnsembleClient.post()
                            .uri("/classify-ensemble")
                            .bodyValue(Map.of(
                                "features", features.get("features"),
                                "text", request.getOrDefault("text", "")
                            ))
                            .retrieve()
                            .toEntity(Map.class);
                })
                .timeout(Duration.ofSeconds(5))
                .onErrorReturn(ResponseEntity.status(503).body(Map.of("error", "ML ensemble unavailable")));
    }

    // =========================================================================
    // CLAUDE DEMOS (Proxy to FastAPI)
    // =========================================================================

    @PostMapping("/analyze-restaurant")
    public Mono<ResponseEntity<Map>> restaurantAnalysis(@RequestBody Map<String, String> request) {
        // Proxy to FastAPI (keep Claude logic)
        return fastApiClient.post()
                .uri("/api/analyze-restaurant")
                .bodyValue(request)
                .retrieve()
                .toEntity(Map.class)
                .timeout(Duration.ofSeconds(30));
    }

    @PostMapping("/score-email")
    public Mono<ResponseEntity<Map>> emailScoring(@RequestBody Map<String, Object> request) {
        // Proxy to FastAPI (keep Claude logic)
        return fastApiClient.post()
                .uri("/api/score-email")
                .bodyValue(request)
                .retrieve()
                .toEntity(Map.class)
                .timeout(Duration.ofSeconds(30));
    }

    @PostMapping("/prompt-engineering")
    public Mono<ResponseEntity<Map>> promptEngineering(@RequestBody Map<String, String> request) {
        // Proxy to FastAPI (keep Claude logic)
        return fastApiClient.post()
                .uri("/api/prompt-engineering")
                .bodyValue(request)
                .retrieve()
                .toEntity(Map.class)
                .timeout(Duration.ofSeconds(30));
    }

    @PostMapping("/contact")
    public Mono<ResponseEntity<Map>> contact(@RequestBody Map<String, String> request) {
        // Proxy to FastAPI
        return fastApiClient.post()
                .uri("/api/contact")
                .bodyValue(request)
                .retrieve()
                .toEntity(Map.class)
                .timeout(Duration.ofSeconds(5));
    }

    // =========================================================================
    // HEALTH & INFO
    // =========================================================================

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        try {
            // Check C++ processor
            Map<String, Object> cppHealth = cppClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(2))
                    .block();

            // Check FastAPI
            Map<String, Object> fastApiHealth = fastApiClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(2))
                    .block();

            return ResponseEntity.ok(Map.of(
                    "status", "healthy",
                    "service", "projectlavos-gateway",
                    "cppProcessor", cppHealth != null ? cppHealth : Map.of("status", "unknown"),
                    "fastApiBackend", fastApiHealth != null ? fastApiHealth : Map.of("status", "unknown"),
                    "demos_available", 6
            ));

        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of(
                    "status", "unhealthy",
                    "error", e.getMessage()
            ));
        }
    }

    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> root() {
        return ResponseEntity.ok(Map.of(
                "name", "Project Lavos - AI Demos API",
                "consultant", "Matthew Scott",
                "location", "Louisville, KY",
                "architecture", "Spring Boot Gateway + C++ Processor + FastAPI Backend",
                "demos", Map.of(
                        "sentiment", "/api/sentiment (C++ - <5ms)",
                        "leads", "/api/leads (C++ - <3ms)",
                        "phishing", "/api/phishing (C++ - <10ms)",
                        "restaurant", "/api/analyze-restaurant (Claude AI)",
                        "email-scorer", "/api/score-email (Claude AI)",
                        "prompt-engineering", "/api/prompt-engineering (Claude AI)"
                ),
                "website", "https://projectlavos.com",
                "github", "https://github.com/guitargnarr"
        ));
    }
}
