import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SHA256 from "crypto-js/sha256";
import { createAccount, loginUser } from "../utils/handle-apis";

const LoginScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { userType } = location.state as { userType: string };
  const [login, setLogin] = useState(false);
  const [create, setCreate] = useState(false);

  return (
    (!login && !create ? (
    <>
        <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
        <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
            <div className="mt-6 flex flex-col gap-4">
            <button
                className="w-full py-2 !bg-blue-500 text-white rounded-md hover:!bg-blue-600"
                onClick={() => setLogin(true)}
            >
                Login
            </button>
                <button
                className="w-full py-2 !bg-green-500 text-white rounded-md hover:!bg-blue-600"
                onClick={() => setCreate(true)}
                >
                Create Account
                </button>
            </div>
        </div>
        </div>
    </>
    ) : (
      (create ? (
        <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
            <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
                <h2 className="text-2xl font-bold mb-4">Create Account</h2>
                <form
                    onSubmit={async (e) => {
                        e.preventDefault();
                        const form = e.target as HTMLFormElement;
                        const id = (form.elements.namedItem("id") as HTMLInputElement).value;
                        const password = (form.elements.namedItem("password") as HTMLInputElement).value;
                        const name = (form.elements.namedItem("name") as HTMLInputElement).value;
                        const hashedPassword = SHA256(password).toString();

                        const user = { host_id: id, host_password: hashedPassword, host_name: name};
                        const response = await createAccount(user);

                        if (response) {
                            console.log("userType: " + userType)
                            navigate(`/${userType}`, { state: { user: response } });
                        }

                    }}
                >
                    <div className="mb-4">
                        <label htmlFor="name" className="block text-left font-medium mb-2">
                            Name
                        </label>
                        <input
                            type="text"
                            id="name"
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter Name"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="id" className="block text-left font-medium mb-2">
                            User ID
                        </label>
                        <input
                            type="text"
                            id="id"
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter User ID"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="password" className="block text-left font-medium mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter Password"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full py-2 !bg-green-500 text-white rounded-md hover:!bg-green-600"
                    >
                        Submit
                    </button>
                </form>
                <button
                    className="mt-4 w-full py-2 !bg-gray-500 text-white rounded-md hover:!bg-gray-600"
                    onClick={() => setCreate(false)}
                >
                    Back
                </button>
            </div>
        </div>
    ) : (
        <div className="w-screen h-screen flex justify-center items-center bg-gray-600">
            <div className="w-full max-w-4xl bg-white p-8 rounded-lg shadow-md text-center text-black">
                <h2 className="text-2xl font-bold mb-4">Login</h2>
                <form
                    onSubmit={async (e) => {
                        e.preventDefault();
                        const form = e.target as HTMLFormElement;
                        const id = (form.elements.namedItem("id") as HTMLInputElement).value;
                        const password = (form.elements.namedItem("password") as HTMLInputElement).value;
                        const hashedPassword = SHA256(password).toString();

                        const user = { id: id, password_hash: hashedPassword };
                        const response = await loginUser(user);
                        if (response) {
                            navigate(`/${userType}`, { state: { user: response } });
                        } else {
                            alert("Invalid credentials. Please try again.");
                        }
                    }}
                >
                    <div className="mb-4">
                        <label htmlFor="id" className="block text-left font-medium mb-2">
                            User ID
                        </label>
                        <input
                            type="text"
                            id="id"
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter User ID"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="password" className="block text-left font-medium mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter Password"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full py-2 !bg-green-500 text-white rounded-md hover:!bg-green-600"
                    >
                        Submit
                    </button>
                </form>
                <button
                    className="mt-4 w-full py-2 !bg-gray-500 text-white rounded-md hover:!bg-gray-600"
                    onClick={() => setLogin(false)}
                >
                    Back
                </button>
            </div>
        </div>
    ))
  )));
};

export default LoginScreen;