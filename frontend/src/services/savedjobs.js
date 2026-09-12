import { apiRequest } from "./api";

export const getSavedJobs = async () => {
  return await apiRequest(
    "/saved-jobs/"
  );
};

export const saveJob = async (job) => {
  return await apiRequest(
    "/saved-jobs/",
    {
      method: "POST",
      body: JSON.stringify(job),
    }
  );
};

export const removeSavedJob = async (
  jobId
) => {
  return await apiRequest(
    `/saved-jobs/${jobId}`,
    {
      method: "DELETE",
    }
  );
};