import os
import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    environment = os.getenv('ENV', 'development')
    log_file_path = os.getenv('WG_EXPORTER_LOG_FILE', config[environment]['WG_EXPORTER_LOG_FILE'])
    return log_file_path
