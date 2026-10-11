# Smart City Air Quality Monitoring & Cloud IoT Pipeline

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![GCP](https://img.shields.io/badge/Google%20Cloud-Pub%2FSub%2 %20Functions-orange)
![Node-RED](https://img.shields.io/badge/Node--RED-Dashboard-red)
![License](https://img.shields.io/badge/license-MIT-green)

An enterprise-grade, event-driven IoT and Cloud architecture designed to ingest, stream, process, and visualize real-time environmental sensor telemetry for smart cities. Built and tested using high-resolution urban air quality data (Edinburgh Nicolson Street telemetry).

---

## 🏗️ Architecture & Technology Stack (V1)

* **Edge/IoT Device Simulation (`/nodered_flows`):** Node-RED flows parsing historical multi-parameter sensor datasets (Nitric Oxide, Nitrogen Dioxide, and meteorological metrics).
* **Cloud Messaging (GCP Pub/Sub):** Decoupled ingestion layer handling high-throughput telemetry and device state topics.
* **Serverless Processing (GCP Cloud Functions):** Event-driven Python backend code (`main.py`) triggered asynchronously via Pub/Sub events.
* **NoSQL Persistence (GCP Firestore):** Scalable, document-based real-time telemetry storage.
* **Visualization & Analytics (Node-RED Dashboards):** Real-time monitoring UI integrated with GIS map components and automated incident-response webhooks.

---

## 📁 Repository Structure

```text
smart-city-air-quality-monitoring/
├── cloud_functions/
│   ├── main.py               # Serverless event processor for Firestore ingestion
│   └── requirements.txt      # Python dependencies (google-cloud-firestore)
├── data/
│   └── edinburgh_sensor_data.xlsx # Cleaned historical urban environmental dataset
├── nodered_flows/
│   ├── cloud_flow.json       # Cloud integration and routing flows
│   ├── device_simulator.json # IoT sensor telemetry generator flow
│   └── sensor_reader.json    # Dataset reader and parser flow
└── README.md                 # Project documentation
