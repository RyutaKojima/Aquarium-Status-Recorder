#!/usr/bin/env pyton
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import subprocess
import numpy
import dht11
import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#define GPIO 14 as DHT11 data pin
Temp_sensor = 14

SENSOR_INFO_FILE = os.getenv("SENSOR_INFO_FILE", "")
FIREBASE_SDK_JSON = os.getenv("FIREBASE_SDK_JSON", "")
TEMPERATURE_THRESHOLD = float(os.getenv("TEMPERATURE_THRESHOLD", 0))

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

def main():
	nowTime = datetime.datetime.now(JST)
	nowTemp = get_temp()
	temperature, humidity = get_temp_sensor()

	if is_hot(nowTemp):
		set_usb_power(True)
	#else:
		#set_usb_power(False)

	save_to_firestore(nowTime, nowTemp, temperature, humidity)

def is_hot(temp):
	return temp > TEMPERATURE_THRESHOLD

def set_usb_power(isOn):
	if isOn:
		os.system('sudo hub-ctrl -b 1 -d 2 -P 2 -p 1')
	else:
		os.system('sudo hub-ctrl -b 1 -d 2 -P 2 -p 0')

def get_temp():
	sensorData = get_sensor_raw()
	if sensorData is None:
		sys.exit(1)

	temp_val = sensorData.split('=')
	return round(float(temp_val[-1]) / 1000, 1)

def get_sensor_raw():
	try:
		return subprocess.check_output(['cat', SENSOR_INFO_FILE]).decode()
	except:
		return None

def get_temp_sensor():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	instance = dht11.DHT11(pin = Temp_sensor)
	while True:
		result = instance.read()
		if result.temperature > 0:
			return result.temperature,result.humidity
		time.sleep(0.05)

def save_to_firestore(now, water_temp, temperature, humidity):
	credential = credentials.Certificate(FIREBASE_SDK_JSON)
	firebase_admin.initialize_app(credential)

	db = firestore.client()
	doc_ref = db.collection(u'water_tank_condition').document(now.strftime('%Y-%m-%dT%H:%M'))
	doc_ref.set({
            u'date': now.strftime('%Y-%m-%d'),
            u'time': now.strftime('%H:%M'),
	    u'water_temperature': water_temp,
	    u'temperature': temperature,
	    u'humidity': humidity,
	    })

if __name__ == '__main__':
	main()

