import React from 'react';

interface WeekdayPickerProps {
  value: number; // Bit flags: Mon=1, Tue=2, Wed=4, Thu=8, Fri=16, Sat=32, Sun=64
  onChange: (weekdays: number) => void;
  className?: string;
}

const WEEKDAYS = [
  { label: '월', value: 1, fullName: '월요일' },
  { label: '화', value: 2, fullName: '화요일' },
  { label: '수', value: 4, fullName: '수요일' },
  { label: '목', value: 8, fullName: '목요일' },
  { label: '금', value: 16, fullName: '금요일' },
  { label: '토', value: 32, fullName: '토요일' },
  { label: '일', value: 64, fullName: '일요일' },
];

export const WeekdayPicker: React.FC<WeekdayPickerProps> = ({
  value,
  onChange,
  className = '',
}) => {
  const toggleWeekday = (dayValue: number) => {
    const newValue = value ^ dayValue; // XOR to toggle bit
    onChange(newValue);
  };

  const isSelected = (dayValue: number): boolean => {
    return (value & dayValue) !== 0;
  };

  const selectAll = () => {
    onChange(127); // 1 + 2 + 4 + 8 + 16 + 32 + 64 = 127 (all days)
  };

  const selectWeekdays = () => {
    onChange(31); // 1 + 2 + 4 + 8 + 16 = 31 (Mon-Fri)
  };

  const selectWeekends = () => {
    onChange(96); // 32 + 64 = 96 (Sat-Sun)
  };

  const clearAll = () => {
    onChange(0);
  };

  const selectedCount = WEEKDAYS.filter((day) => isSelected(day.value)).length;

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          반복 요일 선택 <span className="text-red-500">*</span>
          {selectedCount > 0 && (
            <span className="ml-2 text-xs text-gray-500">
              ({selectedCount}개 선택됨)
            </span>
          )}
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={selectWeekdays}
            className="text-xs text-indigo-600 hover:text-indigo-700 underline"
          >
            평일
          </button>
          <button
            type="button"
            onClick={selectWeekends}
            className="text-xs text-indigo-600 hover:text-indigo-700 underline"
          >
            주말
          </button>
          <button
            type="button"
            onClick={selectAll}
            className="text-xs text-indigo-600 hover:text-indigo-700 underline"
          >
            전체
          </button>
          <button
            type="button"
            onClick={clearAll}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            지우기
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {WEEKDAYS.map((day) => {
          const selected = isSelected(day.value);
          const isSaturday = day.value === 32;
          const isSunday = day.value === 64;

          return (
            <button
              key={day.value}
              type="button"
              onClick={() => toggleWeekday(day.value)}
              title={day.fullName}
              className={`
                flex items-center justify-center h-12 rounded-lg font-medium transition-all
                ${
                  selected
                    ? isSunday
                      ? 'bg-red-500 text-white hover:bg-red-600'
                      : isSaturday
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                    : isSunday
                    ? 'bg-red-50 text-red-400 hover:bg-red-100'
                    : isSaturday
                    ? 'bg-blue-50 text-blue-400 hover:bg-blue-100'
                    : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                }
              `}
            >
              {day.label}
            </button>
          );
        })}
      </div>

      {selectedCount === 0 && (
        <p className="text-sm text-red-500">최소 1개 이상의 요일을 선택해주세요</p>
      )}
    </div>
  );
};

export default WeekdayPicker;
