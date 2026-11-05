from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command
from launch.event_handlers import OnProcessStart
from launch.actions import RegisterEventHandler

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # -------------------- pub_cmds --------------------- #
    teleop_twist_keyboard = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        output="screen",
        prefix='xterm -e'
    )

    # --------------------- control --------------------- #
    motor_commands = Node(
        package="esp_bridge",
        executable="motor_commands",
        output="screen"
    )

    # --------------------- LiDAR ---------------------- #
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('sllidar_ros2'),
                'launch',
                'view_sllidar_a1_launch.py'
            )
        ),
        launch_arguments={
            'scan_mode': 'Standard',
            # Specify port as a launch argument
        }.items()
    )

    return LaunchDescription(
        [
            teleop_twist_keyboard,
            # motor_commands,
            lidar_launch
        ]
    )