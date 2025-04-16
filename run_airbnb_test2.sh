#!/usr/bin/env bash

set -euo pipefail

# Node ports (ensure these match your Node_DHT.py configuration)
port1=9000
port2=9200
port3=9300
log_dir="logs"

mkdir -p "$log_dir"

echo "=== Starting nodes ==="
nohup python3 -u Node_DHT.py $port1              > "$log_dir/node1.log" 2>&1 &
sleep 1
nohup python3 -u Node_DHT.py $port2 $port1           > "$log_dir/node2.log" 2>&1 &
sleep 1
nohup python3 -u Node_DHT.py $port3 $port1           > "$log_dir/node3.log" 2>&1 &
sleep 1

# Helper function to send socket messages via netcat
send() {
    # $1 is the message, $2 is the port to send to.
    echo -e "$1\n" | nc localhost "$2"
    sleep 0.2
}

# ========== DEFINE 10 LISTINGS ==========
# Modify the listings so that multiple listings share the same city and zipcode.
# For example:
# - Listings l1, l4, l7 use "Seattle"/98101
# - Listings l2, l5, l8 use "New York"/10001
# - Listings l3, l6, l9, l10 use "San Francisco"/94121

listings=(
'{"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200,"zipcode":98101}'
'{"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150,"zipcode":10001}'
'{"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300,"zipcode":94121}'
'{"id":"l4","title":"Seattle Downtown Condo","host_id":"u4","host_name":"Dana","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Entire home","price":150,"minimum_nights":2,"number_of_reviews":10,"last_review":"2023-03-10","reviews_per_month":0.5,"calculated_host_listings_count":1,"availability_365":180,"zipcode":98101}'
'{"id":"l5","title":"NYC Loft","host_id":"u5","host_name":"Evan","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Loft","price":120,"minimum_nights":2,"number_of_reviews":18,"last_review":"2023-01-20","reviews_per_month":0.6,"calculated_host_listings_count":2,"availability_365":220,"zipcode":10001}'
'{"id":"l6","title":"SF Modern Flat","host_id":"u6","host_name":"Fiona","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Apartment","price":130,"minimum_nights":2,"number_of_reviews":25,"last_review":"2023-04-01","reviews_per_month":0.8,"calculated_host_listings_count":4,"availability_365":160,"zipcode":94121}'
'{"id":"l7","title":"Seattle Loft","host_id":"u7","host_name":"George","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Loft","price":140,"minimum_nights":3,"number_of_reviews":22,"last_review":"2023-02-28","reviews_per_month":0.9,"calculated_host_listings_count":3,"availability_365":210,"zipcode":98101}'
'{"id":"l8","title":"NYC Studio","host_id":"u8","host_name":"Hannah","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Studio","price":90,"minimum_nights":1,"number_of_reviews":12,"last_review":"2023-03-05","reviews_per_month":0.4,"calculated_host_listings_count":1,"availability_365":190,"zipcode":10001}'
'{"id":"l9","title":"SF Downtown Cabin","host_id":"u9","host_name":"Ian","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cabin","price":110,"minimum_nights":2,"number_of_reviews":15,"last_review":"2023-01-15","reviews_per_month":0.5,"calculated_host_listings_count":2,"availability_365":170,"zipcode":94121}'
'{"id":"l10","title":"SF Cozy Cottage","host_id":"u10","host_name":"Jack","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cottage","price":95,"minimum_nights":1,"number_of_reviews":7,"last_review":"2023-04-01","reviews_per_month":0.2,"calculated_host_listings_count":1,"availability_365":150,"zipcode":94121}'
'{"id":"l11","title":"SF Cozy Cottage 2","host_id":"u10","host_name":"Jack","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cottage","price":95,"minimum_nights":1,"number_of_reviews":7,"last_review":"2023-04-01","reviews_per_month":0.2,"calculated_host_listings_count":1,"availability_365":150,"zipcode":94121}'
)

user=(
'{"host_id":"u1","host_password":"u1_pass","host_name":"Alice", listing="l1"}'
'{"host_id":"u2","host_password":"u2_pass", "host_name":"Bob", listing="l2"}'
'{"host_id":"u3","host_name":"Carol","host_password":"u3_pass",  listing="l3"}'
'{"host_id":"u4","host_name":"Dana","host_password":"u4_pass",  listing="l4"}'
'{"host_id":"u5","host_name":"Evan","host_password":"u5_pass",  listing="l5"}'
'{"host_id":"u6","host_name":"Fiona","host_password":"u6_pass",  listing="l6"}'
'{"host_id":"u7","host_name":"George","host_password":"u7_pass",  listing="l7"}'
'{"host_id":"u8","host_name":"Hannah","host_password":"u8_pass",  listing="l8"}'
'{"host_id":"u9","host_name":"Ian","host_password":"u9_pass", listing="l9"}'
'{"host_id":"u10","host_name":"Jack","host_password":"u10_pass",  listing="l10"}'
'{"host_id":"u10","host_name":"Jack","host_password":"u10_pass",  listing="l11"}'
)



echo "=== Adding 10 listings using a loop ==="
# We'll round-robin through 3 ports
ports=($port1 $port2 $port3)
for i in "${!listings[@]}"; do
    listing="${listings[$i]}"
    port="${ports[$(( i % ${#ports[@]} ))]}"
    listing_id=$(echo "$listing" | jq -r '.id')
    echo "Adding listing $listing_id on port $port"
    send "add_listing|$listing" "$port"

    echo "Querying added city"

    response=$(send "get_listing_by_id|$listing_id" "$port")
    echo "Resp: $response"
done

# ========== QUERY BY CITY: For each individual city ==========
echo
echo "=== Individual city queries ==="
# We assume the following cities based on our listings.
cities=("Seattle" "New York" "San Francisco")
for city in "${cities[@]}"; do
    echo
    echo "Query for city: $city"
    # send query to one of the nodes (using port1 as example)
    response=$(send "get_listings_by_city|$city" $port2)
    echo "Response: $response"
done

# ========== QUERY BY ZIPCODE: For each individual zipcode ==========
echo
echo "=== Individual zipcode queries ==="
# Based on our listings:
zips=(98101 10001 94121)
for zip in "${zips[@]}"; do
    echo
    echo "Query for zipcode: $zip"
    # send query to one of the nodes (using port2 as example)
    response=$(send "get_listings_by_zip|$zip" $port1)
    echo "Response: $response"
done






# ========== TEARDOWN ==========
echo
echo "=== Tearing down nodes ==="
pkill -f Node_DHT.py || true
sleep 1
echo "✅ Test complete. Logs available in $log_dir/"
