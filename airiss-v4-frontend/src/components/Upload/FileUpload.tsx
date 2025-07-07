import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { uploadFile } from '../../services/api';
import { FileUploadResponse } from '../../types';

interface FileUploadProps {
  onUploadSuccess?: (data: {
    fileId: string;
    fileName: string;
    totalRecords: number;
    columns: string[];
  }) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const navigate = useNavigate();
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileInfo, setFileInfo] = useState<FileUploadResponse | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // 파일 크기 검증 (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('파일 크기는 100MB를 초과할 수 없습니다.');
      return;
    }

    // 파일 타입 검증
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xls|xlsx)$/)) {
      setError('CSV 또는 Excel 파일만 업로드 가능합니다.');
      return;
    }

    setError(null);
    setUploadStatus('uploading');
    setUploadProgress(0);

    // 진행률 시뮬레이션
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const response = await uploadFile(file);
      console.log('📡 Upload Response:', response);
      
      setFileInfo(response);
      setUploadProgress(100);
      setUploadStatus('success');
      
      if (onUploadSuccess) {
        // 백엔드에서 받은 columns를 직접 사용
        console.log('📤 Columns from backend:', response.columns);
        console.log('📤 Column count:', response.columns?.length || 0);
        
        onUploadSuccess({
          fileId: response.file_id,
          fileName: response.filename,
          totalRecords: response.total_records,
          columns: response.columns || [] // 백엔드에서 받은 columns 직접 사용
        });
      }
      
      // 2초 후 분석 페이지로 자동 이동
      setTimeout(() => {
        navigate('/analysis');
      }, 2000);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || '파일 업로드 실패');
      setUploadStatus('error');
    } finally {
      clearInterval(progressInterval);
    }
  }, [onUploadSuccess, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false
  });

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        파일 업로드
      </Typography>

      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          p: 4,
          mt: 2,
          mb: 2,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease'
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? '파일을 놓으세요' : '파일을 드래그하거나 클릭하여 선택'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          CSV, Excel (XLS, XLSX) 파일 지원 (최대 100MB)
        </Typography>
      </Box>

      {uploadStatus === 'uploading' && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
          <Typography variant="body2" sx={{ mt: 1 }}>
            업로드 중... {uploadProgress}%
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {fileInfo && uploadStatus === 'success' && (
        <Alert severity="success" sx={{ mb: 2 }}>
          파일 업로드 완료! 잠시 후 분석 페이지로 이동합니다...
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>파일명:</strong> {fileInfo.filename}
            </Typography>
            <Typography variant="body2">
              <strong>레코드 수:</strong> {fileInfo.total_records.toLocaleString()}개
            </Typography>
            <Typography variant="body2">
              <strong>컬럼 수:</strong> {fileInfo.columns.length}개
            </Typography>
            <Box sx={{ mt: 1 }}>
              {fileInfo.uid_columns.length > 0 && (
                <Chip
                  label={`UID 컬럼: ${fileInfo.uid_columns.join(', ')}`}
                  size="small"
                  color="primary"
                  sx={{ mr: 1 }}
                />
              )}
              {fileInfo.opinion_columns.length > 0 && (
                <Chip
                  label={`의견 컬럼: ${fileInfo.opinion_columns.join(', ')}`}
                  size="small"
                  color="secondary"
                  sx={{ mr: 1 }}
                />
              )}
              {fileInfo.quantitative_columns.length > 0 && (
                <Chip
                  label={`정량 컬럼: ${fileInfo.quantitative_columns.length}개`}
                  size="small"
                  color="success"
                />
              )}
            </Box>
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button 
                variant="contained" 
                size="small" 
                onClick={() => navigate('/analysis')}
              >
                지금 분석하기
              </Button>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => {
                  setFileInfo(null);
                  setUploadStatus('idle');
                }}
              >
                다른 파일 업로드
              </Button>
            </Box>
          </Box>
        </Alert>
      )}

      <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
        지원되는 파일 형식
      </Typography>
      <List>
        <ListItem>
          <ListItemIcon>
            <InsertDriveFile color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="CSV (Comma-Separated Values)"
            secondary="UTF-8, CP949 인코딩 지원"
          />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <InsertDriveFile color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="Excel"
            secondary=".xls, .xlsx 형식 지원"
          />
        </ListItem>
      </List>
    </Paper>
  );
};

export default FileUpload;