#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
regions = []
count = adj_mat = resolution = origin = None
goal = 0
ready = False

def getLoc(reg_id):
	global regions, count
	prolog = open('/home/sunxyz/catkin_ws/src/sun_project/scripts/sun.pl')
	while True:
		line = prolog.readline()
		if not line: break
		line = line.replace("(",",").replace(")","").replace(",,",",").replace(".","")
		line = line.replace("\n","").replace("\r","")
		tokens = line.split(",")
		if(tokens[0]=="count"):
			count = int(tokens[1])
			adj_mat = [[0 for x in range(count)] for y in range(count)]
		elif(tokens[0]=="region"):
			regions.append([int(tokens[2].replace("r","")),int(tokens[3].replace("r",""))])
		elif(tokens[0]=="connected"):
			adj_mat[int(tokens[1].replace("r",""))][int(tokens[2].replace("r",""))] = 1
			adj_mat[int(tokens[2].replace("r",""))][int(tokens[1].replace("r",""))] = 1

	yaml = open('/home/sunxyz/catkin_ws/src/sun_project/scripts/file.yaml')
	while True:
		line = yaml.readline()
		if not line: break
		tokens = line.split(":")
		if(tokens[0] == "resolution"):
			resolution = float(tokens[1].replace(" ",""))
		elif(tokens[0] == "origin"):
			line = tokens[1].replace(" ","").replace("[","").replace("]","")
			line = line.replace("\n","").replace("'","")
			float_tokens = line.split(",")
			origin = [float(float_tokens[0]),float(float_tokens[1])]

	region_id = reg_id
	region_x = regions[region_id][0]
	region_y = regions[region_id][1]
	return [region_x*resolution+origin[0],-1*(region_y*resolution+origin[1])]

def publishGoal(pub):
	global ready, goal
	if not ready: return
	msg = PoseStamped()
	msg.header.stamp = rospy.Time.now()
	msg.header.frame_id = "map"
	loc = getLoc(goal)
	msg.pose.position.x = loc[0]
	msg.pose.position.y = loc[1]
	msg.pose.orientation.z = 1
	msg.pose.orientation.w = 1
	pub.publish(msg)

def setGoal(data):
	global ready, goal
	ready = True
	goal = int(data.data)

if __name__ == '__main__':
	rospy.init_node('Sunout', anonymous=True)
	pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
	rospy.Subscriber("sun_goal", String, setGoal)
	try:
		rate = rospy.Rate(1)
		while not rospy.is_shutdown():
			publishGoal(pub)
			rate.sleep()
	except rospy.ROSInterruptException:
		pass
