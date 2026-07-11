import axios from "axios";

const API = axios.create({

    baseURL:  "https://resumejobrecommendationapplication-production-5c81.up.railway.app"

});

export default API;