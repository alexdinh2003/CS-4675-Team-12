import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { enterListing, loginUser } from "../utils/handle-apis";

const CreateListing: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const user = location.state?.user;

    const [formValues, setFormValues] = useState({
        title: "",
        address: "",
        price: "",
        room_type: "",
        minimum_nights: "",
        host_name: user.host_name,
    });

    const [images, setImages] = useState<File[]>([]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormValues((prevValues) => ({
            ...prevValues,
            [name]: value,
        }));
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setImages(Array.from(e.target.files));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        console.log("Form submitted:", formValues);

        // Send form data as JSON
        const formPayload = {
            host_id: user.host_id,
            host_password: user.password_hash,
            ...formValues,
        };

        console.log("Form Payload:", formPayload);

        console.log("Images Payload:", images);

        await enterListing(formPayload, images);

        const result = await loginUser({
            id: user.host_id,
            password_hash: user.password_hash,
        });
        navigate("/host", { state: { user: result } });
    };

    return (
        <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
            <button
                onClick={() => navigate("/host", { state: { user } })}
                className="absolute top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
            >
                Back
            </button>
            <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
                <h1 className="text-3xl font-bold">Create a New Listing</h1>
                <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
                    <div>
                        <label
                            htmlFor="title"
                            className="block text-left font-medium"
                        >
                            Listing Name
                        </label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formValues.title}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter listing name"
                        />
                    </div>
                    <div>
                        <label
                            htmlFor="address"
                            className="block text-left font-medium"
                        >
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
                        <label
                            htmlFor="price"
                            className="block text-left font-medium"
                        >
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
                        <label
                            htmlFor="roomType"
                            className="block text-left font-medium"
                        >
                            Room Type
                        </label>
                        <input
                            type="text"
                            id="room_type"
                            name="room_type"
                            value={formValues.room_type}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter room type"
                        />
                    </div>
                    <div>
                        <label
                            htmlFor="minimum_nights"
                            className="block text-left font-medium"
                        >
                            Minimum Nights
                        </label>
                        <input
                            type="number"
                            id="minimum_nights"
                            name="minimum_nights"
                            value={formValues.minimum_nights}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter minimum nights"
                        />
                    </div>
                    <div>
                        <label
                            htmlFor="images"
                            className="block text-left font-medium"
                        >
                            Upload Images
                        </label>
                        <input
                            type="file"
                            id="images"
                            name="images"
                            multiple
                            onChange={handleImageChange}
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
