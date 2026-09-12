import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import Onboarding from "./pages/Onboarding";
import OnboardingComplete from "./pages/OnboardingComplete";
import EmissionsDashboard from "./pages/EmissionsDashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/onboarding/complete/:factoryId" element={<OnboardingComplete />} />
        <Route path="/factories/:factoryId/emissions" element={<EmissionsDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
