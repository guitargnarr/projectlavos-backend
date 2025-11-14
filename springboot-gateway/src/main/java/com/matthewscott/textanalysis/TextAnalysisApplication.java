package com.matthewscott.textanalysis;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

@SpringBootApplication
public class TextAnalysisApplication {

    public static void main(String[] args) {
        System.out.println("=== Spring Boot Text Analysis Gateway ===");
        System.out.println("Author: Matthew David Scott");
        System.out.println("Tech: Spring Boot 3.x, Java 17, WebClient");
        System.out.println();
        SpringApplication.run(TextAnalysisApplication.class, args);
    }

    @Bean
    public WebClient webClient() {
        // Use environment variable for Docker, fallback to localhost
        String cppUrl = System.getenv().getOrDefault("CPP_PROCESSOR_URL", "http://localhost:9000");
        return WebClient.builder()
                .baseUrl(cppUrl)
                .build();
    }
}
