#!/usr/bin/env bash
set -euo pipefail

NUM_USERS=50
NUM_LISTINGS=50
NUM_BOOKINGS=3
BASE_PORT=10000
log_dir="logs"
mkdir -p "$log_dir"

# Get NUM_NODES from user input, default to 12 if not provided
NUM_NODES=${1:-12}

send() {
    echo -e "$1\n" | nc localhost "$2" || echo "[WARN] Failed to send to port $2"
}

wait_for_port() {
    local port=$1
    local retries=20
    local wait_seconds=1
    local count=0

    while ! nc -z localhost "$port"; do
        sleep "$wait_seconds"
        ((count++))
        if [ "$count" -ge "$retries" ]; then
            echo "ERROR: Port $port did not open after $((retries * wait_seconds)) seconds."
            exit 1
        fi
    done
    echo "Port $port is open!"
}

echo "=== Starting DHT Nodes ==="
ports=()
first_node_port=$BASE_PORT

nohup python3 -u Node_DHT.py "$first_node_port" > "$log_dir/node_$first_node_port.log" 2>&1 &
ports+=($first_node_port)

wait_for_port "$first_node_port"

for i in $(seq 1 $((NUM_NODES-1))); do
    port=$((BASE_PORT + i * 200))
    ports+=($port)
    nohup python3 -u Node_DHT.py "$port" "$first_node_port" > "$log_dir/node_$port.log" 2>&1 &
    echo "Began $port"
    sleep 0.5
done
sleep 10
echo "All nodes up!"

echo "=== Registering Users ==="
users=(
'{"host_id":"u1","host_password":"pw_u1","host_name":"Alice"}'
'{"host_id":"u2","host_password":"pw_u2","host_name":"Bob"}'
'{"host_id":"u3","host_password":"pw_u3","host_name":"Carol"}'
'{"host_id":"u4","host_password":"pw_u4","host_name":"Dana"}'
'{"host_id":"u5","host_password":"pw_u5","host_name":"Evan"}'
'{"host_id":"u6","host_password":"pw_u6","host_name":"Fiona"}'
'{"host_id":"u7","host_password":"pw_u7","host_name":"George"}'
'{"host_id":"u8","host_password":"pw_u8","host_name":"Hannah"}'
'{"host_id":"u9","host_password":"pw_u9","host_name":"Ian"}'
'{"host_id":"u10","host_password":"pw_u10","host_name":"Jack"}'
)
user_start=$(date +%s.%N)

pids=()
for i in "${!users[@]}"; do
    user="${users[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"

    (
        send "register_user|$user" "10000"
    ) &
    pids+=($!)  # Save the PID immediately

    if (( i % 20 == 0 && i != 0 )); then
        sleep 1 
    fi
done

# Explicitly wait for each PID and capture its exit code
for pid in "${pids[@]}"; do
    wait "$pid"
    status=$?
    if [ $status -ne 0 ]; then
        echo "[WARN] Registration task PID $pid failed with exit code $status"
    fi
done

user_end=$(date +%s.%N)

echo "Waiting after user registration..."
sleep 2

listings=()
for i in $(seq 1 $NUM_LISTINGS); do
    user_id="u$(( (i % NUM_USERS) + 1 ))"
    listings+=("{\"id\":\"l$i\",\"title\":\"Listing$i\",\"host_id\":\"$user_id\",\"host_name\":\"User${user_id#u}\",\"host_password\":\"pw_${user_id#u}\",\"location\":\"City$((i%3))\",\"latitude\":40.0,\"longitude\":-70.0,\"room_type\":\"Room\",\"price\":$((50 + i)),\"minimum_nights\":1,\"number_of_reviews\":0,\"last_review\":\"2025-01-01\",\"reviews_per_month\":0.1,\"calculated_host_listings_count\":1,\"availability_365\":300,\"zipcode\":$((10000 + i % 3))}")
done


echo
echo "=== Adding Listings ==="
listing_start=$(date +%s.%N)
pids=()
for i in "${!listings[@]}"; do
    listing="${listings[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    (
        echo "Adding listing $listing to $port"
        send "add_listing|$listing" "$port"
    ) &
    pids+=($!)  # Save the PID immediately
    # Control the flood: wait every N background jobs
    if (( i % 20 == 0 && i != 0 )); then
        echo "Sleeping 5 sec, $i completed"
        sleep 1
    fi
done

# Explicitly wait for each PID and capture its exit code
for pid in "${pids[@]}"; do
    wait "$pid"
    status=$?
    if [ $status -ne 0 ]; then
        echo "[WARN] Registration task PID $pid failed with exit code $status"
    fi
done


echo "SETUP COMPLETE!"