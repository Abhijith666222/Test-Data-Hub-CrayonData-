import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProductOverviewPage from './pages/ProductOverviewPage';
import CreateSystemPage from './pages/CreateSystemPage';
import DataSourcePage from './pages/DataSourcePage';
import DataPreviewPage from './pages/DataPreviewPage';
import SchemaAnalysisPage from './pages/SchemaAnalysisPage';
import DataGenerationPage from './pages/DataGenerationPage';
import DestinationPage from './pages/DestinationPage';
import RunDetailsPage from './pages/RunDetailsPage';
import CreateTaskPipelinePage from './pages/CreateTaskPipelinePage';
import { AppProvider } from './context/AppContext';
import { NotificationProvider } from './context/NotificationContext';

function App() {
  return (
    <AppProvider>
      <NotificationProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="overview" element={<ProductOverviewPage />} />
                <Route path="create" element={<CreateSystemPage />} />
                <Route path="data-source" element={<DataSourcePage />} />
                <Route path="data-preview" element={<DataPreviewPage />} />
                <Route path="schema-analysis" element={<SchemaAnalysisPage />} />
                <Route path="data-generation" element={<DataGenerationPage />} />
                <Route path="destination" element={<DestinationPage />} />
                <Route path="run/:runId" element={<RunDetailsPage />} />
                <Route path="create-pipeline" element={<CreateTaskPipelinePage />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </NotificationProvider>
    </AppProvider>
  );
}

export default App; 