import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Truck, ArrowLeft, ChevronRight, ChevronLeft, Check } from 'lucide-react';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import api from '../api/client';
import { toast } from 'react-hot-toast';

interface SignupFormData {
  // 계정 정보
  username: string;
  password: string;
  confirmPassword: string;
  role: string;
  
  // 기본 인적사항
  name: string;
  name_en: string;
  phone: string;
  address: string;
  emergency_contact: string;
  
  // 조직 정보
  employment_type: string;
  department: string;
  position: string;
  
  // 근무 정보
  hire_date: string;
  
  // 운전면허
  license_type: string;
  license_number: string;
  license_issue_date: string;
  
  // 화물운송자격증
  has_cargo_license: boolean;
  cargo_license_number: string;
  cargo_license_issue_date: string;
  cargo_license_expiry_date: string;
  
  // 지게차 자격
  can_drive_forklift: boolean;
  has_forklift_certificate: boolean;
  forklift_certificate_number: string;
  forklift_certificate_issue_date: string;
  forklift_certificate_expiry_date: string;
}

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  
  const [formData, setFormData] = useState<SignupFormData>({
    // 계정 정보
    username: '',
    password: '',
    confirmPassword: '',
    role: 'DRIVER',
    
    // 기본 인적사항
    name: '',
    name_en: '',
    phone: '',
    address: '',
    emergency_contact: '',
    
    // 조직 정보
    employment_type: 'FULL_TIME',
    department: '',
    position: '',
    
    // 근무 정보
    hire_date: new Date().toISOString().split('T')[0],
    
    // 운전면허
    license_type: '',
    license_number: '',
    license_issue_date: '',
    
    // 화물운송자격증
    has_cargo_license: false,
    cargo_license_number: '',
    cargo_license_issue_date: '',
    cargo_license_expiry_date: '',
    
    // 지게차 자격
    can_drive_forklift: false,
    has_forklift_certificate: false,
    forklift_certificate_number: '',
    forklift_certificate_issue_date: '',
    forklift_certificate_expiry_date: ''
  });

  const [errors, setErrors] = useState<Partial<Record<keyof SignupFormData, string>>>({});

  const steps = [
    { number: 1, title: '계정 정보', description: '로그인 정보 입력' },
    { number: 2, title: '기본 정보', description: '인적사항 입력' },
    { number: 3, title: '조직/근무', description: '조직 및 근무 정보' },
    { number: 4, title: '자격증', description: '운전면허 및 자격증' }
  ];

  const handleChange = (field: keyof SignupFormData, value: any) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  // 전화번호 자동 하이픈 포맷팅
  const formatPhoneNumber = (value: string): string => {
    // 숫자만 추출
    const numbers = value.replace(/[^\d]/g, '');
    
    // 길이에 따라 포맷팅
    if (numbers.length <= 3) {
      return numbers;
    } else if (numbers.length <= 7) {
      return `${numbers.slice(0, 3)}-${numbers.slice(3)}`;
    } else if (numbers.length <= 11) {
      return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(7)}`;
    }
    // 11자리 초과는 잘라냄
    return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(7, 11)}`;
  };

  const handlePhoneChange = (field: 'phone' | 'emergency_contact', value: string) => {
    const formatted = formatPhoneNumber(value);
    setFormData({ ...formData, [field]: formatted });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  const validateStep1 = (): boolean => {
    const newErrors: Partial<Record<keyof SignupFormData, string>> = {};
    
    if (!formData.username || formData.username.length < 3) {
      newErrors.username = '사용자명은 최소 3자 이상이어야 합니다';
    }
    
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = '비밀번호는 최소 6자 이상이어야 합니다';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호가 일치하지 않습니다';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: Partial<Record<keyof SignupFormData, string>> = {};
    
    if (!formData.name || formData.name.length < 2) {
      newErrors.name = '이름을 입력하세요';
    }
    
    if (!formData.phone || !/^\d{3}-\d{4}-\d{4}$/.test(formData.phone)) {
      newErrors.phone = '올바른 전화번호를 입력하세요 (예: 010-1234-5678)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = (): boolean => {
    const newErrors: Partial<Record<keyof SignupFormData, string>> = {};
    
    if (!formData.hire_date) {
      newErrors.hire_date = '입사일을 선택하세요';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = (e?: React.MouseEvent) => {
    // 이벤트가 있으면 기본 동작 방지
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    let isValid = false;
    
    switch (currentStep) {
      case 1:
        isValid = validateStep1();
        break;
      case 2:
        isValid = validateStep2();
        break;
      case 3:
        isValid = validateStep3();
        break;
      case 4:
        // Step 4에서는 handleNext가 호출되지 않아야 함
        console.warn('handleNext called on step 4 - this should not happen');
        return;
      default:
        isValid = true;
    }
    
    if (isValid && currentStep < 4) {
      console.log('Moving to step:', currentStep + 1);
      setCurrentStep(currentStep + 1);
    } else if (!isValid) {
      console.log('Validation failed for step:', currentStep);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateStep1() || !validateStep2() || !validateStep3()) {
      toast.error('필수 정보를 모두 입력해주세요');
      return;
    }

    setIsLoading(true);
    
    try {
      const { confirmPassword, ...signupData } = formData;
      
      // 빈 문자열을 null로 변환 (선택적 날짜 필드들)
      const cleanedData = {
        ...signupData,
        name_en: signupData.name_en || undefined,
        address: signupData.address || undefined,
        emergency_contact: signupData.emergency_contact || undefined,
        department: signupData.department || undefined,
        position: signupData.position || undefined,
        license_type: signupData.license_type || undefined,
        license_number: signupData.license_number || undefined,
        license_issue_date: signupData.license_issue_date || undefined,
        cargo_license_number: signupData.cargo_license_number || undefined,
        cargo_license_issue_date: signupData.cargo_license_issue_date || undefined,
        cargo_license_expiry_date: signupData.cargo_license_expiry_date || undefined,
        forklift_certificate_number: signupData.forklift_certificate_number || undefined,
        forklift_certificate_issue_date: signupData.forklift_certificate_issue_date || undefined,
        forklift_certificate_expiry_date: signupData.forklift_certificate_expiry_date || undefined,
      };
      
      await api.post('/auth/signup', cleanedData);
      
      toast.success('회원가입이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.');
      
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

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: 'linear-gradient(to bottom right, #2563eb, #1e40af)'
      }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl p-8">
        {/* Header */}
        <button
          onClick={() => navigate('/login')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          로그인으로 돌아가기
        </button>

        <div className="flex justify-center mb-6">
          <div 
            className="p-3 rounded-full"
            style={{ backgroundColor: '#2563eb' }}
          >
            <Truck className="text-white" size={36} />
          </div>
        </div>

        <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
          회원가입
        </h1>
        <p className="text-center text-gray-600 mb-8">
          인사카드 양식으로 회원 정보를 입력하세요
        </p>

        {/* Step Indicator */}
        <div className="mb-8">
          <div className="flex justify-between">
            {steps.map((step) => (
              <div key={step.number} className="flex-1">
                <div className="flex flex-col items-center">
                  <div className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors
                    ${currentStep >= step.number 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-500'}
                  `}>
                    {currentStep > step.number ? <Check size={20} /> : step.number}
                  </div>
                  <div className="text-center mt-2">
                    <div className={`text-sm font-medium ${currentStep >= step.number ? 'text-blue-600' : 'text-gray-500'}`}>
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-400">
                      {step.description}
                    </div>
                  </div>
                </div>
                {step.number < 4 && (
                  <div className={`
                    h-1 w-full mt-5 transition-colors
                    ${currentStep > step.number ? 'bg-blue-600' : 'bg-gray-200'}
                  `} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            // currentStep이 4일 때만 실제 제출 허용
            if (currentStep === 4) {
              handleSubmit(e);
            } else {
              // Step 1-3에서는 절대 제출되지 않도록 명시적으로 차단
              console.log('Form submission blocked - current step:', currentStep);
            }
          }}
          onKeyDown={(e) => {
            // Enter 키로 폼 제출 방지 (마지막 단계의 제출 버튼만 허용)
            if (e.key === 'Enter' && currentStep < 4) {
              e.preventDefault();
              e.stopPropagation();
            }
          }}
        >
          {/* Step 1: 계정 정보 */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-4">계정 정보</h3>
              
              <Input
                label="사용자명 *"
                type="text"
                placeholder="로그인 시 사용할 아이디 (3자 이상)"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                error={errors.username}
                disabled={isLoading}
              />

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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  시스템 권한 *
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
          )}

          {/* Step 2: 기본 정보 */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-4">기본 인적사항</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="이름 *"
                  type="text"
                  placeholder="홍길동"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  error={errors.name}
                  disabled={isLoading}
                />

                <Input
                  label="영문명"
                  type="text"
                  placeholder="Hong Gildong"
                  value={formData.name_en}
                  onChange={(e) => handleChange('name_en', e.target.value)}
                  disabled={isLoading}
                />

                <Input
                  label="전화번호 *"
                  type="text"
                  placeholder="010-1234-5678"
                  value={formData.phone}
                  onChange={(e) => handlePhoneChange('phone', e.target.value)}
                  error={errors.phone}
                  disabled={isLoading}
                  helperText="숫자만 입력하면 자동으로 하이픈이 추가됩니다"
                />

                <Input
                  label="비상연락처"
                  type="text"
                  placeholder="010-9876-5432"
                  value={formData.emergency_contact}
                  onChange={(e) => handlePhoneChange('emergency_contact', e.target.value)}
                  disabled={isLoading}
                  helperText="숫자만 입력하면 자동으로 하이픈이 추가됩니다"
                />
              </div>

              <Input
                label="주소"
                type="text"
                placeholder="서울시 강남구..."
                value={formData.address}
                onChange={(e) => handleChange('address', e.target.value)}
                disabled={isLoading}
              />
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
                <p className="text-sm text-blue-800">
                  💡 사원번호는 관리자가 승인 시 부여합니다
                </p>
              </div>
            </div>
          )}

          {/* Step 3: 조직/근무 정보 */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-4">조직 및 근무 정보</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    고용 형태 *
                  </label>
                  <select
                    value={formData.employment_type}
                    onChange={(e) => handleChange('employment_type', e.target.value)}
                    disabled={isLoading}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="FULL_TIME">정규직</option>
                    <option value="CONTRACT">계약직</option>
                    <option value="PART_TIME">파트타임</option>
                    <option value="DAILY">일용직</option>
                  </select>
                </div>

                <Input
                  label="부서"
                  type="text"
                  placeholder="운송부, 관리부 등"
                  value={formData.department}
                  onChange={(e) => handleChange('department', e.target.value)}
                  disabled={isLoading}
                />

                <Input
                  label="직책"
                  type="text"
                  placeholder="팀장, 주임 등"
                  value={formData.position}
                  onChange={(e) => handleChange('position', e.target.value)}
                  disabled={isLoading}
                />

                <Input
                  label="입사일 *"
                  type="date"
                  value={formData.hire_date}
                  onChange={(e) => handleChange('hire_date', e.target.value)}
                  error={errors.hire_date}
                  disabled={isLoading}
                />
              </div>
            </div>
          )}

          {/* Step 4: 자격증 정보 */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold mb-4">운전면허 및 자격증</h3>
              
              {/* 운전면허 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium mb-3">운전면허</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input
                    label="면허 종류"
                    type="text"
                    placeholder="1종 대형, 2종 보통 등"
                    value={formData.license_type}
                    onChange={(e) => handleChange('license_type', e.target.value)}
                    disabled={isLoading}
                  />

                  <Input
                    label="면허 번호"
                    type="text"
                    placeholder="11-12-345678-90"
                    value={formData.license_number}
                    onChange={(e) => handleChange('license_number', e.target.value)}
                    disabled={isLoading}
                  />

                  <Input
                    label="발급일"
                    type="date"
                    value={formData.license_issue_date}
                    onChange={(e) => handleChange('license_issue_date', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* 화물운송자격증 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    id="has_cargo_license"
                    checked={formData.has_cargo_license}
                    onChange={(e) => handleChange('has_cargo_license', e.target.checked)}
                    disabled={isLoading}
                    className="mr-2"
                  />
                  <label htmlFor="has_cargo_license" className="font-medium">
                    화물운송자격증 보유
                  </label>
                </div>
                
                {formData.has_cargo_license && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="자격증 번호"
                      type="text"
                      placeholder="CARGO-123456"
                      value={formData.cargo_license_number}
                      onChange={(e) => handleChange('cargo_license_number', e.target.value)}
                      disabled={isLoading}
                    />

                    <Input
                      label="발급일"
                      type="date"
                      value={formData.cargo_license_issue_date}
                      onChange={(e) => handleChange('cargo_license_issue_date', e.target.value)}
                      disabled={isLoading}
                    />

                    <Input
                      label="만료일"
                      type="date"
                      value={formData.cargo_license_expiry_date}
                      onChange={(e) => handleChange('cargo_license_expiry_date', e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                )}
              </div>

              {/* 지게차 자격 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="can_drive_forklift"
                      checked={formData.can_drive_forklift}
                      onChange={(e) => handleChange('can_drive_forklift', e.target.checked)}
                      disabled={isLoading}
                      className="mr-2"
                    />
                    <label htmlFor="can_drive_forklift" className="font-medium">
                      지게차 운전 가능
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="has_forklift_certificate"
                      checked={formData.has_forklift_certificate}
                      onChange={(e) => handleChange('has_forklift_certificate', e.target.checked)}
                      disabled={isLoading}
                      className="mr-2"
                    />
                    <label htmlFor="has_forklift_certificate" className="font-medium">
                      지게차 운전 자격증 보유
                    </label>
                  </div>
                </div>
                
                {formData.has_forklift_certificate && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <Input
                      label="자격증 번호"
                      type="text"
                      placeholder="FORK-123456"
                      value={formData.forklift_certificate_number}
                      onChange={(e) => handleChange('forklift_certificate_number', e.target.value)}
                      disabled={isLoading}
                    />

                    <Input
                      label="발급일"
                      type="date"
                      value={formData.forklift_certificate_issue_date}
                      onChange={(e) => handleChange('forklift_certificate_issue_date', e.target.value)}
                      disabled={isLoading}
                    />

                    <Input
                      label="만료일"
                      type="date"
                      value={formData.forklift_certificate_expiry_date}
                      onChange={(e) => handleChange('forklift_certificate_expiry_date', e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <Button
              type="button"
              variant="secondary"
              onClick={currentStep === 1 ? () => navigate('/login') : handlePrev}
              disabled={isLoading}
            >
              <ChevronLeft size={20} className="mr-1" />
              {currentStep === 1 ? '취소' : '이전'}
            </Button>

            {currentStep < 4 ? (
              <Button
                type="button"
                variant="primary"
                onClick={handleNext}
                disabled={isLoading}
              >
                다음
                <ChevronRight size={20} className="ml-1" />
              </Button>
            ) : (
              <Button
                type="submit"
                variant="primary"
                isLoading={isLoading}
              >
                <Check size={20} className="mr-1" />
                회원가입 완료
              </Button>
            )}
          </div>
        </form>

        {/* Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
          <p className="text-sm text-yellow-800 font-medium mb-2">
            ⚠️ 회원가입 안내
          </p>
          <ul className="text-xs text-yellow-700 space-y-1 list-disc list-inside">
            <li>인사카드 양식으로 모든 정보를 입력해주세요</li>
            <li>가입 신청 후 총괄관리자 또는 운영부의 승인이 필요합니다</li>
            <li>승인 완료 시 이메일로 안내해드립니다</li>
            <li>승인 후 입력하신 정보가 인사카드에 자동으로 등록됩니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
