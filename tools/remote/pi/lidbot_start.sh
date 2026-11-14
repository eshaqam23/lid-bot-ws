#!/bin/bash
# Starts repo launch file (lidar) and repo motor_commands (ESP) in tmux server "lidbot".
# LIDAR=0 skips lidar, MOTORS=0 skips motors. Extra args go to ros2 launch.
# motor_commands (repo code) always opens /dev/ttyUSB0 -> run: sudo ~/lidbot_fix_ports.sh first.
tmux -L lidbot kill-server 2>/dev/null; sleep 1
tmux -L lidbot new-session -d -s lidbot -n shell "bash"
if [ "${MOTORS:-1}" = 1 ]; then
  tmux -L lidbot new-window -t lidbot -n motors "bash -c \"source ~/lidbot_env.sh; ros2 run esp_bridge motor_commands; exec bash\""
fi
if [ "${LIDAR:-1}" = 1 ]; then
  tmux -L lidbot new-window -t lidbot -n launch "bash -c \"source ~/lidbot_env.sh; unset DISPLAY; ros2 launch robot_bringup start_rc.launch.py ${*:-serial_port:=/dev/ttyUSB1}; exec bash\""
fi
echo "started (view: tmux -L lidbot attach -t lidbot   next window: Ctrl-b n   detach: Ctrl-b d   stop: ~/lidbot_stop.sh)"
