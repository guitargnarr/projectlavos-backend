package com.matthewscott.textanalysis.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for ProjectLavosController
 * Tests routing to C++ and FastAPI backends
 *
 * @author Matthew David Scott
 */
@SpringBootTest
@AutoConfigureMockMvc
class ProjectLavosControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("healthy"))
                .andExpect(jsonPath("$.service").value("projectlavos-gateway"));
    }

    @Test
    void testRootEndpoint() throws Exception {
        mockMvc.perform(get("/api/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.consultant").value("Matthew Scott"))
                .andExpect(jsonPath("$.name").value("Project Lavos - AI Demos API"));
    }

    @Test
    void testSentimentAnalysisRouting() throws Exception {
        String requestBody = "{\"text\":\"This is amazing and wonderful\"}";

        mockMvc.perform(post("/api/sentiment")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sentiment").exists())
                .andExpect(jsonPath("$.confidence").exists());
    }

    @Test
    void testLeadScoringRouting() throws Exception {
        String requestBody = "{\"name\":\"Test\",\"email\":\"test@acme.com\",\"company\":\"Acme\",\"budget\":\"100k\",\"timeline\":\"asap\"}";

        mockMvc.perform(post("/api/leads")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.score").exists())
                .andExpect(jsonPath("$.priority").exists());
    }

    @Test
    void testPhishingDetectionRouting() throws Exception {
        String requestBody = "{\"sender\":\"scam@gmail.com\",\"subject\":\"URGENT\",\"body\":\"click here\"}";

        mockMvc.perform(post("/api/phishing")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.is_phishing").exists())
                .andExpect(jsonPath("$.risk_level").exists());
    }
}
