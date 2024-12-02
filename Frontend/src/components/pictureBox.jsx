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
            style={{
              display: "inline-block",
              marginTop: "10px",
              padding: "10px 20px",
              backgroundColor: "#4CAF50",
              color: "#fff",
              textDecoration: "none",
              borderRadius: "5px",
            }}
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
