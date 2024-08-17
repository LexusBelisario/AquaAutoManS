import Navbar from "../components/NavBar";
import Dashing from "../components/Dashing";
import Turbidity from "./turbidity";
import Temperature from "./temp";
import Oxygen from "./oxygen";
import PhLevel from "./phLevel";

export default function Homepage() {
  return (
    <div className="flex  flex-wrap flex-row md:flex-row">
      <Navbar></Navbar>
      <div className="flex">
      <div className=" grid grid-cols-2 gap-5">

        <Turbidity></Turbidity>
        <Temperature></Temperature>
      
        <Oxygen></Oxygen>
        <PhLevel></PhLevel></div>
        </div>
    </div>
  );
}
