#!/usr/bin/env python
import rospy
from nav_msgs.msg import Path
from std_msgs.msg import String
from sys import exit
from Tkinter import *
import Image, ImageTk
i = 0
finished = False
status = False
top = Tk()
v = StringVar()
img = ImageTk.PhotoImage(Image.open("/home/sunxyz/catkin_ws/src/sun_project/maps/my_floor.pgm"))
w = Label(top,image = img)
w.pack()
Label(top,textvariable = v).pack()
prev_data = ""
def readSeg(data):
	global status, i, w
	fname = rospy.get_param('~map')
	if (data.data == "RCC8-Succ" and not status):
		status = True
		img = ImageTk.PhotoImage(Image.open(fname+"/outputs/output.bmp"))
		w.configure(image=img)
		w.image = img
		

def readChoice(data):
	global i, prev_data, finished
	if finished:
		return
	if(data.data=="-1"):
		v.set("Choosen: "+ prev_data)
		finished = True
	else:
		v.set("Select? " + data.data)
		prev_data = data.data

if __name__ == '__main__':
	rospy.init_node('Path_Listener', anonymous=True)
	rospy.Subscriber("sunsegstatus", String, readSeg)
	rospy.Subscriber("sunsegchoice", String, readChoice)
	top.mainloop()
	rospy.spin()
