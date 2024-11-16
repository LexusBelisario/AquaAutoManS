import React, { useState } from "react";

import catfishWP from "../images/catfishWallpaper.png";
import { useNavigate } from "react-router-dom";

export default function Login({ setAuth }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (username === "admin" && password === "admin") {
      setAuth(true);
      navigate("/main");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="grid md:grid-cols-2 items-center gap-4 max-w-6xl w-full p-4 m-4 shadow-md rounded-md bg-white">
        <div className="w-full p-6">
          <form onSubmit={handleSubmit}>
            <div className="mb-12">
              <h3 className="text-gray-800 text-3xl font-extrabold">Sign in</h3>
              <p className="text-sm mt-4 text-gray-800">
                Don't have an account?{" "}
                <a
                  href="#"
                  className="text-blue-600 font-semibold hover:underline ml-1"
                >
                  Register here
                </a>
              </p>
            </div>
            <div>
              <label className="text-gray-800 text-xs block mb-2">
                Username
              </label>
              <div className="relative flex items-center">
                <input
                  name="username"
                  type="text"
                  required
                  className="w-full text-gray-800 text-sm border-b border-gray-300 focus:border-blue-600 px-2 py-3 outline-none"
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>
            <div className="mt-8">
              <label className="text-gray-800 text-xs block mb-2">
                Password
              </label>
              <div className="relative flex items-center">
                <input
                  name="password"
                  type="password"
                  required
                  className="w-full text-gray-800 text-sm border-b border-gray-300 focus:border-blue-600 px-2 py-3 outline-none"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-4 mt-6">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-3 text-sm text-gray-800"
                >
                  Remember me
                </label>
              </div>
              <div>
                <a
                  href="#"
                  className="text-blue-600 font-semibold text-sm hover:underline"
                >
                  Forgot Password?
                </a>
              </div>
            </div>
            <div className="mt-12">
              <button
                type="submit"
                className="w-full shadow-xl py-2.5 px-4 text-sm rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-all duration-300"
              >
                Sign in
              </button>
            </div>
          </form>
        </div>
        <div className="flex-1 bg-[#342c5c] text-center hidden lg:flex rounded-b-lg rounded-t-lg overflow-hidden">
          <img
            src={catfishWP}
            alt="Catfish Wallpaper"
            className="w-full h-4/5 object-cover"
          />
        </div>
      </div>
    </div>
  );
}
