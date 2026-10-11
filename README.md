# Smart City Air Quality Monitoring & Cloud IoT Pipeline

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PENDING.svg)](https://doi.org/10.5281/zenodo.PENDING)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![GCP](https://img.shields.io/badge/Google%20Cloud-Pub%2FSub%20%26%20Functions-orange)
![Node-RED](https://img.shields.io/badge/Node--RED-Dashboard-red)
![License](https://img.shields.io/badge/license-MIT-green)

An enterprise-grade, event-driven IoT and Cloud architecture designed to ingest, stream, process, and visualize real-time environmental sensor telemetry for smart cities. Built and tested using high-resolution urban air quality data (Edinburgh Nicolson Street telemetry). Developed as part of an advanced IoT and Cloud Systems research initiative.

> **Status:** This repository preserves the foundational V1 event-driven IoT pipeline. The V2 multi-modal computer vision extension (for traffic-pollution correlation) is currently in development.

## **Architecture & Technology Stack (V1)**

- **Edge/IoT Device Simulation (/nodered_flows):** Node-RED flows parsing historical multi-parameter sensor datasets (Nitric Oxide, Nitrogen Dioxide, and meteorological metrics).
- **Cloud Messaging (GCP Pub/Sub):** Decoupled ingestion layer handling high-throughput telemetry and device state topics.
- **Serverless Processing (GCP Cloud Functions):** Event-driven Python backend code (main.py) triggered asynchronously via Pub/Sub events.
- **NoSQL Persistence (GCP Firestore):** Scalable, document-based real-time telemetry storage.
- **Visualization & Analytics (Node-RED Dashboards):** Real-time monitoring UI integrated with GIS map components and automated incident-response webhooks.

## **Repository Structure**

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

## **Getting Started & Setup Guide**

### **1. Prerequisites**
- Node-RED installed locally or on an edge gateway.
- Google Cloud SDK configured with an active GCP project and billing enabled.
- Python 3.9+ for Cloud Function deployment.

### **2. Configure Cloud Infrastructure**
- Create two Pub/Sub Topics: telemetry-topic and state-topic.
- Provision a Firestore Database in Native Mode.
- Deploy the serverless function from the cloud_functions/ directory using command: gcloud functions deploy process_telemetry --runtime python39 --trigger-topic telemetry-topic --entry-point process_telemetry

### **3. Import Node-RED Flows**
- Open your Node-RED dashboard.
- Import the JSON flows located in the nodered_flows/ directory (device_simulator.json, sensor_reader.json, and cloud_flow.json).
- Bind your GCP service account credentials to the Google Cloud nodes.

## **Limitations and Planned V2 Roadmap**

While the V1 pipeline successfully establishes a robust, event-driven telemetry cloud architecture, several limitations motivate the ongoing V2 research expansion:

1. **Spatial Sparsity of Physical Sensors:** Fixed point-source monitoring stations (like those on Nicolson Street) cannot capture micro-scale pollution variations across an entire urban corridor.
2. **Lack of Predictive Causality:** V1 tracks current telemetry but does not forecast upcoming pollutant spikes caused by sudden traffic congestion.
3. **Unimodal Telemetry:** Relying solely on gas/meteorological sensors misses the direct visual drivers of emissions.

### **Planned V2 (Research & PhD Direction):**
1. **Computer Vision Integration:** Deploying CVPR-grade object detection models (e.g., YOLOv8 / Vision Transformers) on urban traffic camera feeds to track vehicle classification, density, and congestion in real-time.
2. **Multi-Modal Data Fusion:** Correlating visual traffic dynamics with physical pollutant spikes to build predictive environmental degradation models.
3. **Academic Benchmarking & Archiving:** Registering the pipeline on Papers with Code and archiving releases via Zenodo with an official DOI.

## **Dataset Attribution**
This project utilizes urban environmental monitoring datasets structured around municipal sensor deployments (specifically validated against Edinburgh Nicolson Street air quality telemetry logs stored in /data).

## **References**
- Wang, S. et al. Smart City IoT Telemetry and Event-Driven Cloud Architectures.
- IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) guidelines for Vision-based Environmental Sensing.

## **Author**

**Muzammal Hussain** — Software Engineer, MSc Big Data Technologies (Glasgow Caledonian University)

- GitHub: MHKhan50 (https://github.com/MHKhan50)

## **Citation**

If you use this code, please cite:

> Hussain, M. (2026). *Smart City Air Quality Monitoring & Cloud IoT Pipeline* (Version v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.PENDING
