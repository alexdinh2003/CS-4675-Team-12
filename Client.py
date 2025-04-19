import socket
import json
import time
import hashlib
import numpy as np

m = 7  # must match server

def send(ip, port, message, artificial_delay=0.0):
    """
    Sends a message with an optional artificial delay to simulate network latency.
    Returns (response_str, round_trip_time).
    """
    if artificial_delay > 0:
        time.sleep(artificial_delay)
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message.encode('utf-8'))
    data = sock.recv(4096).decode('utf-8')
    sock.close()
    return data, time.perf_counter() - start


def compute_hash(message: str) -> str:
    """SHA‑256 hash mod 2^m, returned as decimal string."""
    digest = hashlib.sha256(message.encode()).hexdigest()
    return str(int(digest, 16) % (2**m))


def bench_direct_hash(ip, port, listing_hashes):
    """Measure get_listing_by_hash for each hash."""
    times = []
    for h in listing_hashes:
        _, dt = send(ip, port, f"get_listing_by_hash|{h}")
        times.append(dt)
    return times


def bench_attribute_lookup(ip, port, city):
    """
    1) get_listings_by_city to fetch IDs  
    2) for each ID, compute hash and get_listing_by_hash  
    Returns (list_stage_time, per_hash_times_list)
    """
    start0 = time.perf_counter()
    raw, dt0 = send(ip, port, f"get_listings_by_city|{city}")
    ids = json.loads(raw)
    t0 = time.perf_counter() - start0

    times = []
    for listing_id in ids:
        h = compute_hash(f"listing:{listing_id}")
        _, dt = send(ip, port, f"get_listing_by_hash|{h}")
        times.append(dt)
    return t0, times


def measure_latency_sweep(ip, port, delays=None, n=100):
    """
    Runs get_successor ping n times for each artificial delay in delays.
    Prints average, median, and 95th percentile.
    """
    if delays is None:
        delays = [0.0, 0.01, 0.05, 0.1]
    print(f"\n{'Delay(s)':>10} | {'Avg RTT(s)':>10} | {'Median':>7} | {'95th %ile':>10}")
    print('-'*50)
    for d in delays:
        samples = []
        for _ in range(n):
            _, dt = send(ip, port, "get_successor|0", artificial_delay=d)
            samples.append(dt)
        avg = np.mean(samples)
        med = np.median(samples)
        p95 = np.percentile(samples, 95)
        print(f"{d:>10.3f} | {avg:>10.4f} | {med:>7.4f} | {p95:>10.4f}")


def measure_storage_efficiency():
    """
    Prompts user for a listing, then compares raw JSON, marshalled, and key-value sizes.
    """
    print("\nEnter sample listing fields for storage-size comparison:")
    listing = {
        "id": input("Listing ID: "),
        "title": input("Title: "),
        "host_id": input("Host ID: "),
        "host_name": input("Host Name: "),
        "location": input("City/Neighborhood: "),
        "zipcode": input("Zipcode: ")
    }
    raw_json = json.dumps(listing)
    marshalled = repr(raw_json)
    kv_pairs = "|".join(f"{k}={v}" for k, v in listing.items())

    size_json = len(raw_json)
    size_m = len(marshalled)
    size_kv = len(kv_pairs)
    ov_m = (size_m - size_json) / size_json * 100
    ov_kv = (size_kv - size_json) / size_json * 100

    print(f"\nRaw JSON size:      {size_json} bytes")
    print(f"Marshalled size:    {size_m} bytes ({ov_m:.1f}% overhead)")
    print(f"Key-Value size:     {size_kv} bytes ({ov_kv:.1f}% vs JSON)")


