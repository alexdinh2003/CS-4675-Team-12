import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { handleAddressEnter } from "../utils/google-maps";
import { getListingsByLocation } from "../utils/handleListings";

const GuestScreen: React.FC = () => {
    const navigate = useNavigate();

    const [address, setAddress] = useState("");
    const [addressInfo, setAddressInfo] = useState<any>(null);
    const [listings, setListings] = useState<any[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            console.log("Updated addressInfo:", addressInfo);
            try {
                (document.querySelector('input[type="text"]') as HTMLInputElement).value = "";
                const result = await getListingsByLocation(addressInfo);
                if (result !== undefined && result !== null) {
                    console.log("Listings fetched:", result);
                    setListings(result);
                } else {
                    console.error("No result returned from requestHashes");
                }
            } catch (error) {
                console.error("Error in requestHashes:", error);
            }
        };

        if (addressInfo) {
            fetchData();
        }
    }, [addressInfo]);

    useEffect(() => {
        if (listings.length > 0) {
            navigate("/guest/listings", { state: { listings } });
        }
    }, [listings, navigate]);

    return (
        <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
            <button
                onClick={() => navigate("/")}
                className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
            >
                Back
            </button>
            <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
                <h1 className="text-3xl font-bold">Enter a Nearby Address</h1>
                <div className="mt-4 flex gap-4 items-center justify-center">
                    <input
                        type="text"
                        placeholder="Enter Address"
                        className="w-full max-w-xs p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onChange={(e) => setAddress(e.target.value)}
                    />
                    <button
                        onClick={async () => {
                            try {
                                (document.querySelector('input[type="text"]') as HTMLInputElement).value = "";
                                const result = await handleAddressEnter(address);
                                if (result !== undefined && result !== null) {
                                    setAddressInfo(result);
                                } else {
                                    console.error("No result returned from handleAddressEnter");
                                }
                            } catch (error) {
                                console.error("Error in handleAddressEnter:", error);
                            }
                        }}
                        className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
                    >
                        Enter
                    </button>
                </div>
            </div>
        </div>
    );
};

export default GuestScreen;
