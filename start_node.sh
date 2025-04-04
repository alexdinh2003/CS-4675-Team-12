#!/bin/bash

# ========= CONFIG ========= #
port1=9000
port2=9200
port3=9300
log_dir="logs"
sleep_time=2

# Listings to add (you can expand this later or load from a file)
listing1='{"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200,"zipcode":98101}'

listing2='{"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150,"zipcode":10001}'

listing3='{"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300,"zipcode":94121}'

listing4='{"id":"l4","title":"Beachfront Bungalow","host_id":"u4","host_name":"Dana","location":"Miami","latitude":25.7,"longitude":-80.2,"room_type":"Entire home","price":150,"minimum_nights":2,"number_of_reviews":10,"last_review":"2023-03-10","reviews_per_month":0.5,"calculated_host_listings_count":1,"availability_365":100,"zipcode":33101}'

# ========= FUNCTIONS ========= #
send() {
    echo -e "$1\n" | nc localhost $2
    sleep 0.5
}

# ========= START NODES ========= #
mkdir -p $log_dir
echo "🔄 Starting nodes..."

nohup python3 Node_DHT.py $port1 > $log_dir/node1.log 2>&1 &
sleep $sleep_time

nohup python3 Node_DHT.py $port2 $port1 > $log_dir/node2.log 2>&1 &
sleep $sleep_time

nohup python3 Node_DHT.py $port3 $port1 > $log_dir/node3.log 2>&1 &
sleep $sleep_time

echo "✅ Nodes started: $port1, $port2, $port3"

# ========= INSERT LISTINGS ========= #
echo "📦 Adding listings to DHT..."
send "add_listing|$listing1" $port1
send "add_listing|$listing2" $port2
send "add_listing|$listing3" $port3
send "add_listing|$listing4" $port1

echo "✅ Listings added. You can now run your client and connect to one of the ports."

