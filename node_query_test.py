import socket
import threading
import time
import sys

# Read command-line arguments
if len(sys.argv) != 4:
    print("Usage: python3 node_query_test.py <num_nodes> <requests_per_second> <test_type: city|id|fail|register>")
    sys.exit(1)

NUM_NODES = int(sys.argv[1])
REQUESTS_PER_SECOND = float(sys.argv[2])
TEST_TYPE = sys.argv[3]  # "city", "id", "fail", or "register"

BASE_PORT = 10000
TOTAL_REQUESTS = 30
NUM_LISTINGS = 50
CITIES = ["City0", "City1", "City2"]

ports = [BASE_PORT + i * 200 for i in range(NUM_NODES)]
sleep_time = 1.0 / REQUESTS_PER_SECOND

response_times = []
lock = threading.Lock()

def send_request(city, port, listing_id, bad_listing_id, user_json):
    startTime, endTime = 0, 0
    b = False

    if TEST_TYPE == "city":
        message = f"get_listings_by_city|{city}"
    elif TEST_TYPE == "id":
        message = f"get_listing_by_id|{listing_id}"
    elif TEST_TYPE == "fail":
        message = f"get_listing_by_id|{bad_listing_id}"
    elif TEST_TYPE == "register":
        message = f"register_user|{user_json}"
    else:
        print(f"[ERROR] Unknown test type: {TEST_TYPE}")
        return

    for _ in range(3):
        try:
            startTime = time.time()
            print("Sending message:", message, "to", port)
            with socket.create_connection(("localhost", port), timeout=5) as sock:
                sock.sendall((message + "\n").encode('utf-8'))
                raw = sock.recv(4096)
                msg = raw.decode()
                print(f"Received from {port} for query '{message}': {msg.strip()}")
                b = True
            endTime = time.time()
            break
        except Exception as e:
            print(f"[WARN] Failed to send to port {port}: {e}")
            print("Retrying...")
            time.sleep(5)
    if not b:
        print("Failed to get output after retrying.")

    with lock:
        if b:
            response_times.append(endTime - startTime)

threads = []

for i in range(TOTAL_REQUESTS):
    city = CITIES[i % len(CITIES)]
    port = ports[i % len(ports)]
    listing_id = f"l{(i % NUM_LISTINGS) + 1}"          # good listing like l1, l2, ..., l50
    bad_listing_id = f"l{NUM_LISTINGS + 1000 + i}"      # bad listing like l1050, l1051, l1052...
    user_json = (
        f'{{"host_id":"u{500 + i}","host_password":"pw_u{500 + i}","host_name":"User{500 + i}"}}'
    )

    thread = threading.Thread(target=send_request, args=(city, port, listing_id, bad_listing_id, user_json))
    thread.start()
    threads.append(thread)
    time.sleep(sleep_time)

# Wait for all threads to finish
count = 0
for thread in threads:
    count += 1
    if count % 5 == 0:
        print(count, "completed..")
    thread.join()

# Compute average response time
if response_times:
    average_response_time = sum(response_times) / len(response_times)
    print(f"\n=== Benchmark Result ===")
    print(f"Average {TEST_TYPE} response time: {average_response_time:.6f} seconds")
    print(f"Total successful responses: {len(response_times)} / {TOTAL_REQUESTS}")
else:
    print("No successful responses collected.")