def main():
    ip = "127.0.0.1"
    port = int(input("Enter the port number of the node to connect to: "))

    while True:
        print("\n========= MENU =========")
        print("1. Add a Listing")
        print("2. Get Listings by City")
        print("3. Book a Listing")
        print("4. Write a Review")
        print("5. Get Reviews for a Listing")
        print("6. Get Listings by City + Zipcode")
        print("7. Exit")
        print("8. Benchmark Latency (single delay)")
        print("9. Benchmark Retrieval Performance")
        print("10. Benchmark Direct‑vs‑Attribute Retrieval")
        print("11. Benchmark Storage Efficiency")
        print("12. Latency Sweep Evaluation")
        print("========================")

        choice = input("Your choice: ").strip()

        if choice == '1':
            listing = {
                "id": input("Listing ID: "),
                "title": input("Title: "),
                "host_id": input("Host ID: "),
                "host_name": input("Host Name: "),
                "location": input("City/Neighborhood: "),
                "latitude": float(input("Latitude: ")),
                "longitude": float(input("Longitude: ")),
                "room_type": input("Room Type: "),
                "price": float(input("Price per night: ")),
                "minimum_nights": int(input("Minimum nights: ")),
                "number_of_reviews": int(input("Number of reviews: ")),
                "last_review": input("Last review (YYYY-MM-DD): "),
                "reviews_per_month": float(input("Reviews/month: ")),
                "calculated_host_listings_count": int(input("Host's listing count: ")),
                "availability_365": int(input("Availability (days/year): ")),
                "zipcode": int(input("Zipcode: "))
            }
            msg = "add_listing|" + json.dumps(listing)
            resp, dt = send(ip, port, msg)
            print(f"{resp}  (RTT {dt:.4f}s)")

        elif choice == '2':
            city = input("Enter city name: ").strip()
            resp, dt = send(ip, port, f"get_listings_by_city|{city}")
            listing_ids = json.loads(resp)
            print(f"Fetched in {dt:.4f}s → Listings in {city}:")
            if listing_ids:
                print(f"Listings in {city}:")
                for lid in listing_ids:
                    print("-", lid)
            else:
                print(f"No listings found in {city}.")

        elif choice == '3':
            booking = {
                "id": input("Booking ID: "),
                "listing_id": input("Listing ID: "),
                "guest": input("Guest User ID: "),
                "date": input("Date (YYYY-MM-DD): ")
            }
            msg = "book_listing|" + json.dumps(booking)
            resp, dt = send(ip, port, msg)
            print(f"{resp}  (RTT {dt:.4f}s)")

        elif choice == '4':
            listing_id = input("Listing ID: ")
            review = input("Your review: ")
            msg = f"write_review|{listing_id}|{review}"
            resp, dt = send(ip, port, msg)
            print(f"{resp}  (RTT {dt:.4f}s)")

        elif choice == '5':
            listing_id = input("Listing ID: ")
            resp, dt = send(ip, port, f"get_reviews|{listing_id}")
            reviews = json.loads(resp)
            print(f"Fetched in {dt:.4f}s → Reviews for {listing_id}:")
            if reviews:
                for r in reviews:
                    print("-", r)
            else:
                print("No reviews yet.")

        elif choice == '6':
            city = input("Enter city name: ").strip()
            zipcode = input("Enter zipcode: ").strip()
            msg = f"get_listings_by_zip|{zipcode}" if city == "" else f"get_listings_by_city|{city}"
            resp, dt = send(ip, port, msg)
            listing_ids = json.loads(resp)
            print(f"Fetched in {dt:.4f}s → Listings in {city}, {zipcode}:")
            if listing_ids:
                for lid in listing_ids:
                    print("-", lid)
            else:
                print("No listings found for this location and zipcode.")

        elif choice == '7':
            print("Exiting client.")
            break

        elif choice == '8':
            delay = float(input("Enter artificial delay in seconds (e.g. 0.01): "))
            n = int(input("How many pings? "))
            times = []
            for _ in range(n):
                _, d = send(ip, port, "get_successor|0", artificial_delay=delay)
                times.append(d)
            print(f"Avg RTT: {np.mean(times):.4f}s; 95th %ile: {np.percentile(times,95):.4f}s")

        elif choice == '9':
            city = input("Enter city name for retrieval test: ").strip().lower()
            start = time.perf_counter()
            resp, dt0 = send(ip, port, f"get_listings_by_city|{city}")
            ids = json.loads(resp)
            t_list = time.perf_counter() - start
            print(f"List IDs: {len(ids)} in {t_list:.4f}s (RTT {dt0:.4f}s)")
            if not ids:
                print("No listings to fetch.")
                continue
            fetch_times = []
            for lid in ids:
                h = compute_hash(f"listing:{lid}")
                _, d = send(ip, port, f"get_listing_by_hash|{h}")
                fetch_times.append(d)
            print(f"Per‑listing fetch avg: {np.mean(fetch_times):.4f}s; 95th %ile: {np.percentile(fetch_times,95):.4f}s")

        elif choice == '10':
            city = input("City for attribute-lookup test: ").strip().lower()
            raw, _ = send(ip, port, f"get_listings_by_city|{city}")
            try:
                ids = json.loads(raw)
            except json.JSONDecodeError:
                ids = []
            if not ids:
                print(f"No listings found in '{city}'. Cannot benchmark direct vs attribute retrieval.")
                continue
            hashes = [compute_hash(f"listing:{i}") for i in ids]
            direct = bench_direct_hash(ip, port, hashes)
            overhead, per_hash = bench_attribute_lookup(ip, port, city)
            print(f"Direct‑hash avg: {np.mean(direct):.4f}s; 95th %ile: {np.percentile(direct,95):.4f}s")
            print(f"Attribute‑lookup list stage: {overhead:.4f}s")
            print(f"Per‑hash avg: {np.mean(per_hash):.4f}s; 95th %ile: {np.percentile(per_hash,95):.4f}s")

        elif choice == '11':
            measure_storage_efficiency()

        elif choice == '12':
            n = int(input("How many pings per delay? "))
            measure_latency_sweep(ip, port, n=n)

        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
