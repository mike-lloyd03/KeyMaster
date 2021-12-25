SHELL := /usr/bin/env bash
PWD := $(shell pwd)

.PHONY: venv
venv: requirements.txt
	python -m venv .venv
	source .venv/bin/activate; pip install -r requirements.txt

.PHONY: deploy
deploy: 
	sed "s|WORKING_DIRECTORY|${PWD}|g" deployment/systemd/server-status-mqtt.service | sudo tee /etc/systemd/system/server-status-mqtt.service > /dev/null
	systemctl daemon-reload
