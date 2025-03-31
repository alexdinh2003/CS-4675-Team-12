import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const GuestListings: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { listings } = location.state || { listings: [] };

  const [selectedListing, setSelectedListing] = useState<any>(null); // State for the selected listing
  const [isModalOpen, setIsModalOpen] = useState(false); // State to track if the modal is open

  // Function to open the modal with the selected listing
  const openModal = (listing: any) => {
    setSelectedListing(listing);
    setIsModalOpen(true);
  };

  // Function to close the modal
  const closeModal = () => {
    setSelectedListing(null);
    setIsModalOpen(false);
  };

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
      <button
        onClick={() => navigate("/guest")}
        className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      >
        Back
      </button>
      <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
        <h1 className="text-3xl font-bold">Nearby Listings</h1>
        <div className="mt-6 max-h-96 overflow-y-auto">
          {listings.length > 0 ? (
            listings.map((listing: any, index: number) => (
              <div
                key={index}
                className="p-4 mb-4 border rounded-md shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => openModal(listing)} // Open modal on click
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
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4 text-black">{selectedListing.title}</h2>
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

export default GuestListings;