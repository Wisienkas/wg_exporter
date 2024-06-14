#!/usr/bin/env bash

sudo mkdir -p /etc/local/bin/wg_exporter
cd wg_exporter
sudo cp -r * /etc/local/bin/wg_exporter/
cd ..
sudo chown -R wgexporter:wgexporter /etc/local/bin/wg_exporter