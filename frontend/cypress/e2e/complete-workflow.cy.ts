/**
 * Complete Order to Dispatch Workflow E2E Test
 * 
 * Tests the entire flow from order creation to dispatch completion
 */

describe('Complete Order to Dispatch Workflow', () => {
  let authToken: string;
  let orderId: number;
  let dispatchId: number;

  before(() => {
    // Login and get auth token
    cy.request('POST', '/api/v1/auth/login', {
      username: 'test_dispatcher',
      password: 'TestPass123!'
    }).then((response) => {
      expect(response.status).to.eq(200);
      authToken = response.body.access_token;
      Cypress.env('authToken', authToken);
    });
  });

  it('should create a new order', () => {
    cy.visit('/orders');
    
    // Wait for page load
    cy.get('[data-cy=orders-page]').should('be.visible');
    
    // Click create order button
    cy.get('[data-cy=create-order-btn]').click();
    
    // Fill order form
    cy.get('[data-cy=order-form]').should('be.visible');
    cy.get('[data-cy=client-select]').select('Test Client');
    cy.get('[data-cy=pickup-location]').type('Seoul, Gangnam');
    cy.get('[data-cy=delivery-location]').type('Seoul, Jamsil');
    cy.get('[data-cy=temperature-select]').select('냉동');
    cy.get('[data-cy=pallets-input]').clear().type('5');
    cy.get('[data-cy=weight-input]').clear().type('500');
    cy.get('[data-cy=notes-textarea]').type('Test order for E2E testing');
    
    // Submit order
    cy.get('[data-cy=submit-order-btn]').click();
    
    // Verify success message
    cy.get('[data-cy=success-message]').should('contain', '주문이 생성되었습니다');
    
    // Capture order ID
    cy.url().should('include', '/orders/');
    cy.url().then((url) => {
      orderId = parseInt(url.split('/').pop() || '0');
      expect(orderId).to.be.greaterThan(0);
    });
  });

  it('should view order details', () => {
    cy.visit(`/orders/${orderId}`);
    
    // Verify order details
    cy.get('[data-cy=order-detail]').should('be.visible');
    cy.get('[data-cy=order-id]').should('contain', orderId);
    cy.get('[data-cy=order-status]').should('contain', '대기');
    cy.get('[data-cy=order-temperature]').should('contain', '냉동');
    cy.get('[data-cy=order-pallets]').should('contain', '5');
    cy.get('[data-cy=order-weight]').should('contain', '500');
  });

  it('should optimize dispatch with order', () => {
    cy.visit('/dispatches');
    
    // Click optimize button
    cy.get('[data-cy=optimize-dispatch-btn]').click();
    
    // Select orders for optimization
    cy.get('[data-cy=order-selection-modal]').should('be.visible');
    cy.get(`[data-cy=order-checkbox-${orderId}]`).check();
    
    // Start optimization
    cy.get('[data-cy=start-optimization-btn]').click();
    
    // Wait for optimization (may take a few seconds)
    cy.get('[data-cy=optimization-progress]', { timeout: 30000 })
      .should('not.exist');
    
    // Verify optimization results
    cy.get('[data-cy=optimization-results]').should('be.visible');
    cy.get('[data-cy=optimized-routes]').should('have.length.greaterThan', 0);
  });

  it('should create dispatch from optimization', () => {
    // Approve optimized route
    cy.get('[data-cy=approve-route-btn]').first().click();
    
    // Confirm dispatch creation
    cy.get('[data-cy=confirm-dispatch-modal]').should('be.visible');
    cy.get('[data-cy=confirm-dispatch-btn]').click();
    
    // Verify success
    cy.get('[data-cy=success-message]').should('contain', '배차가 생성되었습니다');
    
    // Navigate to dispatch detail
    cy.get('[data-cy=view-dispatch-btn]').click();
    
    // Capture dispatch ID
    cy.url().should('include', '/dispatches/');
    cy.url().then((url) => {
      dispatchId = parseInt(url.split('/').pop() || '0');
      expect(dispatchId).to.be.greaterThan(0);
    });
  });

  it('should assign driver to dispatch', () => {
    cy.visit(`/dispatches/${dispatchId}`);
    
    // Open driver assignment dialog
    cy.get('[data-cy=assign-driver-btn]').click();
    
    // Select driver
    cy.get('[data-cy=driver-select-modal]').should('be.visible');
    cy.get('[data-cy=driver-option]').first().click();
    
    // Confirm assignment
    cy.get('[data-cy=confirm-assignment-btn]').click();
    
    // Verify assignment
    cy.get('[data-cy=dispatch-status]').should('contain', '할당됨');
    cy.get('[data-cy=assigned-driver]').should('be.visible');
  });

  it('should start dispatch', () => {
    // Start dispatch
    cy.get('[data-cy=start-dispatch-btn]').click();
    
    // Confirm start
    cy.get('[data-cy=confirm-start-modal]').should('be.visible');
    cy.get('[data-cy=confirm-start-btn]').click();
    
    // Verify status change
    cy.get('[data-cy=dispatch-status]').should('contain', '진행중');
  });

  it('should track dispatch in real-time', () => {
    // Navigate to tracking page
    cy.get('[data-cy=track-dispatch-btn]').click();
    
    // Verify tracking page
    cy.get('[data-cy=tracking-page]').should('be.visible');
    cy.get('[data-cy=dispatch-map]').should('be.visible');
    cy.get('[data-cy=vehicle-marker]').should('be.visible');
    
    // Verify real-time updates (WebSocket)
    cy.wait(6000); // Wait for WebSocket update
    cy.get('[data-cy=last-update-time]').should('not.contain', '--');
  });

  it('should complete dispatch', () => {
    cy.visit(`/dispatches/${dispatchId}`);
    
    // Complete dispatch
    cy.get('[data-cy=complete-dispatch-btn]').click();
    
    // Confirm completion
    cy.get('[data-cy=confirm-complete-modal]').should('be.visible');
    cy.get('[data-cy=delivery-notes]').type('Delivered successfully');
    cy.get('[data-cy=confirm-complete-btn]').click();
    
    // Verify completion
    cy.get('[data-cy=dispatch-status]').should('contain', '완료');
  });

  it('should verify order status is completed', () => {
    cy.visit(`/orders/${orderId}`);
    
    // Verify order is completed
    cy.get('[data-cy=order-status]').should('contain', '완료');
    cy.get('[data-cy=completed-dispatch]').should('be.visible');
    cy.get('[data-cy=completed-dispatch]').should('contain', dispatchId);
  });

  it('should generate dispatch report', () => {
    cy.visit(`/dispatches/${dispatchId}`);
    
    // Generate report
    cy.get('[data-cy=generate-report-btn]').click();
    
    // Select report format
    cy.get('[data-cy=report-format-modal]').should('be.visible');
    cy.get('[data-cy=format-pdf]').click();
    
    // Wait for download
    cy.get('[data-cy=download-progress]', { timeout: 10000 })
      .should('not.exist');
    
    // Verify download started
    cy.get('[data-cy=success-message]').should('contain', '리포트가 생성되었습니다');
  });
});


