# Smart City Air Quality Monitoring & Cloud IoT Pipeline

An enterprise-grade, event-driven IoT and Cloud architecture designed to ingest, stream, process, and visualize real-time environmental sensor data for smart cities (using Edinburgh Nicolson Street air quality telemetry).

## Architecture & Technology Stack
* **Edge / IoT Device Simulation:** Node-RED flows parsing historical sensor datasets (Nitric Oxide & Nitrogen Dioxide).
* **Cloud Messaging:** Google Cloud Pub/Sub (`telemetry` and `state` topics).
* **Serverless Processing:** Google Cloud Functions (Python) triggered via Pub/Sub events.
* **NoSQL Database:** Google Cloud Firestore for scalable real-time telemetry storage.
* **Visualization & Analytics:** Node-RED dashboards integrated with Google Maps GIS APIs and automated Slack alerting webhooks.

## Repository Structure
* `cloud_functions/` - Serverless Python backend code (`main.py`, `requirements.txt`) for Firestore ingestion.
* `nodered_flows/` - JSON exports for cloud flows, device simulators, and data readers.
* `data/` - Cleaned historical environmental datasets (`edinburgh_sensor_data.xlsx`).