import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  DatePicker,
  LocalizationProvider,
} from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import koLocale from 'date-fns/locale/ko';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  LocalGasStation as GasIcon,
  CalendarToday as CalendarIcon,
  DirectionsCar as CarIcon,
} from '@mui/icons-material';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface DailyMileage {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  date: string;
  total_distance_km: number;
  total_driving_minutes: number;
  engine_on_minutes: number;
  idle_minutes: number;
  max_speed_kmh: number;
  avg_speed_kmh: number;
  gps_point_count: number;
  start_time: string | null;
  end_time: string | null;
  calculation_method: string;
}

interface MileageSummary {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  total_distance_km: number;
  total_driving_minutes?: number;
  total_driving_hours?: number;
  total_idle_minutes?: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  driving_days: number;
  avg_distance_per_day: number;
}

interface Statistics {
  vehicle_count: number;
  total_distance_km: number;
  total_driving_hours: number;
  avg_speed_kmh: number;
  record_count: number;
}

const VehicleMileagePage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedDate, setSelectedDate] = useState<Date>(subDays(new Date(), 1));
  const [startDate, setStartDate] = useState<Date>(startOfMonth(new Date()));
  const [endDate, setEndDate] = useState<Date>(endOfMonth(new Date()));
  
  const [dailyMileages, setDailyMileages] = useState<DailyMileage[]>([]);
  const [weeklySummary, setWeeklySummary] = useState<MileageSummary[]>([]);
  const [monthlySummary, setMonthlySummary] = useState<MileageSummary[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 일별 주행거리 조회
  const fetchDailyMileages = async (date: Date) => {
    setLoading(true);
    setError(null);
    try {
      const dateStr = format(date, 'yyyy-MM-dd');
      const response = await axios.get(`${API_BASE_URL}/api/v1/vehicle-mileage/daily`, {
        params: { target_date: dateStr },
      });
      setDailyMileages(response.data.mileages || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || '일별 주행거리 조회 실패');
      console.error('Failed to fetch daily mileages:', err);
    } finally {
      setLoading(false);
    }
  };

  // 주간 주행거리 조회
  const fetchWeeklySummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/vehicle-mileage/weekly`);
      setWeeklySummary(response.data.summary || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || '주간 주행거리 조회 실패');
      console.error('Failed to fetch weekly summary:', err);
    } finally {
      setLoading(false);
    }
  };

  // 월별 주행거리 조회
  const fetchMonthlySummary = async (year: number, month: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/vehicle-mileage/monthly`, {
        params: { year, month },
      });
      setMonthlySummary(response.data.summary || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || '월별 주행거리 조회 실패');
      console.error('Failed to fetch monthly summary:', err);
    } finally {
      setLoading(false);
    }
  };

  // 통계 조회
  const fetchStatistics = async (start: Date, end: Date) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/vehicle-mileage/statistics`, {
        params: {
          start_date: format(start, 'yyyy-MM-dd'),
          end_date: format(end, 'yyyy-MM-dd'),
        },
      });
      setStatistics(response.data.total_statistics || null);
    } catch (err: any) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  // 탭 변경 시 데이터 로드
  useEffect(() => {
    if (tabValue === 0) {
      fetchDailyMileages(selectedDate);
    } else if (tabValue === 1) {
      fetchWeeklySummary();
    } else if (tabValue === 2) {
      const year = selectedDate.getFullYear();
      const month = selectedDate.getMonth() + 1;
      fetchMonthlySummary(year, month);
    }
  }, [tabValue]);

  // 통계는 항상 로드
  useEffect(() => {
    fetchStatistics(startDate, endDate);
  }, [startDate, endDate]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    if (tabValue === 0) {
      fetchDailyMileages(selectedDate);
    } else if (tabValue === 1) {
      fetchWeeklySummary();
    } else if (tabValue === 2) {
      const year = selectedDate.getFullYear();
      const month = selectedDate.getMonth() + 1;
      fetchMonthlySummary(year, month);
    }
  };

  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}시간 ${mins}분`;
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={koLocale}>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            <CarIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            차량 주행거리 관리
          </Typography>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
          >
            새로고침
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* 통계 카드 */}
        {statistics && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CarIcon color="primary" sx={{ mr: 1 }} />
                    <Typography color="text.secondary" variant="body2">
                      운행 차량
                    </Typography>
                  </Box>
                  <Typography variant="h4">{statistics.vehicle_count}대</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                    <Typography color="text.secondary" variant="body2">
                      총 주행거리
                    </Typography>
                  </Box>
                  <Typography variant="h4">{statistics.total_distance_km.toFixed(1)}km</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarIcon color="info" sx={{ mr: 1 }} />
                    <Typography color="text.secondary" variant="body2">
                      총 운행시간
                    </Typography>
                  </Box>
                  <Typography variant="h4">{statistics.total_driving_hours.toFixed(1)}h</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <SpeedIcon color="warning" sx={{ mr: 1 }} />
                    <Typography color="text.secondary" variant="body2">
                      평균 속도
                    </Typography>
                  </Box>
                  <Typography variant="h4">{statistics.avg_speed_kmh.toFixed(1)}km/h</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* 탭 */}
        <Paper sx={{ mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="일별 조회" />
            <Tab label="주간 통계" />
            <Tab label="월별 통계" />
          </Tabs>
        </Paper>

        {/* 일별 조회 */}
        {tabValue === 0 && (
          <Box>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <DatePicker
                label="조회 날짜"
                value={selectedDate}
                onChange={(newValue) => {
                  if (newValue) {
                    setSelectedDate(newValue);
                    fetchDailyMileages(newValue);
                  }
                }}
                slotProps={{ textField: { size: 'small' } }}
              />
            </Box>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell>차량번호</TableCell>
                      <TableCell align="right">주행거리</TableCell>
                      <TableCell align="right">운행시간</TableCell>
                      <TableCell align="right">평균속도</TableCell>
                      <TableCell align="right">최고속도</TableCell>
                      <TableCell align="right">공회전</TableCell>
                      <TableCell align="right">GPS포인트</TableCell>
                      <TableCell>운행시작</TableCell>
                      <TableCell>운행종료</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dailyMileages.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} align="center">
                          데이터가 없습니다
                        </TableCell>
                      </TableRow>
                    ) : (
                      dailyMileages.map((row) => (
                        <TableRow key={row.vehicle_id} hover>
                          <TableCell>
                            <Typography fontWeight="bold">{row.plate_number}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {row.vehicle_code}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography fontWeight="bold" color="primary.main">
                              {row.total_distance_km.toFixed(1)} km
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {formatDuration(row.total_driving_minutes)}
                          </TableCell>
                          <TableCell align="right">{row.avg_speed_kmh.toFixed(1)} km/h</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${row.max_speed_kmh} km/h`}
                              size="small"
                              color={row.max_speed_kmh > 100 ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="right">{row.idle_minutes}분</TableCell>
                          <TableCell align="right">{row.gps_point_count}개</TableCell>
                          <TableCell>
                            {row.start_time ? format(new Date(row.start_time), 'HH:mm') : '-'}
                          </TableCell>
                          <TableCell>
                            {row.end_time ? format(new Date(row.end_time), 'HH:mm') : '-'}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}

        {/* 주간 통계 */}
        {tabValue === 1 && (
          <Box>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell>차량번호</TableCell>
                      <TableCell align="right">총 주행거리</TableCell>
                      <TableCell align="right">총 운행시간</TableCell>
                      <TableCell align="right">평균속도</TableCell>
                      <TableCell align="right">최고속도</TableCell>
                      <TableCell align="right">운행일수</TableCell>
                      <TableCell align="right">1일 평균</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {weeklySummary.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          데이터가 없습니다
                        </TableCell>
                      </TableRow>
                    ) : (
                      weeklySummary.map((row) => (
                        <TableRow key={row.vehicle_id} hover>
                          <TableCell>
                            <Typography fontWeight="bold">{row.plate_number}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography fontWeight="bold" color="primary.main">
                              {row.total_distance_km.toFixed(1)} km
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {formatDuration(row.total_driving_minutes || 0)}
                          </TableCell>
                          <TableCell align="right">{row.avg_speed_kmh.toFixed(1)} km/h</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${row.max_speed_kmh} km/h`}
                              size="small"
                              color={row.max_speed_kmh > 100 ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="right">{row.driving_days}일</TableCell>
                          <TableCell align="right">
                            {row.avg_distance_per_day.toFixed(1)} km
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}

        {/* 월별 통계 */}
        {tabValue === 2 && (
          <Box>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <DatePicker
                label="조회 월"
                views={['year', 'month']}
                value={selectedDate}
                onChange={(newValue) => {
                  if (newValue) {
                    setSelectedDate(newValue);
                    const year = newValue.getFullYear();
                    const month = newValue.getMonth() + 1;
                    fetchMonthlySummary(year, month);
                  }
                }}
                slotProps={{ textField: { size: 'small' } }}
              />
            </Box>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell>차량번호</TableCell>
                      <TableCell align="right">총 주행거리</TableCell>
                      <TableCell align="right">총 운행시간</TableCell>
                      <TableCell align="right">공회전</TableCell>
                      <TableCell align="right">평균속도</TableCell>
                      <TableCell align="right">최고속도</TableCell>
                      <TableCell align="right">운행일수</TableCell>
                      <TableCell align="right">1일 평균</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {monthlySummary.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          데이터가 없습니다
                        </TableCell>
                      </TableRow>
                    ) : (
                      monthlySummary.map((row) => (
                        <TableRow key={row.vehicle_id} hover>
                          <TableCell>
                            <Typography fontWeight="bold">{row.plate_number}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography fontWeight="bold" color="primary.main">
                              {row.total_distance_km.toFixed(1)} km
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {row.total_driving_hours?.toFixed(1)} h
                          </TableCell>
                          <TableCell align="right">{row.total_idle_minutes}분</TableCell>
                          <TableCell align="right">{row.avg_speed_kmh.toFixed(1)} km/h</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${row.max_speed_kmh} km/h`}
                              size="small"
                              color={row.max_speed_kmh > 100 ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="right">{row.driving_days}일</TableCell>
                          <TableCell align="right">
                            {row.avg_distance_per_day.toFixed(1)} km
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Box>
    </LocalizationProvider>
  );
};

export default VehicleMileagePage;
