const axios = require('axios');

// Test login with correct API endpoint
async function testLogin() {
  try {
    const response = await axios.post('http://localhost:8065/api/v1/auth/login', {
      email: 'admin@bettafish.com',
      password: 'admin123'
    });
    
    console.log('✅ Login successful!');
    console.log('Access token:', response.data.access_token.substring(0, 50) + '...');
    console.log('User:', response.data.user);
    
    // Test auth/me endpoint
    const meResponse = await axios.get('http://localhost:8065/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${response.data.access_token}`
      }
    });
    
    console.log('✅ Auth/me successful!');
    console.log('User data:', meResponse.data);
    
  } catch (error) {
    console.error('❌ Login failed:', error.response?.data || error.message);
  }
}

testLogin();