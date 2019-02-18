from flask import Flask, render_template, jsonify, request,Response

import mysql.connector
import sys
from time import sleep
import json
import numpy
import datetime
import decimal
from rpi_lcd import LCD
import dynamodb
import telepot
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

global my_rpi
dataReal = {}

class GenericEncoder(json.JSONEncoder):
    def default(self, obj):  
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj) 
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:  
            return json.JSONEncoder.default(self, obj)

def data_to_json(data):
    json_data = json.dumps(data,cls=GenericEncoder)
    #print(json_data)
    return json_data
	
def customCallback(client, userdata, message):	
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	#print(message.payload["camera_id"])
	#dataReal[message.payload.camera_id] = message.payload["camera_id"]
	#dataReal[message.payload["camera_id"]] = message.payload
	#dataReal = {'getAllTempHum': data_to_json(message.payload)}
	print("bottom")
	temp = json.loads(message.payload)
	print(temp)
	print("camera_id: %s" % temp["camera_id"] )
	dataReal[temp["camera_id"]] = temp
	print(dataReal)


host = "<END POINT"
rootCAPath = "<ROOT CA PATH>"
certificatePath = "<CERTIFICATE PATH>"
privateKeyPath = "<PRIVATE KEY PATH>"

my_rpi = AWSIoTMQTTClient("kuma-basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureAutoReconnectBackoffTime(1, 32, 20) 
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing 
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

my_rpi.connect()
my_rpi.subscribe("kuma/crowdsize", 1, customCallback)
sleep(2)


app = Flask(__name__)

@app.route("/api/lcdDisplay",methods=['POST','GET'])
def LCD_publish():
	print("inside method")
	result = "Display is updated"
	if request.method == 'POST' or request.method == 'GET':
		countCarOne = int(dynamodb.getLatestRecordCarOne())
		countCarTwo = int(dynamodb.getLatestRecordCarTwo())
        if countCarOne > countCarTwo:
            message = {"message":"1"}
        elif countCarOne == countCarTwo:
            message = {"message":"2"}	  
        elif countCarOne < countCarTwo:
            message = {"message":"3"}
	messages = json.dumps(message)	
	my_rpi.publish("kuma/sensor/lcd", messages , 1)
	return result

@app.route("/api/getAllTempHum",methods=['POST','GET'])
def apidata_getdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
			data = {'getAllTempHum': data_to_json(dynamodb.getHumidityTempAll()), 
             'title': "Temp and Hum Data"}
			return jsonify(data)
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
			

# get all car for both car id 			
@app.route("/api/getAllCar",methods=['POST','GET'])
def getCarCounts():
    if request.method == 'POST' or request.method == 'GET':
        try:
			data = {'getAllCarOne': data_to_json(dynamodb.getCarOneCount()), 'getAllCarTwo': data_to_json(dynamodb.getCarTwoCount()),
             'title': "Car Count"}
			return jsonify(data)
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
			

			
@app.route("/api/getRealTimeData",methods=['POST','GET'])
def realTimeData():
	global dataReal
	if request.method == 'POST' or request.method == 'GET':
		print("testing 1")
		test = "testing"
		print(dataReal)
	return jsonify(dataReal)
	
	
@app.route("/")
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
	while True:
		app.run(debug=True,host='0.0.0.0')
		


