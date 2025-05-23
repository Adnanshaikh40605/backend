#!/usr/bin/env node

/**
 * Deployment Helper Script
 * This script helps you update your environment variables
 */

console.log('========================================');
console.log('Blog CMS Deployment Helper');
console.log('========================================');
console.log('\nThis script will help you update your environment variables for deployment.\n');

console.log('BACKEND (Railway) Configuration:');
console.log('--------------------------------');
console.log('URL: https://backend-production-0150.up.railway.app/');
console.log('\nEnvironment variables to set on Railway:');
console.log(`
DEBUG=False
ALLOWED_HOSTS=backend-production-0150.up.railway.app,.railway.app
CORS_ALLOWED_ORIGINS=https://dohblog.vercel.app
CORS_ALLOW_ALL_ORIGINS=False
FRONTEND_URL=https://dohblog.vercel.app
CSRF_TRUSTED_ORIGINS=https://dohblog.vercel.app
`);

console.log('\nFRONTEND (Vercel) Configuration:');
console.log('--------------------------------');
console.log('URL: https://dohblog.vercel.app/');
console.log('\nEnvironment variables to set on Vercel:');
console.log(`
VITE_API_BASE_URL=https://backend-production-0150.up.railway.app
VITE_MEDIA_URL=https://backend-production-0150.up.railway.app/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=false
`);

console.log('\nIMPORTANT STEPS:');
console.log('---------------');
console.log('1. Set the environment variables on Railway and Vercel');
console.log('2. Redeploy your frontend on Vercel');
console.log('3. Test the connection between frontend and backend');
console.log('\nFor more details, see DEPLOYMENT_GUIDE.md');
console.log('========================================'); 