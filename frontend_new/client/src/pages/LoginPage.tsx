import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import {
    signInWithPopup,
    GoogleAuthProvider,
    signOut,
    onAuthStateChanged
} from 'firebase/auth';
import { auth } from '../firebase';
import { getCurrentUser, deleteUser } from '../utils/api'; // 🔧 API 함수 import

export const LoginPage = (): JSX.Element => {
    const [, setLocation] = useLocation();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [apiResult, setApiResult] = useState(null); // 🔧 API 결과 저장
    const [apiLoading, setApiLoading] = useState(false); // 🔧 API 호출 로딩
    const [deleteLoading, setDeleteLoading] = useState(false); // 🔧 탈퇴 로딩

    // Firebase Auth 상태 감지
    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            setUser(user);
            if (user) {
                console.log('사용자 로그인 감지:', user);
                setLocation("/main"); // 자동으로 메인으로 이동
            }
        });

        return () => unsubscribe();
    }, [setLocation]);

    // 페이지 로드 시 스크롤 맨 위로 이동
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    // Google 로그인
    const handleGoogleLogin = async () => {
        setLoading(true);
        setError('');

        try {
            const provider = new GoogleAuthProvider();
            const result = await signInWithPopup(auth, provider);

            console.log('Google 로그인 성공:', result.user);
            setUser(result.user);
            setLocation("/main");
        } catch (error) {
            console.error('Google 로그인 실패:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    // 🔧 백엔드 API 테스트 함수
    const testBackendAPI = async () => {
        setApiLoading(true);
        setApiResult(null);
        setError('');

        try {
            console.log('🔑 백엔드 API 호출 시작...');
            const result = await getCurrentUser(); // 🔑 토큰 자동 포함됨

            console.log('✅ 백엔드 API 호출 성공:', result);
            setApiResult(result);

        } catch (error) {
            console.error('❌ 백엔드 API 호출 실패:', error);
            setError(`API 호출 실패: ${error.message}`);
        } finally {
            setApiLoading(false);
        }
    };

    // 로그아웃
    const handleLogout = async () => {
        try {
            await signOut(auth);

            // sessionStorage 정리
            window.sessionStorage.removeItem('chatSessionId');
            console.log("세션 스토리지 정리 완료");

            console.log('✅ 로그아웃 성공');
            setUser(null);
            setApiResult(null); // 🔧 API 결과도 초기화
            window._replit = false; // 더미 모드 비활성화
            localStorage.removeItem('dummyUser'); // 더미 사용자 정보 제거
        } catch (error) {
            console.error('로그아웃 실패:', error);
        }
    };

    // 🔧 사용자 탈퇴
    const handleDeleteAccount = async () => {
        if (!window.confirm('정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
            return;
        }

        setDeleteLoading(true);
        setError('');

        try {
            console.log('🗑️ 계정 삭제 시작...');
            const result = await deleteUser();

            console.log('✅ 계정 삭제 성공:', result);

            // Firebase에서도 로그아웃
            await signOut(auth);
            setUser(null);
            setApiResult(null);

            alert('계정이 성공적으로 삭제되었습니다.');
        } catch (error) {
            console.error('❌ 계정 삭제 실패:', error);
            setError(`계정 삭제 실패: ${error.message}`);
        } finally {
            setDeleteLoading(false);
        }
    };

    // 🔧 개발용 더미 로그인
    const handleDummyLogin = () => {
        console.log('더미 로그인 실행');
        // 더미 모드 활성화
        window._replit = true;
        // 더미 사용자 정보를 localStorage에 저장
        const dummyUser = {
            uid: "dummy_user_123",
            email: "test@example.com",
            displayName: "테스트 사용자",
            photoURL: "https://via.placeholder.com/150"
        };
        localStorage.setItem('dummyUser', JSON.stringify(dummyUser));
        setLocation("/main"); // Redirect to main page
    };

    return (
        <main className="relative w-full max-w-[393px] h-[852px] mx-auto bg-white flex flex-col items-center justify-between py-16">
            <div className="flex flex-col items-center gap-8 mt-24">
                <h1 className="[font-family:'Micro_5',Helvetica] font-normal text-[#1a1a1a] text-[100px] tracking-[0] leading-[normal]">
                    CAFFY
                </h1>

                <p className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-black text-xl text-center tracking-[0] leading-8">
                    지금 로그인하고, 딱 맞는 <br />
                    주식 정보를 확인하세요
                </p>
            </div>

            {error && (
                <div className="w-[345px] p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 mb-4">
                    {error}
                </div>
            )}

            <Button
                variant="outline"
                className="flex w-[345px] items-center gap-1 px-6 py-[15px] bg-white rounded-[100px] border border-solid border-[#eaeaea] hover:bg-gray-50"
                onClick={handleGoogleLogin}
                disabled={loading}
            >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                <span className="flex-1 font-medium text-[#1a1a1a] text-base text-center">
                    {loading ? '로그인 중...' : '구글로 시작'}
                </span>
            </Button>

            {/* 🔧 개발용 더미 로그인 버튼 */}
            <Button
                onClick={handleDummyLogin}
                variant="outline"
                className="w-full mt-2"
            >
                🚀 개발용 더미 로그인
            </Button>
        </main>
    );
};