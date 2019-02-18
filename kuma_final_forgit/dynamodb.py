import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import telepot   
from time import sleep


my_bot_token = '<BOT TOKEN>'	
	
dynamodb = boto3.resource('dynamodb', region_name='us-west-2' ,  aws_access_key_id ='<ACCESS KEY>',
         aws_secret_access_key ='<SECRET KEY>')

	
def getHumidityTempAll():
	try:
		table = dynamodb.Table('kuma_sensor')

		response = table.scan()
		items = response['Items']
		n=12 # limit to last 12 items
		data = items[:n]
		data_reversed = data[::-1]
		#records = data_to_json(data_reversed)
		return data_reversed
		
	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])

	#print("Successfully inside method 1")

# get latest values crowd from car 1
def getCarOneCount():
	try:
		table = dynamodb.Table('kuma_crowdsize')
		response = table.query(
			KeyConditionExpression=Key('camera_id').eq('1'),ScanIndexForward=False , Limit=10)
		items = response['Items']
		#records = data_to_json(items)
		return items

	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])
		

# get latest values crowd from car 2  // use for display graphic
def getCarTwoCount():
	try:
		table = dynamodb.Table('kuma_crowdsize')
		response = table.query(
			KeyConditionExpression=Key('camera_id').eq('2'),ScanIndexForward=False , Limit=10)
		items = response['Items']
		#records = data_to_json(items)
		return items

	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])


# get all result of crowd 
def getAllCarCount():
	try:
		table = dynamodb.Table('kuma_crowdsize')

		startdate = '2019-02-08T'
		
		response = table.query(
			KeyConditionExpression=Key('camera_id').eq('2'),ScanIndexForward=False , Limit=12)
		items = response['Items']
		#n=10 # limit to last 10 items
		#data = items[:n]
		#data_reversed = data[::-1]
		#print("Successfully connected to database!")
		#print(items)
		#print(data)
		#print(data_reversed)
		return items
	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])
		
print("Successfully inside method")

#for the telegram bot
def getLatestRecordCarOne():
	
	try:
		table = dynamodb.Table('kuma_crowdsize')
		response = table.query(
			KeyConditionExpression=Key('camera_id').eq('1'),ScanIndexForward=False , Limit=1)
		items = response['Items']
		record = []
		for i in response['Items']:
			record.append(i['people_count'])
		record_count = (''.join(str(i) for i in record))
		return record_count
	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])

#for the telegram bot		
def getLatestRecordCarTwo():
	
	try:
		table = dynamodb.Table('kuma_crowdsize')
		response = table.query(
			KeyConditionExpression=Key('camera_id').eq('2'),ScanIndexForward=False , Limit=1)
		items = response['Items']
		record = []
		for i in response['Items']:
			record.append(i['people_count'])
		record_count = (''.join(str(i) for i in record))
		return record_count
	except:
		import sys
		print(sys.exc_info()[0])
		print(sys.exc_info()[1])
		
#for the telegram bot
def respondToMsg(msg):
	chat_id = msg['chat']['id']
	command = msg['text']
	CarOneCountLevel = ''
	CarTwoCountLevel = ''
	countCarOne = int(getLatestRecordCarOne())
	countCarTwo = int(getLatestRecordCarTwo())
	if command == '/status':		
		tempList = getHumidityTempAll()
		record = []
		for i in tempList:
			record.append(i['temperature'])
		temp = record[0]
		
		# get count person per car 
		if countCarOne == 0:
			CarOneCountLevel = "low"
		elif countCarOne == 1:
			CarOneCountLevel = "medium"
		else:
			CarOneCountLevel = "high"
		
		if countCarTwo == 0:
			CarTwoCountLevel = "low"
		elif countCarOne == 1:
			CarTwoCountLevel = "medium"
		else:
			CarTwoCountLevel = "high"
		
		messageTemp = 'Crowd level in Car 1 is ' + str(CarOneCountLevel) + ' [People: ' + str(countCarOne) + ']' + "\n" + 'Crowd level in Car 2 is ' + str(CarTwoCountLevel) + ' [People: ' + str(countCarTwo) + ']' + "\n" + 'The Current Temperature is ' + str(temp) + ' Celsius.'
		bot.sendMessage(chat_id , messageTemp)
		
	elif command == '/check':
		print("inside check")
		if countCarOne > countCarTwo:
			message = 'Car 2 have lesser people. Please Move to Car 2.'
		elif countCarOne == countCarTwo:
			message = 'Car 1 and Car 2 have equal amount of people.'
		elif countCarOne < countCarTwo:
			message = 'Car 1 have lesser people. Please Move to Car 1.'

		bot.sendMessage(chat_id , message)

		
#bot = telepot.Bot(my_bot_token)
#bot.message_loop(respondToMsg)
