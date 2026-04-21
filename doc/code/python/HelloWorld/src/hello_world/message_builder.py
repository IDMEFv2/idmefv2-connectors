"""IDMEFv2 message builder for Hello World application."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4


class IDMEFv2MessageBuilder:
    """Builds IDMEFv2 Hello World messages.

    This class loads the hello-world-idmefv2.json template and
    generates a complete IDMEFv2 message with unique identifiers and timestamps.
    """

    def __init__(self) -> None:
        """Initialize the message builder."""
        self.template_path = Path(__file__).parent / "hello-world-idmefv2.json"

    def build_hello_world_message(self) -> str:
        """Build a complete IDMEFv2 Hello World message.

        Returns:
            JSON string containing the complete IDMEFv2 message

        Raises:
            FileNotFoundError: If the template file cannot be found
            json.JSONDecodeError: If the template JSON is invalid
        """
        # Load the template
        template = self._load_template()

        # Replace placeholders
        message_uuid = str(uuid4())
        analyzer_uuid = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        template["ID"] = message_uuid
        template["CreateTime"] = timestamp

        # Update Analyzer UUID
        if "Analyzer" in template:
            template["Analyzer"]["ID"] = analyzer_uuid

        # Return the message as formatted JSON string
        return json.dumps(template, indent=2)

    def _load_template(self) -> Dict[str, Any]:
        """Load the hello-world-idmefv2.json template.

        Returns:
            Dictionary containing the template data

        Raises:
            FileNotFoundError: If the template file cannot be found
            json.JSONDecodeError: If the template JSON is invalid
        """
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Template file not found: {self.template_path}") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in template: {e}", e.doc, e.pos) from e
