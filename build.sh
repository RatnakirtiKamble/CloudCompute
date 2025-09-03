#!/bin/bash

BACKEND_DIR="$(pwd)/backend"
FRONTEND_DIR="$(pwd)/frontend"

# Track child PIDs so we can kill them
PIDS=()

restart_process() {
    local name=$1
    local cmd=$2
    local dir=$3

    while true; do
        echo "[INFO] Starting $name..."
        cd "$dir" || exit
        $cmd &
        pid=$!
        PIDS+=($pid)
        wait $pid || true
        echo "[WARN] $name exited. Restarting in 2 seconds..."
        sleep 2
    done
}

# Kill background jobs on Ctrl+C
cleanup() {
    echo "[INFO] Caught Ctrl+C. Stopping all processes..."
    for pid in "${PIDS[@]}"; do
        kill -9 "$pid" 2>/dev/null || true
    done
    exit 0
}
trap cleanup SIGINT SIGTERM

# Run processes in background
restart_process "Backend Server" "python server.py" "$BACKEND_DIR" &
restart_process "Celery Worker" "celery -A celery_workers.compute_worker.celery worker --loglevel=INFO" "$BACKEND_DIR" &
restart_process "Frontend Dev" "npm run dev" "$FRONTEND_DIR" &

# Wait for all background processes
wait
