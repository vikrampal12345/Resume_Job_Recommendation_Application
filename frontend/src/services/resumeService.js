import API from "./api";


// =========================================================
// Upload Resume
// =========================================================

export const uploadResume = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await API.post(
        "/predict",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


// =========================================================
// Fetch Live Jobs for User Selected Role
// =========================================================

export const fetchLiveJobs = async (targetRole) => {

    const response = await API.post(
        "/live-jobs",
        {
            target_role: targetRole,
        }
    );

    return response.data;
};