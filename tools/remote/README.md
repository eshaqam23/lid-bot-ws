# Remote RViz + teleop for the lid bot

Helper scripts and setup notes for running the lid bot from a laptop over Wi-Fi:
the LiDAR scan shows up in RViz on the laptop, and `teleop_twist_keyboard` on the
laptop drives the car through the Pi.

Nothing in `src/` is changed. These scripts only set environment variables, start the
existing `robot_bringup` launch file and `esp_bridge motor_commands` node, and fix the
USB port order.

```
Laptop (WSL, Jazzy)                              Pi 5 (Ubuntu 24.04, Jazzy)
 teleop ──/cmd_vel──┐                     ┌──> motor_commands ──USB serial──> ESP ──> motors
                    │   ROS 2 DDS (UDP)   │
 RViz <───/scan─────┘   ports 7400-7500   └─── sllidar_node <──USB── RPLIDAR A1
```

Tested 2026-11-13 on VT Open WiFi: `/scan` at ~7.5 Hz on the laptop, and a
`cmd_vel` from the laptop reached the ESP (it replied `OK`).

## Layout

| Path | Goes to | What it does |
| --- | --- | --- |
| `pi/lidbot_env.sh` | Pi `~/` | Sources ROS + workspace, domain 0, `ROS_STATIC_PEERS` = laptop IP |
| `pi/lidbot_start.sh` | Pi `~/` | Starts `motor_commands` and `start_rc.launch.py` in tmux server `lidbot` |
| `pi/lidbot_stop.sh` | Pi `~/` | Stops both |
| `pi/lidbot_fix_ports.sh` | Pi `~/` | Re-binds cp210x so ESP = `/dev/ttyUSB0`, LiDAR = `/dev/ttyUSB1` (run with sudo) |
| `laptop/lidbot_env.sh` | WSL `~/lidbot/` | Fast DDS, domain 0, `ROS_STATIC_PEERS` = Pi IP, starts `ros2 daemon` |
| `laptop/lidbot_rviz.sh` | WSL `~/lidbot/` | Opens RViz with `lidbot.rviz` and software OpenGL |
| `laptop/lidbot_teleop.sh` | WSL `~/lidbot/` | Runs `teleop_twist_keyboard` |
| `laptop/lidbot.rviz` | WSL `~/lidbot/` | Copy of `sllidar_ros2/rviz/sllidar_ros2.rviz` (fixed frame `laser`, LaserScan on `/scan`) |
| `windows/add_wsl_firewall_rule.ps1` | Windows (admin) | Hyper-V firewall rule letting the Pi's DDS traffic into WSL |

The scripts default to Pi `100.64.83.52` and laptop `100.64.217.78`. Override with
`PI_IP=...` (laptop) or `LAPTOP_IP=...` (Pi), or edit the env files. Campus Wi-Fi can
hand out new addresses; when it does, update the env files and both firewall rules.

## Pi setup (once)

Follow the main README first (clone `sllidar_ros2` into `src/`, `colcon build --symlink-install`).
Then:

```bash
sudo apt install xterm python3-serial ros-jazzy-teleop-twist-keyboard ros-jazzy-rviz2
sudo usermod -aG dialout ubuntu
sudo ufw allow proto udp from <LAPTOP_IP> to any port 7400:7500 comment "lidbot ROS2 DDS from laptop"
cp tools/remote/pi/*.sh ~/ && chmod +x ~/lidbot_*.sh
```

- `rviz2` is needed even on a headless Pi: `view_sllidar_a1_launch.py` (included by
  `start_rc.launch.py`) starts an `rviz2` node, and a missing package aborts the whole launch.
- `dialout` is needed to open `/dev/ttyUSB*`. Log out and back in afterwards. A tmux server
  started before the group change will not have it, which is why `lidbot_start.sh` uses its
  own socket (`tmux -L lidbot`).
- The Pi had `ufw` enabled with only SSH allowed, so DDS traffic needs the rule above.

## Laptop setup (once, Windows + WSL Ubuntu 24.04 with ROS 2 Jazzy desktop)

1. WSL mirrored networking, so WSL uses the laptop's Wi-Fi IP. Add to `%UserProfile%\.wslconfig`
   under `[wsl2]`, then run `wsl --shutdown`:
   ```ini
   networkingMode=mirrored
   ```
2. Allow the Pi's DDS traffic into WSL (the Hyper-V firewall blocks inbound by default).
   In an admin PowerShell (edit the Pi IP inside first if it changed):
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\remote\windows\add_wsl_firewall_rule.ps1
   ```
3. In WSL:
   ```bash
   mkdir -p ~/lidbot && cp tools/remote/laptop/* ~/lidbot/ && chmod +x ~/lidbot/*.sh
   sudo apt install ros-jazzy-teleop-twist-keyboard
   ```

## Running

On the Pi:

```bash
sudo ~/lidbot_fix_ports.sh
~/lidbot_start.sh
```

`lidbot_start.sh` passes `serial_port:=/dev/ttyUSB1` to the launch file by default (the LiDAR,
after the port fix). `LIDAR=0` or `MOTORS=0` skips one side. View the logs with
`tmux -L lidbot attach -t lidbot` (Ctrl-b n for the next window, Ctrl-b d to detach).

On the laptop, two WSL terminals:

```bash
~/lidbot/lidbot_rviz.sh
```

```bash
~/lidbot/lidbot_teleop.sh
```

Teleop keys: `i` forward, `,` back, `j`/`l` turn, `k` stop, `q`/`z` faster/slower, `e`/`c` turn speed.

## Known issues

- **Safety: no command timeout.** `motor_commands` and the ESP sketch keep the last PWM until
  a new command arrives. Releasing a key does not stop the car (press `k`), and if Wi-Fi drops
  the car keeps going. Test with the wheels off the ground. Default teleop speed 0.5 m/s maps
  to PWM 255 (full speed); press `z` first.
- **USB port order.** `motor_commands` hardcodes `/dev/ttyUSB0`, and the ESP (CP2102N) and LiDAR
  (CP2102) enumerate in whatever order the kernel finds them. After every boot or replug, run
  `sudo ~/lidbot_fix_ports.sh`.
- **Headless Pi.** `start_rc.launch.py` runs teleop with `prefix='xterm -e'`, and the Slamtec
  view launch starts `rviz2`. Without a display both exit with errors right away; `sllidar_node`
  keeps running. Drive from the laptop instead.
- **Power.** On a Pi 5, a supply that negotiates less than 5 A caps USB peripherals at 600 mA.
  Powered from a laptop USB-C port (3 A, 4.74 V) the Pi browned out and rebooted when the LiDAR
  motor and ESP started together. Use a 5 V / 5 A supply. Check with
  `sudo vcgencmd get_throttled` (want `0x0`) and `sudo vcgencmd pmic_read_adc EXT5V_V`.
- **Multicast.** VT Open WiFi does not pass DDS multicast discovery, hence `ROS_STATIC_PEERS`.
- **WSL quirks.** In mirrored mode the `ros2` CLI hangs if no daemon is running
  (`lidbot_env.sh` starts one). If the RViz window is blank or shows `[WARN:COPY MODE]` in its
  title, run `wsl --shutdown` and reopen it. `lidbot_rviz.sh` sets `LIBGL_ALWAYS_SOFTWARE=1`
  because the WSLg GPU path drew a blank RViz window.
- **sllidar shutdown crash.** `sllidar_node` throws `RCLError ... context is not valid` on
  Ctrl-C. Harmless, upstream behaviour.
