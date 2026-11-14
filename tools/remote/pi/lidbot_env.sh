# Network env for lid-bot <-> laptop RViz (not part of the lid-bot-ws repo).
# Campus Wi-Fi blocks multicast, so DDS discovery uses unicast to the laptop.
source /opt/ros/jazzy/setup.bash
source ~/lid-bot-ws/install/setup.bash
export ROS_DOMAIN_ID=0
export ROS_STATIC_PEERS="${LAPTOP_IP:-100.64.217.78}"
