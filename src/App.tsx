import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { SearchPage } from './pages/SearchPage';
import SessionPage from './pages/SessionPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SearchPage />} />

        <Route
          path="/session/:sessionId"
          element={<SessionPage />}
        />
      </Routes>
    </BrowserRouter>
  );
}