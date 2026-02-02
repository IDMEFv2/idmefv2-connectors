"""
Poll the Prometheus API for active alerts and forward them to IDMEFv2.

Polls the /api/v1/alerts endpoint at configurable intervals.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

import requests

from .prometheusconverter import PrometheusConverter
from ..idmefv2client import IDMEFv2Client

log = logging.getLogger("prometheus-poller")


def _generate_alert_fingerprint(alert: dict[str, Any]) -> str:
    """
    Generate a unique fingerprint for an alert to track duplicates.

    Args:
        alert: The Prometheus alert dict.

    Returns:
        str: A hash string identifying this specific alert instance.
    """
    # Combine alertname, labels, and activeAt to create unique fingerprint
    alertname = alert.get('labels', {}).get('alertname', '')
    active_at = alert.get('activeAt', '')
    labels_str = json.dumps(alert.get('labels', {}), sort_keys=True)
    fingerprint_data = f"{alertname}:{active_at}:{labels_str}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]


# pylint: disable=too-few-public-methods
class PrometheusPoller:
    """Continuously polls Prometheus and relays active alerts as IDMEFv2 messages."""

    def __init__(
        self,
        *,
        prometheus_url: str,
        client: IDMEFv2Client,
        converter: PrometheusConverter,
        poll_interval: int = 30,
        disable_seeding: bool = False,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Initialize the Prometheus poller.

        Args:
            prometheus_url: Base URL of the Prometheus server.
            client: IDMEFv2 client for sending converted alerts.
            converter: Converter instance for transforming alerts.
            poll_interval: Seconds between polling cycles.
            disable_seeding: If True, send all alerts including existing ones.
        """
        self.prometheus_url = prometheus_url.rstrip('/')
        self.client = client
        self.converter = converter
        self.poll_interval = poll_interval
        self.disable_seeding = disable_seeding
        self.session = requests.Session()
        self.seen_alerts: set[str] = set()

    def _fetch_alerts(self) -> list[dict[str, Any]]:
        """
        Fetch active alerts from Prometheus API.

        Returns:
            list: List of alert dicts from Prometheus.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.prometheus_url}/api/v1/alerts"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get('status') != 'success':
            log.warning("Prometheus API returned non-success status: %s", data)
            return []

        return data.get('data', {}).get('alerts', [])

    def run(self) -> None:
        # pylint: disable=too-many-statements,too-many-branches
        """
        Start the polling loop.

        Continuously polls Prometheus for alerts and forwards new ones
        to the IDMEFv2 server.
        """
        log.info(
            "Starting Prometheus poller, URL=%s, interval=%ds",
            self.prometheus_url,
            self.poll_interval
        )

        # Initial fetch to seed seen_alerts
        if self.disable_seeding:
            log.info("Seeding disabled - will send all existing alerts")
            print("[PROMETHEUS] Seeding disabled - will send all existing alerts")
        else:
            try:
                initial_alerts = self._fetch_alerts()
                for alert in initial_alerts:
                    fingerprint = _generate_alert_fingerprint(alert)
                    self.seen_alerts.add(fingerprint)
                log.info("Seeded with %d existing alerts", len(self.seen_alerts))
                print(f"[PROMETHEUS] Seeded with {len(self.seen_alerts)} existing alerts")
            except requests.RequestException as exc:
                log.warning("Initial fetch failed: %s", exc)
                print("[PROMETHEUS] Initial fetch failed - starting with empty seed")

        # Main polling loop
        while True:
            try:
                alerts = self._fetch_alerts()
                current_fingerprints: set[str] = set()

                for alert in alerts:
                    fingerprint = _generate_alert_fingerprint(alert)
                    current_fingerprints.add(fingerprint)

                    if fingerprint in self.seen_alerts:
                        continue

                    self.seen_alerts.add(fingerprint)
                    log.debug("Processing new alert: %s", alert)
                    alertname = alert.get('labels', {}).get('alertname', 'unknown')
                    print(f"\n[PROMETHEUS] New alert detected: {alertname}")
                    print(f"[PROMETHEUS] Full alert: {alert}")

                    should_convert, idmef = self.converter.convert(alert)
                    if should_convert:
                        print("[PROMETHEUS] Conversion successful, sending IDMEFv2...")
                        print(f"[PROMETHEUS] IDMEFv2 message: {idmef}")
                        log.info(
                            "Sending IDMEFv2 alert for: %s",
                            alert.get('labels', {}).get('alertname', 'unknown')
                        )
                        try:
                            self.client.post(idmef)
                            print("[PROMETHEUS] ✓ Send successful!\n")
                        except requests.RequestException as post_err:
                            log.error("Failed to send IDMEFv2 alert: %s", post_err)
                            print(f"[PROMETHEUS] ✗ Send error: {post_err}\n")
                    else:
                        print("[PROMETHEUS] Alert filtered (not in 'firing' state)\n")

                # Clean up resolved alerts from seen set
                resolved = self.seen_alerts - current_fingerprints
                if resolved:
                    log.debug("Removing %d resolved alerts from tracking", len(resolved))
                    self.seen_alerts -= resolved

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                log.info("Interrupted by user")
                break
            except requests.RequestException as exc:
                log.error("Polling error: %s", exc)
                time.sleep(self.poll_interval)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.exception("Unexpected error: %s", exc)
                time.sleep(self.poll_interval)
