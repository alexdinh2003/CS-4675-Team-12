import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomeScreen from "./screens/HomeScreen";
import HostScreen from "./screens/HostScreen";
import GuestScreen from "./screens/GuestScreen";
import GuestListings from "./screens/GuestListings";
import CreateListing from "./screens/CreateListing";

const App: React.FC = () => {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/host" element={<HostScreen />} />
          <Route path="/guest" element={<GuestScreen />} />
          <Route path="/guest/listings" element={<GuestListings />} />
          <Route path="/host/create-listing" element={<CreateListing />} />
        </Routes>
    </Router>
  );
};

export default App;