import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { requestMyListings } from "../utils/hash";

const HostScreen: React.FC = () => {
  const navigate = useNavigate();

  const [listings, setListings] = useState<any[]>([]);
  const [selectedListing, setSelectedListing] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await requestMyListings();
        setListings(response);
      } catch (error) {
        console.error("Failed to fetch listings:", error);
      }
    };

    fetchListings();
  }, []);

  const openModal = (listing: any) => {
    setSelectedListing(listing);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedListing(null);
    setIsModalOpen(false);
  };

  return (
    <div
      className={`w-screen h-screen flex justify-center items-center ${
        isModalOpen ? "backdrop-blur-sm" : ""
      } bg-gray-600`}
    >
      <button
        onClick={() => navigate("/")}
        className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      >
        Back
      </button>
      <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
        <h1 className="text-3xl font-bold">My Listings</h1>
        <div className="mt-6 max-h-96 overflow-y-auto">
          {listings.length > 0 ? (
            listings.map((listing: any, index: number) => (
              <div
                key={index}
                className="p-4 mb-4 border rounded-md shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => openModal(listing)}
              >
                <h2 className="text-xl font-semibold text-black">{listing.title}</h2> {/* Title is now black */}
                <p className="text-gray-700">{listing.description}</p>
                <p className="text-gray-500 text-sm">Price: {listing.price}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No listings available.</p>
          )}
        </div>
        <button
          className="w-full py-2 !bg-blue-500 text-white rounded-md hover:!bg-blue-600"
          onClick={() => navigate("/host/create-listing")}
        >
          Create a New Listing
        </button>
      </div>

      {/* Modal */}
      {isModalOpen && selectedListing && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-10 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <h2 className="text-xl font-semibold text-black">{selectedListing.title}</h2>
            <p className="text-gray-500 mb-2">Price: {selectedListing.price}</p>
            <p className="text-gray-500 mb-2">Location: {selectedListing.location}</p>
            <p className="text-gray-500 mb-2">Host: {selectedListing.host_name}</p>
            <p className="text-gray-500 mb-2">Room Type: {selectedListing.room_type}</p>
            <p className="text-gray-500 mb-2">Minimum Nights: {selectedListing.minimum_nights}</p>
            <button
              onClick={closeModal}
              className="mt-4 bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default HostScreen;