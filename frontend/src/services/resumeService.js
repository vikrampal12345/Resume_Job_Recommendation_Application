import API from "./api";

// =========================================================
// Upload Resume
// =========================================================

export const uploadResume = async (file) => {
    const formData = new FormData();

    formData.append("file", file);

    try {
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

    } catch (error) {
        console.error("Resume upload error:", error);

        // Backend returned an HTTP error
        if (error.response) {
            const detail = error.response.data?.detail;

            // Backend returned structured error
            if (detail && typeof detail === "object") {
                throw new Error(
                    detail.message ||
                    detail.reason ||
                    "The uploaded document is not a valid resume."
                );
            }

            // Backend returned normal string error
            if (typeof detail === "string") {
                throw new Error(detail);
            }

            throw new Error(
                `Request failed with status ${error.response.status}.`
            );
        }

        // Backend/server could not be reached
        if (error.request) {
            throw new Error(
                "Unable to connect to the backend. Please try again."
            );
        }

        // Other Axios/client error
        throw new Error(
            error.message ||
            "Unable to upload the resume."
        );
    }
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