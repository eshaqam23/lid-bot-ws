#!/bin/bash
for w in launch motors; do tmux -L lidbot send-keys -t lidbot:$w C-c 2>/dev/null; done
sleep 3; tmux -L lidbot kill-server 2>/dev/null; echo stopped
