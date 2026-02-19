import React from 'react';
import { X } from 'lucide-react';

interface MobileActionSheetAction {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: 'default' | 'danger';
  disabled?: boolean;
}

interface MobileActionSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  actions: MobileActionSheetAction[];
}

/**
 * iOS-style action sheet for mobile
 * Bottom sheet with action buttons
 */
export const MobileActionSheet: React.FC<MobileActionSheetProps> = ({
  isOpen,
  onClose,
  title,
  actions,
}) => {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50 md:hidden animate-fadeIn"
        onClick={onClose}
      />

      {/* Action Sheet */}
      <div
        className={`
          fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-50 md:hidden
          transform transition-transform duration-300 ease-out
          ${isOpen ? 'translate-y-0' : 'translate-y-full'}
          pb-safe
        `}
      >
        {/* Handle Bar */}
        <div className="flex justify-center py-2">
          <div className="w-12 h-1.5 bg-gray-300 rounded-full" />
        </div>

        {/* Title */}
        {title && (
          <div className="px-6 py-3 border-b border-gray-200">
            <h3 className="text-center text-sm font-medium text-gray-600">{title}</h3>
          </div>
        )}

        {/* Actions */}
        <div className="p-4 space-y-2">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                action.onClick();
                onClose();
              }}
              disabled={action.disabled}
              className={`
                w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl
                font-medium text-base transition-all touch-manipulation
                ${
                  action.variant === 'danger'
                    ? 'bg-red-50 text-red-600 hover:bg-red-100 active:bg-red-200'
                    : 'bg-gray-50 text-gray-800 hover:bg-gray-100 active:bg-gray-200'
                }
                ${action.disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {action.icon && <span>{action.icon}</span>}
              <span>{action.label}</span>
            </button>
          ))}

          {/* Cancel Button */}
          <button
            onClick={onClose}
            className="w-full px-6 py-4 bg-white border-2 border-gray-300 text-gray-800 rounded-xl font-semibold text-base hover:bg-gray-50 active:bg-gray-100 transition-all touch-manipulation"
          >
            취소
          </button>
        </div>
      </div>
    </>
  );
};

interface MobileFABProps {
  icon: React.ReactNode;
  label?: string;
  onClick: () => void;
  position?: 'bottom-right' | 'bottom-center';
  variant?: 'primary' | 'secondary';
}

/**
 * Floating Action Button for mobile
 */
export const MobileFAB: React.FC<MobileFABProps> = ({
  icon,
  label,
  onClick,
  position = 'bottom-right',
  variant = 'primary',
}) => {
  const positionClasses = {
    'bottom-right': 'bottom-20 right-6',
    'bottom-center': 'bottom-20 left-1/2 transform -translate-x-1/2',
  };

  const variantClasses = {
    primary: 'bg-blue-600 text-white shadow-lg hover:bg-blue-700',
    secondary: 'bg-white text-gray-800 shadow-xl border border-gray-200',
  };

  return (
    <button
      onClick={onClick}
      className={`
        fixed z-30 md:hidden
        flex items-center gap-2 px-6 py-4 rounded-full
        font-semibold text-base transition-all
        active:scale-95 touch-manipulation
        ${positionClasses[position]}
        ${variantClasses[variant]}
      `}
    >
      {icon}
      {label && <span>{label}</span>}
    </button>
  );
};

interface MobileSwipeableItemProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftAction?: {
    label: string;
    icon?: React.ReactNode;
    color: string;
  };
  rightAction?: {
    label: string;
    icon?: React.ReactNode;
    color: string;
  };
}

/**
 * Swipeable list item for mobile
 * iOS-style swipe actions
 */
export const MobileSwipeableItem: React.FC<MobileSwipeableItemProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftAction,
  rightAction,
}) => {
  const [touchStart, setTouchStart] = React.useState(0);
  const [touchEnd, setTouchEnd] = React.useState(0);
  const [swiping, setSwiping] = React.useState(false);

  const minSwipeDistance = 100;

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.touches[0].clientX);
    setTouchEnd(e.touches[0].clientX);
    setSwiping(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.touches[0].clientX);
  };

  const handleTouchEnd = () => {
    setSwiping(false);
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft();
    } else if (isRightSwipe && onSwipeRight) {
      onSwipeRight();
    }

    // Reset
    setTimeout(() => {
      setTouchStart(0);
      setTouchEnd(0);
    }, 300);
  };

  const swipeDistance = swiping ? touchEnd - touchStart : 0;

  return (
    <div className="relative overflow-hidden">
      {/* Left Action */}
      {leftAction && (
        <div
          className={`absolute inset-y-0 left-0 flex items-center justify-start pl-6 ${leftAction.color}`}
          style={{ width: Math.abs(Math.min(swipeDistance, 0)) }}
        >
          {leftAction.icon}
          <span className="ml-2 text-white font-medium">{leftAction.label}</span>
        </div>
      )}

      {/* Right Action */}
      {rightAction && (
        <div
          className={`absolute inset-y-0 right-0 flex items-center justify-end pr-6 ${rightAction.color}`}
          style={{ width: Math.max(Math.abs(swipeDistance), 0) }}
        >
          <span className="mr-2 text-white font-medium">{rightAction.label}</span>
          {rightAction.icon}
        </div>
      )}

      {/* Content */}
      <div
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          transform: `translateX(${swipeDistance}px)`,
          transition: swiping ? 'none' : 'transform 0.3s',
        }}
        className="bg-white"
      >
        {children}
      </div>
    </div>
  );
};

export default MobileActionSheet;
