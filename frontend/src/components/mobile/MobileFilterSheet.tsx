import React, { useState } from 'react';
import { X, Filter as FilterIcon } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';

interface MobileFilterSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  onApply?: () => void;
  onReset?: () => void;
  title?: string;
}

/**
 * Mobile-optimized bottom sheet for filters
 * Slides up from bottom on mobile devices
 */
export const MobileFilterSheet: React.FC<MobileFilterSheetProps> = ({
  isOpen,
  onClose,
  children,
  onApply,
  onReset,
  title = '필터',
}) => {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden animate-fadeIn"
        onClick={onClose}
      />

      {/* Bottom Sheet */}
      <div
        className={`
          fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-50 md:hidden
          transform transition-transform duration-300 ease-out
          ${isOpen ? 'translate-y-0' : 'translate-y-full'}
          max-h-[85vh] overflow-hidden flex flex-col
        `}
      >
        {/* Handle Bar */}
        <div className="flex justify-center py-2">
          <div className="w-12 h-1.5 bg-gray-300 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <FilterIcon size={20} className="text-gray-700" />
            <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {children}
        </div>

        {/* Actions */}
        <div className="flex gap-3 p-4 border-t border-gray-200 bg-white">
          {onReset && (
            <Button
              variant="outline"
              onClick={onReset}
              className="flex-1"
            >
              초기화
            </Button>
          )}
          <Button
            onClick={() => {
              onApply?.();
              onClose();
            }}
            className="flex-1"
          >
            적용
          </Button>
        </div>
      </div>
    </>
  );
};

interface MobileSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onFilterClick?: () => void;
  filterCount?: number;
}

/**
 * Mobile-optimized search bar with filter button
 */
export const MobileSearchBar: React.FC<MobileSearchBarProps> = ({
  value,
  onChange,
  placeholder = '검색...',
  onFilterClick,
  filterCount = 0,
}) => {
  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-white sticky top-0 z-10 border-b border-gray-100">
      {/* Search Input */}
      <div className="flex-1 relative">
        <input
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-3 pr-10 bg-gray-100 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-base"
        />
        {value && (
          <button
            onClick={() => onChange('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Filter Button */}
      {onFilterClick && (
        <button
          onClick={onFilterClick}
          className="relative p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 active:bg-blue-800 transition-colors"
        >
          <FilterIcon size={20} />
          {filterCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
              {filterCount}
            </span>
          )}
        </button>
      )}
    </div>
  );
};

interface MobileFilterGroupProps {
  title: string;
  children: React.ReactNode;
}

/**
 * Filter group for mobile bottom sheet
 */
export const MobileFilterGroup: React.FC<MobileFilterGroupProps> = ({
  title,
  children,
}) => {
  return (
    <div className="mb-6">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">{title}</h4>
      <div className="space-y-2">{children}</div>
    </div>
  );
};

interface MobileFilterChipProps {
  label: string;
  selected: boolean;
  onClick: () => void;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'gray';
}

/**
 * Chip-style filter button for mobile
 */
export const MobileFilterChip: React.FC<MobileFilterChipProps> = ({
  label,
  selected,
  onClick,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: selected
      ? 'bg-blue-600 text-white border-blue-600'
      : 'bg-white text-gray-700 border-gray-300 hover:border-blue-600',
    green: selected
      ? 'bg-green-600 text-white border-green-600'
      : 'bg-white text-gray-700 border-gray-300 hover:border-green-600',
    purple: selected
      ? 'bg-purple-600 text-white border-purple-600'
      : 'bg-white text-gray-700 border-gray-300 hover:border-purple-600',
    orange: selected
      ? 'bg-orange-600 text-white border-orange-600'
      : 'bg-white text-gray-700 border-gray-300 hover:border-orange-600',
    gray: selected
      ? 'bg-gray-600 text-white border-gray-600'
      : 'bg-white text-gray-700 border-gray-300 hover:border-gray-600',
  };

  return (
    <button
      onClick={onClick}
      className={`
        px-4 py-2.5 rounded-xl border-2 font-medium text-sm transition-all
        active:scale-95 touch-manipulation
        ${colorClasses[color]}
      `}
    >
      {label}
    </button>
  );
};

export default MobileFilterSheet;
