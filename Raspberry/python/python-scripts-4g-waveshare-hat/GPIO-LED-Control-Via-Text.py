#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time
import re

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.LOW)


ser = serial.Serial("/dev/ttyS0",115200)
ser.flushInput()

phone_number = '' #********** change it to the phone number you want to call
text_message = ''
power_key = 6
rec_buff = ''


def send_at(command,back,timeout):
	global rec_buff
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	if rec_buff != '':
		decoded = rec_buff.decode()
		print(decoded)
		if 'red' in decoded: GPIO.output(21, GPIO.HIGH), time.sleep(3), GPIO.output(21, GPIO.LOW)
		if back not in decoded:
			print(command + ' back:\t' + decoded)
			return 0
		return 1
	else:
		return 0


def DeleteMessage(index):
	send_at('AT+CMGD=%d' % index, 'OK', 1)


def ReceiveShortMessage():
	#print('Setting SMS mode...')
	send_at('AT+CMGF=1','OK',1)
	# The response to CMGL is prefixed with '+CMGL:', not the unsolicited '+CMTI' new-message notice
	answer = send_at('AT+CMGL="REC UNREAD"', '+CMGL', 1)
	
	if 1 == answer:
		decoded = rec_buff.decode()
		if 'red' in decoded:
			print('Turning LEDS onto RED')
		# Delete every listed message now that it has been read and printed, freeing SIM storage
		indexes = re.findall(r'\+CMGL:\s*(\d+)', decoded)
		for index in indexes:
			DeleteMessage(int(index))
		return True
	else:
		print('No New text')
	return False

def power_on(power_key):
	print('SIM7600X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(20)
	ser.flushInput()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is loging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	print('Good bye')

power_on(power_key)
while True:
	
	ReceiveShortMessage()
