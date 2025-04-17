import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { enterListing } from "../utils/handle-apis";

const CreateListing: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = location.state?.user;

  const [formValues, setFormValues] = useState({
    listingName: "",
    address: "",
    price: "",
    roomType: "",
    minimumNights: "",
    hostName: user.host_name,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormValues((prevValues) => ({
      ...prevValues,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form submitted:", formValues);

    console.log(user);
    enterListing({ ...formValues, host_id: user.host_id, host_password: user.password_hash }) ;
    navigate("/host", { state: { user } });
  };


  return (
    <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
      <button
        onClick={() => navigate("/host")}
        className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      >
        Back
      </button>
      <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
        <h1 className="text-3xl font-bold">Create a New Listing</h1>
        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="listingName" className="block text-left font-medium">
              Listing Name
            </label>
            <input
              type="text"
              id="listingName"
              name="listingName"
              value={formValues.listingName}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter listing name"
            />
          </div>
          <div>
            <label htmlFor="address" className="block text-left font-medium">
              Address
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formValues.address}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter address"
            />
          </div>
          <div>
            <label htmlFor="price" className="block text-left font-medium">
              Price
            </label>
            <input
              type="text"
              id="price"
              name="price"
              value={formValues.price}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter Price"
            />
          </div>
          <div>
            <label htmlFor="roomType" className="block text-left font-medium">
              Room Type
            </label>
            <input
              type="text"
              id="roomType"
              name="roomType"
              value={formValues.roomType}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter room type"
            />
          </div>
          <div>
            <label htmlFor="minimumNights" className="block text-left font-medium">
              Minimum Nights
            </label>
            <input
              type="number"
              id="minimumNights"
              name="minimumNights"
              value={formValues.minimumNights}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter minimum nights"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateListing;