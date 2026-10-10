from google.cloud import firestore
import json
# Initialize Firestore Client
client = firestore.Client()

# See: https://cloud.google.com/functions/docs/calling/pubsub
# The `data` field maps to the PubsubMessage data in a base64-encoded string. For IoT originated data, all the 'payload' values are contained here.
# The `attributes` field maps to the PubsubMessage attributes if any is present. For IoT originated data, the device attribute data is
# contained here, such as 'deviceId', 'deviceNumId', deviceRegistryId, etc.

def store_telemetry_firebase(event, context):
    import base64

    print(f'This function was triggered by messageId {context.event_id}, published at {context.timestamp} to {context.resource["name"]}') # debugging 

    # store IoT data in Firestore
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8') # get the IoT data fields (originated in Node-RED as 'payload')
        print(f'IoT Data: {data}') # debugging 
        dataDict = json.loads(data) # Python Data Dictionary. See: https://www.w3schools.com/python/python_dictionaries.asp 
        # write to a new doc in Firestore
        doc = client.collection('process-monitor-data').document()
        doc.set(dataDict)