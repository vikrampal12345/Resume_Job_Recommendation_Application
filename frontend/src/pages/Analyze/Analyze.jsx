import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import UploadResume from "../../components/UploadResume/UploadResume";
import LiveJobs from "../../components/LiveJobs/LiveJobs";

function Analyze() {
  return (
    <>
      <Navbar />
      <Hero />
      <UploadResume />
      <LiveJobs />
    </>
  );
}

export default Analyze;