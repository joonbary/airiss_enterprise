import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  TextField,
  Box,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Toolbar,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Description as DescriptionIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import api from '../../services/api';

interface Report {
  id?: string;
  job_id?: string;
  filename: string;
  createdAt?: string;
  created_at?: string;
  status: string;
  recordCount?: number;
  processed_records?: number;
  analysisMode?: string;
  analysis_mode?: string;
  averageScore?: number;
  average_score?: number;
  downloadUrl?: string;
  enable_ai_feedback?: boolean;
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMode, setFilterMode] = useState('all');
  const [sortBy, setSortBy] = useState('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await api.get('/analysis/jobs');
      setReports(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || '보고서를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (reportId: string) => {
    try {
      const response = await api.get(`/reports/${reportId}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `AIRISS_Report_${reportId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('다운로드 실패:', err);
    }
  };

  const filteredReports = reports
    .filter(report => {
      if (searchTerm && !report.filename.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      if (filterMode !== 'all' && report.analysisMode !== filterMode) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      const aValue = a[sortBy as keyof Report];
      const bValue = b[sortBy as keyof Report];
      
      // undefined 체크
      if (aValue === undefined || bValue === undefined) {
        return 0;
      }
      
      // 문자열과 숫자 비교를 위한 타입 체크
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      // 숫자 비교
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      }
      return aValue < bValue ? 1 : -1;
    });

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusChip = (status: string) => {
    const statusMap: Record<string, { label: string; color: 'success' | 'error' | 'warning' | 'default' }> = {
      completed: { label: '완료', color: 'success' },
      failed: { label: '실패', color: 'error' },
      processing: { label: '진행중', color: 'warning' },
    };
    const config = statusMap[status] || { label: status, color: 'default' };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const getModeChip = (mode: string) => {
    const modeMap: Record<string, { label: string; color: 'primary' | 'secondary' | 'default' }> = {
      hybrid: { label: '하이브리드', color: 'primary' },
      text: { label: '텍스트', color: 'secondary' },
      quantitative: { label: '정량', color: 'default' },
    };
    const config = modeMap[mode] || { label: mode, color: 'default' };
    return <Chip label={config.label} color={config.color} size="small" variant="outlined" />;
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        분석 보고서
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Toolbar sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 } }}>
          <Box sx={{ display: 'flex', gap: 2, flex: 1 }}>
            <TextField
              variant="outlined"
              size="small"
              placeholder="파일명 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 200 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>분석 모드</InputLabel>
              <Select
                value={filterMode}
                label="분석 모드"
                onChange={(e) => setFilterMode(e.target.value)}
              >
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="hybrid">하이브리드</MenuItem>
                <MenuItem value="text">텍스트</MenuItem>
                <MenuItem value="quantitative">정량</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>정렬</InputLabel>
              <Select
                value={sortBy}
                label="정렬"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="createdAt">생성일</MenuItem>
                <MenuItem value="filename">파일명</MenuItem>
                <MenuItem value="averageScore">평균점수</MenuItem>
                <MenuItem value="recordCount">데이터수</MenuItem>
              </Select>
            </FormControl>
          </Box>
          
          <Tooltip title="새로고침">
            <IconButton onClick={fetchReports}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>파일명</TableCell>
                <TableCell align="center">생성일시</TableCell>
                <TableCell align="center">상태</TableCell>
                <TableCell align="center">AI 피드백</TableCell>
                <TableCell align="center">분석모드</TableCell>
                <TableCell align="right">데이터수</TableCell>
                <TableCell align="right">평균점수</TableCell>
                <TableCell align="center">다운로드</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredReports
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <DescriptionIcon color="action" fontSize="small" />
                        <Typography variant="body2">{report.filename}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      {(() => {
                        const created = report.createdAt || report.created_at || '';
                        return created && !isNaN(new Date(created).getTime())
                          ? format(new Date(created), 'yyyy-MM-dd HH:mm', { locale: ko })
                          : '-';
                      })()}
                    </TableCell>
                    <TableCell align="center">
                      {getStatusChip(report.status)}
                    </TableCell>
                    <TableCell align="center">
                      {report.enable_ai_feedback ? <CheckIcon color="primary" fontSize="small" /> : <CloseIcon color="disabled" fontSize="small" />}
                    </TableCell>
                    <TableCell align="center">
                      {getModeChip(report.analysisMode || report.analysis_mode || '')}
                    </TableCell>
                    <TableCell align="right">{report.recordCount}</TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="primary" fontWeight="bold">
                        {(report.averageScore ?? report.average_score ?? 0).toFixed(1)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Excel 다운로드">
                        <IconButton
                          onClick={() => handleDownload(report.id || '')}
                          disabled={report.status !== 'completed'}
                          color="primary"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredReports.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      보고서가 없습니다.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredReports.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="페이지당 행 수:"
        />
      </Paper>
    </Container>
  );
};

export default Reports;