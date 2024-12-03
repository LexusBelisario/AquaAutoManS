import React, { useEffect, useState } from "react";

const LatestImage = () => {
  const [imageUrl, setImageUrl] = useState(null);

  useEffect(() => {
    // Fetch the image URL
    fetch("http://127.0.0.1:5000/latest-image")
      .then((response) => {
        if (response.ok) {
          return response.blob();
        } else {
          throw new Error("Failed to fetch image");
        }
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
      })
      .catch((error) => {
        console.error("Error fetching image:", error);
      });
  }, []);

  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold text-black mb-2">
        Latest Captured Image
      </h2>
      {imageUrl ? (
        <div>
          <img
            src={imageUrl}
            alt="Latest Detection"
            style={{
              width: "100%",
              maxWidth: "400px",
              border: "1px solid #ccc",
            }}
          />
          <br />
          <a
            href={imageUrl}
            download="latest-detection.jpg"
            className="text-white bg-gradient-to-r from-cyan-400 via-cyan-500 to-cyan-600 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
          >
            Download Image
          </a>
        </div>
      ) : (
        <p>No image available</p>
      )}
    </div>
  );
};

export default LatestImage;
