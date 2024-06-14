import unittest
import wg_exporter as wg

class MyTestCase(unittest.TestCase):
    def test_extract_metrics(self):
        wg_output = """
        interface: wg0
          peer: abc123
            endpoint: 192.168.1.2:51820
            latest handshake: 2022-06-01T12:34:56Z
            transfer: 123456 B received, 654321 B sent
        """
        expected_metrics = [
            {
                "interface": "wg0",
                "peer": "abc123",
                "endpoint": "192.168.1.2:51820",
                "handshake": "2022-06-01T12:34:56Z",
                "rx_bytes": "123456",
                "tx_bytes": "654321"
            }
        ]
        result = wg.extract_metrics(wg_output)
        self.assertEqual(result, expected_metrics)


if __name__ == '__main__':
    unittest.main()
