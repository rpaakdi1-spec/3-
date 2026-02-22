import React from 'react';
import { ChevronRight, MoreVertical } from 'lucide-react';

interface MobileListItemProps {
  title: string;
  subtitle?: string;
  badge?: {
    text: string;
    color: 'blue' | 'green' | 'yellow' | 'red' | 'gray' | 'purple';
  };
  avatar?: React.ReactNode;
  rightContent?: React.ReactNode;
  onClick?: () => void;
  onMenuClick?: () => void;
  selected?: boolean;
  onSelectChange?: (selected: boolean) => void;
}

/**
 * Mobile-optimized list item component
 * Replaces table rows on mobile devices
 */
export const MobileListItem: React.FC<MobileListItemProps> = ({
  title,
  subtitle,
  badge,
  avatar,
  rightContent,
  onClick,
  onMenuClick,
  selected,
  onSelectChange,
}) => {
  const badgeColors = {
    blue: 'bg-blue-100 text-blue-700 border-blue-200',
    green: 'bg-green-100 text-green-700 border-green-200',
    yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    red: 'bg-red-100 text-red-700 border-red-200',
    gray: 'bg-gray-100 text-gray-700 border-gray-200',
    purple: 'bg-purple-100 text-purple-700 border-purple-200',
  };

  return (
    <div
      className={`
        flex items-center gap-3 p-4 bg-white border-b border-gray-100
        active:bg-gray-50 transition-colors touch-manipulation
        ${onClick ? 'cursor-pointer' : ''}
        ${selected ? 'bg-blue-50' : ''}
      `}
      onClick={onClick}
    >
      {/* Selection Checkbox */}
      {onSelectChange && (
        <input
          type="checkbox"
          checked={selected}
          onChange={(e) => {
            e.stopPropagation();
            onSelectChange(e.target.checked);
          }}
          className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 touch-manipulation"
        />
      )}

      {/* Avatar */}
      {avatar && <div className="flex-shrink-0">{avatar}</div>}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-semibold text-gray-800 truncate">{title}</h3>
          {badge && (
            <span
              className={`
                px-2 py-0.5 text-xs font-medium rounded-full border
                ${badgeColors[badge.color]}
              `}
            >
              {badge.text}
            </span>
          )}
        </div>
        {subtitle && <p className="text-sm text-gray-600 truncate">{subtitle}</p>}
      </div>

      {/* Right Content */}
      {rightContent && <div className="flex-shrink-0">{rightContent}</div>}

      {/* Menu or Arrow */}
      {onMenuClick ? (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onMenuClick();
          }}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors touch-manipulation"
        >
          <MoreVertical size={20} className="text-gray-600" />
        </button>
      ) : onClick ? (
        <ChevronRight size={20} className="text-gray-400" />
      ) : null}
    </div>
  );
};

interface MobileListSectionProps {
  title?: string;
  children: React.ReactNode;
  count?: number;
}

/**
 * Section header for mobile lists
 */
export const MobileListSection: React.FC<MobileListSectionProps> = ({
  title,
  children,
  count,
}) => {
  return (
    <div className="mb-4">
      {title && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-50 sticky top-0 z-10">
          <h3 className="text-sm font-semibold text-gray-700 uppercase">{title}</h3>
          {count !== undefined && (
            <span className="text-sm text-gray-600">{count}개</span>
          )}
        </div>
      )}
      <div className="bg-white">{children}</div>
    </div>
  );
};

interface MobileEmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Empty state for mobile lists
 */
export const MobileEmptyState: React.FC<MobileEmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
      {icon && <div className="mb-4 text-gray-400">{icon}</div>}
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      {description && <p className="text-sm text-gray-600 mb-6">{description}</p>}
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 active:bg-blue-800 transition-colors touch-manipulation"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

interface MobilePullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
}

/**
 * Pull-to-refresh wrapper for mobile lists
 */
export const MobilePullToRefresh: React.FC<MobilePullToRefreshProps> = ({
  onRefresh,
  children,
}) => {
  const [isPulling, setIsPulling] = React.useState(false);
  const [startY, setStartY] = React.useState(0);
  const [pullDistance, setPullDistance] = React.useState(0);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartY(e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentY = e.touches[0].clientY;
    const distance = currentY - startY;

    if (distance > 0 && window.scrollY === 0) {
      setPullDistance(Math.min(distance, 100));
      setIsPulling(true);
    }
  };

  const handleTouchEnd = async () => {
    if (pullDistance > 60) {
      await onRefresh();
    }
    setIsPulling(false);
    setPullDistance(0);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {/* Pull indicator */}
      {isPulling && (
        <div
          className="absolute top-0 left-0 right-0 flex items-center justify-center transition-all"
          style={{ height: pullDistance }}
        >
          <div className="text-blue-600">
            {pullDistance > 60 ? '↓ 놓아서 새로고침' : '↓ 당겨서 새로고침'}
          </div>
        </div>
      )}

      <div style={{ transform: `translateY(${pullDistance}px)`, transition: isPulling ? 'none' : 'transform 0.3s' }}>
        {children}
      </div>
    </div>
  );
};

export default MobileListItem;
