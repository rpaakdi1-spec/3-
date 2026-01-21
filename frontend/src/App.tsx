import { useState } from 'react'
import Dashboard from './components/Dashboard'
import ClientUpload from './components/ClientUpload'
import VehicleUpload from './components/VehicleUpload'
import OrderUpload from './components/OrderUpload'
import DispatchOptimization from './components/DispatchOptimization'
import DispatchList from './components/DispatchList'
import RealtimeDashboard from './components/RealtimeDashboard'
import NoticeBoard from './components/NoticeBoard'
import PurchaseOrders from './components/PurchaseOrders'

type Page = 'dashboard' | 'clients' | 'vehicles' | 'orders' | 'dispatch' | 'dispatch-list' | 'realtime' | 'notices' | 'purchase-orders'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'clients':
        return <ClientUpload />
      case 'vehicles':
        return <VehicleUpload />
      case 'orders':
        return <OrderUpload />
      case 'dispatch':
        return <DispatchOptimization />
      case 'dispatch-list':
        return <DispatchList />
      case 'realtime':
        return <RealtimeDashboard />
      case 'notices':
        return <NoticeBoard />
      case 'purchase-orders':
        return <PurchaseOrders />
      default:
        return <Dashboard />
    }
  }

  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>🚛 냉동·냉장 배차 시스템</h1>
          <p>AI 기반 팔레트 배차 최적화</p>
          <nav className="nav">
            <a
              className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              대시보드
            </a>
            <a
              className={`nav-link ${currentPage === 'realtime' ? 'active' : ''}`}
              onClick={() => setCurrentPage('realtime')}
            >
              실시간 모니터링
            </a>
            <a
              className={`nav-link ${currentPage === 'clients' ? 'active' : ''}`}
              onClick={() => setCurrentPage('clients')}
            >
              거래처 관리
            </a>
            <a
              className={`nav-link ${currentPage === 'vehicles' ? 'active' : ''}`}
              onClick={() => setCurrentPage('vehicles')}
            >
              차량 관리
            </a>
            <a
              className={`nav-link ${currentPage === 'orders' ? 'active' : ''}`}
              onClick={() => setCurrentPage('orders')}
            >
              주문 관리
            </a>
            <a
              className={`nav-link ${currentPage === 'dispatch' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dispatch')}
            >
              AI 배차
            </a>
            <a
              className={`nav-link ${currentPage === 'dispatch-list' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dispatch-list')}
            >
              배차 내역
            </a>
            <a
              className={`nav-link ${currentPage === 'notices' ? 'active' : ''}`}
              onClick={() => setCurrentPage('notices')}
            >
              📢 공지사항
            </a>
            <a
              className={`nav-link ${currentPage === 'purchase-orders' ? 'active' : ''}`}
              onClick={() => setCurrentPage('purchase-orders')}
            >
              📝 발주서
            </a>
          </nav>
        </div>
      </div>
      <div className="container">
        {renderPage()}
      </div>
    </div>
  )
}

export default App
