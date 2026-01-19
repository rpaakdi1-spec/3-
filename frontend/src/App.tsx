import { useState } from 'react'
import Dashboard from './components/Dashboard'
import ClientUpload from './components/ClientUpload'
import VehicleUpload from './components/VehicleUpload'
import OrderUpload from './components/OrderUpload'
import DispatchOptimization from './components/DispatchOptimization'

type Page = 'dashboard' | 'clients' | 'vehicles' | 'orders' | 'dispatch'

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
