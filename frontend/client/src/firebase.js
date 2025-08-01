
// Firebase 설정
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Validate required environment variables
if (!import.meta.env.VITE_FIREBASE_API_KEY || 
    !import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 
    !import.meta.env.VITE_FIREBASE_PROJECT_ID || 
    !import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 
    !import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || 
    !import.meta.env.VITE_FIREBASE_APP_ID || 
    !import.meta.env.VITE_FIREBASE_MEASUREMENT_ID) {
    throw new Error("Missing required Firebase environment variables. Please check your .env file.");
}

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};
// Firebase 초기화
const app = initializeApp(firebaseConfig);

// Auth 인스턴스 export
export const auth = getAuth(app);

// Firebase Auth 설정
auth.languageCode = 'ko';

export default app;
