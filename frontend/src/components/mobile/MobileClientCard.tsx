import React from 'react';
import { Building2, Phone, Mail, MapPin, User } from 'lucide-react';

interface MobileClientCardProps {
  client: {
    id: number;
    name: string;
    business_number?: string;
    contact_person?: string;
    phone: string;
    email?: string;
    address: string;
    is_active: boolean;
  };
  onEdit?: () => void;
  onCall?: () => void;
  onEmail?: () => void;
  onViewMap?: () => void;
}

export const MobileClientCard: React.FC<MobileClientCardProps> = ({
  client,
  onEdit,
  onCall,
  onEmail,
  onViewMap,
}) => {
  return (
    <div
      className="bg-white rounded-lg shadow-sm p-4 mb-3 border border-gray-200"
      onClick={onEdit}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center flex-1">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <Building2 className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-base text-gray-900">{client.name}</h3>
            {client.business_number && (
              <p className="text-xs text-gray-500 mt-0.5">
                사업자: {client.business_number}
              </p>
            )}
          </div>
        </div>
        
        {!client.is_active && (
          <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">
            비활성
          </span>
        )}
      </div>

      {/* Contact Person */}
      {client.contact_person && (
        <div className="flex items-center gap-2 text-sm text-gray-700 mb-2">
          <User className="w-4 h-4 text-gray-400" />
          <span>{client.contact_person}</span>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {/* Call */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onCall?.();
          }}
          className="flex items-center justify-center gap-1.5 px-3 py-2 bg-green-50 hover:bg-green-100 rounded-lg active:scale-95 transition-all"
        >
          <Phone className="w-4 h-4 text-green-600" />
          <span className="text-xs font-medium text-green-700">전화</span>
        </button>

        {/* Email */}
        {client.email && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEmail?.();
            }}
            className="flex items-center justify-center gap-1.5 px-3 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg active:scale-95 transition-all"
          >
            <Mail className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-medium text-blue-700">메일</span>
          </button>
        )}

        {/* Map */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onViewMap?.();
          }}
          className="flex items-center justify-center gap-1.5 px-3 py-2 bg-purple-50 hover:bg-purple-100 rounded-lg active:scale-95 transition-all"
        >
          <MapPin className="w-4 h-4 text-purple-600" />
          <span className="text-xs font-medium text-purple-700">지도</span>
        </button>
      </div>

      {/* Address */}
      <div className="pt-3 border-t border-gray-100">
        <div className="flex items-start gap-2 text-sm">
          <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
          <span className="text-gray-600 leading-relaxed">{client.address}</span>
        </div>
      </div>
    </div>
  );
};
