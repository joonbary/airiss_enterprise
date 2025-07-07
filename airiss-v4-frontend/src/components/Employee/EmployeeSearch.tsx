import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Autocomplete,
  Chip,
  Avatar,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  Search,
  Person,
  Assessment,
  TrendingUp,
  Download,
  Refresh
} from '@mui/icons-material';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip
} from 'recharts';
import { getCompletedJobs, searchEmployee } from '../../services/api';

interface Job {
  job_id: string;
  filename: string;
  processed: number;
  analysis_mode: string;
  created_at: string;
}

interface Employee {
  UID: string;
  AIRISS_v4_종합점수: number;
  OK등급: string;
  등급설명: string;
  백분위: string;
  분석신뢰도: number;
  텍스트_종합점수: number;
  정량_종합점수: number;
  AI_장점?: string;
  AI_개선점?: string;
  AI_종합피드백?: string;
  업무성과_텍스트점수?: number;
  KPI달성_텍스트점수?: number;
  태도마인드_텍스트점수?: number;
  커뮤니케이션_텍스트점수?: number;
  리더십협업_텍스트점수?: number;
  전문성학습_텍스트점수?: number;
  창의혁신_텍스트점수?: number;
  조직적응_텍스트점수?: number;
}

interface Statistics {
  total_count: number;
  average_scores: {
    hybrid_avg: number;
    text_avg: number;
    quant_avg: number;
    confidence_avg: number;
  };
  grade_distribution: { [key: string]: number };
  top_grade_ratio: number;
}

