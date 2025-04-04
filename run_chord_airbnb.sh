#!/bin/bash

# Node ports
port1=9000
port2=9200
port3=9300
log_dir="logs"

mkdir -p $log_dir

# ========== START NODES ========== #
echo "Starting node on port: $port1"
nohup python3 Node_DHT.py $port1 > $log_dir/node1.log 2>&1 &
sleep 1

echo "Starting node on port: $port2"
nohup python3 Node_DHT.py $port2 $port1 > $log_dir/node2.log 2>&1 &
sleep 2

echo "Starting node on port: $port3"
nohup python3 Node_DHT.py $port3 $port1 > $log_dir/node3.log 2>&1 &
sleep 2

# Helper function to send requests
send() {
    echo -e "$1\n" | nc localhost $2
    sleep 1
}

# ========== ADD LISTINGS ========== #
echo
echo "Adding 3 listings to various ports..."

listing1='{"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200,"zipcode":98101}'

listing2='{"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150,"zipcode":10001}'

listing3='{"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300,"zipcode":94121}'

send "add_listing|$listing1" $port1
send "add_listing|$listing2" $port2
send "add_listing|$listing3" $port3

# ========== SEARCH LISTINGS BY CITY ========== #
echo
echo "Getting listings for Seattle"
send "get_listings_by_location|Seattle" $port2

echo "Getting listings for New York"
send "get_listings_by_location|New York" $port1

echo "Getting listings for San Francisco"
send "get_listings_by_location|San Francisco" $port3

# ========== SEARCH LISTINGS BY CITY + ZIPCODE ========== #
echo
echo "Getting listings for San Francisco, 94121"
send "get_listings_by_location_zip|San Francisco|94121" $port1

echo "Getting listings for New York, 10001"
send "get_listings_by_location_zip|New York|10001" $port2

echo "Getting listings for Seattle, 98101"
send "get_listings_by_location_zip|Seattle|98101" $port3

# ========== BOOK A LISTING ========== #
echo
echo "Booking listing l2"
booking='{"id":"b123","listing_id":"l2","guest":"user_42","date":"2025-04-15"}'
send "book_listing|$booking" $port1

# ========== WRITE REVIEWS ========== #
echo
echo "Writing reviews for listing l2"
send "write_review|l2|Absolutely loved the location!" $port2
send "write_review|l2|Very clean and quiet. Will return!" $port3
send "write_review|l2|Perfect for a NYC trip." $port1

# ========== GET REVIEWS ========== #
echo
echo "Retrieving reviews for listing l2"
send "get_reviews|l2" $port3

# ========== SEARCH FOR A SPECIFIC LISTING ========== #
echo
echo "Searching for listing l3's full record"
send "search_server|listing:l3" $port2

# ========== DELETE A LISTING AND VERIFY REMOVAL ========== #
echo
echo "Deleting listing l3"
send "delete|listing:l3" $port1

echo "Searching for deleted listing l3 (should be NOT FOUND)"
send "search|listing:l3" $port3

# ========== SEARCH REVIEWS FOR DELETED LISTING ========== #
echo
echo "Trying to get reviews for deleted listing l3"
send "get_reviews|l3" $port1

# ========== ADD A 4th LISTING ========== #
echo
echo "Adding a 4th listing (Miami, 33101)"
listing4='{"id":"l4","title":"Beachfront Bungalow","host_id":"u4","host_name":"Dana","location":"Miami","latitude":25.7,"longitude":-80.2,"room_type":"Entire home","price":150,"minimum_nights":2,"number_of_reviews":10,"last_review":"2023-03-10","reviews_per_month":0.5,"calculated_host_listings_count":1,"availability_365":180,"zipcode":33101}'
send "add_listing|$listing4" $port1

echo "Getting listings for Miami"
send "get_listings_by_location|Miami" $port2

echo "Getting listings for Miami, 33101"
send "get_listings_by_location_zip|Miami|33101" $port3

# ========== BOOK NON-EXISTENT LISTING ========== #
echo
echo "Trying to book a listing that doesn't exist"
fake_booking='{"id":"b404","listing_id":"ghost","guest":"phantom_user","date":"2025-10-31"}'
send "book_listing|$fake_booking" $port3

# ========== GET NON-EXISTENT LISTING ========== #
echo
echo "Trying to fetch listings for an unknown city"
send "get_listings_by_location|Atlantis" $port2

# ========== TEARDOWN ========== #
echo
echo "Tearing down all nodes..."
pkill -f Node_DHT.py
sleep 1
echo "✅ Done."

echo
echo "🎉 Test run complete. Logs available in $log_dir/"
