cmake_minimum_required(VERSION 2.8.3)
project(ca-cc)

find_package(catkin REQUIRED COMPONENTS
  rospy
  roscpp
  std_msgs
  roslib
)
find_package(OpenCV REQUIRED)
catkin_package()
include_directories(include ${catkin_INCLUDE_DIRS})
add_executable(createRCC8 src/FindSegments.cpp)
add_executable(sendGoal src/SendGoal.cpp)
target_link_libraries(createRCC8 ${OpenCV_LIBS})
target_link_libraries(createRCC8 ${catkin_LIBRARIES})
target_link_libraries(sendGoal ${catkin_LIBRARIES})
