# wg_exporter

`wg_exporter` is a Python-based tool designed to collect and expose WireGuard VPN metrics. It runs as a service on your system and provides metrics in a format that can be scraped by Prometheus.

## Features

- Collects WireGuard interface and peer metrics.
- Exposes metrics via an HTTP endpoint.
- Configurable logging for development and production environments.

## Prerequisites

- Python 3.6+
- WireGuard installed and configured
- Prometheus (for scraping the metrics)
- Git

## Installation

1. **Clone the Repository**

   ```bash
   git clone git@github.com:Wisienkas/wg_exporter.git
   cd repository
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Setting log location through `WG_EXPORTER_LOG_FILE`**
   
   Only configuration needed is `WG_EXPORTER_LOG_FILE`,
   which defaults to `wg_exporter.log`.

## Setting Up the Service User

To enhance security, it is recommended to run the `wg_exporter` service as a dedicated, non-privileged user. Follow these steps to create the user and set up the service.

1. **Create the `wgexporter` User**

   ```bash
   sudo useradd --system --no-create-home --shell /usr/sbin/nologin wgexporter
   ```

## Setting Up the Directory Structure

1. **Create the Directory Structure**

   Create the preferred directory structure under `/etc/local/bin/wg_exporter/`:

   ```bash
   sudo mkdir -p /etc/local/bin/wg_exporter
   sudo cp -r * /etc/local/bin/wg_exporter/
   sudo chown -R wgexporter:wgexporter /etc/local/bin/wg_exporter
   ```

   Ensure your project files (`__init__.py` and `wg_exporter.py`) are copied to this directory.

**`install.sh` file can also be run to achieve this, as `./install.sh`

## Running the Exporter

### Development

To run the exporter in development mode:

```bash
python /etc/local/bin/wg_exporter/__init__.py
```

### Production

1. **Set Up Logging Directory**

   ```bash
   sudo mkdir /var/log/wgexporter
   sudo chown wgexporter:wgexporter /var/log/wgexporter
   ```

2. **Systemd Service Configuration**

   Create a systemd service file `/etc/systemd/system/wg_exporter.service`:

   ```ini
   [Unit]
   Description=WireGuard Exporter
   After=network.target

   [Service]
   User=wgexporter
   Group=wgexporter
   Environment=WG_EXPORTER_LOG_FILE=/var/log/wgexporter/wg_exporter.log
   ExecStart=/usr/bin/env python3 /etc/local/bin/wg_exporter/__init__.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start the Service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable wg_exporter
   sudo systemctl start wg_exporter
   ```

## Accessing Metrics

The metrics are exposed via an HTTP endpoint on port 9586. You can access them by navigating to:

```plaintext
http://localhost:9586/metrics
```

## Prometheus Configuration

Add the following job to your Prometheus configuration file (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'wireguard'
    static_configs:
      - targets: ['localhost:9586']
```

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Prometheus](https://prometheus.io/)
- [WireGuard](https://www.wireguard.com/)