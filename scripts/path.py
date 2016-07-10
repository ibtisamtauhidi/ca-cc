#!/usr/bin/env python
import rospy
from nav_msgs.msg import Path
from sys import exit

def readDestination(data):
	print data
	print "oogleewoo"

def readPlan(data):
	print data
	print "yahoo"

if __name__ == '__main__':
	rospy.init_node('Path_Listener', anonymous=True)
	rospy.Subscriber("/move_base/NavfnROS/plan", Path, readJS)
	rospy.spin()
