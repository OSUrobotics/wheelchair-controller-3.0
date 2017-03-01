#!/usr/bin/env python

import rospy
import RPi.GPIO as GPIO
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
import time

class Controller(object):
    def __init__(self):
        rospy.init_node('controller')

        rospy.Subscriber("cmd_vel", Twist, self.twist_callback)
	rospy.Subscriber("joy", Joy, self.joy_callback)

        self.fwd = 5
        self.bkw = 6
        self.lft = 13
        self.rgt = 19

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(self.fwd, GPIO.OUT)
	GPIO.setup(self.bkw, GPIO.OUT)
        GPIO.setup(self.lft, GPIO.OUT)
        GPIO.setup(self.rgt, GPIO.OUT)

	self.safe = False
	self.num_unsafe = 0
	self.N = 5

	self.old_axes = -99;
	#rospy.Timer(rospy.Duration(0.1), self.runstop_callback)
	rospy.spin()

    def runstop_callback(self,event):
	#self.num_safe += 1
	if self.num_unsafe > self.N and self.safe:
            GPIO.output(self.fwd, GPIO.LOW)
            GPIO.output(self.bkw, GPIO.LOW)
            GPIO.output(self.lft, GPIO.LOW)
            GPIO.output(self.rgt, GPIO.LOW)
            print("TIMER RUNSTOP WORKED!")
	    self.safe = False
	    self.num_unsafe = 0
    
    def joy_callback(self, joy_msg):
        if joy_msg.buttons[5] == self.old_axes:
	    self.num_unsafe += 1
	if joy_msg.buttons[5] != self.old_axes:
	    print("SAFE")
	    self.safe = True
	    self.num_unsafe = 0

	    self.old_axes = joy_msg.buttons[5]
    

    def twist_callback(self, twist_msg):
	print("got twist")
	    #If the killswitch (A) is not pressed, or self.N twist commands are executed without an update, unsafe.
	    #if self.safe == False or self.num_unsafe > self.N:
	        #return

        xvel = twist_msg.linear.x
        zvel = twist_msg.angular.z * -1
   
        #x velocity
	if xvel > 1:
            xvel = 1

        if xvel < -1:  
            xvel = -1

        
        if zvel > 1:
            zvel = 1
        if zvel < -1:
            zvel = -1
            
        if xvel > 0:
            GPIO.output(self.fwd, GPIO.HIGH)
            GPIO.output(self.bkw, GPIO.LOW)
        if xvel < 0:
            GPIO.output(self.bkw, GPIO.HIGH)
            GPIO.output(self.fwd, GPIO.LOW)
        if xvel == 0:
            GPIO.output(self.bkw, GPIO.LOW)
            GPIO.output(self.fwd, GPIO.LOW)

        if zvel > 0:
            GPIO.output(self.rgt, GPIO.HIGH)
            GPIO.output(self.lft, GPIO.LOW)
        if zvel < 0:
            GPIO.output(self.lft, GPIO.HIGH)
            GPIO.output(self.rgt, GPIO.LOW)
        if zvel == 0:
            GPIO.output(self.lft, GPIO.LOW)
            GPIO.output(self.rgt, GPIO.LOW) 
            

if __name__ == '__main__':
    Controller()
