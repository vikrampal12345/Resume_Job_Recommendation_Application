import "./LiveJobs.css";

function LiveJobs({ jobs }) {

    console.log("LiveJobs Component:", jobs);
    if (!jobs || jobs.length === 0) {

        return null;

    }

    return (

        <section className="live-jobs-section">

            <h2>Live Jobs Recommended For You</h2>

            <div className="jobs-container">

                {jobs.map((job, index) => (

                    <div className="job-card" key={index}>

                        <h3>{job.job_title}</h3>

                        <p>

                            <strong>Company:</strong> {job.company}

                        </p>

                        <p>

                            <strong>Location:</strong> {job.location}

                        </p>

                        <p>

                            <strong>Employment:</strong> {job.employment_type}

                        </p>

                        <p>

                            <strong>Salary:</strong> {job.salary || "Not Mentioned"}

                        </p>

                        <p>

                            <strong>Posted:</strong> {job.posted_date}

                        </p>

                        <a

                            href={job.apply_link}

                            target="_blank"

                            rel="noopener noreferrer"

                            className="apply-btn"

                        >

                            Apply Now

                        </a>

                    </div>

                ))}

            </div>

        </section>

    );
    // return (
    //     <section className="live-jobs-section">

    //         <h2>🔥 Live Jobs Recommended For You</h2>

    //         {jobs.map((job, index) => (
    //             <div key={index}>
    //                 <h3 style={{ color: "red", fontSize: "24px" }}>
    //                     {job.job_title}
    //                 </h3>
    //             </div>
    //         ))}

    //     </section>
    // );
}

export default LiveJobs;