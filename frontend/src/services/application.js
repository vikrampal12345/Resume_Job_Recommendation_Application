import { apiRequest } from "./api";

export const getApplications = async () => {
  return await apiRequest(
    "/applications/"
  );
};

export const createApplication = async (
  application
) => {
  return await apiRequest(
    "/applications/",
    {
      method: "POST",
      body: JSON.stringify(application),
    }
  );
};

export const updateApplication = async (
  id,
  application
) => {
  return await apiRequest(
    `/applications/${id}`,
    {
      method: "PUT",
      body: JSON.stringify(application),
    }
  );
};

export const deleteApplication = async (
  id
) => {
  return await apiRequest(
    `/applications/${id}`,
    {
      method: "DELETE",
    }
  );
};