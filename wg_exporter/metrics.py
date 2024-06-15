import logging
import subprocess
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Pattern, AnyStr, Tuple

logger = logging.getLogger(__name__)

interface_pattern = re.compile(r'interface:\s*(\w+)')
peer_pattern = re.compile(r'peer:\s*([\w+/=]+)')
endpoint_pattern = re.compile(r'endpoint:\s*([\d.]+:\d+)')
handshake_pattern = re.compile(r'latest handshake:\s*(.+ ago)')
transfer_pattern = re.compile(r'transfer:\s*([\d.]+ \w+) received, ([\d.]+ \w+) sent')
byte_reading_pattern = re.compile(r'([\d.]+) (\w+)')

overrides = {}
def override(key: str, value: any):
    overrides[key] = value


def run_command(command: List[str]) -> Optional[str]:
    logger.debug(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f'Command output: {result.stdout}')
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        return None


def parse_handshake_time(handshake: str) -> str:
    time_units = {
        'day': 3600 * 24,
        'hour': 3600,
        'minute': 60,
        'second': 1
    }
    seconds_ago = 0
    for unit, seconds in time_units.items():
        match = re.search(r'(\d+)\s+' + unit, handshake)
        if match:
            seconds_ago += int(match.group(1)) * seconds

    # Get the current time
    current_time = overrides["override_current_time"] if "override_current_time" in overrides else datetime.now()
    time_difference = timedelta(seconds=seconds_ago)
    target_time = current_time - time_difference

    return target_time.isoformat()


def parse_to_bytes(byte_reading: str) -> int:
    match = byte_reading_pattern.search(byte_reading)
    if match:
        byte_size = match.group(1)
        indicator = match.group(2)
        multiplier = {
            "B": 1,
            "KiB": 1024**1,
            "MiB": 1024**2,
            "GiB": 1024**3,
            "TiB": 1024**4,
            "PiB": 1024**5
        }
        return int(float(byte_size) * multiplier[indicator])


def parse_wg_output(wg_output: str) -> List[Dict[str, str]]:
    metrics = []


    interfaces_lines = split_lines_by_key("interface:", wg_output.splitlines())
    for interface_lines in interfaces_lines:
        interface_name = find_first(interface_pattern, interface_lines)
        peers_lines = split_lines_by_key("peer:", interface_lines)
        for peer_lines in peers_lines:
            transfer = find_first_multiple_groups(transfer_pattern, peer_lines)
            metrics.append({
                "interface": interface_name,
                "peer": find_first(peer_pattern, peer_lines),
                "endpoint": find_first(endpoint_pattern, peer_lines),
                "handshake": parse_handshake_time(find_first(handshake_pattern, peer_lines)),
                "rx_bytes": parse_to_bytes(transfer[0]),
                "tx_bytes": parse_to_bytes(transfer[1])
            })

    logger.debug(f'Extracted metrics: {metrics}')
    return metrics


def find_first_multiple_groups(pattern: Pattern[AnyStr], lines: List[str]) -> Optional[List[str]]:
    for line in lines:
        match = re.search(pattern, line)
        if match:
            return list(match.groups())


def find_first(pattern: Pattern[AnyStr], lines: List[str]) -> Optional[str]:
    for line in lines:
        match = re.search(pattern, line)
        if match:
            return match.group(1)


def split_lines_by_key(split_key, lines):
    indexes = []
    for index, line in enumerate(lines):
        if split_key in line:
            indexes.append(index)

    interface_parts = []
    for index, start in enumerate(indexes):
        if index == len(indexes) - 1:
            interface_parts.append(lines[start:])
        else:
            interface_parts.append(lines[start:indexes[index + 1]])

    return interface_parts

def format_metrics(metrics: List[Dict[str, str]]) -> str:
    formatted_metrics = []
    for metric in metrics:
        formatted_metrics.append(
            f'wg_peer_info{{interface="{metric["interface"]}",peer="{metric["peer"]}",endpoint="{metric["endpoint"]}",last_handshake="{metric["handshake"]}"}} 1'
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
    wg_output = run_command(['sudo', 'wg', 'show'])
    if wg_output:
        metrics = parse_wg_output(wg_output)
        return format_metrics(metrics)
    else:
        return "Failed to retrieve WireGuard metrics."
