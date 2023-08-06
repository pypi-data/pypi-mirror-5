#!/usr/bin/python
from time import sleep
from sys import exit

#Select which IO version by commenting the unused version 
from matrix_keypad import MCP230xx
#from matrix_keypad import RPi_GPIO
 
# Initialize the keypad class. Using the **optional** variable "columnCount" to change it to a 4x4 keypad
kp = MCP230xx.keypad(address = 0x21, num_gpios = 8, columnCount = 4)
# kp = RPi_GPIO.keypad(ColumnCount = 3)


# Setup variables
attempt = "0000"
passcode = "1912"
counter = 0

# Loop while waiting for a keypress
while True:
	# Loop to get a pressed digit
	digit = None
	while digit == None:
		digit = kp.getKey()
 
	# Print the result
	print "Digit Entered:       %s"%digit
	attempt = (attempt[1:] + str(digit))  
	print "Attempt value:       %s"%attempt
	
	# Check for passcode match
	if (attempt == passcode):
		print "Your code was correct, goodbye."
		exit()
	else:
		counter += 1
		print "Entered digit count: %s"%counter
		if (counter >= 4):
			print "Incorrect code!"
			sleep(3)
			print "Try Again" 
			sleep(1)
			counter = 0
	
	sleep(0.5)
