// src/components/Jobs/JobDashboard.tsx

import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  LinearProgress,
  Alert,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import {
  Visibility,
  FileDownload,
  Refresh
} from '@mui/icons-material';
import { getAnalysisJobs } from '../../services/api';

interface JobInfo {
  job_id: string;
  filename: string;
  analysis_mode: string;
  status: string;
  processed: number;
  end_time: string;
  progress?: number;
  average_score?: number;
  created_at?: string;
}

const JobDashboard: React.FC = () => {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // jobs API에서 작업 목록 받아오기
  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAnalysisJobs();
      // response가 배열인지 확인
      if (Array.isArray(response)) {
        setJobs(response);
      } else if (response && response.jobs && Array.isArray(response.jobs)) {
        setJobs(response.jobs);
      } else {
        console.error('Unexpected response format:', response);
        setJobs([]);
      }
    } catch (error: any) {
      console.error('Failed to fetch jobs:', error);
      setError('작업 목록을 불러올 수 없습니다.');
      setJobs([]);  // 에러 시에도 빈 배열로 설정
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    
    // 3초마다 새로고침
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      case 'pending':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return '완료';
      case 'processing':
        return '처리중';
      case 'failed':
        return '실패';
      case 'pending':
        return '대기';
      default:
        return status;
    }
  };

  const handleViewResults = (jobId: string) => {
    window.open(`/results/${jobId}`, '_blank');
  };

  const handleDownload = async (jobId: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8002'}/analysis/download/${jobId}/excel`);
      if (!response.ok) {
        throw new Error('Download failed');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AIRISS_분석결과_${jobId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('다운로드 실패:', error);
      alert('결과 다운로드에 실패했습니다.');
    }
  };

  if (loading && jobs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            AIRISS 작업 목록 대시보드
          </Typography>
          <Typography variant="body1" color="text.secondary">
            진행 중인 분석 작업과 완료된 결과를 확인하세요
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchJobs}
          disabled={loading}
        >
          새로고침
        </Button>
      </Box>

      {/* 오류 메시지 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 작업 통계 카드 */}
      <Box display="flex" gap={2} mb={4}>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" variant="body2">
              총 작업 수
            </Typography>
            <Typography variant="h4" fontWeight="bold">
              {jobs.length}
            </Typography>
          </CardContent>
        </Card>
        
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" variant="body2">
              완료된 작업
            </Typography>
            <Typography variant="h4" fontWeight="bold" color="success.main">
              {jobs.filter(job => job.status === 'completed').length}
            </Typography>
          </CardContent>
        </Card>
        
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" variant="body2">
              진행 중인 작업
            </Typography>
            <Typography variant="h4" fontWeight="bold" color="warning.main">
              {jobs.filter(job => job.status === 'processing').length}
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* 작업 목록 테이블 */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>파일명</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">분석모드</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">상태</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">진행률</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">평균점수</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">완료시간</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {jobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      작업 이력이 없습니다.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                jobs.map((job) => (
                  <TableRow key={job.job_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {job.filename}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ID: {job.job_id.substring(0, 8)}...
                      </Typography>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip
                        label={job.analysis_mode}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip
                        label={getStatusText(job.status)}
                        size="small"
                        color={getStatusColor(job.status) as any}
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      {job.progress !== undefined ? (
                        <Box sx={{ width: 80 }}>
                          <LinearProgress
                            variant="determinate"
                            value={job.progress}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                          <Typography variant="caption">
                            {job.progress}%
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    
                    <TableCell align="center">
                      {job.average_score !== undefined ? (
                        <Chip
                          label={job.average_score.toFixed(1)}
                          size="small"
                          color={job.average_score >= 80 ? 'success' : job.average_score >= 70 ? 'warning' : 'default'}
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    
                    <TableCell align="center">
                      <Typography variant="body2">
                        {job.end_time ? new Date(job.end_time).toLocaleDateString('ko-KR', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        }) : '-'}
                      </Typography>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Box display="flex" justifyContent="center" gap={1}>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleViewResults(job.job_id)}
                          disabled={job.status !== 'completed'}
                        >
                          <Visibility />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleDownload(job.job_id)}
                          disabled={job.status !== 'completed'}
                        >
                          <FileDownload />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* 자동 새로고침 표시 */}
      {loading && jobs.length > 0 && (
        <Box display="flex" justifyContent="center" alignItems="center" mt={2}>
          <CircularProgress size={20} sx={{ mr: 1 }} />
          <Typography variant="caption" color="text.secondary">
            데이터 업데이트 중...
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default JobDashboard;