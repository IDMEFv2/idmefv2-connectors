"""
Poll Elasticsearch for T-Pot honeypot events and forward them as IDMEFv2.
"""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

import requests

from .tpotconverter import TpotConverter
from ..idmefv2client import IDMEFv2Client

log = logging.getLogger("tpot-poller")

def _generate_event_fingerprint(hit: dict[str, Any]) -> str:
    """Generate a unique fingerprint for an Elasticsearch hit."""
    event_type = hit.get('type', '')
    timestamp = hit.get('@timestamp', '')
    src_ip = hit.get('src_ip', '')
    dst_ip = hit.get('dst_ip', '')
    fingerprint_data = f"{event_type}:{timestamp}:{src_ip}:{dst_ip}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]


class TpotPoller:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Continuously polls Elasticsearch for T-Pot honeypot events."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        elasticsearch_url: str,
        index_pattern: str,
        client: IDMEFv2Client,
        converter: TpotConverter,
        poll_interval: int = 30,
        catch_up: bool = False,
    ) -> None:
        """Initialize the T-Pot Elasticsearch poller."""
        self.elasticsearch_url = elasticsearch_url.rstrip('/')
        self.index_pattern = index_pattern
        self.client = client
        self.converter = converter
        self.poll_interval = poll_interval
        self.catch_up = catch_up  # save state
        self.session = requests.Session()
        self.seen_events: set[str] = set()
        self.last_timestamp: str | None = None

    def _build_query(self) -> dict[str, Any]:
        """Build the Elasticsearch query."""
        query: dict[str, Any] = {
            "size": 100,
            "sort": [{"@timestamp": {"order": "asc"}}],
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "src_ip"}}
                    ]
                }
            }
        }

        if self.last_timestamp:
            query["query"]["bool"]["filter"] = [
                {"range": {"@timestamp": {"gt": self.last_timestamp}}}
            ]

        return query

    def _fetch_events(self) -> list[dict[str, Any]]:
        """Fetch T-Pot honeypot events from Elasticsearch."""
        url = f"{self.elasticsearch_url}/{self.index_pattern}/_search"
        query = self._build_query()

        response = self.session.post(
            url,
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        hits = data.get('hits', {}).get('hits', [])

        results = []
        for hit in hits:
            source = hit.get('_source', {})
            if source:
                results.append(source)

        return results

    def _update_last_timestamp(self, event: dict[str, Any]) -> None:
        """Update the internal last seen timestamp from an event."""
        ts = event.get('@timestamp')
        if ts:
            self.last_timestamp = ts

    def run(self):
        """Start the polling loop with initial sync logic."""
        first_run = True
        log.info("Starting T-Pot poller loop (catch_up=%s)", self.catch_up)

        while True:
            try:
                events = self._fetch_events()

                for event in events:
                    fingerprint = _generate_event_fingerprint(event)

                    if fingerprint in self.seen_events:
                        continue

                    # Catch-up logic
                    if first_run and not self.catch_up:
                        log.debug("Silent sync: skipping initial event %s", fingerprint)
                    else:
                        should_convert, idmef = self.converter.convert(event)
                        if should_convert:
                            log.info("Sending IDMEFv2 alert for: %s", event.get('type'))
                            self.client.post(idmef)

                    self.seen_events.add(fingerprint)
                    self._update_last_timestamp(event)

                first_run = False

            except Exception as e:  # pylint: disable=broad-exception-caught
                log.error("Unexpected error during polling: %s", str(e), exc_info=True)

            time.sleep(self.poll_interval)
