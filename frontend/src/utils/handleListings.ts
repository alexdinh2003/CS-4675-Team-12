import { handleAddressEnter } from "./google-maps";

export const getListingsByLocation = async (addressInfo: { city: string; postal_code: string; latitude: number; longitude: number } | null) => {
  if (!addressInfo) {
      return null;
  }

  // Construct the query parameters
  const queryParams = new URLSearchParams({
      city: addressInfo.city,
      postal_code: addressInfo.postal_code,
      latitude: addressInfo.latitude.toString(),
      longitude: addressInfo.longitude.toString(),
  });

  const apiUrl = `http://localhost:5000/api/get-listings-by-location?${queryParams.toString()}`;

  try {
      const res = await fetch(apiUrl, {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json',
          },
      });

      const result = await res.json();
      if (res.ok) {
          console.log("Listings fetched successfully:", result);
          return result;
      } else {
          console.log("Error fetching listings:", result.error);
          return null;
      }
  } catch (error) {
      console.error("Error:", error);
      return null;
  }
};

export const enterListing = async (listingData: { listingName: string, address: string, hostName: string, roomType: string, minimumNights: string } | null) => {
    if (!listingData) {
        return null;
    }

    //TODO: Find out how to do ID generation in meeting
    const id = 1000
    const addressInfo = await handleAddressEnter(listingData.address);
    const message = { id: id, ...listingData, ...addressInfo };

    const apiUrl = 'http://localhost:5000/api/add-listing';

    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
      });

      const result = await res.json();

      if (res.ok) {
        console.log("Listing entered successfully:", result);
      } else {
        console.log("Error entering listing:", result.error);
      }
    } catch (error) {
      console.error("Error:", error);
    }
};

export const requestMyListings = () => {

    //This is where we can fetch the host's listings
    //Return dummy data for now.
    const listing1 = {"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200}
    const listing2 = {"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150}
    const listing3 = {"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300}

    return [listing1, listing2, listing3];
};