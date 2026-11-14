# Laptop-side network env for the lid-bot (Pi at 100.64.83.52). Source in each terminal.
# Overrides the Cyclone/domain-42 settings from ~/.bashrc for this terminal only.
source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=0
export ROS_STATIC_PEERS="${PI_IP:-100.64.83.52}"
# In WSL mirrored mode the ros2 CLI hangs if no daemon is running; start one up front.
timeout 15 ros2 daemon start >/dev/null 2>&1