const EmployeeSearch: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [statistics, setStatistics] = useState<Statistics | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const jobList = await getCompletedJobs();
      setJobs(jobList);
      if (jobList.length > 0) {
        setSelectedJob(jobList[0]);
      }
    } catch (error) {
      console.error('Failed to load jobs:', error);
      setError('분석 작업 목록을 불러올 수 없습니다.');
    }
  };

  const handleSearch = async () => {
    if (!selectedJob) {
      setError('분석 작업을 선택해주세요.');
      return;
    }
    
    // UID나 등급 중 적어도 하나는 있어야 함 (또는 둘 다 비어있으면 전체 첫 번째 결과)
    if (!searchQuery.trim() && !gradeFilter) {
      // 두 조건 모두 비어있으면 첫 번째 직원 반환 (또는 경고 메시지)
      console.log('⚠️ 검색 조건 없음 - 첫 번째 직원 반환');
    }

    setLoading(true);
    setError(null);
    setEmployee(null);

    try {
      const result = await searchEmployee(
        selectedJob.job_id,
        searchQuery.trim() || undefined,
        gradeFilter || undefined
      );
      
      if (result.employee) {
        setEmployee(result.employee);
        setStatistics(result.statistics);
      } else {
        setError('검색 결과가 없습니다.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.includes('★★★')) return '#4caf50';
    if (grade.includes('★★')) return '#8bc34a';
    if (grade.includes('★')) return '#cddc39';
    if (grade.includes('A')) return '#ff9800';
    if (grade.includes('B+')) return '#ff5722';
    if (grade.includes('B')) return '#f44336';
    if (grade.includes('C')) return '#9e9e9e';
    return '#757575';
  };

  // 레이더 차트 데이터 준비
  const prepareRadarData = () => {
    if (!employee) return [];

    return [
      { subject: '업무성과', score: employee.업무성과_텍스트점수 || 0, fullMark: 100 },
      { subject: 'KPI달성', score: employee.KPI달성_텍스트점수 || 0, fullMark: 100 },
      { subject: '태도마인드', score: employee.태도마인드_텍스트점수 || 0, fullMark: 100 },
      { subject: '커뮤니케이션', score: employee.커뮤니케이션_텍스트점수 || 0, fullMark: 100 },
      { subject: '리더십협업', score: employee.리더십협업_텍스트점수 || 0, fullMark: 100 },
      { subject: '전문성학습', score: employee.전문성학습_텍스트점수 || 0, fullMark: 100 },
      { subject: '창의혁신', score: employee.창의혁신_텍스트점수 || 0, fullMark: 100 },
      { subject: '조직적응', score: employee.조직적응_텍스트점수 || 0, fullMark: 100 }
    ];
  };

  const handleGradeFilterChange = (event: SelectChangeEvent) => {
    setGradeFilter(event.target.value);
  };

  return (
    <Box>
      {/* 검색 섹션 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          개인별 성과 조회
        </Typography>
        
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={jobs}
              getOptionLabel={(option) => `${option.filename} (${option.processed}명)`}
              value={selectedJob}
              onChange={(_, value) => setSelectedJob(value)}
              renderInput={(params) => (
                <TextField {...params} label="분석 작업 선택" fullWidth />
              )}
              disabled={jobs.length === 0}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="직원 ID (UID)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="EMP001"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>등급 필터</InputLabel>
              <Select value={gradeFilter} onChange={handleGradeFilterChange}>
                <MenuItem value="">전체</MenuItem>
                <MenuItem value="OK★★★">OK★★★ (최우수)</MenuItem>
                <MenuItem value="OK★★">OK★★ (우수)</MenuItem>
                <MenuItem value="OK★">OK★ (우수+)</MenuItem>
                <MenuItem value="OK A">OK A (양호)</MenuItem>
                <MenuItem value="OK B+">OK B+ (양호-)</MenuItem>
                <MenuItem value="OK B">OK B (보통)</MenuItem>
                <MenuItem value="OK C">OK C (개선필요)</MenuItem>
                <MenuItem value="OK D">OK D (집중개선)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Search />}
              onClick={handleSearch}
              disabled={!selectedJob || loading}
              sx={{ height: '56px' }}
            >
              검색
            </Button>
          </Grid>
          
          <Grid item xs={12} md={1}>
            <Tooltip title="새로고침">
              <IconButton onClick={loadJobs} sx={{ height: '56px' }}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Grid>
        </Grid>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
      </Paper>

      {/* 로딩 */}
      {loading && (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      )}

      {/* 통계 정보 */}
      {statistics && !loading && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            전체 분석 통계
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    총 인원
                  </Typography>
                  <Typography variant="h4">
                    {statistics.total_count}명
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    평균 점수
                  </Typography>
                  <Typography variant="h4">
                    {statistics.average_scores.hybrid_avg.toFixed(1)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    상위 등급 비율
                  </Typography>
                  <Typography variant="h4">
                    {statistics.top_grade_ratio}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    평균 신뢰도
                  </Typography>
                  <Typography variant="h4">
                    {statistics.average_scores.confidence_avg.toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 직원 정보 */}
      {employee && !loading && (
        <>
          {/* 기본 정보 */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box display="flex" alignItems="center" mb={3}>
              <Avatar sx={{ width: 60, height: 60, bgcolor: 'primary.main', mr: 2 }}>
                <Person sx={{ fontSize: 30 }} />
              </Avatar>
              <Box flex={1}>
                <Typography variant="h5" fontWeight="bold">
                  {employee.UID}
                </Typography>
                <Box display="flex" gap={1} mt={1}>
                  <Chip
                    label={employee.OK등급}
                    sx={{
                      backgroundColor: getGradeColor(employee.OK등급),
                      color: 'white',
                      fontWeight: 'bold'
                    }}
                  />
                  <Chip label={employee.백분위} variant="outlined" />
                  <Chip
                    label={`신뢰도 ${employee.분석신뢰도}%`}
                    color={employee.분석신뢰도 >= 80 ? 'success' : 'default'}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* 점수 요약 */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    하이브리드 종합점수
                  </Typography>
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    {employee.AIRISS_v4_종합점수.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    평균: {statistics?.average_scores.hybrid_avg.toFixed(1)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    텍스트 분석
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {employee.텍스트_종합점수.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    평균: {statistics?.average_scores.text_avg.toFixed(1)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    정량 분석
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {employee.정량_종합점수.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    평균: {statistics?.average_scores.quant_avg.toFixed(1)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    등급 설명
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    {employee.등급설명}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* 8대 영역 분석 */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 450 }}>
                <Typography variant="h6" gutterBottom>
                  AIRISS 8대 영역 분석
                </Typography>
                <ResponsiveContainer width="100%" height={380}>
                  <RadarChart data={prepareRadarData()}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar
                      name="점수"
                      dataKey="score"
                      stroke="#FF5722"
                      fill="#FF5722"
                      fillOpacity={0.6}
                    />
                    <RechartsTooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 450 }}>
                <Typography variant="h6" gutterBottom>
                  영역별 상세 점수
                </Typography>
                <List>
                  {[
                    { name: '업무성과', score: employee.업무성과_텍스트점수, weight: 25 },
                    { name: 'KPI달성', score: employee.KPI달성_텍스트점수, weight: 20 },
                    { name: '태도마인드', score: employee.태도마인드_텍스트점수, weight: 15 },
                    { name: '커뮤니케이션', score: employee.커뮤니케이션_텍스트점수, weight: 15 },
                    { name: '리더십협업', score: employee.리더십협업_텍스트점수, weight: 10 },
                    { name: '전문성학습', score: employee.전문성학습_텍스트점수, weight: 8 },
                    { name: '창의혁신', score: employee.창의혁신_텍스트점수, weight: 5 },
                    { name: '조직적응', score: employee.조직적응_텍스트점수, weight: 2 }
                  ].map((item) => (
                    <ListItem key={item.name}>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between">
                            <Typography variant="body1">{item.name}</Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip
                                label={`${item.score?.toFixed(1) || 0}점`}
                                size="small"
                                color={
                                  (item.score || 0) >= 80 ? 'success' :
                                  (item.score || 0) >= 60 ? 'warning' : 'default'
                                }
                              />
                              <Typography variant="body2" color="text.secondary">
                                (가중치: {item.weight}%)
                              </Typography>
                            </Box>
                          </Box>
                        }
                        secondary={
                          <LinearProgress
                            variant="determinate"
                            value={item.score || 0}
                            sx={{
                              mt: 1,
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 3
                              }
                            }}
                          />
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>

          {/* AI 피드백 */}
          {(employee.AI_장점 || employee.AI_개선점 || employee.AI_종합피드백) && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI 분석 피드백
              </Typography>
              
              {employee.AI_장점 && (
                <Box mb={3}>
                  <Typography variant="subtitle1" fontWeight="bold" color="success.main" gutterBottom>
                    핵심 장점
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {employee.AI_장점}
                  </Typography>
                </Box>
              )}
              
              {employee.AI_개선점 && (
                <Box mb={3}>
                  <Typography variant="subtitle1" fontWeight="bold" color="warning.main" gutterBottom>
                    개선 방향
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {employee.AI_개선점}
                  </Typography>
                </Box>
              )}
              
              {employee.AI_종합피드백 && (
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom>
                    종합 피드백
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {employee.AI_종합피드백}
                  </Typography>
                </Box>
              )}
            </Paper>
          )}
        </>
      )}
    </Box>
  );
};

export default EmployeeSearch;