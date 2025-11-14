package com.matthewscott.textanalysis.model;

import java.time.LocalDateTime;
import java.util.Map;

public class AnalysisResponse {
    private String id;
    private String text;
    private Map<String, Object> analysis;
    private LocalDateTime timestamp;
    private String processorType;

    public AnalysisResponse() {}

    public AnalysisResponse(String id, String text, Map<String, Object> analysis) {
        this.id = id;
        this.text = text;
        this.analysis = analysis;
        this.timestamp = LocalDateTime.now();
        this.processorType = "cpp-high-performance";
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public Map<String, Object> getAnalysis() { return analysis; }
    public void setAnalysis(Map<String, Object> analysis) { this.analysis = analysis; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }

    public String getProcessorType() { return processorType; }
    public void setProcessorType(String processorType) { this.processorType = processorType; }
}
