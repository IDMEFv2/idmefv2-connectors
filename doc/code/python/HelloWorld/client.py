"""HTTP client for sending IDMEFv2 messages."""

import requests

class IDMEFv2Client:
    """Client for sending IDMEFv2 messages to a remote server via HTTP/HTTPS.

    This client encapsulates the HTTP communication logic for posting IDMEFv2
    messages to a destination server.
    """

    def __init__(self, server_url: str, timeout: int = 30) -> None:
        """Initialize the client with server URL.

        Args:
            server_url: The HTTP(S) address of the destination server
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout

    def send_message(self, json_message: str) -> bool:
        """Send an IDMEFv2 message to the destination server.

        Args:
            json_message: The IDMEFv2 message as a JSON string

        Returns:
            True if the message was sent successfully, False otherwise

        Raises:
            requests.RequestException: If an HTTP error occurs
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(
                self.server_url,
                data=json_message,
                headers=headers,
                timeout=self.timeout
            )

            print(f"Server response status: {response.status_code}")

            if response.status_code in (200, 201, 202):
                print(f"✓ IDMEFv2 message sent successfully to {self.server_url}")
                return True

            print(f"✗ Server returned status code: {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            return False

        except requests.RequestException as e:
            print(f"✗ HTTP request failed: {e}")
            raise

    @property
    def server_url(self) -> str:
        """Get the configured server URL."""
        return self._server_url

    @server_url.setter
    def server_url(self, value: str) -> None:
        """Set the server URL."""
        if not value.startswith(("http://", "https://")):
            raise ValueError("Server URL must start with http:// or https://")
        self._server_url = value
