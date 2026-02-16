'''
Main for Kismet connector
'''
import time
import hashlib
import requests
from .kismetconverter import KismetConverter
from ..connector import ConnectorArgumentParser, Configuration, Connector

# pylint: disable=too-many-nested-blocks, too-many-branches

class KismetConnector(Connector):
    '''
    Connector for Kismet API
    '''
    def __init__(self, cfg: Configuration, converter: KismetConverter):
        super().__init__('kismet', cfg, converter)
        self.url = cfg.get('kismet', 'url')
        self.username = cfg.get('kismet', 'username', fallback=None)
        self.password = cfg.get('kismet', 'password', fallback=None)
        self.interval = int(cfg.get('kismet', 'polling_interval', fallback=10))
        self.seen_alerts = set()
        self.last_alerts = {}

    def get_alert_hash(self, alert: dict) -> str:
        '''
        Compute a unique hash for the alert to handle deduplication.
        We combine timestamp, header and text.
        Handles both flat keys (with dots) and nested dictionaries.
        '''
        def get_val(d, path_str):
            # Try direct access (flat key)
            if path_str in d:
                return d[path_str]
            # Try nested access
            keys = path_str.split('.')
            val = d
            try:
                for k in keys:
                    val = val[k]
                return val
            except (KeyError, TypeError):
                return ''

        ts = get_val(alert, 'kismet.alert.timestamp')
        header = get_val(alert, 'kismet.alert.header')
        text = get_val(alert, 'kismet.alert.text')

        # fallback if empty
        if not ts and not header:
            return str(hash(str(alert)))

        s = f"{ts}-{header}-{text}"
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def is_duplicate(self, alert: dict) -> bool:
        '''
        Check if duplicate using strict hash OR fuzzy timestamp matching
        '''
        aid = self.get_alert_hash(alert)
        if aid in self.seen_alerts:
            return True

        # Fuzzy check
        def get_val(d, path_str):
            if path_str in d:
                return d[path_str]
            keys = path_str.split('.')
            val = d
            try:
                for k in keys:
                    val = val[k]
                return val
            # pylint: disable=broad-exception-caught
            except Exception:
                return ''

        header = get_val(alert, 'kismet.alert.header')
        text = get_val(alert, 'kismet.alert.text')
        ts = get_val(alert, 'kismet.alert.timestamp')

        key = (header, text)
        if key in self.last_alerts:
            last_ts = self.last_alerts[key]
            # If same header+text seen within 2 seconds, treat as duplicate
            if abs(ts - last_ts) < 2.0:
                self.logger.info("Ignoring duplicate alert (fuzzy match): %s", header)
                return True

        # Update last seen
        self.last_alerts[key] = ts
        return False

    def run(self):
        self.logger.info("Starting Kismet polling on %s", self.url)

        # Auth
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)

        # Initial fetch to seed seen_alerts (avoid sending old alerts)
        try:
            self.logger.info("Seeding initial alerts...")
            response = requests.get(self.url, auth=auth, timeout=10)
            if response.status_code == 200:
                alerts = response.json()
                if isinstance(alerts, list):
                    for alert in alerts:
                        aid = self.get_alert_hash(alert)
                        self.seen_alerts.add(aid)
                    self.logger.info(
                        "Seeded %d existing alerts. They will not be sent.",
                        len(self.seen_alerts)
                    )
        # pylint: disable=broad-exception-caught
        except Exception as e:
            self.logger.warning("Failed to seed initial alerts: %s", str(e))

        while True:
            try:
                response = requests.get(self.url, auth=auth, timeout=10)
                if response.status_code == 200:
                    alerts = response.json()
                    # alerts should be a list
                    if isinstance(alerts, list):
                        new_count = 0
                        for alert in alerts:
                            aid = self.get_alert_hash(alert)
                            if not self.is_duplicate(alert):
                                self.seen_alerts.add(aid) # Always add strict hash
                                self.alert(alert)
                                new_count += 1
                        if new_count > 0:
                            self.logger.info("Processed %d new alerts", new_count)
                    else:
                        self.logger.warning(
                            "Unexpected response format (not a list): %s",
                            type(alerts)
                        )
                else:
                    self.logger.error(
                        "Failed to fetch alerts: %s %s",
                        response.status_code,
                        response.text
                    )

            # pylint: disable=broad-exception-caught
            except Exception as e:
                self.logger.error("Polling error: %s", str(e))

            time.sleep(self.interval)

if __name__ == '__main__':
    opts = ConnectorArgumentParser('kismet').parse_args()
    config = Configuration(opts)
    kismet_converter = KismetConverter()
    connector = KismetConnector(config, kismet_converter)
    connector.run()
