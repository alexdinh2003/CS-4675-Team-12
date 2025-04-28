import React from "react";
import { useNavigate } from "react-router-dom";

const HomeScreen: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
      <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
        <h1 className="text-3xl font-bold">Welcome to P2P Home Rentals</h1>
        <div className="mt-6 flex flex-col gap-4">
          <button
            className="w-full py-2 !bg-blue-500 text-white rounded-md hover:!bg-blue-600"
            onClick={() => navigate("/login", { state: { userType: "host" } })}
          >
            Enter as Host
          </button>
            <button
            className="w-full py-2 !bg-green-500 text-white rounded-md hover:!bg-blue-600"
            onClick={() => navigate("/login", { state: { userType: "guest" } })}
            >
            Enter as Guest
            </button>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;