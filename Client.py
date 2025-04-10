import socket
import json

def send(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message.encode('utf-8'))
    data = sock.recv(4096).decode('utf-8')
    sock.close()
    return data

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
        print("========================")
        choice = input("Your choice: ")

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
            print(send(ip, port, msg))

        elif choice == '2':
            city = input("Enter city name: ").strip()
            msg = f"get_listings_by_location|{city}"
            listing_ids = json.loads(send(ip, port, msg))
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
            print(send(ip, port, msg))

        elif choice == '4':
            listing_id = input("Listing ID: ")
            review = input("Your review: ")
            msg = f"write_review|{listing_id}|{review}"
            print(send(ip, port, msg))

        elif choice == '5':
            listing_id = input("Listing ID: ")
            msg = f"get_reviews|{listing_id}"
            reviews = json.loads(send(ip, port, msg))
            print(f"Reviews for listing {listing_id}:")
            if reviews:
                for r in reviews:
                    print("-", r)
            else:
                print("No reviews yet.")

        elif choice == '6':
            city = input("Enter city name: ").strip()
            zipcode = input("Enter zipcode: ").strip()
            msg = f"get_listings_by_location_zip|{city}|{zipcode}"
            listing_ids = json.loads(send(ip, port, msg))
            print(f"Listings in {city}, {zipcode}:")
            if listing_ids:
                for lid in listing_ids:
                    print("-", lid)
            else:
                print("No listings found for this location and zipcode.")

        elif choice == '7':
            print("Exiting client.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()