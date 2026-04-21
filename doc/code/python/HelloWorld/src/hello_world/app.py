"""IDMEFv2 Hello World Application main entry point."""

import sys
import traceback
from typing import List

from .client import IDMEFv2Client
from .message_builder import IDMEFv2MessageBuilder


def main() -> None:
    """Main entry point of the application.

    Accepts a server URL as command-line argument, builds an IDMEFv2 Hello World
    message, and sends it to the specified server.
    """
    app = App()
    app.run(sys.argv[1:])


class App:
    """IDMEFv2 Hello World Application.

    This application builds and sends an IDMEFv2 "Hello world" message to a
    specified HTTP(S) server endpoint.
    """

    def run(self, args: List[str]) -> None:
        """Run the application.

        Args:
            args: Command-line arguments containing the server URL
        """
        if not args:
            print("Error: Missing required argument.", file=sys.stderr)
            print("Usage: hello-world <server_url>", file=sys.stderr)
            print("Example: hello-world http://localhost:8080/api/events", file=sys.stderr)
            sys.exit(1)

        server_url = args[0]

        try:
            print("═══════════════════════════════════════════════════════════════")
            print("IDMEFv2 Hello World Message Sender")
            print("═══════════════════════════════════════════════════════════════")
            print()

            # Step 1: Build the IDMEFv2 Hello World message
            print("📋 Building IDMEFv2 Hello World message...")
            message_builder = IDMEFv2MessageBuilder()
            json_message = message_builder.build_hello_world_message()
            print("✓ Message built successfully")
            print()

            # Step 2: Display the message
            print("📦 Generated Message:")
            print("───────────────────────────────────────────────────────────────")
            print(json_message)
            print("───────────────────────────────────────────────────────────────")
            print()

            # Step 3: Send the message to the server
            print(f"🚀 Sending message to: {server_url}")
            client = IDMEFv2Client(server_url)
            success = client.send_message(json_message)

            print()
            if success:
                print("✓ IDMEFv2 Hello World message sent successfully!")
                print("═══════════════════════════════════════════════════════════════")
                sys.exit(0)
            else:
                print("✗ Failed to send message to server")
                print("═══════════════════════════════════════════════════════════════")
                sys.exit(1)

        except Exception as e: # pylint: disable=broad-except
            print(f"✗ Error: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

    def greet(self, name: str) -> str:
        """Return a greeting message.

        Args:
            name: The name to greet

        Returns:
            A greeting message
        """
        return f"Hello, {name}!"


if __name__ == "__main__":
    main()
