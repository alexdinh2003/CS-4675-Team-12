//import { handleAddressEnter } from "./google-maps";
export const requestHashes = (addressInfo: { city: string; postal_code: string; latitude: number; longitude: number } | null) => {
    if (!addressInfo) {
        return null;
    }

    //const { city, postal_code, latitude, longitude } = addressInfo;

    //This is where we can send request to get enterListinges with the same city and postal code.
    //Will also call to get corresponding data here instead of returning the following dummy data.

    const listing1 = {"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200}
    const listing2 = {"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150}
    const listing3 = {"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300}

    return [listing1, listing2, listing3];
};

export const enterListing = async (listingData: { listingName: string, address: string, hostName: string, roomType: string, minimumNights: string } | null) => {
    if (!listingData) {
        return null;
    }

    // Format the listing data into the required string format
    //const listingString = `add_listing|${JSON.stringify(listingData)}`;
};

export const requestMyListings = () => {

    //This is where we can fetch the host's listings
    //Return dummy data for now.
    const listing1 = {"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200}
    const listing2 = {"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150}
    const listing3 = {"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300}

    return [listing1, listing2, listing3];
};