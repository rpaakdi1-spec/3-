import React from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  action?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ children, title, className, action }) => {
  return (
    <div className={clsx('bg-white rounded-lg shadow-md overflow-hidden', className)}>
      {(title || action) && (
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};

export default Card;
