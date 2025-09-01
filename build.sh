#!/bin/bash

BACKEND_DIR="$(pwd)/backend"
FRONTEND_DIR="$(pwd)/frontend"

restart_process() {
    local name=$1
    local cmd=$2
    local dir=$3

    while true; do
        echo "[INFO] Starting $name..."
        cd "$dir" || exit
        # Run the command
        $cmd
        echo "[WARN] $name exited. Restarting in 2 seconds..."
        sleep 2
    done
}

# Run processes in background
restart_process "Backend Server" "python server.py" "$BACKEND_DIR" &
restart_process "Celery Worker" "celery -A celery_workers.compute_worker.celery worker --loglevel=INFO" "$BACKEND_DIR" &
restart_process "Frontend Dev" "npm run dev" "$FRONTEND_DIR" &

# Wait for all background processes
wait
