#!/usr/bin/env bash

sudo mkdir -p /etc/local/bin/wg_exporter
sudo cp -r wg_exporter /etc/local/bin/wg_exporter/
sudo chown -R wgexporter:wgexporter /etc/local/bin/wg_exporter