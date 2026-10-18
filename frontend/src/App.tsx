import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Layout } from './components/Layout';
import { DiscoverPage } from './pages/DiscoverPage';
import { CommunityPage } from './pages/CommunityPage';
import { BriefsPage } from './pages/BriefsPage';
import { WorkspacesPage } from './pages/WorkspacesPage';
import { LeaderboardPage } from './pages/LeaderboardPage';
import { CreatorProfilePage } from './pages/CreatorProfilePage';
import { ProjectRequestsPage } from './pages/ProjectRequestsPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SavedCreatorsPage } from './pages/SavedCreatorsPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>

        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/discover" replace />} />
            <Route path="discover" element={<DiscoverPage />} />
            <Route path="saved-creators" element={<SavedCreatorsPage />} />
            <Route path="shortlist" element={<SavedCreatorsPage />} />
            <Route path="community" element={<CommunityPage />} />
            <Route path="briefs" element={<BriefsPage />} />
            <Route path="workspaces" element={<WorkspacesPage />} />
            <Route path="requests" element={<ProjectRequestsPage />} />
            <Route path="project-requests" element={<ProjectRequestsPage />} />
            <Route path="leaderboard" element={<LeaderboardPage />} />
            <Route path="creators/:id" element={<CreatorProfilePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="*" element={<Navigate to="/discover" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </ThemeProvider>
  );
};

export default App;

