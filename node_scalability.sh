#!/usr/bin/env bash
set -euo pipefail

NUM_USERS=50
NUM_LISTINGS=50
NUM_NODES=3
NUM_BOOKINGS=1
BASE_PORT=10000
log_dir="logs"
mkdir -p "$log_dir"

send() {
    echo -e "$1\n" | nc localhost "$2" || echo "[WARN] Failed to send to port $2"
    sleep 0.5 
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
    sleep 2 
done

sleep 10 
echo "Nodes stabilized."


users=()
for i in $(seq 1 $NUM_USERS); do
    users+=("{\"host_id\":\"u$i\",\"host_password\":\"pw_u$i\",\"host_name\":\"User$i\"}")
done

echo
echo "=== Registering Users ==="
user_start=$(date +%s.%N)
for i in "${!users[@]}"; do
    user="${users[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    send "register_user|$user" "$port"

    if (( i % 20 == 0 && i != 0 )); then
        sleep 5 
    fi
done
user_end=$(date +%s.%N)

echo "Waiting after user registration..."
sleep 15


listings=()
for i in $(seq 1 $NUM_LISTINGS); do
    user_id="u$(( (i % NUM_USERS) + 1 ))"
    listings+=("{\"id\":\"l$i\",\"title\":\"Listing$i\",\"host_id\":\"$user_id\",\"host_name\":\"User${user_id#u}\",\"host_password\":\"pw_${user_id#u}\",\"location\":\"City$((i%3))\",\"latitude\":40.0,\"longitude\":-70.0,\"room_type\":\"Room\",\"price\":$((50 + i)),\"minimum_nights\":1,\"number_of_reviews\":0,\"last_review\":\"2025-01-01\",\"reviews_per_month\":0.1,\"calculated_host_listings_count\":1,\"availability_365\":300,\"zipcode\":$((10000 + i % 3))}")
done


echo
echo "=== Adding Listings ==="
listing_start=$(date +%s.%N)
for i in "${!listings[@]}"; do
    listing="${listings[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    send "add_listing|$listing" "$port"

    if (( i % 10 == 0 && i != 0 )); then
        sleep 5
    fi
done
listing_end=$(date +%s.%N)

echo "Waiting after listing addition..."
sleep 15


echo
echo "=== Indexing Cities ==="
cities=("City0" "City1" "City2")
index_start=$(date +%s.%N)
for city in "${cities[@]}"; do
    send "get_listings_by_city|$city" "${ports[0]}"
    sleep 1 
done
index_end=$(date +%s.%N)

sleep 10


echo
echo "=== Booking Listings ==="
booking_start=$(date +%s.%N)
for i in $(seq 1 $NUM_BOOKINGS); do
    user_id="u$(( (i % NUM_USERS) + 1 ))"
    listing_id="l$(( (i % NUM_LISTINGS) + 1 ))"
    booking_data="{\"id\":\"$user_id\",\"renter_password\":\"pw_${user_id#u}\",\"listing_id\":\"$listing_id\"}"
    send "book_listing|$booking_data" "${ports[1]}"
    sleep 0.5 
done
booking_end=$(date +%s.%N)

sleep 10


echo
echo "=== Node Storage Info ==="
for port in "${ports[@]}"; do
    echo -n "Node on port $port is storing "
    send "get_storage_info" "$port"
    sleep 0.5
done

sleep 10


total_user_time=$(echo "$user_end - $user_start" | bc)
avg_user_time=$(echo "$total_user_time / $NUM_USERS" | bc -l)

total_listing_time=$(echo "$listing_end - $listing_start" | bc)
avg_listing_time=$(echo "$total_listing_time / $NUM_LISTINGS" | bc -l)

total_index_time=$(echo "$index_end - $index_start" | bc)
avg_index_time=$(echo "$total_index_time / ${#cities[@]}" | bc -l)

total_booking_time=$(echo "$booking_end - $booking_start" | bc)
avg_booking_time=$(echo "$total_booking_time / $NUM_BOOKINGS" | bc -l)


echo
echo "=== Benchmark Results ==="
printf "Total user registration time: %.1f s\n" "$total_user_time"
printf "Avg user registration time:   %.20f s\n" "$avg_user_time"
printf "Total listing addition time:  %.1f s\n" "$total_listing_time"
printf "Avg listing addition time:    %.20f s\n" "$avg_listing_time"
printf "Total indexing time:          %.1f s\n" "$total_index_time"
printf "Avg indexing time:            %.20f s\n" "$avg_index_time"
printf "Total booking time (%d):      %.1f s\n" "$NUM_BOOKINGS" "$total_booking_time"
printf "Avg booking time:             %.20f s\n" "$avg_booking_time"


echo
echo "=== Tearing Down Nodes ==="
pkill -f Node_DHT.py || true
sleep 1
