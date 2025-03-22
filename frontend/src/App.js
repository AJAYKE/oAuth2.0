import { IntegrationForm } from "./components/IntegrationForm";
import { AppProvider } from "./context/AppContext";

function App() {
  return (
    <AppProvider>
      <IntegrationForm />
    </AppProvider>
  );
}

export default App;
