import "./App.css";
import React, { useEffect, useState } from "react";

import Navbar from "./mentee/components/Navbar";
import Login from "./mentee/pages/Login";
import Logout from "./mentee/pages/Logout";
import Projects from "./mentee/pages/Projects";
import "./mentee/components/scrollable.css";

import { Routes, Route } from "react-router-dom";

import Register from "./mentee/pages/Register";
import ProjectDetails from "./mentee/pages/ProjectDetails";
import PreferenceForm from "./mentee/pages/PreferenceForm";
import VerifyEmail from "./mentee/pages/VerifyEmail";
import RegisterSuccess from "./mentee/pages/RegisterSuccess";
import ProtectedRoutes from "./mentee/components/ProtectedRoutes";
import LoginRoute from "./mentee/components/LoginRoute";
import PreferenceFormFilled from "./mentee/pages/PreferenceFormFilled";
import api from "./utils/api";
import Wishlist from "./mentee/pages/Wishlist";
import Home from "./mentee/pages/Home";
import MentorPortal from "./mentor/MentorPortal";
import MenteeList from "./mentor/MenteeList";
import LandingPage from "./mentor/LandingPage";
import Form from "./mentor/Form";

export default function App() {
  const [authToken, setAuthToken] = useState(null);

  useEffect(() => {
    // localStorage.removeItem("authToken"); // Clear stored token
    // sessionStorage.removeItem("authToken"); // Clear session storage (if used)
  
    api
      .get(process.env.REACT_APP_BACKEND_URL + "/accounts/isloggedin/")
      .then((res) => {
        console.log(res.data.status);
        setAuthToken(res.data.status === "YES");
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);
  

  if (authToken === null) {
    return (
      <div className="h-screen flex justify-center items-center">
        <div className="flex gap-2">
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="background">
        <Navbar title="SOC" authToken={authToken} />
        <Routes>
          <Route path="/" element={<Home />} />

          {/* Routes for Unauthenticated Users */}
          <Route element={<LoginRoute authToken={authToken} />}>
            <Route path="/register" element={<Register />} />
            <Route path="/registerSuccess" element={<RegisterSuccess />} />
            <Route path="/verify-email/:token" element={<VerifyEmail />} />
            <Route path="/login" element={<Login />} />
          </Route>

          {/* Routes for Authenticated Users */}
          <Route element={<ProtectedRoutes authToken={authToken} />}>
            <Route path="/current_projects" element={<Projects />} />
            <Route
              path="/current_projects/:ProjectId"
              element={<ProjectDetails />}
            />
            <Route path="/wishlist" element={<Wishlist />} />
            <Route path="/PreferenceForm" element={<PreferenceForm />} />
            <Route
              path="/PreferenceFormFilled"
              element={<PreferenceFormFilled />}
            />
            <Route path="/mentor/add-project" element={<Form/>} />
            <Route path="/mentor/home" element={<LandingPage/>} />
            <Route path="/logout" element={<Logout />} />
          </Route>
        </Routes>

        {/* You can enable this section once these components are ready */}
        {/* <div className="containerscrollable">
          <Reviews Name="abc" text="what he has to say" value={0} />
          <Reviews Name="abc" text="what he has to say" value={50} />
          <Reviews Name="cde" text="what he has to say" value={50} />
          <div>
            <button onClick={<Button />}>
              click
            </button>
          </div>
        </div> */}
      </div>
    </>
  );
}
