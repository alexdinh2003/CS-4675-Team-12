#!/usr/bin/env bash

set -euo pipefail

# Ports and logs
port1=9000
port2=9200
port3=9300
log_dir="logs"
mkdir -p "$log_dir"

echo "=== Starting DHT Nodes ==="
nohup python3 -u Node_DHT.py $port1              > "$log_dir/node1.log" 2>&1 &
sleep 1
nohup python3 -u Node_DHT.py $port2 $port1       > "$log_dir/node2.log" 2>&1 &
sleep 1
nohup python3 -u Node_DHT.py $port3 $port1       > "$log_dir/node3.log" 2>&1 &
sleep 1

echo "Waiting for user registration to stabilize..."
sleep 5

send() {
    echo -e "$1\n" | nc localhost "$2"
    sleep 0.2
}

ports=($port1 $port2 $port3)

echo
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

for i in "${!users[@]}"; do
    user="${users[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    send "register_user|$user" "$port"
done

echo "Waiting for user registration to stabilize..."
sleep 5

echo
echo "=== Adding Listings ==="
listings=(
'{"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","host_password":"pw_u1","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200,"zipcode":98101}'
'{"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","host_password":"pw_u2","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150,"zipcode":10001}'
'{"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","host_password":"pw_u3","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300,"zipcode":94121}'
'{"id":"l4","title":"Seattle Downtown Condo","host_id":"u4","host_name":"Dana","host_password":"pw_u4","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Entire home","price":150,"minimum_nights":2,"number_of_reviews":10,"last_review":"2023-03-10","reviews_per_month":0.5,"calculated_host_listings_count":1,"availability_365":180,"zipcode":98101}'
'{"id":"l5","title":"NYC Loft","host_id":"u5","host_name":"Evan","host_password":"pw_u5","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Loft","price":120,"minimum_nights":2,"number_of_reviews":18,"last_review":"2023-01-20","reviews_per_month":0.6,"calculated_host_listings_count":2,"availability_365":220,"zipcode":10001}'
'{"id":"l6","title":"SF Modern Flat","host_id":"u6","host_name":"Fiona","host_password":"pw_u6","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Apartment","price":130,"minimum_nights":2,"number_of_reviews":25,"last_review":"2023-04-01","reviews_per_month":0.8,"calculated_host_listings_count":4,"availability_365":160,"zipcode":94121}'
'{"id":"l7","title":"Seattle Loft","host_id":"u7","host_name":"George","host_password":"pw_u7","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Loft","price":140,"minimum_nights":3,"number_of_reviews":22,"last_review":"2023-02-28","reviews_per_month":0.9,"calculated_host_listings_count":3,"availability_365":210,"zipcode":98101}'
'{"id":"l8","title":"NYC Studio","host_id":"u8","host_name":"Hannah","host_password":"pw_u8","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Studio","price":90,"minimum_nights":1,"number_of_reviews":12,"last_review":"2023-03-05","reviews_per_month":0.4,"calculated_host_listings_count":1,"availability_365":190,"zipcode":10001}'
'{"id":"l9","title":"SF Downtown Cabin","host_id":"u9","host_name":"Ian","host_password":"pw_u9","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cabin","price":110,"minimum_nights":2,"number_of_reviews":15,"last_review":"2023-01-15","reviews_per_month":0.5,"calculated_host_listings_count":2,"availability_365":170,"zipcode":94121}'
'{"id":"l10","title":"SF Cozy Cottage","host_id":"u10","host_name":"Jack","host_password":"pw_u10","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cottage","price":95,"minimum_nights":1,"number_of_reviews":7,"last_review":"2023-04-01","reviews_per_month":0.2,"calculated_host_listings_count":1,"availability_365":150,"zipcode":94121}'
'{"id":"l11","title":"SF Cozy Cottage 2","host_id":"u10","host_name":"Jack","host_password":"pw_u10","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cottage","price":95,"minimum_nights":1,"number_of_reviews":7,"last_review":"2023-04-01","reviews_per_month":0.2,"calculated_host_listings_count":1,"availability_365":150,"zipcode":94121}'
)

for i in "${!listings[@]}"; do
    listing="${listings[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    send "add_listing|$listing" "$port"
done

echo "Waiting for user registration to stabilize..."
sleep 5

echo
echo "=== Creating Bookings ==="
bookings=(
'{"id":"b1","renter_password":"pw_u2","listing_id":"l1","date":"2025-04-20"}'
'{"id":"b2","renter_password":"pw_u3","listing_id":"l2","date":"2025-04-21"}'
'{"id":"b3","renter_password":"pw_u4","listing_id":"l3","date":"2025-04-22"}'
)

for i in "${!bookings[@]}"; do
    booking="${bookings[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    send "book_listing|$booking" "$port"
done

echo "Waiting for user registration to stabilize..."
sleep 5
echo
echo "=== Verifying Users' Currently Renting Lists ==="
for id_pw in "u2|pw_u2" "u3|pw_u3" "u4|pw_u4" "u10|pw_u10"; do
    echo "→ ${id_pw#*|}:"
    send "get_user_info|$id_pw" "$port1"
done
echo "Waiting for user registration to stabilize..."
sleep 10

echo
echo "=== Individual City Queries ==="
cities=("Seattle" "New York" "San Francisco")
for city in "${cities[@]}"; do
    echo
    echo "Query for city: $city"
    send "get_listings_by_city|$city" $port2
done
echo "Waiting for user registration to stabilize..."
sleep 10


echo
echo "=== Individual Zipcode Queries ==="
zips=(98101 10001 94121)
for zip in "${zips[@]}"; do
    echo
    echo "Query for zipcode: $zip"
    send "get_listings_by_zip|$zip" $port1
done
echo "Waiting for user registration to stabilize..."
sleep 5


echo
echo "=== Individual Zipcode Queries ==="
zips=(98101 10001 94121)
for zip in "${zips[@]}"; do
    echo
    echo "Query for zipcode: $zip"
    send "get_listings_by_zip|$zip" $port1
done
echo "Waiting for user registration to stabilize..."
sleep 5


# echo
# echo "=== Tearing Down Nodes ==="
# pkill -f Node_DHT.py || true
# sleep 1
# echo "✅ Test complete. Logs saved to $log_dir/"

