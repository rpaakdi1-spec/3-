import React from 'react';
import type { RecurringFrequency } from '../../types';

interface FrequencySelectorProps {
  value: RecurringFrequency;
  onChange: (frequency: RecurringFrequency) => void;
  className?: string;
}

const FREQUENCY_OPTIONS: { value: RecurringFrequency; label: string; description: string }[] = [
  { value: 'DAILY', label: '매일', description: '평일/주말 매일 반복' },
  { value: 'WEEKLY', label: '매주', description: '특정 요일에 반복' },
  { value: 'MONTHLY', label: '매월', description: '특정 날짜에 반복' },
  { value: 'CUSTOM', label: '사용자 지정', description: '특정 날짜 배열' },
];

export const FrequencySelector: React.FC<FrequencySelectorProps> = ({
  value,
  onChange,
  className = '',
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      <label className="block text-sm font-medium text-gray-700">
        반복 주기 <span className="text-red-500">*</span>
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {FREQUENCY_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`
              relative flex flex-col items-start p-4 border-2 rounded-lg transition-all
              ${
                value === option.value
                  ? 'border-indigo-600 bg-indigo-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }
            `}
          >
            <div className="flex items-center justify-between w-full mb-2">
              <span
                className={`font-semibold ${
                  value === option.value ? 'text-indigo-700' : 'text-gray-700'
                }`}
              >
                {option.label}
              </span>
              {value === option.value && (
                <svg
                  className="w-5 h-5 text-indigo-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </div>
            <p
              className={`text-sm ${
                value === option.value ? 'text-indigo-600' : 'text-gray-500'
              }`}
            >
              {option.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default FrequencySelector;
