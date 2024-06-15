import unittest
from datetime import datetime

from wg_exporter.metrics import parse_handshake_time, parse_wg_output, override


class TestMetrics(unittest.TestCase):

    def test_parse_handshake_time(self):
        override("override_current_time", datetime(2024, 6, 15, 12, 0, 0))
        self.assertEqual(parse_handshake_time("13 hours, 56 minutes, 18 seconds ago"), "2024-06-14T22:03:42")

    def test_extract_metrics(self):
        override("override_current_time", datetime(2024, 6, 15, 12, 0, 0))

        wg_output = """
interface: wg0
  public key: 2kf22B83434RaAFck5Mch3GJxk=
  private key: (hidden)
  listening port: (hidden)

peer: EaQ2EEbG12312awoIon+12322=
  preshared key: (hidden)
  endpoint: 2.224.11.21:6341
  allowed ips: (hidden)
  latest handshake: 13 hours, 56 minutes, 18 seconds ago
  transfer: 2.11 MiB received, 279.10 MiB sent
"""
        expected_metrics = [
            {
                 'interface': 'wg0',
                 'peer': 'EaQ2EEbG12312awoIon+12322=',
                 'endpoint': '2.224.11.21:6341',
                 'handshake': '2024-06-14T22:03:42',
                 'rx_bytes': 2212495,
                 'tx_bytes': 292657561
             }
        ]
        metrics = parse_wg_output(wg_output)
        print(metrics)
        self.assertEqual(metrics, expected_metrics)


if __name__ == '__main__':
    unittest.main()
