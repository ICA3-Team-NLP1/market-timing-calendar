// Firebase 설정
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Firebase 설정 (환경변수에서 가져오기)
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyCaYBhQEGujz-oj-j2mvaSNHFlVnzrGztA",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "market-timing-calendar.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "market-timing-calendar",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "market-timing-calendar.firebasestorage.app",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "539122761808",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:539122761808:web:016249bad69b51190d1155",
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-5LPG8SK2EK"
};

// Firebase 초기화
const app = initializeApp(firebaseConfig);

// Auth 인스턴스 export
export const auth = getAuth(app);
export default app; 