import subprocess
import re
from typing import List, Dict, Optional, Tuple
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os

# Get log file path from environment variable, with a default for development
log_file_path = os.getenv('WG_EXPORTER_LOG_FILE', 'wg_exporter.log')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_command(command: List[str]) -> Optional[str]:
    try:
        result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f'Command output: {result.stdout}')
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        return None


def extract_metrics(wg_output: str) -> List[Dict[str, str]]:
    metrics: List[Dict[str, str]] = []
    interfaces: List[str] = re.findall(r'interface: (\w+)', wg_output)
    for interface in interfaces:
        peers: List[Tuple[str, str, str, str, str]] = re.findall(
            r'peer: (\w+)\n.*?endpoint: (\S+:\d+)\n.*?latest handshake: (\S.*?)\n.*?transfer: (\d+) B received, (\d+) B sent',
            wg_output, re.DOTALL
        )
        for peer in peers:
            peer_key, endpoint, handshake, rx_bytes, tx_bytes = peer
            metric: Dict[str, str] = {
                "interface": interface,
                "peer": peer_key,
                "endpoint": endpoint,
                "handshake": handshake,
                "rx_bytes": rx_bytes,
                "tx_bytes": tx_bytes
            }
            metrics.append(metric)
    logger.debug(f'Extracted metrics: {metrics}')
    return metrics


def format_metrics(metrics: List[Dict[str, str]]) -> str:
    formatted_metrics: List[str] = []
    for metric in metrics:
        formatted_metrics.append(
            f'wg_peer_info{{interface="{metric["interface"]}",peer="{metric["peer"]}"' +
            f',endpoint="{metric["endpoint"]}",handshake="{metric["handshake"]}"}} 1'
        )
        formatted_metrics.append(
            f'wg_peer_rx_bytes{{interface="{metric["interface"]}",peer="{metric["peer"]}"}} {metric["rx_bytes"]}'
        )
        formatted_metrics.append(
            f'wg_peer_tx_bytes{{interface="{metric["interface"]}",peer="{metric["peer"]}"}} {metric["tx_bytes"]}'
        )
    logger.debug(f'Formatted metrics: {formatted_metrics}')
    return '\n'.join(formatted_metrics)


def collect_metrics() -> str:
    wg_output: Optional[str] = run_command(['sudo', 'wg', 'show'])
    if wg_output:
        metrics: List[Dict[str, str]] = extract_metrics(wg_output)
        return format_metrics(metrics)
    else:
        return "Failed to retrieve WireGuard metrics."


class WireGuardMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            metrics: str = collect_metrics()
            self.wfile.write(metrics.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run(server_class: type = HTTPServer, handler_class: type = WireGuardMetricsHandler, port: int = 9586) -> None:
    server_address: Tuple[str, int] = ('', port)
    httpd: HTTPServer = server_class(server_address, handler_class)
    logger.info(f'Starting wg_exporter...')
    logger.info(f'Starting httpd on port {port}...')
    httpd.serve_forever()

