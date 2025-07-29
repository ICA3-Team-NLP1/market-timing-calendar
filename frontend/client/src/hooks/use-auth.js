import { useEffect, useState } from 'react';
import { useLocation } from 'wouter';
import { auth } from '../firebase.js';
import { onAuthStateChanged } from 'firebase/auth';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [, setLocation] = useLocation();

  useEffect(() => {
    // 더미 모드 체크 (더 강력한 감지)
    const isDummyMode = window._replit === true;
    const dummyUser = localStorage.getItem('dummyUser');
    
    console.log('🔍 useAuth 초기화');
    console.log('🔍 window._replit:', window._replit);
    console.log('🔍 isDummyMode:', isDummyMode);
    console.log('🔍 dummyUser 존재:', !!dummyUser);
    console.log('🔍 dummyUser 내용:', dummyUser);
    
    // 더미 모드가 활성화되어 있고 더미 사용자가 있으면
    if (isDummyMode && dummyUser) {
      console.log('✅ 더미 모드 감지 - localStorage에서 사용자 로드');
      try {
        const parsedUser = JSON.parse(dummyUser);
        console.log('✅ 더미 사용자 파싱 성공:', parsedUser);
        setUser(parsedUser);
        setLoading(false);
        console.log('✅ 더미 사용자 설정 완료, Firebase 리스너 생략');
        return;
      } catch (error) {
        console.error('❌ 더미 사용자 정보 파싱 오류:', error);
      }
    }

    console.log('🔥 Firebase 인증 리스너 등록 시작');
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      console.log('🔥 Firebase 인증 상태 변경:', user ? '로그인됨' : '로그아웃됨');
      if (user) {
        console.log('🔥 Firebase 사용자 정보:', user.uid, user.email);
      }
      setUser(user);
      setLoading(false);
    });

    return () => {
      console.log('🔥 Firebase 인증 리스너 해제');
      unsubscribe();
    };
  }, []);

  const redirectToLogin = () => {
    console.log('🚨 redirectToLogin 함수 호출됨');
    
    // 더미 모드 체크를 더 강력하게
    const isDummyMode = window._replit === true;
    const dummyUser = localStorage.getItem('dummyUser');
    
    console.log('🚨 현재 상태 체크:');
    console.log('🚨 window._replit:', window._replit);
    console.log('🚨 isDummyMode:', isDummyMode);
    console.log('🚨 dummyUser 존재:', !!dummyUser);
    console.log('🚨 dummyUser 내용:', dummyUser);
    
    // 더미 모드이고 더미 사용자가 있으면 리다이렉트하지 않음
    if (isDummyMode && dummyUser) {
      console.log('✋ 더미 모드 감지 - 리다이렉트 차단함');
      console.log('✋ /login으로 이동하지 않음');
      return;
    }
    
    console.log('➡️ 일반 모드 - /login으로 리다이렉트 실행');
    setLocation('/login');
  };

  return { user, loading, redirectToLogin };
}; 