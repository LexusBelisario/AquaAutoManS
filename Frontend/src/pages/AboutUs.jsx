import React from "react";
import { useNavigate } from "react-router-dom";
import image1 from "../images/aboutus-images/aboutus1.jpg";
import image2 from "../images/aboutus-images/aboutus2.jpeg";

const AboutUs = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate("/main"); // Navigates back to the dashboard
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-blue-600 mb-4">
          Automated Aquaculture Management System (AutoAquaManS): Integrating AI
          for Fish Vitality Detection and Real-time Water Quality Monitoring in
          Aquaculture Ponds
        </h1>
        <p className="text-gray-700 text-lg mb-6">
          Our project, the " Automated Aquaculture Management System" was
          created to address the growing need for real-time monitoring and
          management of aquaculture systems. Specifically for Catfishes. The
          system is designed to provide automated tracking of water quality
          parameters such as temperature, pH level, oxygen, and turbidity, while
          also detecting the status of catfishes (alive or dead) in the
          environment.
        </p>
        <p className="text-gray-700 text-lg mb-6">
          The system leverages advanced technologies like Raspberry Pi for
          hardware integration and YOLOv8 for object detection, ensuring
          accurate identification of catfishes and monitoring of water
          conditions. By providing real-time data, it empowers fish farmers to
          take timely actions, improving the health and productivity of their
          aquaculture systems.
        </p>
        <p className="text-gray-700 text-lg mb-6">
          Our motivation behind this project is to help aquaculture farmers
          automate their daily tasks, reduce manual labor, and improve
          efficiency in maintaining healthy conditions for fish farming. With
          increasing demand for sustainable and automated aquaculture solutions,
          we aim to create an innovative, easy-to-use system that benefits the
          industry.
        </p>

        <div className="grid grid-cols-3 gap-4 mt-6">
          <img
            src={image1}
            alt="Project Image 1"
            className="rounded-lg shadow-lg"
          />
          <img
            src={image2}
            alt="Project Image 2"
            className="rounded-lg shadow-lg"
          />
          <img
            src={image1}
            alt="Project Image 3"
            className="rounded-lg shadow-lg"
          />
        </div>

        <button
          onClick={handleBackClick}
          className="mt-8 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default AboutUs;
