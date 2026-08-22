import axios from "axios";

const API = axios.create({
  baseURL: "https://resume-job-recommendation-api-czbgfvegfhg7gkfb.centralindia-01.azurewebsites.net"
});

export default API;
