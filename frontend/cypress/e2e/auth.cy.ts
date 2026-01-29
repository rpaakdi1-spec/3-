describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login page', () => {
    cy.contains('로그인').should('be.visible');
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should login successfully with valid credentials', () => {
    cy.get('input[name="username"]').type('admin');
    cy.get('input[name="password"]').type('admin123');
    cy.get('button[type="submit"]').click();
    
    cy.url().should('include', '/dashboard');
    cy.contains('대시보드').should('be.visible');
  });

  it('should show error with invalid credentials', () => {
    cy.get('input[name="username"]').type('invalid');
    cy.get('input[name="password"]').type('wrongpass');
    cy.get('button[type="submit"]').click();
    
    cy.contains('로그인 실패').should('be.visible');
  });

  it('should validate required fields', () => {
    cy.get('button[type="submit"]').click();
    cy.get('input[name="username"]:invalid').should('exist');
    cy.get('input[name="password"]:invalid').should('exist');
  });

  it('should logout successfully', () => {
    cy.login('admin', 'admin123');
    cy.visit('/dashboard');
    cy.logout();
    cy.url().should('include', '/login');
  });

  it('should redirect to dashboard when already logged in', () => {
    cy.login('admin', 'admin123');
    cy.visit('/login');
    cy.url().should('include', '/dashboard');
  });

  it('should protect routes from unauthenticated users', () => {
    cy.visit('/orders');
    cy.url().should('include', '/login');
  });
});
