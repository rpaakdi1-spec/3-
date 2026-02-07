import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Download Financial Dashboard PDF Report
 * @param start_date Start date (YYYY-MM-DD)
 * @param end_date End date (YYYY-MM-DD)
 */
export const downloadFinancialDashboardPDF = async (
  start_date: string,
  end_date: string
): Promise<void> => {
  try {
    const response = await api.post(
      '/api/v1/reports/financial-dashboard/pdf',
      null,
      {
        params: { start_date, end_date },
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf'
        }
      }
    );

    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/pdf' });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `financial_dashboard_${start_date}_${end_date}.pdf`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('✅ PDF 리포트 다운로드 완료:', link.download);
  } catch (error) {
    console.error('❌ PDF 다운로드 실패:', error);
    throw error;
  }
};

/**
 * Download Financial Dashboard Excel Report
 * @param start_date Start date (YYYY-MM-DD)
 * @param end_date End date (YYYY-MM-DD)
 */
export const downloadFinancialDashboardExcel = async (
  start_date: string,
  end_date: string
): Promise<void> => {
  try {
    const response = await api.post(
      '/api/v1/reports/financial-dashboard/excel',
      null,
      {
        params: { start_date, end_date },
        responseType: 'blob',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      }
    );

    // Create blob from response
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `financial_dashboard_${start_date}_${end_date}.xlsx`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('✅ Excel 리포트 다운로드 완료:', link.download);
  } catch (error) {
    console.error('❌ Excel 다운로드 실패:', error);
    throw error;
  }
};
