#!/bin/bash
source ~/lidbot/lidbot_env.sh
# WSLg GPU (d3d12) path leaves the RViz window blank; software OpenGL renders reliably.
export LIBGL_ALWAYS_SOFTWARE=1
exec rviz2 -d ~/lidbot/lidbot.rviz
