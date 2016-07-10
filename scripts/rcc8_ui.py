#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sys import exit
from Tkinter import *
import Image, ImageTk
finished = False
top = Tk()
v = StringVar()
img = ImageTk.PhotoImage(Image.open("/home/sunxyz/catkin_ws/src/sun_project/maps/my_floor.pgm"))
w = Label(top,image = img)
w.pack()
Label(top,textvariable = v).pack()
prev_data = ""
pub = None

def readSeg():
	global w
	img = ImageTk.PhotoImage(Image.open("/home/sunxyz/catkin_ws/src/sun_project/outputs/output.bmp"))
	w.configure(image=img)
	w.image = img

def readChoice(data):
	global prev_data, pub, finished
	if(data.data=="-1"):
		v.set("Choosen: "+ prev_data)
		finished = True
	else:
		v.set("Select? " + data.data)
		prev_data = data.data
		finished = False
	publishGoal()

def publishGoal():
	global finished
	if not finished: return
	pub.publish(prev_data)
	finished = False

if __name__ == '__main__':
	rospy.init_node('Path_Listener', anonymous=True)
	pub = rospy.Publisher('sun_goal', String, queue_size=10)
	rospy.Subscriber("sunsegchoice", String, readChoice)
	readSeg()
	top.mainloop()
	rospy.spin()
