# 📋 Changelog

All notable changes to the Cold Chain System API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-01-28

### 🎉 Added

#### Phase 19: Security Enhancements
- **Two-Factor Authentication (2FA)**
  - TOTP-based 2FA with QR code generation
  - Backup codes for recovery
  - 2FA login flow
  - Endpoints: `/api/v1/security/2fa/*`

- **Audit Logging**
  - Comprehensive audit trail for all actions
  - IP address and user agent tracking
  - Old/new value comparison
  - Suspicious login detection
  - Endpoints: `/api/v1/security/audit-logs`

- **Security Endpoints**
  - Login history tracking
  - Password change with old password verification
  - Session management
  - Suspicious activity alerts

#### Phase 18: Performance Optimization
- **Advanced Caching**
  - Multi-tier caching strategy (L1: memory, L2: Redis)
  - Cache invalidation patterns
  - Cache statistics endpoint
  - TTL-based expiration

- **Performance Monitoring**
  - Query execution time tracking
  - Slow query logging (>1s)
  - Memory usage monitoring
  - System metrics endpoint

- **Compression Middleware**
  - Gzip compression for responses >1KB
  - Reduced bandwidth usage by ~70%

- **Database Indexes**
  - 45+ optimized indexes
  - Composite indexes for common queries
  - Query performance improved by 3-5x

#### Phase 9: Mobile & Push Notifications
- **FCM Push Notifications**
  - Token registration/unregistration
  - Multiple notification types (dispatch, temperature alert, etc.)
  - Notification history tracking
  - Endpoints: `/api/v1/notifications/*`

- **React Native Mobile App**
  - Complete mobile app structure
  - iOS and Android support
  - Offline capabilities
  - Location tracking

#### Phase 8: Machine Learning Models
- **Delivery Time Prediction**
  - Random Forest regression model
  - Confidence intervals
  - Feature importance analysis
  - MAE < 15 minutes, R² > 0.75
  - Endpoints: `/api/v1/ml/predict/delivery-time`

- **Demand Forecasting**
  - Time series forecasting
  - Seasonal pattern detection
  - Multi-day predictions
  - MAPE < 20%
  - Endpoints: `/api/v1/ml/forecast/demand`

#### Phase 7: Real-time Monitoring
- **Samsung UVIS Integration**
  - Real-time GPS tracking
  - Vehicle temperature monitoring
  - Vehicle status tracking
  - Mock service for testing

- **Real-time Monitoring Service**
  - Combined GPS, temperature, and status monitoring
  - Automatic alert generation
  - WebSocket broadcasting
  - Background monitoring scheduler
  - Endpoints: `/api/v1/realtime/monitor`, `/api/v1/realtime/ws`

### 🔧 Changed
- Upgraded FastAPI to 0.109.0
- Improved error handling across all endpoints
- Enhanced API documentation with detailed examples
- Optimized database queries (N+1 problem fixed)

### 🐛 Fixed
- Token refresh race condition
- Memory leak in WebSocket connections
- Cache invalidation issues
- Timezone handling in reports

### 🔒 Security
- Implemented rate limiting (5-100 req/min depending on endpoint)
- Added CORS protection
- Enhanced password policy (min 12 chars, complexity requirements)
- SQL injection prevention with parameterized queries
- XSS protection in all user inputs

---

## [1.5.0] - 2026-01-15

### Added
- **Analytics Dashboard** (18 endpoints)
  - Daily/weekly/monthly statistics
  - Performance metrics
  - Cost analysis
  - Fleet utilization tracking

- **Reports Generation**
  - PDF reports with Korean font support
  - Excel reports with multiple sheets
  - Automated report scheduling
  - 12 report types

- **Email Notifications**
  - SMTP integration
  - Jinja2 HTML templates
  - Scheduled reports (daily/weekly/monthly)
  - Event-driven alerts

### Changed
- Migrated from SQLite to PostgreSQL
- Improved OR-Tools VRP algorithm
- Enhanced frontend with React Query

### Fixed
- Route optimization timeout issues
- Excel template generation errors
- Date range filtering bugs

---

## [1.0.0] - 2026-01-01

### 🎉 Initial Release

#### Core Features
- **User Authentication**
  - JWT-based authentication
  - Role-based access control (Admin, Dispatcher, Driver, Viewer)
  - Secure password hashing (bcrypt)

- **Order Management**
  - CRUD operations for orders
  - Temperature type classification (냉동, 냉장, 상온)
  - Client management

- **Dispatch Optimization**
  - Google OR-Tools VRP integration
  - Time window constraints
  - Vehicle capacity constraints
  - Temperature type matching
  - Route optimization

- **Vehicle Management**
  - Vehicle tracking
  - Temperature type classification
  - Capacity management
  - GPS integration preparation

- **Frontend Dashboard**
  - React + TypeScript
  - Real-time updates
  - Interactive maps
  - Responsive design

#### Technical Stack
- **Backend**: FastAPI 0.100.0, Python 3.11
- **Database**: PostgreSQL 15, SQLAlchemy 2.0
- **Cache**: Redis 7
- **Frontend**: React 18, TypeScript, Vite
- **Testing**: Pytest (80%+ coverage), Cypress

---

## Versioning Policy

- **Major version** (X.0.0): Breaking API changes, major feature additions
- **Minor version** (1.X.0): New features, backward compatible
- **Patch version** (1.0.X): Bug fixes, documentation updates

---

## Upgrade Guide

### Upgrading from 1.5.0 to 2.0.0

#### Database Migrations
```bash
cd backend
alembic upgrade head
```

#### Environment Variables
New required variables:
```bash
# 2FA
TOTP_ISSUER="Cold Chain System"

# FCM (if using push notifications)
FCM_SERVER_KEY=your_fcm_server_key

# ML Models
ML_MODELS_PATH=/path/to/ml_models
```

#### Breaking Changes
1. **Authentication**
   - 2FA is now available (optional)
   - Token expiration reduced from 2 hours to 1 hour

2. **API Endpoints**
   - `/api/v1/auth/me` response format changed (added `is_2fa_enabled`)
   - `/api/v1/monitoring/*` deprecated, use `/api/v1/realtime/*`

3. **Rate Limits**
   - Login endpoint: reduced from 10 to 5 requests/minute
   - Write operations: reduced from 50 to 30 requests/minute

#### Migration Steps
1. Backup your database
2. Update environment variables
3. Run database migrations
4. Update client code if using deprecated endpoints
5. Test 2FA flow (if enabling)
6. Update mobile apps to register FCM tokens

---

## Support

For issues or questions:
- **GitHub**: [github.com/your-org/cold-chain/issues](https://github.com/your-org/cold-chain/issues)
- **Email**: support@coldchain.com
- **Documentation**: [docs.coldchain.com](https://docs.coldchain.com)

---

**Last Updated**: 2026-01-28  
**Current Version**: 2.0.0
