describe('Orders Management', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    cy.visit('/orders');
  });

  it('should display orders list', () => {
    cy.contains('주문 관리').should('be.visible');
    cy.get('[data-testid="orders-table"]').should('be.visible');
  });

  it('should create new order', () => {
    cy.get('[data-testid="create-order-button"]').click();
    cy.get('[data-testid="order-modal"]').should('be.visible');
    
    cy.get('input[name="customer_name"]').type('Test Customer');
    cy.get('input[name="phone"]').type('010-1234-5678');
    cy.get('input[name="address"]').type('서울시 강남구 테스트로 123');
    cy.get('select[name="temperature_zone"]').select('냉동');
    cy.get('input[name="pallet_count"]').type('2');
    cy.get('input[name="weight"]').type('500');
    
    cy.get('[data-testid="submit-order"]').click();
    cy.contains('주문이 생성되었습니다').should('be.visible');
  });

  it('should search orders', () => {
    cy.get('input[name="search"]').type('Test Customer');
    cy.get('[data-testid="orders-table"]').should('contain', 'Test Customer');
  });

  it('should filter orders by status', () => {
    cy.get('select[name="status"]').select('진행 중');
    cy.get('[data-testid="orders-table"]').should('be.visible');
  });

  it('should view order details', () => {
    cy.get('[data-testid="order-row"]').first().click();
    cy.get('[data-testid="order-detail-modal"]').should('be.visible');
  });

  it('should update order status', () => {
    cy.get('[data-testid="order-row"]').first().within(() => {
      cy.get('[data-testid="status-dropdown"]').select('완료');
    });
    cy.contains('상태가 업데이트되었습니다').should('be.visible');
  });

  it('should delete order', () => {
    cy.get('[data-testid="order-row"]').first().within(() => {
      cy.get('[data-testid="delete-button"]').click();
    });
    cy.get('[data-testid="confirm-dialog"]').within(() => {
      cy.get('[data-testid="confirm-button"]').click();
    });
    cy.contains('주문이 삭제되었습니다').should('be.visible');
  });
});
