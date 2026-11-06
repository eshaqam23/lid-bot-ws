# lid-bot-ws

ROS 2 workspace for the VT CRO lid bot: keyboard teleop, an ESP motor bridge, and a Slamtec RPLIDAR A1.

The robot computer is expected to be Linux. Motor commands go out over USB serial to the ESP firmware in `src/motor_logic`.

## Packages

| Path | What it does |
| --- | --- |
| `src/robot_bringup` | Launch file that starts teleop and the LiDAR. |
| `src/esp_bridge` | `motor_commands` node. Subscribes to `cmd_vel`, converts it to wheel PWM, and writes it to the ESP. |
| `src/motor_logic` | Arduino sketch for the ESP. Drives a differential pair from serial commands. |
| `src/sllidar_ros2` | Slamtec RPLIDAR driver. Not part of this repo; clone it locally (see below). |

## Dependencies

- ROS 2 (rclpy, `geometry_msgs`, `std_msgs`, `teleop_twist_keyboard`)
- `xterm` (the teleop node is launched inside one)
- `python3-serial` (pyserial), used by `esp_bridge`
- The [Slamtec sllidar_ros2](https://github.com/Slamtec/sllidar_ros2) package
- Arduino IDE (or equivalent) to flash `src/motor_logic` onto the ESP

```bash
sudo apt update
sudo apt install xterm python3-serial ros-${ROS_DISTRO}-teleop-twist-keyboard
```

Clone the LiDAR driver into `src/` (this folder is gitignored):

```bash
git clone https://github.com/Slamtec/sllidar_ros2.git src/sllidar_ros2
```

## Build

From the workspace root:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run

Flash `src/motor_logic/motor_logic.ino` to the ESP first. The sketch talks at 9600 baud and expects a line of the form:

```text
left_pwm,left_dir,right_pwm,right_dir
```

PWM is 0–255. Direction is `1` for forward and `0` for backward. The ESP replies `OK` or `ERR`.

`esp_bridge` opens `/dev/ttyUSB0` at 9600 baud. The wheelbase used for the differential-drive split is 8 inches (0.2032 m), and each wheel speed is scaled so 0.5 m/s maps to PWM 255.

Bring up teleop and the A1 LiDAR:

```bash
ros2 launch robot_bringup start_rc.launch.py
```

`motor_commands` is defined in that launch file and is currently commented out. Run it in another terminal when the ESP is connected:

```bash
ros2 run esp_bridge motor_commands
```

Teleop publishes `geometry_msgs/Twist` on `cmd_vel`. Use the keys printed in the xterm window.

Published debug topics:

- `ros_data` — the serial line sent to the ESP
- `esp_data` — the line read back from the ESP

## Motor pins

Defined in `src/motor_logic/helpers.h`:

| Side | Direction pins | PWM pin |
| --- | --- | --- |
| Left | IN3 = 16, IN4 = 4 | ENB = 25 |
| Right | IN1 = 5, IN2 = 17 | ENA = 26 |
