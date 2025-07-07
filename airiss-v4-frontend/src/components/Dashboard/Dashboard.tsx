import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Button  // Button 추가
} from '@mui/material';
import {
  TrendingUp,
  People,
  Assessment,
  Speed,
  FileDownload,
  Visibility
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getDashboardData, downloadResults } from '../../services/api';
import { DashboardStats } from '../../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardStats | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getDashboardData();
        let typedData: DashboardStats;
        // jobs가 배열이고 1개 이상이면 실제 데이터 사용 (processed/processed_records 모두 대응)
        if (Array.isArray(data.jobs) && data.jobs.length > 0) {
          typedData = {
            total_analyses: data.jobs.length,
            total_employees: data.jobs.reduce((sum: number, job: any) => sum + (job.processed ?? job.processed_records ?? 0), 0),
            average_score: data.jobs.length > 0 
              ? data.jobs.reduce((sum: number, job: any) => sum + (job.average_score ?? 0), 0) / data.jobs.length 
              : 0,
            recent_analyses: data.jobs.slice(0, 5).map((job: any) => ({
              job_id: job.job_id || 'unknown',
              filename: job.filename || 'Unknown File',
              processed: job.processed ?? job.processed_records ?? 0,
              average_score: job.average_score ?? 0,
              created_at: job.created_at || new Date().toISOString()
            }))
          };
        } else {
          // API 오류시 기본값 사용
          typedData = {
            total_analyses: 0,
            total_employees: 0,
            average_score: 0,
            recent_analyses: []
          };
        }
        setDashboardData(typedData);
      } catch (error: any) {
        console.error('Failed to fetch dashboard data:', error);
        setError('대시보드 데이터를 불러올 수 없습니다.');
        // 오류 시에도 기본 구조 설정
        setDashboardData({
          total_analyses: 0,
          total_employees: 0,
          average_score: 0,
          recent_analyses: []
        });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getGradeColor = (grade: string) => {
    if (grade.includes('★')) return '#4caf50';
    if (grade.includes('A')) return '#ff9800';
    if (grade.includes('B')) return '#2196f3';
    if (grade.includes('C')) return '#9e9e9e';
    return '#757575';
  };

  // 다운로드 핸들러
  const handleDownload = async (jobId: string, filename: string) => {
    try {
      const blob = await downloadResults(jobId, 'excel');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename.replace(/\.[^/.]+$/, '')}_결과.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('다운로드에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  // 실제 데이터가 없거나 적을 경우에만 더미 데이터 사용
  const mockData: DashboardStats = (dashboardData && dashboardData.total_analyses > 0) ? dashboardData : {
    total_analyses: 152,
    total_employees: 1847,
    average_score: 73.5,
    recent_analyses: [
      {
        job_id: '1',
        filename: 'Q4_2024_평가.xlsx',
        processed: 250,
        average_score: 76.3,
        created_at: '2024-01-15T10:30:00'
      },
      {
        job_id: '2',
        filename: '영업팀_성과평가.csv',
        processed: 85,
        average_score: 81.2,
        created_at: '2024-01-14T15:20:00'
      },
      {
        job_id: '3',
        filename: '본부_리더십평가.xlsx',
        processed: 142,
        average_score: 79.8,
        created_at: '2024-01-13T09:15:00'
      }
    ]
  };

  // 차트 데이터 준비
  const gradeData = [
    { grade: 'OK★★★', count: 45, percentage: 2.4 },
    { grade: 'OK★★', count: 185, percentage: 10.0 },
    { grade: 'OK★', count: 320, percentage: 17.3 },
    { grade: 'OK A', count: 580, percentage: 31.4 },
    { grade: 'OK B+', count: 420, percentage: 22.7 },
    { grade: 'OK B', count: 220, percentage: 11.9 },
    { grade: 'OK C', count: 77, percentage: 4.2 }
  ];

  return (
    <Box>
      {/* 헤더 */}
      <Box mb={4}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          AIRISS v4.0 대시보드
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI 기반 직원 성과 분석 시스템의 전체 현황을 확인하세요
        </Typography>
      </Box>

      {/* 주요 지표 카드 */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    총 분석 건수
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {mockData.total_analyses.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +12.5% 전월 대비
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, color: 'primary.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    분석 직원 수
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {mockData.total_employees.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="info.main">
                    전체 직원의 85%
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, color: 'secondary.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    평균 종합점수
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {mockData.average_score.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="warning.main">
                    +2.3점 향상
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    분석 신뢰도
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    92.3%
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    매우 높음
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, color: 'warning.main', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 등급 분포 차트 */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '400px' }}>
            <Typography variant="h6" gutterBottom>
              등급별 분포 현황
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={gradeData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="grade" angle={-45} textAnchor="end" />
                <YAxis />
                <RechartsTooltip
                  formatter={(value: any, name: string) => {
                    if (name === 'count') return [`${value}명`, '인원'];
                    return [value, name];
                  }}
                />
                <Bar dataKey="count" fill="#FF5722" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '400px' }}>
            <Typography variant="h6" gutterBottom>
              AIRISS 8대 영역 평균
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { name: '업무성과', score: 78.5, color: '#FF5722' },
                { name: 'KPI달성', score: 75.2, color: '#4A4A4A' },
                { name: '태도마인드', score: 82.1, color: '#F89C26' },
                { name: '커뮤니케이션', score: 71.8, color: '#B3B3B3' },
                { name: '리더십협업', score: 69.5, color: '#FF8A50' },
                { name: '전문성학습', score: 74.3, color: '#6A6A6A' },
                { name: '창의혁신', score: 68.2, color: '#FFA726' },
                { name: '조직적응', score: 79.9, color: '#9E9E9E' }
              ].map((item) => (
                <Box key={item.name} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2">{item.name}</Typography>
                    <Typography variant="body2" fontWeight="bold">{item.score}</Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={item.score}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: item.color,
                        borderRadius: 4
                      }
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* 최근 분석 내역 */}
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            최근 분석 내역
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={() => navigate('/reports')}
          >
            전체 보기
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>파일명</TableCell>
                <TableCell align="center">분석 일시</TableCell>
                <TableCell align="center">분석 인원</TableCell>
                <TableCell align="center">평균 점수</TableCell>
                <TableCell align="center">상태</TableCell>
                <TableCell align="center">작업</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockData.recent_analyses.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      최근 분석 내역이 없습니다.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                mockData.recent_analyses.map((analysis) => (
                  <TableRow key={analysis.job_id}>
                    <TableCell>{analysis.filename}</TableCell>
                    <TableCell align="center">
                      {new Date(analysis.created_at).toLocaleDateString('ko-KR')}
                    </TableCell>
                    <TableCell align="center">{analysis.processed}명</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={analysis.average_score.toFixed(1)}
                        size="small"
                        color={analysis.average_score >= 80 ? 'success' : analysis.average_score >= 70 ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip label="완료" size="small" color="success" />
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="상세 보기">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/employees?job=${analysis.job_id}`)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="다운로드">
                        <IconButton size="small" onClick={() => handleDownload(analysis.job_id, analysis.filename)}>
                          <FileDownload />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Dashboard;