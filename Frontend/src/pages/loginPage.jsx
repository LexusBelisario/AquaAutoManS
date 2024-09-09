import React, { useState } from "react";
import projectLogo from "../images/mainLogo.svg";
import catfishWP from "../images/catfishWallpaper.svg";
import { useNavigate } from "react-router-dom";

export default function Login({ setAuth }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Replace this with your actual authentication logic
    if (username === "admin" && password === "admin") {
      setAuth(true);
      navigate("/main");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex justify-center">
      <div className="max-w-screen-xl m-0 sm:m-10 bg-white shadow sm:rounded-lg flex justify-center flex-1">
        <div className="lg:w-1/2 xl:w-5/12 p-6 sm:p-12">
          <div>
            <img src={projectLogo} alt="Project Logo" className="w-mx-auto" />
          </div>
          <div className="mt-12 flex flex-col items-center">
            <form className="w-full flex-1" onSubmit={handleSubmit}>
              <div className="mx-auto max-w-xs">
                <input
                  className="w-full px-8 py-4 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="mx-auto max-w-xs">
                <input
                  type="password"
                  className="my-6 w-full px-8 py-4 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="submit"
                  className="tracking-wide font-semibold bg-green-400 text-white-500 w-full py-4 rounded-lg hover:bg-green-700 transition-all duration-300 ease-in-out flex items-center justify-center focus:shadow-outline focus:outline-none"
                >
                  Log In
                </button>
              </div>
            </form>
          </div>
        </div>
        <div className="flex-1 bg-green-100 text-center hidden lg:flex rounded-br-lg rounded-tr-lg ">
          <img
            src={catfishWP}
            alt="Catfish Wallpaper"
            className="w-full h-full object-cover rounded-br-lg rounded-tr-lg"
          />
        </div>
      </div>
    </div>
  );
}
