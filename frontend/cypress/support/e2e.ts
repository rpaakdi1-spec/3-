// ***********************************************
// Cypress E2E support file
// ***********************************************

import './commands';

// Prevent TypeScript errors
declare global {
  namespace Cypress {
    interface Chainable {
      login(username: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
      seedDatabase(): Chainable<void>;
    }
  }
}

// Example: suppress uncaught exceptions in development
Cypress.on('uncaught:exception', (err, runnable) => {
  // Return false to prevent failing tests on uncaught exceptions
  return false;
});
