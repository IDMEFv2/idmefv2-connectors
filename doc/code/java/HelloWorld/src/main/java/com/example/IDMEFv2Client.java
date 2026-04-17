package com.example;

import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.ContentType;
import org.apache.hc.core5.http.io.entity.StringEntity;
import org.apache.hc.core5.http.HttpStatus;

import java.io.IOException;

/**
 * Client for sending IDMEFv2 messages to a remote server via HTTP/HTTPS.
 *
 * This client encapsulates the HTTP communication logic for posting IDMEFv2
 * messages to a destination server.
 */
public class IDMEFv2Client {

    private final String serverUrl;

    /**
     * Constructs an IDMEFv2Client with the specified server URL.
     *
     * @param serverUrl The HTTP(S) address of the destination server
     */
    public IDMEFv2Client(String serverUrl) {
        this.serverUrl = serverUrl;
    }

    /**
     * Sends an IDMEFv2 message to the destination server.
     *
     * @param jsonMessage The IDMEFv2 message as a JSON string
     * @return true if the message was sent successfully, false otherwise
     * @throws IOException if an I/O error occurs during transmission
     */
    public boolean sendMessage(String jsonMessage) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {

            // Create POST request
            HttpPost httpPost = new HttpPost(serverUrl);

            // Set headers
            httpPost.setHeader("Content-Type", "application/json");
            httpPost.setHeader("Accept", "application/json");

            // Set the message body
            StringEntity entity = new StringEntity(jsonMessage, ContentType.APPLICATION_JSON);
            httpPost.setEntity(entity);

            // Execute the request and handle the response
            return httpClient.execute(httpPost, response -> {
                int statusCode = response.getCode();
                System.out.println("Server response status: " + statusCode);

                if (statusCode == HttpStatus.SC_OK || statusCode == HttpStatus.SC_CREATED ||
                    statusCode == HttpStatus.SC_ACCEPTED) {
                    System.out.println("✓ IDMEFv2 message sent successfully to " + serverUrl);
                    return true;
                } else {
                    System.err.println("✗ Server returned status code: " + statusCode);
                    return false;
                }
            });
        }
    }

    /**
     * Gets the configured server URL.
     *
     * @return The server URL
     */
    public String getServerUrl() {
        return serverUrl;
    }
}
