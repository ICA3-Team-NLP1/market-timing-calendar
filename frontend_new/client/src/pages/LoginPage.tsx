import React from "react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export const LoginPage = (): JSX.Element => {
  const [, setLocation] = useLocation();

  const handleGoogleLogin = () => {
    setLocation("/main");
  };
  return (
    <main className="relative w-full max-w-[393px] h-[852px] mx-auto bg-white flex flex-col items-center justify-between py-16">
      <div className="flex flex-col items-center gap-8 mt-24">
        <h1 className="[font-family:'Micro_5',Helvetica] font-normal text-[#1a1a1a] text-[100px] tracking-[0] leading-[normal]">
          CAFFY
        </h1>

        <p className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-black text-xl text-center tracking-[0] leading-8">
          지금 로그인하고, 딱 맞는 <br />
          주식 정보를 확인해 보세요
        </p>
      </div>

      <Button
        variant="outline"
        className="flex w-[345px] items-center gap-1 px-6 py-[15px] bg-white rounded-[100px] border border-solid border-[#eaeaea] hover:bg-gray-50"
        onClick={handleGoogleLogin}
      >
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        <span className="flex-1 font-medium text-[#1a1a1a] text-base text-center">
          구글로 시작하기
        </span>
      </Button>
    </main>
  );
};