// Quick test to verify imports work
import { navigationConfig, filterMenuByRole, getMobileNavigation, MenuItem } from './src/config/navigation';

console.log('✅ Navigation config imported successfully');
console.log(`📋 Total menu items: ${navigationConfig.length}`);

// Test filterMenuByRole
const adminMenu = filterMenuByRole(navigationConfig, 'ADMIN');
console.log(`👤 ADMIN menu items: ${adminMenu.length}`);

const dispatcherMenu = filterMenuByRole(navigationConfig, 'DISPATCHER');
console.log(`👤 DISPATCHER menu items: ${dispatcherMenu.length}`);

// Test getMobileNavigation
const mobileMenu = getMobileNavigation(adminMenu);
console.log(`📱 Mobile navigation items: ${mobileMenu.length}`);

console.log('\n✅ All imports and functions work correctly!');
