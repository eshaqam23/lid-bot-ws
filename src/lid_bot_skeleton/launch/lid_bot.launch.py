"""Full lid-bot bringup: motor serial bridge + RPLidar, optional keyboard teleop.

  ros2 launch lid_bot_skeleton lid_bot.launch.py
  ros2 launch lid_bot_skeleton lid_bot.launch.py teleop:=true   # needs xterm
  ros2 launch lid_bot_skeleton lid_bot.launch.py motor_port:=/dev/ttyUSB1 lidar_port:=/dev/ttyUSB0

Ports come from config/params.yaml unless *_port is passed on the command line.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def port_override(context, arg, param):
    # Only override params.yaml when the user actually passed a port.
    value = LaunchConfiguration(arg).perform(context)
    return {param: value} if value else {}


def launch_nodes(context, config_file):
    return [
        Node(
            package="lid_bot_skeleton",
            executable="serial_bridge",
            name="serial_bridge",
            output="screen",
            parameters=[config_file, port_override(context, "motor_port", "port")],
        ),
        Node(
            package="rplidar_ros",
            executable="rplidar_composition",
            name="rplidar_node",
            output="screen",
            parameters=[config_file, port_override(context, "lidar_port", "serial_port")],
        ),
    ]


def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory("lid_bot_skeleton"),
        "config",
        "params.yaml",
    )

    teleop = LaunchConfiguration("teleop")

    return LaunchDescription(
        [
            DeclareLaunchArgument("motor_port", default_value="",
                                  description="Override serial_bridge port from params.yaml"),
            DeclareLaunchArgument("lidar_port", default_value="",
                                  description="Override rplidar serial_port from params.yaml"),
            DeclareLaunchArgument("teleop", default_value="false"),
            OpaqueFunction(function=launch_nodes, args=[config_file]),
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
