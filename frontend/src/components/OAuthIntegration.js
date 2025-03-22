import { Box, Button, CircularProgress } from "@mui/material";
import { useEffect, useState } from "react";
import { integrationConfig } from "../config/integrations";
import { apiService } from "../services/apiService";

export const OAuthIntegration = ({
  integrationType,
  user,
  org,
  integrationParams,
  setIntegrationParams,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const config = integrationConfig[integrationType];

  const handleConnectClick = async () => {
    try {
      setIsConnecting(true);
      const authURL = await apiService.authorize(integrationType, user, org);

      const newWindow = window.open(
        authURL,
        config.windowName,
        "width=600, height=600"
      );

      const pollTimer = window.setInterval(() => {
        if (newWindow?.closed !== false) {
          window.clearInterval(pollTimer);
          handleWindowClosed();
        }
      }, 200);
    } catch (e) {
      setIsConnecting(false);
      alert(
        `Failed to connect to ${config.displayName}: ${e?.response?.data?.detail}`
      );
    }
  };

  const handleWindowClosed = async () => {
    try {
      const credentials = await apiService.getCredentials(
        integrationType,
        user,
        org
      );
      if (credentials) {
        setIsConnected(true);
        setIntegrationParams((prev) => ({
          ...prev,
          credentials,
          type: integrationType,
        }));
      }
    } catch (e) {
      alert(
        `Failed to retrieve ${config.displayName} credentials: ${e?.response?.data?.detail}`
      );
    } finally {
      setIsConnecting(false);
    }
  };

  useEffect(() => {
    setIsConnected(!!integrationParams?.credentials);
  }, [integrationParams?.credentials]);

  return (
    <Box sx={{ mt: 2 }}>
      Parameters
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        sx={{ mt: 2 }}
      >
        <Button
          variant="contained"
          onClick={isConnected ? () => {} : handleConnectClick}
          color={isConnected ? "success" : "primary"}
          disabled={isConnecting}
          style={{
            pointerEvents: isConnected ? "none" : "auto",
            cursor: isConnected ? "default" : "pointer",
            opacity: isConnected ? 1 : undefined,
          }}
        >
          {isConnected ? (
            `${config.displayName} Connected`
          ) : isConnecting ? (
            <CircularProgress size={20} />
          ) : (
            `Connect to ${config.displayName}`
          )}
        </Button>
      </Box>
    </Box>
  );
};