/**
 * Authentication Flow E2E Tests
 */

describe('Authentication Flow', () => {
  it('should register new user', () => {
    cy.visit('/register');
    
    const username = `test_user_${Date.now()}`;
    
    cy.get('[data-cy=username-input]').type(username);
    cy.get('[data-cy=email-input]').type(`${username}@example.com`);
    cy.get('[data-cy=password-input]').type('SecurePass123!');
    cy.get('[data-cy=confirm-password-input]').type('SecurePass123!');
    cy.get('[data-cy=full-name-input]').type('Test User');
    cy.get('[data-cy=register-btn]').click();
    
    // Verify success
    cy.get('[data-cy=success-message]').should('contain', '회원가입이 완료되었습니다');
  });

  it('should login with valid credentials', () => {
    cy.visit('/login');
    
    cy.get('[data-cy=username-input]').type('test_dispatcher');
    cy.get('[data-cy=password-input]').type('TestPass123!');
    cy.get('[data-cy=login-btn]').click();
    
    // Verify redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-cy=user-menu]').should('be.visible');
  });

  it('should fail login with invalid credentials', () => {
    cy.visit('/login');
    
    cy.get('[data-cy=username-input]').type('invalid_user');
    cy.get('[data-cy=password-input]').type('WrongPass123!');
    cy.get('[data-cy=login-btn]').click();
    
    // Verify error message
    cy.get('[data-cy=error-message]').should('contain', '로그인에 실패했습니다');
    cy.url().should('include', '/login');
  });

  it('should logout successfully', () => {
    // Login first
    cy.visit('/login');
    cy.get('[data-cy=username-input]').type('test_dispatcher');
    cy.get('[data-cy=password-input]').type('TestPass123!');
    cy.get('[data-cy=login-btn]').click();
    
    // Logout
    cy.get('[data-cy=user-menu]').click();
    cy.get('[data-cy=logout-btn]').click();
    
    // Verify redirect to login
    cy.url().should('include', '/login');
    cy.get('[data-cy=user-menu]').should('not.exist');
  });

  it('should handle token expiration', () => {
    // Login
    cy.visit('/login');
    cy.get('[data-cy=username-input]').type('test_dispatcher');
    cy.get('[data-cy=password-input]').type('TestPass123!');
    cy.get('[data-cy=login-btn]').click();
    
    // Set expired token
    cy.window().then((win) => {
      win.localStorage.setItem('authToken', 'expired.token.here');
    });
    
    // Try to access protected page
    cy.visit('/orders');
    
    // Should redirect to login
    cy.url().should('include', '/login');
    cy.get('[data-cy=error-message]').should('contain', '다시 로그인해주세요');
  });
});


