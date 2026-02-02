// Test if localStorage has the token
const token = localStorage.getItem('auth_token');
console.log('Token in localStorage:', token ? token.substring(0, 50) + '...' : 'NOT FOUND');
