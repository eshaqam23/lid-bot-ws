# lid-bot-ws

Minimal ROS 2 workspace skeleton for the lid bot.

## Build

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch lid_bot_skeleton skeleton.launch.py
```

## Full robot bringup (motors + lidar)

```bash
sudo apt install ros-jazzy-rplidar-ros ros-jazzy-teleop-twist-keyboard python3-serial xterm
colcon build --symlink-install
source install/setup.bash
ros2 launch lid_bot_skeleton lid_bot.launch.py teleop:=true
```

- Ports, wheel spacing, and lidar baud live in `src/lid_bot_skeleton/config/params.yaml`.
- Override ports at launch: `motor_port:=/dev/ttyUSB1 lidar_port:=/dev/ttyUSB0`.

## ESP32 firmware

`firmware/lidbot_motor/lidbot_motor.ino` drives the L298N. Flash with Arduino IDE (board: ESP32 Dev Module).
It reads `"<left> <right>\n"` (each -255..255) at 115200 baud and stops the motors if no command arrives for 0.5 s.
Set the pin numbers at the top of the file to match the wiring before flashing.
