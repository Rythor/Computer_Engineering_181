# IoTCloudConnect
* Source: Prof. Kaikai Liu
* Repository Link: https://github.com/lkk688/IoTCloudConnect
* Edited By: Ryan Biesty

This sample code implements the IoT client device connection with the cloud, and perform serverless computing in the cloud backend as shown in this diagram:
![Figure](./Resources/Picture1.png)

## IoT Python Client
Activate the python virtual environment, install the required Python packages based on the [requirements](/iotpython/requirements.txt)
```bash
pyclient % pip install -r requirements.txt
```
Use the following code to run the IoT python client to connect to Google Cloud IoT, you need to add your connection parameters in class Args or enable command line argument parsing by uncomment: args = parse_command_line_args()
```bash
pyclient % python3 gcpIoTclient.py
```
[CMPE-GoogleIoTdata.ipynb](/Notebook/CMPE-GoogleIoTdata.ipynb) is the Colab file to demonstrate the IoT Python code that publish IoT sensor data to Google Cloud IoT

## IoT Nodejs Client
Use the following code to run the IoT nodejs client to connect to Google Cloud IoT, you can add arguments in the command line or change the default arguments in the code
```bash
nodejsclient % node index.js mqttDeviceDemo
```

## Google Pubsub
Use the sub.py code to receive the realtime data from the IoT client, this can be used to check whether the Cloud received the data or not. 
1. Before you run the code, you need to link the service account credential in the command line: 
```bash
% export GOOGLE_APPLICATION_CREDENTIALS=XXX/certs/cmpe-181-hw1-rbiesty-0ed8459c6103.json
```
2. setup the subscription for Pubsub in the command line: 
```bash
% gcloud pubsub subscriptions create projects/cmpe-181-hw1-rbiesty/subscriptions/CMPE181RB-subscription --topic=projects/cmpe-181-hw1-rbiesty/topics/CMPEIoTdeviceRB
```
3. Run your IoT client code to send continuous data to the cloud, in another terminal, run the [gcpsub.py](/pyclient/gcpsub.py) to receive the realtime data from the IoT client
```bash
pyclient % gcpsub.py $PROJECT my-subscription
```

## Google Cloud Function
Write the [index.js](/gcpnodefunction/index.js) code inside the gcpnodefunction folder, then deploy the cloud function to the Google Cloud.

### IoT Device connection and data store
1. Run the following code to deploy the IoT pubsub functions to the Cloud Function, the trigger will be the Pubsub topic, whenever the pubsub received the data from the IoT client, this Pubsub topic will trigger this google cloud function
```bash
gcpnodefunction % gcloud functions deploy iotPubSubBQ --runtime nodejs10 --trigger-topic CMPEIoTdeviceRB
```
iotPubSubBQ will parse the received sensor data (json format) and send the data to BigQuery (you need to create the BigQuery dataset and table with schema first) and the two collections of firestore (one for latest data and one for all data)

2. Using the following command line to test the send command to IoT devices
```bash
% gcloud iot devices commands send \
    --command-data='test iot1' \   
    --region=us-central1  \
    --registry=CMPE181IoTRB \   
    --device=cmpe181devRB
```
You will received the print out from the IoT device side "Received message 'test iot1' on topic '/devices/cmpe181devRB/commands' with Qos 0"

Deploy the "IoTdeviceHTTPApi" cloud funtion to send command to iot device via HTTP POST
```bash
gcpnodefunction % gcloud functions deploy IoTdeviceHTTPApi --runtime nodejs10 --trigger-http
```
You can check the HTTP api (url address) via
```bash
% gcloud functions describe IoTdeviceHTTPApi
```
Using the following curl POST command to test the send command to IoT devices (make sure your IoT device is running)
```bash
% curl -X POST https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/IoTdeviceHTTPApi -H "Content-Type:application/json" -d '{"deviceId":"cmpe181devRB","message":"test message"}'
```

### HTTP Backend
Add the httpApi in [index.js](/gcpnodefunction/index.js) code, write the REST API, add create, read, update, and delete (CRUD) note to Firestore database. Run the following code to deploy the HTTP based cloud function. HTTP message will trigger this cloud function
```bash
gcpnodefunction % gcloud functions deploy httpApi --runtime nodejs10 --trigger-http
```
You can check the HTTP api (url address) via
```bash
% gcloud functions describe httpApi
```
1. Using the following curl command to test the HTTP GET api to read all sensor data:
```bash
% curl -X GET https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi -H "Content-Type:application/json"

[{"id":"testiot","data":{"sensor":"temperature","value":"75","number":"2020"}}]
```
2. If you add the id in the HTTP get query (add "?id=xxx" into the URL), you can get the data from a specific sensor:
```bash
% curl -X GET 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=cmpe181devRB'
No such document!
% curl -X GET 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=testsensor02'

{"time":{"_seconds":1615102571,"_nanoseconds":91000000},"name":"testsensor02","sensors":{"value":"99","sensor":"humidity"}}
```
3. Test the POST API, add the sensor data in the data field ('-d') using the json format. This sensor data will be saved into the Firestore.
```bash
% curl -X POST 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=testsensor03' -H "content-type:application/json" -d '{"bodydata":{"sensor":"humidity","value":"96"}}'

{"name":"testsensor03","sensors":{"sensor":"humidity","value":"96"},"time":"2021-03-07T07:42:47.040Z"}%
```
4. Test the PUT API to change the value of the data for a specific sensor
```bash
% curl -X PUT 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=testsensor02' -H "content-type:application/json" -d '{"bodydata":{"sensor":"humidity","value":"99"}}'

{"name":"testsensor02","sensors":{"sensor":"humidity","value":"99"},"time":"2021-03-07T07:36:11.091Z"}
```
5. Test the DELETE API
```bash
% curl -X DELETE 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=testsensor03' -H "content-type:application/json???
?? ?? ?? ?? ?? ?? ??
Deleted!%?? ??
```
For all the above APIs, you can use the '-v' option to see the detailed output, for example
```bash
% curl -v -X PUT 'https://us-central1-cmpe-181-hw1-rbiesty.cloudfunctions.net/httpApi?id=testsensor02' -H "content-type:application/json" -d '{"bodydata":{"sensor":"humidity","value":"99"}}'
```
