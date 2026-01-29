import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import { Truck } from 'lucide-react';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({ username: '', password: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    const newErrors = { username: '', password: '' };
    if (!credentials.username) newErrors.username = '사용자 이름을 입력하세요';
    if (!credentials.password) newErrors.password = '비밀번호를 입력하세요';
    
    if (newErrors.username || newErrors.password) {
      setErrors(newErrors);
      return;
    }

    try {
      await login(credentials.username, credentials.password);
      navigate('/dashboard');
    } catch (error) {
      // Error handled by store
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="bg-blue-600 p-4 rounded-full">
            <Truck className="text-white" size={48} />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
          Cold Chain Dispatch
        </h1>
        <p className="text-center text-gray-600 mb-8">
          냉동·냉장 화물 배차 시스템
        </p>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="사용자 이름"
            type="text"
            placeholder="사용자 이름을 입력하세요"
            value={credentials.username}
            onChange={(e) => {
              setCredentials({ ...credentials, username: e.target.value });
              setErrors({ ...errors, username: '' });
            }}
            error={errors.username}
            disabled={isLoading}
          />

          <Input
            label="비밀번호"
            type="password"
            placeholder="비밀번호를 입력하세요"
            value={credentials.password}
            onChange={(e) => {
              setCredentials({ ...credentials, password: e.target.value });
              setErrors({ ...errors, password: '' });
            }}
            error={errors.password}
            disabled={isLoading}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            isLoading={isLoading}
          >
            로그인
          </Button>
        </form>

        {/* Demo credentials */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-2">데모 계정:</p>
          <p className="text-xs text-gray-500">관리자: admin / admin123</p>
          <p className="text-xs text-gray-500">배차 담당자: dispatcher / dispatcher123</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
