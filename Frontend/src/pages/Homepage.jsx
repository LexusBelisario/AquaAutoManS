import Navbar from "../components/NavBar";
import Dashing from "../components/Dashing";

export default function Homepage() {
  return (
    <div className="flex  flex-wrap flex-row md:flex-row h-screen bg-[#F0EDE4]">
      <Navbar />
      <div className="">
        <div className="flex text-7xl">
          <Dashing></Dashing>
        </div>
      </div>
    </div>
  );
}
