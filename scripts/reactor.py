#!/usr/bin/env python
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import math

front = 0.0
front_left = 0.0
front_right = 0.0
left = 0.0
right = 0.0
prev_front = 0.0
teleop = rospy.Publisher('/cmd_vel_mux/input/teleop', Twist, queue_size=10)
suggest = rospy.Publisher('/suggest', String, queue_size=10)

def readJoyStick(data):
	global front, left, right
	msg = Twist()
	msg.angular.z = data.angular.z
	if not math.isnan(front) and front < 1.0 and data.linear.x == 0.5:
		msg.linear.x = 0
		if left > right:
			suggest.publish("F_L: "+str(front_left)+"F_L: "+str(front_right)+"L: "+str(left)+", R: "+str(right)+" - GO LEFT")
		else:
			suggest.publish("F_L: "+str(front_left)+"F_L: "+str(front_right)+"L: "+str(left)+", R: "+str(right)+" - GO RIGHT")
	else: 
		msg.linear.x = data.linear.x
	teleop.publish(msg)

def readScan(data):
	global front, left, right
	front = data.ranges[320]
	front_left = data.ranges[275]
	front_right = data.ranges[365]
	left = data.ranges[10]
	right = data.ranges[630]
	if math.isnan(left):
		left = 50.0
	if math.isnan(right):
		right = 50.0

if __name__ == '__main__':
	rospy.init_node('Sun_Reactor', anonymous=True)
	rospy.Subscriber("/scan", LaserScan, readScan)
	rospy.Subscriber("raw_teleop", Twist, readJoyStick)
	rospy.spin()
