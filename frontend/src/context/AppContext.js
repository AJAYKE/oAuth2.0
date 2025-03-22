import { createContext, useContext, useMemo, useState } from "react";
import { IntegrationApiService } from "../services/apiService";

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [userId, setUserId] = useState("TestUser");
  const [orgId, setOrgId] = useState("TestOrg");
  const [integrationType, setIntegrationType] = useState(null);
  const [integrationParams, setIntegrationParams] = useState({});

  const apiService = useMemo(() => {
    const service = new IntegrationApiService();
    service.setUserId(userId);
    service.setOrgId(orgId);
    service.setIntegrationType(integrationType);
    return service;
  }, [integrationType, orgId, userId]);

  useMemo(() => {
    apiService.setUserId(userId);
  }, [userId, apiService]);

  useMemo(() => {
    apiService.setOrgId(orgId);
  }, [orgId, apiService]);

  useMemo(() => {
    apiService.setIntegrationType(integrationType);
  }, [integrationType, apiService]);

  const value = {
    userId,
    setUserId,
    orgId,
    setOrgId,
    integrationType,
    setIntegrationType,
    integrationParams,
    setIntegrationParams,
    apiService,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  return context;
};
