#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import pygame

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

keyPressed = False
choice = 0
pub = rospy.Publisher('sunsegchoice', String, queue_size=10)
def get():
    global keyPressed, choice,pub
    axes = [0,0,0,0,0]
    buttons = [0,0,0,0,0,0,0,0,0,0,0,0]
    pygame.event.pump()
    for i in range(0, j.get_numaxes()):
        axes[i] = int(round(j.get_axis(i)))
    for i in range(0, j.get_numbuttons()):
        buttons[i] = j.get_button(i)

	if(buttons[1] == 1):
		choice = -1
		return
    if((buttons[0] == 1 or buttons[2] == 1) and not keyPressed):
        keyPressed = True
        if(buttons[0] == 1):
            choice = choice + 1
        if(buttons[2] == 1 and choice > 0):
            choice = choice - 1
    if(buttons[0] == 0 and buttons[2] == 0 and keyPressed):
        keyPressed = False

def talker(pub):
	get()
	pub.publish(str(choice))

if __name__ == '__main__':
	rospy.init_node('Sun_Input', anonymous=True)
	try:
		rate = rospy.Rate(10)
		while not rospy.is_shutdown():
			talker(pub)
			rate.sleep()
	except rospy.ROSInterruptException:
		pass
