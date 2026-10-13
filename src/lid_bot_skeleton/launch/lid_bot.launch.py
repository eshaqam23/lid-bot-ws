"""Full lid-bot bringup: motor serial bridge + RPLidar, optional keyboard teleop.

  ros2 launch lid_bot_skeleton lid_bot.launch.py
  ros2 launch lid_bot_skeleton lid_bot.launch.py teleop:=true   # needs xterm
  ros2 launch lid_bot_skeleton lid_bot.launch.py motor_port:=/dev/ttyUSB1 lidar_port:=/dev/ttyUSB0

Defaults come from config/params.yaml. The *_port args override them.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory("lid_bot_skeleton"),
        "config",
        "params.yaml",
    )

    motor_port = LaunchConfiguration("motor_port")
    lidar_port = LaunchConfiguration("lidar_port")
    teleop = LaunchConfiguration("teleop")

    return LaunchDescription(
        [
            DeclareLaunchArgument("motor_port", default_value="/dev/ttyUSB0"),
            DeclareLaunchArgument("lidar_port", default_value="/dev/ttyUSB1"),
            DeclareLaunchArgument("teleop", default_value="false"),
            Node(
                package="lid_bot_skeleton",
                executable="serial_bridge",
                name="serial_bridge",
                output="screen",
                parameters=[config_file, {"port": motor_port}],
            ),
            Node(
                package="rplidar_ros",
                executable="rplidar_composition",
                name="rplidar_node",
                output="screen",
                parameters=[config_file, {"serial_port": lidar_port}],
            ),
            # Teleop needs a real keyboard, so it opens in its own xterm window.
            Node(
                package="teleop_twist_keyboard",
                executable="teleop_twist_keyboard",
                name="teleop",
                prefix="xterm -e",
                condition=IfCondition(teleop),
            ),
        ]
    )
