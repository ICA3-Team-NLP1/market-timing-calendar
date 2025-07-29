import React, { useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { InsightsSection } from "./sections/InsightsSection";
import { UpcomingEventsSection } from "./sections/UpcomingEventsSection";
import { AppHeader } from "@/components/common/AppHeader";
import { ChatInput } from "@/components/common/ChatInput";
import { useLocation } from "wouter";
import { auth } from "../firebase.js";
import { onAuthStateChanged } from "firebase/auth";

export const MainPage = (): JSX.Element => {
  const [, setLocation] = useLocation();

  // 인증 상태 확인 및 리다이렉트
  useEffect(() => {
    console.log('🏠 MainPage useEffect 실행');
    
    // 더미 모드 체크
    const isDummyMode = window._replit === true;
    const dummyUser = localStorage.getItem('dummyUser');
    
    console.log('🏠 MainPage 더미 모드 체크:');
    console.log('🏠 isDummyMode:', isDummyMode);
    console.log('🏠 dummyUser 존재:', !!dummyUser);
    
    if (isDummyMode && dummyUser) {
      console.log('🏠 더미 모드 감지 - Firebase 리스너 생략');
      return;
    }

    console.log('🏠 Firebase 인증 리스너 등록');
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      console.log('🏠 Firebase 인증 상태:', user ? '로그인됨' : '로그아웃됨');
      if (!user) {
        console.log('🏠 사용자 없음 - /login으로 리다이렉트');
        setLocation('/login');
      }
    });

    return () => {
      console.log('🏠 Firebase 리스너 해제');
      unsubscribe();
    };
  }, [setLocation]);

  // 페이지 로드 시 스크롤 맨 위로 이동
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <div className="relative w-full max-w-[393px] h-full min-h-[852px] bg-white overflow-y-auto mx-auto">
      <div className="relative w-full h-full">
        <div className="relative w-full h-full bg-[#f5f6fa] rounded-lg overflow-hidden border-[none] before:content-[''] before:absolute before:inset-0 before:p-px before:rounded-lg before:[background:linear-gradient(180deg,rgba(31,31,51,0.04)_0%,rgba(31,31,51,0)_100%)] before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:z-[1] before:pointer-events-none">
          <div className="absolute w-full h-full inset-0">
            {/* Background blur circles */}
            <div className="relative w-[887px] h-[1160px] top-[-89px] left-[-162px]">
              <div className="absolute w-[612px] h-[659px] top-[165px] left-0 bg-gradient-radial from-blue-200/30 to-transparent rounded-full blur-3xl" />
              <div className="absolute w-[441px] h-[334px] top-[116px] left-[183px] bg-gradient-radial from-purple-200/20 to-transparent rounded-full blur-2xl" />
              <div className="absolute w-[427px] h-[315px] top-0 left-[190px] bg-gradient-radial from-white/40 to-transparent rounded-full blur-xl" />
              <div className="absolute w-[755px] h-[772px] top-[388px] left-[131px] bg-gradient-radial from-purple-300/25 to-transparent rounded-full blur-3xl" />
              <div className="absolute w-[439px] h-[496px] top-[325px] left-[191px] bg-gradient-radial from-blue-300/30 to-transparent rounded-full blur-2xl" />
              <div className="absolute w-full h-full top-[89px] left-[162px] bg-[#ffffff8c] backdrop-blur-sm backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(4px)_brightness(100%)]" />
            </div>
          </div>
        </div>

        {/* Status bar - removed time and battery */}
        <div className="fixed w-full max-w-[393px] h-[54px] top-0 left-0 right-0 mx-auto z-50 bg-white/95 backdrop-blur-md">
          <div className="relative h-[54px]">
            {/* Empty status bar space */}
          </div>
        </div>

        {/* Main content container */}
        <div className="relative w-full flex flex-col pt-[104px] pb-[90px]">{/* increased padding-top for fixed header and bottom for chat input */}

          {/* Upcoming Events Section */}
          <div className="mt-4">
            <UpcomingEventsSection />
          </div>

          

          {/* Insights Section */}
          <div className="mt-4 mb-20">
            <InsightsSection />
          </div>
        </div>
      </div>

      {/* Fixed Header */}
      <AppHeader />

      {/* Fixed Chat Input */}
      <ChatInput readOnly={false} />
    </div>
  );
};