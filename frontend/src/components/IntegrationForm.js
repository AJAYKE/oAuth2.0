import { Autocomplete, Box, TextField } from "@mui/material";
import { integrationConfig } from "../config/integrations";
import { useAppContext } from "../context/AppContext";
import { DataForm } from "./dataForm";
import { OAuthIntegration } from "./OAuthIntegration";

export const IntegrationForm = () => {
  const {
    userId,
    setUserId,
    orgId,
    setOrgId,
    integrationType,
    setIntegrationType,
    integrationParams,
  } = useAppContext();

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      flexDirection="column"
      sx={{ width: "100%" }}
    >
      <Box display="flex" flexDirection="column">
        <TextField
          label="User"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          sx={{ mt: 2 }}
        />
        <TextField
          label="Organization"
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
          sx={{ mt: 2 }}
        />
        <Autocomplete
          id="integration-type"
          options={Object.keys(integrationConfig)}
          sx={{ width: 300, mt: 2 }}
          renderInput={(params) => (
            <TextField {...params} label="Integration Type" />
          )}
          onChange={(e, value) => setIntegrationType(value)}
        />
      </Box>
      {integrationType && (
        <Box>
          <OAuthIntegration />
        </Box>
      )}
      {integrationParams?.credentials && (
        <Box sx={{ mt: 2 }}>
          <DataForm />
        </Box>
      )}
    </Box>
  );
};
