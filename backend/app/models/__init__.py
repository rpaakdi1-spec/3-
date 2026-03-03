from .base import Base
from .user import User
from .employee import Employee, EmployeeRole, EmploymentType
from .pending_employee import PendingEmployee
from .client import Client
from .vehicle import Vehicle, VehicleType, VehicleStatus
from .driver import Driver
from .order import Order, OrderStatus
from .dispatch import Dispatch, DispatchRoute, DispatchStatus
from .vehicle_location import VehicleLocation, TemperatureAlert
from .notice import Notice
from .purchase_order import PurchaseOrder
from .band_message import BandMessage, BandChatRoom, BandMessageSchedule
from .uvis_gps import UvisAccessKey, VehicleGPSLog, VehicleTemperatureLog, UvisApiLog
from .fcm_token import FCMToken, PushNotificationLog
from .chat import ChatRoom, ChatParticipant, ChatMessage
from .security import TwoFactorAuth, TwoFactorLog, AuditLog, SecurityAlert
from .ai_chat_history import AIChatHistory
from .ai_usage_log import AIUsageLog
from .recurring_order import RecurringOrder
from .order_template import OrderTemplate
from .driver_schedule import DriverSchedule, ScheduleType
from .notification import Notification, NotificationTemplate, NotificationType, NotificationChannel, NotificationStatus
from .billing import (
    BillingPolicy, Invoice, InvoiceLineItem, Payment, 
    DriverSettlement, DriverSettlementItem,
    BillingCycleType, BillingStatus, PaymentMethod
)
from .billing_enhanced import (
    TaxInvoice, TaxInvoiceStatus,
    AutoInvoiceSchedule,
    SettlementApproval, SettlementApprovalStatus, SettlementApprovalHistory,
    PaymentReminder, PaymentReminderType, PaymentReminderStatus,
    ExportTask, ExportTaskStatus
)
from .vehicle_maintenance import (
    VehicleMaintenanceRecord, VehiclePart, MaintenancePartUsage,
    MaintenanceSchedule, VehicleInspection,
    MaintenanceType, MaintenanceStatus, MaintenancePriority, PartCategory
)
from .mobile_photo import MobilePhoto, NotificationPreferences, MobileSession
# Import simulation models BEFORE dispatch_rule to avoid circular dependency
from .simulation import RuleSimulation, SimulationComparison, SimulationTemplate
from .dispatch_rule import DispatchRule, RuleConstraint, RuleExecutionLog, OptimizationConfig
from .dispatch_template import DispatchTemplate
from .vehicle_daily_mileage import VehicleDailyMileage

__all__ = [
    "Base",
    "User",
    "Employee",
    "EmployeeRole",
    "EmploymentType",
    "PendingEmployee",
    "Client",
    "Vehicle",
    "VehicleType",
    "VehicleStatus",
    "Driver",
    "Order",
    "OrderStatus",
    "Dispatch",
    "DispatchRoute",
    "DispatchStatus",
    "VehicleLocation",
    "TemperatureAlert",
    "Notice",
    "PurchaseOrder",
    "BandMessage",
    "BandChatRoom",
    "BandMessageSchedule",
    "UvisAccessKey",
    "VehicleGPSLog",
    "VehicleTemperatureLog",
    "UvisApiLog",
    "FCMToken",
    "PushNotificationLog",
    "ChatRoom",
    "ChatParticipant",
    "ChatMessage",
    "TwoFactorAuth",
    "TwoFactorLog",
    "AuditLog",
    "SecurityAlert",
    "AIChatHistory",
    "AIUsageLog",
    "RecurringOrder",
    "OrderTemplate",
    "DriverSchedule",
    "ScheduleType",
    "Notification",
    "NotificationTemplate",
    "NotificationType",
    "NotificationChannel",
    "NotificationStatus",
    "BillingPolicy",
    "Invoice",
    "InvoiceLineItem",
    "Payment",
    "DriverSettlement",
    "DriverSettlementItem",
    "BillingCycleType",
    "BillingStatus",
    "PaymentMethod",
    "VehicleMaintenanceRecord",
    "VehiclePart",
    "MaintenancePartUsage",
    "MaintenanceSchedule",
    "VehicleInspection",
    "MaintenanceType",
    "MaintenanceStatus",
    "MaintenancePriority",
    "PartCategory",
    "MobilePhoto",
    "NotificationPreferences",
    "MobileSession",
    # Phase 8: Billing Enhanced
    "TaxInvoice",
    "TaxInvoiceStatus",
    "AutoInvoiceSchedule",
    "SettlementApproval",
    "SettlementApprovalStatus",
    "SettlementApprovalHistory",
    "PaymentReminder",
    "PaymentReminderType",
    "PaymentReminderStatus",
    "ExportTask",
    "ExportTaskStatus",
    # Dispatch Rules & Simulation
    "RuleSimulation",
    "SimulationComparison",
    "SimulationTemplate",
    "DispatchRule",
    "RuleConstraint",
    "RuleExecutionLog",
    "OptimizationConfig",
    "DispatchTemplate",
    "VehicleDailyMileage",
]

# Phase 16.3: Chat models
from app.models.chat import ChatRoom, ChatMessage, ChatParticipant
