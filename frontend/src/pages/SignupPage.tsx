import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Truck, ArrowLeft } from 'lucide-react';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import api from '../api/client';
import { toast } from 'react-hot-toast';

interface SignupForm {
  username: string;
  password: string;
  confirmPassword: string;
  email: string;
  full_name: string;
  phone: string;
  employee_code: string;
  role: string;
}

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<SignupForm>({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    full_name: '',
    phone: '',
    employee_code: '',
    role: 'DRIVER'
  });
  const [errors, setErrors] = useState<Partial<SignupForm>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<SignupForm> = {};
    
    if (!formData.username || formData.username.length < 3) {
      newErrors.username = '사용자명은 최소 3자 이상이어야 합니다';
    }
    
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = '비밀번호는 최소 6자 이상이어야 합니다';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호가 일치하지 않습니다';
    }
    
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '올바른 이메일 주소를 입력하세요';
    }
    
    if (!formData.full_name || formData.full_name.length < 2) {
      newErrors.full_name = '이름을 입력하세요';
    }
    
    if (!formData.phone || !/^\d{3}-\d{3,4}-\d{4}$/.test(formData.phone)) {
      newErrors.phone = '올바른 전화번호를 입력하세요 (예: 010-1234-5678)';
    }
    
    if (!formData.employee_code) {
      newErrors.employee_code = '직원번호를 입력하세요';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    
    try {
      const { confirmPassword, ...signupData } = formData;
      await api.post('/auth/signup', signupData);
      
      toast.success('회원가입이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.');
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (error: any) {
      console.error('Signup error:', error);
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          toast.error(error.response.data.detail);
        } else if (Array.isArray(error.response.data.detail)) {
          const errorMessages = error.response.data.detail
            .map((err: any) => err.msg || JSON.stringify(err))
            .join(', ');
          toast.error(errorMessages);
        }
      } else {
        toast.error('회원가입 중 오류가 발생했습니다');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof SignupForm, value: string) => {
    setFormData({ ...formData, [field]: value });
    // Clear error for this field
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: 'linear-gradient(to bottom right, #2563eb, #1e40af)'
      }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8">
        {/* Back button */}
        <button
          onClick={() => navigate('/login')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          로그인으로 돌아가기
        </button>

        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div 
            className="p-3 rounded-full"
            style={{ backgroundColor: '#2563eb' }}
          >
            <Truck className="text-white" size={36} />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
          회원가입
        </h1>
        <p className="text-center text-gray-600 mb-6">
          인사카드에 등록된 정보로 가입하세요
        </p>

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="사용자명 *"
              type="text"
              placeholder="3자 이상"
              value={formData.username}
              onChange={(e) => handleChange('username', e.target.value)}
              error={errors.username}
              disabled={isLoading}
            />

            <Input
              label="직원번호 *"
              type="text"
              placeholder="예: D001, A001"
              value={formData.employee_code}
              onChange={(e) => handleChange('employee_code', e.target.value)}
              error={errors.employee_code}
              disabled={isLoading}
              helperText="인사카드에 등록된 직원번호"
            />

            <Input
              label="이름 *"
              type="text"
              placeholder="홍길동"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              error={errors.full_name}
              disabled={isLoading}
              helperText="인사카드에 등록된 이름과 일치해야 합니다"
            />

            <Input
              label="전화번호 *"
              type="text"
              placeholder="010-1234-5678"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              error={errors.phone}
              disabled={isLoading}
              helperText="인사카드에 등록된 번호와 일치해야 합니다"
            />

            <Input
              label="이메일 *"
              type="email"
              placeholder="example@company.com"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              error={errors.email}
              disabled={isLoading}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                권한 *
              </label>
              <select
                value={formData.role}
                onChange={(e) => handleChange('role', e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="DRIVER">운전사원</option>
                <option value="VEHICLE_MANAGER">차량관리부</option>
                <option value="ADMIN">운영부</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                총괄관리자는 관리자가 직접 승인합니다
              </p>
            </div>
          </div>

          <Input
            label="비밀번호 *"
            type="password"
            placeholder="6자 이상"
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            error={errors.password}
            disabled={isLoading}
          />

          <Input
            label="비밀번호 확인 *"
            type="password"
            placeholder="비밀번호 재입력"
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            error={errors.confirmPassword}
            disabled={isLoading}
          />

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
            <p className="text-sm text-yellow-800 font-medium mb-2">
              ⚠️ 회원가입 안내
            </p>
            <ul className="text-xs text-yellow-700 space-y-1 list-disc list-inside">
              <li>인사카드에 등록된 직원번호, 이름, 전화번호를 입력하세요</li>
              <li>가입 신청 후 총괄관리자 또는 운영부의 승인이 필요합니다</li>
              <li>승인 완료 시 이메일로 안내해드립니다</li>
            </ul>
          </div>

          <div className="flex gap-3 mt-6">
            <Button
              type="button"
              variant="secondary"
              size="lg"
              className="flex-1"
              onClick={() => navigate('/login')}
              disabled={isLoading}
            >
              취소
            </Button>
            
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="flex-1"
              isLoading={isLoading}
            >
              회원가입
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;
