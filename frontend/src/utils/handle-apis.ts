import { handleAddressEnter } from "./google-maps";

let url: string | null = null;
let listings: any[] = [];

const getPeerUrl = async () => {
  //Replace this with actual API call for centralized server API
  //While in testing, frontend_node_backend.py needs to be running
  const frontend_api = 'http://localhost:5001/get-url';

  try {
    const res = await fetch(frontend_api, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const result = await res.json();
    if (res.ok) {
      return result.url;
    } else {
      console.error("Error fetching peer URL:", result.error);
      return null;
    }
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
};

export const enterListing = async (listingData: { host_id: string, host_password: string, listingName: string, address: string, hostName: string, price: string, roomType: string, minimumNights: string } | null, images: File[] | null) => {
  if (!listingData) {
    return null;
  }

  if (!url) {
    const peerUrl = await getPeerUrl();
    url = peerUrl;
  }

  const id = Date.now() + Math.floor(Math.random() * 1000);
  const addressInfo = await handleAddressEnter(listingData.address);
  const message = { id: id, ...listingData, ...addressInfo, images };
  console.log("Message to be sent:", message);

  const apiUrl = `${url}/api/add-listing`;

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
      if (images) {
        for (const image of images) {
          const formData = new FormData();
          formData.append("id", id.toString());
          formData.append("file", image);

          const uploadUrl = `${url}/api/upload-image`;
          const uploadRes = await fetch(uploadUrl, {
            method: "POST",
            body: formData,
          });

          if (uploadRes.ok) {
            console.log("Image uploaded successfully");
          } else {
            const uploadError = await uploadRes.json();
            console.error("Error uploading image:", uploadError.error);
          }
        }
      }
    } else {
      console.log("Error entering listing:", result.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
};

export const requestMyListings = async (user: {currently_renting: string[], host_id: string, host_name: string, owning_listings: string[], password_hash: string}, userType: string) => {

  listings = []
  if (!url) {
    const peerUrl = await getPeerUrl();
    url = peerUrl;
  }

  const array = (userType == "host" ? user.owning_listings : user.currently_renting);
  for (const listing of array) {
    const apiUrl = `${url}/api/get-listing-by-id?id=${listing}`;
    
    try {
      const res = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await res.json();

      if (res.ok) {
        console.log("Listing fetched successfully:", result);
        listings = [...listings, result];
        let result_images = [];
          for (const image of result.images) {
            if (Object.keys(image).length === 0) continue;
            console.log("Image:", image);
            const imageUrl = `${url}/api/get-image/${image}`;
            const imageRes = await fetch(imageUrl, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              },
            });
            console.log("Image response:", imageRes);
            if (imageRes.ok) {
              const imageBlob = await imageRes.blob();
              console.log("Image blob:", imageBlob);
              result_images.push(URL.createObjectURL(imageBlob));
            } else {
              console.error("Error fetching image:", await imageRes.json());
            }
          }
          result.images = result_images;
          console.log("Updated listing with images:", result);
      } else {
        console.log("Error fetching listings:", result.error);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  return listings;
}

export const getListingsByLocation = async (addressInfo: { location: string; zipcode: string; latitude: number; longitude: number } | null) => {
  if (!addressInfo) {
      return null;
  }

  if (!url) {
    const peerUrl = await getPeerUrl();
    url = peerUrl;
  }

  //Empty the existing listings
  listings = [];

  let queryParams = {};
  if (addressInfo.zipcode) {
    queryParams = new URLSearchParams({
      zipcode: addressInfo.zipcode,
    });
  } else {
    queryParams = new URLSearchParams({
      city: addressInfo.location,
    });
  }

  const apiUrl = `${url}/api/get-listings?${queryParams.toString()}`;

  try {
      const res = await fetch(apiUrl, {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json',
          },
      });

      const result = await res.json();
      if (res.ok) {
          for (const listing of result) {
            const apiUrl = `${url}/api/get-listing-by-id?id=${listing}`;
            
            try {
              const res = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                  'Content-Type': 'application/json',
                },
              });
        
              const result = await res.json();
        
              if (res.ok) {
                console.log("Listing fetched successfully:", result);
                listings = [...listings, result];
                let result_images = [];
                  for (const image of result.images) {
                    if (Object.keys(image).length === 0) continue;
                    console.log("Image:", image);
                    const imageUrl = `${url}/api/get-image/${image}`;
                    const imageRes = await fetch(imageUrl, {
                      method: 'GET',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                    });
                    console.log("Image response:", imageRes);
                    if (imageRes.ok) {
                      const imageBlob = await imageRes.blob();
                      console.log("Image blob:", imageBlob);
                      result_images.push(URL.createObjectURL(imageBlob));
                    } else {
                      console.error("Error fetching image:", await imageRes.json());
                    }
                  }
                  result.images = result_images;
                  console.log("Updated listing with images:", result);
              } else {
                console.log("Error fetching listings:", result.error);
              }
            } catch (error) {
              console.error("Error:", error);
            }
          }
        
          return listings;
      } else {
          console.log("Error fetching listings:", result.error);
          return null;
      }
  } catch (error) {
      console.error("Error:", error);
      return null;
  }
};

export async function createAccount(user: { host_id: string; host_password: string, host_name: string }) {

  try {
      if (!url) {
          const peerUrl = await getPeerUrl();
          url = peerUrl;
      }

      // Make a POST request to the Flask backend to create an account
      const response = await fetch(`${url}/api/register-user`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(user),
      });

      if (!response.ok) {
        throw new Error(`Error logging in: ${response.statusText}`);
      } else {
        const result = await response.json();
        return result;
      }
  } catch (error) {
      console.error('Error creating account:', error);
      throw error;
  }
}

export async function loginUser(user: { id: string; password_hash: string; }) {
  
  try {

      if (!url) {
          const peerUrl = await getPeerUrl();
          url = peerUrl;
      }

      // Construct the query parameters
      const queryParams = new URLSearchParams({
          id: user.id,
          password_hash: user.password_hash,
      });

      // Make a GET request to the Flask backend to login
      const response = await fetch(`${url}/api/get-user-info?${queryParams.toString()}`, {
          method: 'GET',
          headers: {
          'Content-Type': 'application/json',
          },
      });

      if (!response.ok) {
          throw new Error(`Error logging in: ${response.statusText}`);
      } else {
        console.log("Login successful:", response);
        const result = await response.json();
        return result;
      }
  } catch (error) {
      console.error('Error logging in:', error);
      throw error;
  }
}

export const bookListing = async (id: string, renter_password: string, listing_id: string) => {
  if (!url) {
    const peerUrl = await getPeerUrl();
    url = peerUrl;
  }

  const apiUrl = `${url}/api/book-listing`;
  const message = {id: id, renter_password: renter_password, listing_id: listing_id};

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
      console.log("Booking successful:", result);
      return result;
    } else {
      console.log("Error booking listing:", result.error);
      return null;
    }
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
};