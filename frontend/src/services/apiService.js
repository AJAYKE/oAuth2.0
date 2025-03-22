import axios from "axios";

export class IntegrationApiService {
  constructor(baseUrl = "http://localhost:8000/integrations") {
    this.baseUrl = baseUrl;
  }

  async authorize(integrationType, userId, orgId) {
    const formData = new FormData();
    formData.append("integration_type", integrationType);
    formData.append("user_id", userId);
    formData.append("org_id", orgId);
    const response = await axios.post(`${this.baseUrl}/authorize`, formData);
    return response.data;
  }

  async getCredentials(integrationType, userId, orgId) {
    const formData = new FormData();
    formData.append("integration_type", integrationType);
    formData.append("user_id", userId);
    formData.append("org_id", orgId);
    const response = await axios.post(`${this.baseUrl}/credentials`, formData);
    return response.data;
  }

  async loadData(integrationType, credentials) {
    const formData = new FormData();
    formData.append("integration_type", integrationType);
    formData.append("credentials", JSON.stringify(credentials));
    const response = await axios.post(`${this.baseUrl}/load`, formData);
    return response.data;
  }
}

export const apiService = new IntegrationApiService();
