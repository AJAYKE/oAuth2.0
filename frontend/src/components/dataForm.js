import { Box, Button, TextField } from "@mui/material";
import { useState } from "react";
import { apiService } from "../services/apiService";

export const DataForm = ({ integrationType, credentials }) => {
  const [loadedData, setLoadedData] = useState(null);

  const handleLoad = async () => {
    try {
      const data = await apiService.loadData(integrationType, credentials);
      setLoadedData(data);
    } catch (e) {
      alert(e?.response?.data?.detail);
    }
  };

  return (
    <>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="centexr"
        flexDirection="column"
        width="100%"
      >
        <Box display="flex" flexDirection="column" width="100%">
          {loadedData ? (
            <TextField
              label="Data"
              value={JSON.stringify(loadedData, null, 2)}
              sx={{ mt: 2 }}
              InputLabelProps={{ shrink: true }}
              multiline
              rows={10}
              disabled
            />
          ) : (
            <TextField
              label="Loaded Data"
              value={loadedData || ""}
              sx={{ mt: 2 }}
              InputLabelProps={{ shrink: true }}
              disabled
            />
          )}
          <Button onClick={handleLoad} sx={{ mt: 2 }} variant="contained">
            Load Data
          </Button>
          <Button
            onClick={() => setLoadedData(null)}
            sx={{ mt: 1 }}
            variant="contained"
          >
            Clear Data
          </Button>
        </Box>
      </Box>
    </>
  );
};
