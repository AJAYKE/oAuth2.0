import axios from "axios";

export class IntegrationApiService {
  constructor(baseUrl = "http://localhost:8000/integrations") {
    this.baseUrl = baseUrl;
    this.client = axios.create({ baseURL: baseUrl });
    this.integrationType = null;
    this.userId = null;
    this.orgId = null;

    this.client.interceptors.request.use((config) => {
      config.data = config.data || new FormData();
      if (this.integrationType && !config.data.has("integration_type")) {
        config.data.append("integration_type", this.integrationType);
      }
      if (this.userId && !config.data.has("user_id")) {
        config.data.append("user_id", this.userId);
      }
      if (this.orgId && !config.data.has("org_id")) {
        config.data.append("org_id", this.orgId);
      }
      return config;
    });
  }

  setIntegrationType(integrationType) {
    this.integrationType = integrationType;
  }

  setUserId(userId) {
    this.userId = userId;
  }

  setOrgId(orgId) {
    this.orgId = orgId;
  }

  async authorize() {
    const response = await this.client.post("/authorize");
    return response.data;
  }

  async getCredentials() {
    const response = await this.client.post("/credentials");
    return response.data;
  }

  async loadData(credentials) {
    const formData = new FormData();
    formData.append("credentials", JSON.stringify(credentials));
    const response = await this.client.post("/load", formData);
    return response.data;
  }
}
