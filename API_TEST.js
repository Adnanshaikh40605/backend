// API Test Script
// Copy this into your browser console to test Railway API connectivity

// Base API URL
const API_BASE_URL = 'https://backend-production-0150.up.railway.app';

// Helper function to get a CSRF token from cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Function to test API endpoints
async function testAPI() {
  console.log('🔍 Testing Railway API connection...');
  
  try {
    // Test 1: Root URL
    console.log('Test 1: Checking root URL');
    const rootResponse = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
    });
    
    if (rootResponse.ok) {
      console.log('✅ Root URL accessible:', rootResponse.status);
    } else {
      console.error('❌ Root URL error:', rootResponse.status);
    }
    
    // Test 2: API posts endpoint
    console.log('\nTest 2: Checking API posts endpoint');
    const postsResponse = await fetch(`${API_BASE_URL}/api/posts/`, {
      method: 'GET',
    });
    
    if (postsResponse.ok) {
      const postsData = await postsResponse.json();
      console.log('✅ API posts endpoint accessible');
      console.log('📊 Posts data:', postsData);
    } else {
      console.error('❌ API posts endpoint error:', postsResponse.status);
    }
    
    // Test 3: Media access
    console.log('\nTest 3: Checking media access');
    const mediaResponse = await fetch(`${API_BASE_URL}/media/test-access`, {
      method: 'GET',
    });
    
    if (mediaResponse.ok) {
      console.log('✅ Media URL accessible');
    } else {
      console.log('ℹ️ Media URL returned:', mediaResponse.status, '(404 is normal if the test file doesn\'t exist)');
    }
    
    // Test 4: CORS with credentials
    console.log('\nTest 4: Testing CORS with credentials');
    const corsResponse = await fetch(`${API_BASE_URL}/api/posts/`, {
      method: 'GET',
      credentials: 'include'
    });
    
    if (corsResponse.ok) {
      console.log('✅ CORS with credentials successful');
    } else {
      console.error('❌ CORS with credentials failed:', corsResponse.status);
    }
    
    // Test 5: CSRF Token
    console.log('\nTest 5: CSRF Token Check');
    // First, get a CSRF token by visiting the Django site with credentials
    console.log('Checking for existing CSRF token...');
    const csrfToken = getCookie('csrftoken');
    
    if (csrfToken) {
      console.log('✅ CSRF Token found in cookies:', csrfToken.substring(0, 10) + '...');
      
      // Try a simple POST request with the token
      console.log('Testing POST request with CSRF token...');
      try {
        const testPostResponse = await fetch(`${API_BASE_URL}/api/posts/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          credentials: 'include',
          body: JSON.stringify({
            title: 'Test Post (Will be rejected without auth)',
            content: 'This is a test post to verify CSRF functionality.'
          })
        });
        
        console.log('POST request response status:', testPostResponse.status);
        if (testPostResponse.status === 403) {
          console.log('ℹ️ Got 403 - This is expected if you\'re not logged into the Django admin');
          console.log('✅ CSRF token is being properly sent');
        } else if (testPostResponse.status === 201) {
          console.log('✅ POST request successful (you are logged in)');
        } else {
          console.log('⚠️ Unexpected status code for POST request');
        }
      } catch (error) {
        console.error('Error during POST request test:', error);
      }
    } else {
      console.log('⚠️ No CSRF token found in cookies');
      console.log('To get a CSRF token:');
      console.log('1. Visit the Django admin at ' + API_BASE_URL + '/admin/');
      console.log('2. Log in with your admin credentials');
      console.log('3. Run this test again');
    }
    
    console.log('\n📝 Summary:');
    console.log('If all tests pass, your API is configured correctly.');
    console.log('If you see CORS errors, make sure your frontend domain is properly configured in CORS_ALLOWED_ORIGINS.');
    console.log('If CSRF tests failed, ensure your frontend URL is in CSRF_TRUSTED_ORIGINS.');
    
  } catch (error) {
    console.error('❌ API test failed with error:', error);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check if the Railway URL is correct');
    console.log('2. Verify the API is running');
    console.log('3. Check for CORS configuration issues');
    console.log('4. Make sure your internet connection is stable');
  }
}

// Run the tests
testAPI(); 