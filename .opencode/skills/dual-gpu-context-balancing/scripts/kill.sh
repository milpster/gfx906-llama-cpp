#!/usr/bin/env bash
# Kill any running trial.
pkill -9 -f llama-server 2>/dev/null || true
sleep 1
pgrep -af llama-server || echo "no llama-server running"
