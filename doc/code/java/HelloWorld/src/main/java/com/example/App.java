package com.example;

/**
 * IDMEFv2 Hello World Application
 *
 * This application builds and sends an IDMEFv2 "Hello world" message to a
 * specified HTTP(S) server endpoint.
 *
 * Usage:
 *   java com.example.App <server_url>
 *
 * Example:
 *   java com.example.App http://localhost:8080/api/events
 *   java com.example.App https://alert-server.example.com/v2/messages
 */
public class App {

    /**
     * Main entry point of the application.
     *
     * @param args Command-line arguments - expects server URL as first argument
     */
    public static void main(String[] args) {
        App app = new App();
        app.run(args);
    }

    /**
     * Runs the application.
     *
     * Accepts a server URL as command-line argument, builds an IDMEFv2 Hello World
     * message, and sends it to the specified server.
     *
     * @param args Command-line arguments containing the server URL
     */
    public void run(String[] args) {
        if (args.length == 0) {
            System.err.println("Error: Missing required argument.");
            System.err.println("Usage: java -jar hello-world-all.jar <server_url>");
            System.err.println("Example: java -jar hello-world-all.jar http://localhost:8080/api/events");
            System.exit(1);
        }

        String serverUrl = args[0];

        try {
            System.out.println("═══════════════════════════════════════════════════════════════");
            System.out.println("IDMEFv2 Hello World Message Sender");
            System.out.println("═══════════════════════════════════════════════════════════════");
            System.out.println();

            // Step 1: Build the IDMEFv2 Hello World message
            System.out.println("📋 Building IDMEFv2 Hello World message...");
            IDMEFv2MessageBuilder messageBuilder = new IDMEFv2MessageBuilder();
            String jsonMessage = messageBuilder.buildHelloWorldMessage();
            System.out.println("✓ Message built successfully");
            System.out.println();

            // Step 2: Display the message
            System.out.println("📦 Generated Message:");
            System.out.println("───────────────────────────────────────────────────────────────");
            System.out.println(jsonMessage);
            System.out.println("───────────────────────────────────────────────────────────────");
            System.out.println();

            // Step 3: Send the message to the server
            System.out.println("🚀 Sending message to: " + serverUrl);
            IDMEFv2Client client = new IDMEFv2Client(serverUrl);
            boolean success = client.sendMessage(jsonMessage);

            System.out.println();
            if (success) {
                System.out.println("✓ IDMEFv2 Hello World message sent successfully!");
                System.out.println("═══════════════════════════════════════════════════════════════");
                System.exit(0);
            } else {
                System.out.println("✗ Failed to send message to server");
                System.out.println("═══════════════════════════════════════════════════════════════");
                System.exit(1);
            }

        } catch (Exception e) {
            System.err.println("✗ Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * Returns a greeting message.
     *
     * @param name The name to greet
     * @return A greeting message
     */
    public String greet(String name) {
        return "Hello, " + name + "!";
    }
}
