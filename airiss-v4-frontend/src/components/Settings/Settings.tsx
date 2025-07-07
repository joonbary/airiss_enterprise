import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  InputAdornment,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Avatar,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  Palette as PaletteIcon,
  Security as SecurityIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [saveStatus, setSaveStatus] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({
    show: false,
    message: '',
    type: 'success',
  });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: '' });

  // 시스템 설정 상태
  const [systemSettings, setSystemSettings] = useState({
    apiKey: '',
    apiKeyVisible: false,
    defaultAnalysisMode: 'hybrid',
    defaultSampleSize: '25',
    autoDownload: true,
    enableWebSocket: true,
    maxConcurrentAnalysis: 3,
  });

  // 사용자 프로필 상태
  const [userProfile, setUserProfile] = useState({
    name: '관리자',
    email: 'admin@okfg.com',
    department: 'HR팀',
    role: 'admin',
    avatar: '',
  });

  // 알림 설정 상태
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    analysisComplete: true,
    analysisError: true,
    weeklyReport: false,
    systemUpdates: true,
    notificationEmail: 'admin@okfg.com',
  });

  // 데이터 관리 설정
  const [dataSettings, setDataSettings] = useState({
    dataRetention: 90, // days
    autoCleanup: true,
    cacheSize: 500, // MB
    exportFormat: 'xlsx',
    includeRawData: false,
  });

  // 테마 설정
  const [themeSettings, setThemeSettings] = useState({
    darkMode: false,
    primaryColor: '#FF5722',
    accentColor: '#4A4A4A',
    fontSize: 'medium',
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSystemSettingChange = (field: string, value: any) => {
    setSystemSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveSettings = async (section: string) => {
    try {
      // 실제로는 API 호출
      console.log(`Saving ${section} settings...`);
      
      // 임시 저장 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveStatus({
        show: true,
        message: `${section} 설정이 저장되었습니다.`,
        type: 'success',
      });
      
      setTimeout(() => {
        setSaveStatus({ show: false, message: '', type: 'success' });
      }, 3000);
    } catch (error) {
      setSaveStatus({
        show: true,
        message: '설정 저장 중 오류가 발생했습니다.',
        type: 'error',
      });
    }
  };

  const handleResetData = () => {
    setConfirmDialog({ open: true, action: 'reset' });
  };

  const handleConfirmAction = () => {
    if (confirmDialog.action === 'reset') {
      // 데이터 초기화 로직
      console.log('Resetting data...');
      setSaveStatus({
        show: true,
        message: '데이터가 초기화되었습니다.',
        type: 'success',
      });
    }
    setConfirmDialog({ open: false, action: '' });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        설정
      </Typography>

      {/* 저장 상태 알림 */}
      {saveStatus.show && (
        <Alert
          severity={saveStatus.type}
          sx={{ mb: 3 }}
          onClose={() => setSaveStatus({ show: false, message: '', type: 'success' })}
        >
          {saveStatus.message}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<SettingsIcon />} label="시스템" />
          <Tab icon={<PersonIcon />} label="프로필" />
          <Tab icon={<NotificationsIcon />} label="알림" />
          <Tab icon={<StorageIcon />} label="데이터 관리" />
          <Tab icon={<PaletteIcon />} label="테마" />
        </Tabs>

        {/* 시스템 설정 */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    API 설정
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <TextField
                      fullWidth
                      label="OpenAI API 키"
                      type={systemSettings.apiKeyVisible ? 'text' : 'password'}
                      value={systemSettings.apiKey}
                      onChange={(e) => handleSystemSettingChange('apiKey', e.target.value)}
                      placeholder="sk-..."
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => handleSystemSettingChange('apiKeyVisible', !systemSettings.apiKeyVisible)}
                              edge="end"
                            >
                              {systemSettings.apiKeyVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                      helperText="AI 피드백 생성에 사용됩니다"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    분석 기본값
                  </Typography>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>기본 분석 모드</InputLabel>
                        <Select
                          value={systemSettings.defaultAnalysisMode}
                          onChange={(e) => handleSystemSettingChange('defaultAnalysisMode', e.target.value)}
                          label="기본 분석 모드"
                        >
                          <MenuItem value="text">텍스트 분석</MenuItem>
                          <MenuItem value="quantitative">정량 분석</MenuItem>
                          <MenuItem value="hybrid">하이브리드</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>기본 샘플 크기</InputLabel>
                        <Select
                          value={systemSettings.defaultSampleSize}
                          onChange={(e) => handleSystemSettingChange('defaultSampleSize', e.target.value)}
                          label="기본 샘플 크기"
                        >
                          <MenuItem value="10">10개</MenuItem>
                          <MenuItem value="25">25개</MenuItem>
                          <MenuItem value="50">50개</MenuItem>
                          <MenuItem value="100">100개</MenuItem>
                          <MenuItem value="all">전체</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    시스템 옵션
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="분석 완료 시 자동 다운로드"
                        secondary="분석이 완료되면 자동으로 결과 파일을 다운로드합니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={systemSettings.autoDownload}
                          onChange={(e) => handleSystemSettingChange('autoDownload', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="WebSocket 실시간 연결"
                        secondary="실시간 분석 진행 상황을 표시합니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={systemSettings.enableWebSocket}
                          onChange={(e) => handleSystemSettingChange('enableWebSocket', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button variant="outlined" startIcon={<CancelIcon />}>
                  취소
                </Button>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => handleSaveSettings('시스템')}
                >
                  저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 프로필 설정 */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Avatar
                    sx={{
                      width: 120,
                      height: 120,
                      mx: 'auto',
                      mb: 2,
                      bgcolor: 'primary.main',
                      fontSize: '3rem',
                    }}
                  >
                    {userProfile.name.charAt(0)}
                  </Avatar>
                  <Button variant="outlined" size="small">
                    프로필 사진 변경
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    사용자 정보
                  </Typography>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="이름"
                        value={userProfile.name}
                        onChange={(e) => setUserProfile({ ...userProfile, name: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="이메일"
                        type="email"
                        value={userProfile.email}
                        onChange={(e) => setUserProfile({ ...userProfile, email: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="부서"
                        value={userProfile.department}
                        onChange={(e) => setUserProfile({ ...userProfile, department: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>권한</InputLabel>
                        <Select
                          value={userProfile.role}
                          onChange={(e) => setUserProfile({ ...userProfile, role: e.target.value })}
                          label="권한"
                        >
                          <MenuItem value="admin">관리자</MenuItem>
                          <MenuItem value="manager">매니저</MenuItem>
                          <MenuItem value="user">사용자</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => handleSaveSettings('프로필')}
                >
                  저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 알림 설정 */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    알림 설정
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="이메일 알림"
                        secondary="중요한 이벤트에 대해 이메일로 알림을 받습니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={notificationSettings.emailNotifications}
                          onChange={(e) => setNotificationSettings({
                            ...notificationSettings,
                            emailNotifications: e.target.checked
                          })}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText
                        primary="분석 완료 알림"
                        secondary="분석이 완료되면 알림을 받습니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={notificationSettings.analysisComplete}
                          onChange={(e) => setNotificationSettings({
                            ...notificationSettings,
                            analysisComplete: e.target.checked
                          })}
                          disabled={!notificationSettings.emailNotifications}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="오류 알림"
                        secondary="분석 중 오류가 발생하면 알림을 받습니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={notificationSettings.analysisError}
                          onChange={(e) => setNotificationSettings({
                            ...notificationSettings,
                            analysisError: e.target.checked
                          })}
                          disabled={!notificationSettings.emailNotifications}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="주간 리포트"
                        secondary="매주 분석 현황 리포트를 받습니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={notificationSettings.weeklyReport}
                          onChange={(e) => setNotificationSettings({
                            ...notificationSettings,
                            weeklyReport: e.target.checked
                          })}
                          disabled={!notificationSettings.emailNotifications}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                  <Box sx={{ mt: 3 }}>
                    <TextField
                      fullWidth
                      label="알림 받을 이메일"
                      type="email"
                      value={notificationSettings.notificationEmail}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        notificationEmail: e.target.value
                      })}
                      disabled={!notificationSettings.emailNotifications}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => handleSaveSettings('알림')}
                >
                  저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 데이터 관리 */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    데이터 보관
                  </Typography>
                  <Box sx={{ mt: 3 }}>
                    <Typography gutterBottom>
                      데이터 보관 기간: {dataSettings.dataRetention}일
                    </Typography>
                    <Slider
                      value={dataSettings.dataRetention}
                      onChange={(e, value) => setDataSettings({
                        ...dataSettings,
                        dataRetention: value as number
                      })}
                      min={30}
                      max={365}
                      step={30}
                      marks={[
                        { value: 30, label: '30일' },
                        { value: 90, label: '90일' },
                        { value: 180, label: '180일' },
                        { value: 365, label: '1년' },
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                  <Box sx={{ mt: 3 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={dataSettings.autoCleanup}
                          onChange={(e) => setDataSettings({
                            ...dataSettings,
                            autoCleanup: e.target.checked
                          })}
                        />
                      }
                      label="자동 정리 활성화"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    내보내기 설정
                  </Typography>
                  <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel>기본 내보내기 형식</InputLabel>
                    <Select
                      value={dataSettings.exportFormat}
                      onChange={(e) => setDataSettings({
                        ...dataSettings,
                        exportFormat: e.target.value
                      })}
                      label="기본 내보내기 형식"
                    >
                      <MenuItem value="xlsx">Excel (XLSX)</MenuItem>
                      <MenuItem value="csv">CSV</MenuItem>
                      <MenuItem value="json">JSON</MenuItem>
                    </Select>
                  </FormControl>
                  <Box sx={{ mt: 3 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={dataSettings.includeRawData}
                          onChange={(e) => setDataSettings({
                            ...dataSettings,
                            includeRawData: e.target.checked
                          })}
                        />
                      }
                      label="원본 데이터 포함"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ color: 'error.main' }}>
                    위험 구역
                  </Typography>
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    아래 작업은 되돌릴 수 없습니다. 신중하게 진행해주세요.
                  </Alert>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={handleResetData}
                    >
                      모든 데이터 초기화
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => handleSaveSettings('데이터 관리')}
                >
                  저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 테마 설정 */}
        <TabPanel value={activeTab} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    테마 설정
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="다크 모드"
                        secondary="어두운 테마를 사용합니다"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={themeSettings.darkMode}
                          onChange={(e) => setThemeSettings({
                            ...themeSettings,
                            darkMode: e.target.checked
                          })}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                  <Divider sx={{ my: 2 }} />
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>글꼴 크기</InputLabel>
                        <Select
                          value={themeSettings.fontSize}
                          onChange={(e) => setThemeSettings({
                            ...themeSettings,
                            fontSize: e.target.value
                          })}
                          label="글꼴 크기"
                        >
                          <MenuItem value="small">작게</MenuItem>
                          <MenuItem value="medium">보통</MenuItem>
                          <MenuItem value="large">크게</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => handleSaveSettings('테마')}
                >
                  저장
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* 확인 다이얼로그 */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, action: '' })}
      >
        <DialogTitle>확인</DialogTitle>
        <DialogContent>
          <Typography>
            정말로 모든 데이터를 초기화하시겠습니까? 이 작업은 되돌릴 수 없습니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false, action: '' })}>
            취소
          </Button>
          <Button onClick={handleConfirmAction} color="error" variant="contained">
            초기화
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;