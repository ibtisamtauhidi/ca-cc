# ca-cc
ROS implementation of an architecture for creating a cognitive (semantic/graphical/topological) map of an indoor environment segmented by rooms from a grid map.


### Issues :

These initial files are directly uploaded from my own system. There are not expected to work in unconfigured systems- several hardwired dependencies that are to be resolved before these can be used in general systems. Four issues that needs to be addressed:
  - scripts that use absolute addresses should use launch file parameters,
  - the Prolog script generator must be upgraded to new specs,
  - world SDF files should reside inside this package,
  - external dependencies (Turtlebot packages, openCV, pygame, etc.) should be specified in manifest for rosdep.

Resolving these issues (*boring manual labor*) should make this piece of software runnable on any system with ROS.
