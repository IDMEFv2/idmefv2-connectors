package com.example;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.io.InputStream;
import java.time.Instant;
import java.util.UUID;

/**
 * Builds IDMEFv2 Hello World messages.
 *
 * This class loads the hello-world-idmefv2.json template from resources and
 * generates a complete IDMEFv2 message with unique identifiers and timestamps.
 */
public class IDMEFv2MessageBuilder {

    private static final String TEMPLATE_RESOURCE = "/hello-world-idmefv2.json";
    private final ObjectMapper objectMapper;

    public IDMEFv2MessageBuilder() {
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Builds a complete IDMEFv2 Hello World message.
     *
     * @return JSON string containing the complete IDMEFv2 message
     * @throws IOException if the template cannot be loaded or processed
     */
    public String buildHelloWorldMessage() throws IOException {
        // Load the template
        JsonNode template = loadTemplate();

        // Create a mutable copy
        ObjectNode message = (ObjectNode) template;

        // Replace placeholders
        String messageUUID = UUID.randomUUID().toString();
        String analyzerUUID = UUID.randomUUID().toString();
        String timestamp = Instant.now().toString();

        message.put("ID", messageUUID);
        message.put("CreateTime", timestamp);

        // Update Analyzer UUID
        ObjectNode analyzer = (ObjectNode) message.get("Analyzer");
        if (analyzer != null) {
            analyzer.put("ID", analyzerUUID);
        }

        // Return the message as JSON string
        return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(message);
    }

    /**
     * Loads the hello-world-idmefv2.json template from resources.
     *
     * @return JsonNode containing the template
     * @throws IOException if the template cannot be loaded
     */
    private JsonNode loadTemplate() throws IOException {
        try (InputStream inputStream = this.getClass().getResourceAsStream(TEMPLATE_RESOURCE)) {
            if (inputStream == null) {
                throw new IOException("Template resource not found: " + TEMPLATE_RESOURCE);
            }
            return objectMapper.readTree(inputStream);
        }
    }
}
