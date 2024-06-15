import logging
from http.server import HTTPServer
from handlers import WireGuardMetricsHandler
from config import load_config

def run():
    log_file_path = load_config()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    server_address = ('', 9586)
    httpd = HTTPServer(server_address, WireGuardMetricsHandler)
    logger.info(f'Starting httpd on port {server_address[1]}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
