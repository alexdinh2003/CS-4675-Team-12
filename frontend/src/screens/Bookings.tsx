import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { requestMyListings } from "../utils/handle-apis";

const Bookings: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = location.state?.user;
  const [listings, setListings] = useState<any[]>([]);
  const [selectedListing, setSelectedListing] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await requestMyListings(user, "guest");
        setListings(response);
      } catch (error) {
        console.error("Failed to fetch listings:", error);
      }
    };

    fetchListings();
  }, []);

  const openModal = (listing: any) => {
    setSelectedListing({
      ...listing,
      currentImageIndex: 0,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedListing(null);
    setIsModalOpen(false);
  };

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
      <button
        onClick={() => navigate("/guest", { state: { user } })}
        className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      >
        Back
      </button>
      <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
        <h1 className="text-3xl font-bold">My Bookings</h1>
        <div className="mt-6 max-h-96 overflow-y-auto">
          {listings.length > 0 ? (
            listings.map((listing: any, index: number) => (
              <div
                key={index}
                className="p-4 mb-4 border rounded-md shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => openModal(listing)}
              >
                <h2 className="text-xl font-semibold text-black">{listing.title}</h2>
                <p className="text-gray-700">{listing.description}</p>
                <p className="text-gray-500 text-sm">Price: {listing.price}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No listings available.</p>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && selectedListing && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-3xl w-full flex">
            {/* Text Info */}
            <div className="flex-1 pr-4">
              <h2 className="text-2xl font-bold mb-4 text-black">{selectedListing.listingName}</h2>
              <p className="text-gray-500 mb-2">Price: {selectedListing.price}</p>
              <p className="text-gray-500 mb-2">Location: {selectedListing.location}</p>
              <p className="text-gray-500 mb-2">Host: {selectedListing.hostName}</p>
              <p className="text-gray-500 mb-2">Room Type: {selectedListing.roomType}</p>
              <p className="text-gray-500 mb-2">Minimum Nights: {selectedListing.minimumNights}</p>
              {/* Close Button */}
              <button
                onClick={closeModal}
                className="text-white px-4 py-2 rounded-md hover:bg-red-600 !bg-red-500"
              >
                Close
              </button>
            </div>

            {/* Image and Controls */}
            <div className="flex-1 flex flex-col items-center relative">
              <div className="relative w-full h-64 overflow-hidden rounded-md">
                {selectedListing.images && selectedListing.images.length > 0 ? (
                  <img
                    src={URL.createObjectURL(
                      selectedListing.images[selectedListing.currentImageIndex || 0]
                    )}
                    alt={`Listing Image ${(selectedListing.currentImageIndex || 0) + 1}`}
                    className="object-cover w-full h-full rounded-md"
                  />
                ) : (
                  <p className="text-gray-500 text-center">No images available</p>
                )}

                {/* Scroll Buttons */}
                {selectedListing.images && selectedListing.images.length > 1 && (
                  <>
                    {/* Previous Button */}
                    <button
                      onClick={() =>
                        setSelectedListing((prev: any) => ({
                          ...prev,
                          currentImageIndex:
                            (prev.currentImageIndex - 1 + prev.images.length) % prev.images.length,
                        }))
                      }
                      className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700"
                    >
                      &#8249; {/* Left Arrow Icon */}
                    </button>

                    {/* Next Button */}
                    <button
                      onClick={() =>
                        setSelectedListing((prev: any) => ({
                          ...prev,
                          currentImageIndex:
                            (prev.currentImageIndex + 1) % prev.images.length,
                        }))
                      }
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gray-800 text-white p-2 rounded-full hover:bg-gray-700"
                    >
                      &#8250; {/* Right Arrow Icon */}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Bookings;
