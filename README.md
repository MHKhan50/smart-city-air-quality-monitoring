# 🏙️ Smart City Air Quality Monitoring & Cloud IoT Pipeline

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Pub%2FSub%20%7C%20Functions%20%7C%20Firestore-orange.svg)](https://cloud.google.com/)
[![Node-RED](https://img.shields.io/badge/Node-RED-red.svg)](https://nodered.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, event-driven IoT and Cloud architecture designed to ingest, stream, process, and visualize real-time environmental sensor telemetry for smart cities. Built and tested using high-resolution urban air quality data (Edinburgh Nicolson Street telemetry).

---

## 🏗️ Architecture & Technology Stack
* **Edge / IoT Device Simulation (`/nodered_flows`):** Node-RED flows parsing historical multi-parameter sensor datasets (Nitric Oxide, Nitrogen Dioxide, and meteorological metrics).
* **Cloud Messaging (`GCP Pub/Sub`):** Decoupled ingestion layer handling high-throughput telemetry and device state topics.
* **Serverless Processing (`GCP Cloud Functions`):** Event-driven Python backend code (`main.py`) triggered asynchronously via Pub/Sub events.
* **NoSQL Persistence (`GCP Firestore`):** Scalable, document-based real-time telemetry storage.
* **Visualization & Analytics (`Node-RED Dashboards`):** Real-time monitoring UI integrated with GIS map components and automated incident-response webhooks.

---

## 📂 Repository Structure

```text
smart-city-air-quality-monitoring/
│
├── cloud_functions/
│   ├── main.py                # Serverless event processor for Firestore ingestion
│   └── requirements.txt       # Python dependencies (google-cloud-firestore)
│
├── data/
│   └── edinburgh_sensor_data.xlsx  # Cleaned historical urban environmental dataset
│
├── nodered_flows/
│   ├── cloud_flow.json        # Cloud integration and routing flows
│   ├── device_simulator.json  # IoT sensor telemetry generator flow
│   └── sensor_reader.json     # Dataset reader and parser flow
│
└── README.md                  # Project documentation

🚀 Getting Started & Setup Guide

1. Prerequisites
Node-RED installed locally or on an edge gateway.
Google Cloud SDK configured with an active GCP project and billing enabled.
Python 3.9+ for Cloud Function deployment.
2. Configure Cloud Infrastructure
Create two Pub/Sub Topics: telemetry-topic and state-topic.
Provision a Firestore Database in Native Mode.
Deploy the serverless function from the cloud_functions/ directory:
gcloud functions deploy process_telemetry \
  --runtime python39 \
  --trigger-topic telemetry-topic \
  --entry-point process_telemetry

3. Import Node-RED Flows
Open your Node-RED dashboard.
Import the JSON flows located in the nodered_flows/ directory (device_simulator.json, sensor_reader.json, and cloud_flow.json).
Bind your GCP service account credentials to the Google Cloud nodes.
📊 Dataset Attribution
This project utilizes urban environmental monitoring datasets structured around municipal sensor deployments (specifically validated against Edinburgh Nicolson Street air quality telemetry logs stored in /data).
🛡️ License
Distributed under the MIT License. See LICENSE for more information.