/**
 * Form Validation E2E Tests
 */

describe('Form Validation', () => {
  beforeEach(() => {
    // Login
    cy.visit('/login');
    cy.get('[data-cy=username-input]').type('test_dispatcher');
    cy.get('[data-cy=password-input]').type('TestPass123!');
    cy.get('[data-cy=login-btn]').click();
  });

  it('should validate required fields in order form', () => {
    cy.visit('/orders/create');
    
    // Try to submit empty form
    cy.get('[data-cy=submit-order-btn]').click();
    
    // Verify validation errors
    cy.get('[data-cy=client-error]').should('contain', '거래처를 선택하세요');
    cy.get('[data-cy=pickup-error]').should('contain', '출발지를 입력하세요');
    cy.get('[data-cy=delivery-error]').should('contain', '도착지를 입력하세요');
  });

  it('should validate numeric fields', () => {
    cy.visit('/orders/create');
    
    // Fill with invalid values
    cy.get('[data-cy=pallets-input]').type('abc');
    cy.get('[data-cy=weight-input]').type('-100');
    
    cy.get('[data-cy=submit-order-btn]').click();
    
    // Verify validation
    cy.get('[data-cy=pallets-error]').should('contain', '올바른 숫자를 입력하세요');
    cy.get('[data-cy=weight-error]').should('contain', '양수를 입력하세요');
  });

  it('should validate range constraints', () => {
    cy.visit('/orders/create');
    
    cy.get('[data-cy=client-select]').select('Test Client');
    cy.get('[data-cy=pickup-location]').type('Seoul');
    cy.get('[data-cy=delivery-location]').type('Busan');
    cy.get('[data-cy=pallets-input]').type('100'); // Max 30
    cy.get('[data-cy=weight-input]').type('50000'); // Max 25000
    
    cy.get('[data-cy=submit-order-btn]').click();
    
    // Verify range validation
    cy.get('[data-cy=pallets-error]').should('contain', '최대 30개');
    cy.get('[data-cy=weight-error]').should('contain', '최대 25000kg');
  });
});


/**
 * Search and Filter E2E Tests
 */

describe('Search and Filter', () => {
  beforeEach(() => {
    cy.visit('/login');
    cy.get('[data-cy=username-input]').type('test_dispatcher');
    cy.get('[data-cy=password-input]').type('TestPass123!');
    cy.get('[data-cy=login-btn]').click();
  });

  it('should search orders by order number', () => {
    cy.visit('/orders');
    
    cy.get('[data-cy=search-input]').type('ORD-2026-0001');
    cy.get('[data-cy=search-btn]').click();
    
    // Verify filtered results
    cy.get('[data-cy=order-row]').should('have.length', 1);
    cy.get('[data-cy=order-number]').should('contain', 'ORD-2026-0001');
  });

  it('should filter orders by status', () => {
    cy.visit('/orders');
    
    cy.get('[data-cy=status-filter]').select('pending');
    
    // Verify all shown orders have pending status
    cy.get('[data-cy=order-status]').each(($el) => {
      cy.wrap($el).should('contain', '대기');
    });
  });

  it('should filter by date range', () => {
    cy.visit('/orders');
    
    const startDate = '2026-01-01';
    const endDate = '2026-01-31';
    
    cy.get('[data-cy=start-date]').type(startDate);
    cy.get('[data-cy=end-date]').type(endDate);
    cy.get('[data-cy=apply-filter-btn]').click();
    
    // Verify filtered results are within date range
    cy.get('[data-cy=order-date]').each(($el) => {
      const dateText = $el.text();
      // Basic date validation
      expect(dateText).to.match(/2026-01/);
    });
  });

  it('should combine multiple filters', () => {
    cy.visit('/orders');
    
    cy.get('[data-cy=status-filter]').select('pending');
    cy.get('[data-cy=temperature-filter]').select('frozen');
    cy.get('[data-cy=start-date]').type('2026-01-01');
    cy.get('[data-cy=apply-filter-btn]').click();
    
    // Verify combined filters
    cy.get('[data-cy=order-row]').each(($el) => {
      cy.wrap($el).find('[data-cy=order-status]').should('contain', '대기');
      cy.wrap($el).find('[data-cy=order-temperature]').should('contain', '냉동');
    });
  });

  it('should clear all filters', () => {
    cy.visit('/orders');
    
    // Apply filters
    cy.get('[data-cy=status-filter]').select('pending');
    cy.get('[data-cy=apply-filter-btn]').click();
    
    // Clear filters
    cy.get('[data-cy=clear-filters-btn]').click();
    
    // Verify all filters are reset
    cy.get('[data-cy=status-filter]').should('have.value', '');
    cy.get('[data-cy=temperature-filter]').should('have.value', '');
  });
});
