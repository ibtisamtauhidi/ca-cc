#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
import pygame

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

def get():
    axes = [0,0,0,0,0]
    buttons = [0,0,0,0,0,0,0,0,0,0,0,0]
    pygame.event.pump()
    for i in range(0, j.get_numaxes()):
        axes[i] = int(round(j.get_axis(i)))
    for i in range(0, j.get_numbuttons()):
        buttons[i] = j.get_button(i)
    
    linear = 0.0
    angular = 0.0

    if axes[1] == 0:
	linear = 0.0
    elif axes[1] == -1:
	linear = 0.5
    elif axes[1] == 1:
	linear = -0.5
    if axes[0] == 0:
	angular = 0.0
    elif axes[0] == -1:
	angular = 0.5
    elif axes[0] == 1:
	angular = -0.5
    return [linear,angular]

def talker(pub):
	msg = Twist()
	arr = get()
	msg.linear.x = arr[0]
	msg.angular.z = arr[1]
	pub.publish(msg)

if __name__ == '__main__':
	pub = rospy.Publisher('raw_teleop', Twist, queue_size=10)
	rospy.init_node('Sun_Input', anonymous=True)
	try:
		rate = rospy.Rate(10)
		while not rospy.is_shutdown():
			talker(pub)
			rate.sleep()
	except rospy.ROSInterruptException:
		pass
