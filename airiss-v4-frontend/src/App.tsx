import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import Layout from './components/Layout/Layout';
import theme from './theme';
import Dashboard from './components/Dashboard/Dashboard';
import FileUpload from './components/Upload/FileUpload';
import { AnalysisView } from './components/Analysis/AnalysisView'; // named import로 변경
import AdvancedSearch from './components/Search/AdvancedSearch';
import Reports from './components/Reports/Reports';
import Settings from './components/Settings/Settings';

interface FileData {
  fileId: string;
  fileName: string;
  totalRecords: number;
  columns: string[];
}

function App() {
  // SessionStorage에서 데이터 불러오기
  const getStoredFileData = (): FileData | null => {
    const stored = sessionStorage.getItem('airiss_file_data');
    return stored ? JSON.parse(stored) : null;
  };

  const [fileData, setFileData] = useState<FileData | null>(getStoredFileData());

  const handleFileUpload = (data: FileData) => {
    setFileData(data);
    // SessionStorage에 저장
    sessionStorage.setItem('airiss_file_data', JSON.stringify(data));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route 
              path="/upload" 
              element={<FileUpload onUploadSuccess={handleFileUpload} />} 
            />
            <Route 
              path="/analysis" 
              element={
                fileData ? (
                  <AnalysisView 
                    fileId={fileData.fileId}
                    fileName={fileData.fileName}
                    totalRecords={fileData.totalRecords}
                    columns={fileData.columns}
                  />
                ) : (
                  <Navigate to="/upload" replace />
                )
              } 
            />
            <Route path="/employees" element={<AdvancedSearch />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;