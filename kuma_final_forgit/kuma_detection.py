import threading
import boto3
import botocore
import RPi.GPIO as GPIO
from rpi_lcd import LCD
import time
from time import sleep
#from picamera import PiCamera
from time import sleep
import picamera
import sys
import os
import tinys3
import yaml
import Adafruit_DHT
import datetime
import argparse
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import threading
import dynamodb



ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", type=str, default="1",
  help="Set ID for this device")
args = vars(ap.parse_args())

camera_id = args["id"]

lcd = LCD()
pin = 4
led_one = {
    "red": 29,
    "green": 33,
    "blue": 31,
    "redled": 36
}
led_two = {
    "red": 13,
    "green": 11,
    "blue": 15,
    "redled": 16
}
# red1 = 29
# green1 = 33
# blue1 = 31
# redLed = 36
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(led_one["red"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_one["green"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_one["blue"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_one["redled"], GPIO.OUT , initial=GPIO.LOW)
GPIO.output(led_one["red"], True)
GPIO.output(led_one["green"], True)
GPIO.output(led_one["blue"], True)
GPIO.output(led_one["red"], True)
GPIO.output(led_one["green"], True)
GPIO.output(led_one["blue"], True)
GPIO.output(led_one["redled"], False)

GPIO.setup(led_two["red"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_two["green"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_two["blue"], GPIO.OUT , initial=GPIO.LOW)
GPIO.setup(led_two["redled"], GPIO.OUT , initial=GPIO.LOW)
GPIO.output(led_two["red"], True)
GPIO.output(led_two["green"], True)
GPIO.output(led_two["blue"], True)
GPIO.output(led_two["redled"], False)

print "HERE ONE"

host = "<END POINT"
rootCAPath = "<ROOT CA PATH>"
certificatePath = "<CERTIFICATE PATH>"
privateKeyPath = "<PRIVATE KEY PATH>"


my_rpi = AWSIoTMQTTClient("basicPubSub%s" % camera_id)
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# testing
print "HERE ONE.5"
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# photo props
image_width = cfg['image_settings']['horizontal_res']
image_height = cfg['image_settings']['vertical_res']
file_extension = cfg['image_settings']['file_extension']

#file_name = cfg['image_settings']['file_name']
photo_interval = cfg['image_settings']['photo_interval'] # Interval between photo (in seconds)
image_folder = cfg['image_settings']['folder_name']


# Set the filename and bucket name
username = "1819s2_iot_Kuma"  # CHANGE THIS to yr AWS login acct
BUCKET = 'iot-ay1819s2' # **DO NOT** CHANGE THIS
location = {'LocationConstraint': 'us-west-2'} # **DO NOT** CHANGE THIS
#file_path = "/home/pi/dora/WeeKiat_CA1/images/test.jpg" # CHANGE THIS to point to the path of your file
file_namee = "home/" + username  +"/" # **DO NOT** CHANGE THIS

print "HERE ONE.75"
# camera setup
camera = picamera.PiCamera()
print "HERE ONE.75.5"
camera.resolution = (image_width, image_height)
print "HERE ONE.75.75"
camera.awb_mode = cfg['image_settings']['awb_mode']
print "HERE ONE.75.3"

# verify image folder exists and create if it does not
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

print "HERE TWO"

def sensor_detection(delay, run_event):
    while run_event.is_set():
        #COPY CAMERA/DHT11 CODE HERE
        humidity, temperature = Adafruit_DHT.read_retry(11, pin)
        print(temperature)
        print('Temp: {:.1f} C'.format(temperature))
        print('Humidity: {:.1f}'.format(humidity))
        payload = {
        "camera_id": camera_id,
        "temperature": temperature,
        "humidity": humidity, 
        "timestamp": datetime.datetime.now().isoformat()
        }
        my_rpi.publish("kuma/sensor", json.dumps(payload), 1)

        # Build filename string
        file_name = datetime.datetime.now().isoformat()
        file_path = "/home/pi/dora/kuma_final/images/" + file_name + file_extension
        file_namee = "home/" + username  +"/" + file_name + file_extension
        filepath = image_folder + '/' + file_name + file_extension

        if cfg['debug'] == True:
            print '[debug] Taking photo and saving to path ' + filepath

        # Take Photo
        camera.capture(filepath)

        if cfg['debug'] == True:
            print '[debug] Uploading ' + filepath + ' to s3'
            
        uploadToS3(file_path,file_namee, BUCKET,location)
        #sleep(2)


def lcd_callback(client, userdata, message):
        data = json.loads(message.payload)
        resultOfLcd = data
        #print(resultOfLcd["message"])
        print message.payload
        messagetitle = "Please Move to"
        response = "Display Message have been updated"
        if resultOfLcd["message"] == '1':		
            lcd.text(messagetitle , 1)
            lcd.text("Car 2" , 2)			
        elif resultOfLcd["message"] == '2':
            lcd.text("Both Car same" , 1)
            lcd.text("crowd level" , 2)
        elif resultOfLcd["message"] == '3':
            lcd.text(messagetitle , 1)
            lcd.text("Car 1" , 2)

def led_callback(delay, run_event): 
    print "LED DATA STARTING...."
    while run_event.is_set():
        crowdsizeOne = int(dynamodb.getLatestRecordCarOne())
        print crowdsizeOne
        if crowdsizeOne == 0:
            GPIO.output(led_one["red"], False)
            GPIO.output(led_one["green"], False)
            GPIO.output(led_one["blue"], False)
            GPIO.output(led_one["redled"], False)
            # ON
            GPIO.output(led_one["red"], True)
            GPIO.output(led_one["green"], True)
            GPIO.output(led_one["blue"], True)
        elif crowdsizeOne == 1:
            GPIO.output(led_one["red"], False)
            GPIO.output(led_one["green"], False)
            GPIO.output(led_one["blue"], False)
            GPIO.output(led_one["redled"], False)
            # ON
            GPIO.output(led_one["red"], True)
            GPIO.output(led_one["green"], True)
            GPIO.output(led_one["blue"], False)
        else:
            GPIO.output(led_one["red"], False)
            GPIO.output(led_one["green"], False)
            GPIO.output(led_one["blue"], False)
            GPIO.output(led_one["redled"], False)
            # ON
            GPIO.output(led_one["redled"], True)
        

        crowdSizeTwo = int(dynamodb.getLatestRecordCarTwo())
        print crowdSizeTwo
        if crowdSizeTwo == 0:
            GPIO.output(led_two["red"], False)
            GPIO.output(led_two["green"], False)
            GPIO.output(led_two["blue"], False)
            GPIO.output(led_two["redled"], False)
            #ON
            GPIO.output(led_two["red"], True)
            GPIO.output(led_two["green"], True)
            GPIO.output(led_two["blue"], True)
        elif crowdSizeTwo == 1:
            GPIO.output(led_two["red"], False)
            GPIO.output(led_two["green"], False)
            GPIO.output(led_two["blue"], False)
            GPIO.output(led_two["redled"], False)
            # ON
            GPIO.output(led_two["red"], True)
            GPIO.output(led_two["green"], True)
            GPIO.output(led_two["blue"], False)
        else:
            GPIO.output(led_two["red"], False)
            GPIO.output(led_two["green"], False)
            GPIO.output(led_two["blue"], False)
            GPIO.output(led_two["redled"], False)
            # ON
            GPIO.output(led_two["redled"], True)
        
        sleep(0.5)
    



def uploadToS3(file_path,file_namee, bucket_name,location):
    s3 = boto3.resource('s3', aws_access_key_id="ACCESS KEY", aws_secret_access_key= "SECRET KET") # Create an S3 resource
    exists = True

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False

    if exists == False:
        s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    
    # Upload the file
    #full_path = file_path + "/" + file_name
    full_path = file_path
    s3.Object(bucket_name, file_namee).put(Body=open(full_path, 'rb'), Metadata={'camera_id': camera_id })
    print("File uploaded")


def main():
    print "HERE THREE"
    run_event = threading.Event()
    run_event.set()
    d1 = 1
    t1 = threading.Thread(target = sensor_detection, args = (d1, run_event))
    t1.start()

    t2 = threading.Thread(target = led_callback, args = (d1, run_event))
    t2.start()

    #sleep(.5)
    # Connect and subscribe to AWS IoT
    my_rpi.connect()


    #PUT SUBSCRIBE LCD HERE
    my_rpi.subscribe("kuma/sensor/lcd", 1, lcd_callback)

    try:
        while 1:
            temp = 1
            #sleep(5)
    except KeyboardInterrupt:
        print "attempting to close threads. Max wait =",max(d1,2)
        run_event.clear()
        t1.join()
        t2.join()
        print "threads successfully closed"

if __name__ == '__main__':
    main()