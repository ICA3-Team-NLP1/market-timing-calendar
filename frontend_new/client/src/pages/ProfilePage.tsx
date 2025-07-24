import { ChevronLeftIcon, ChevronRightIcon, InfoIcon } from "lucide-react";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useLocation } from "wouter";
import { Level2GemLarge } from "@/components/icons/Level2GemLarge";
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';
import { deleteUser } from '../utils/api';

export const ProfilePage = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState('');

  // 로그아웃 함수
  const handleLogout = async () => {
    try {
      await signOut(auth);
      window._replit = false; // 더미 모드 비활성화
      localStorage.removeItem('dummyUser'); // 더미 사용자 정보 제거
      console.log('✅ 로그아웃 성공');
      setLocation("/login");
    } catch (error) {
      console.error('로그아웃 실패:', error);
      setError('로그아웃 중 오류가 발생했습니다.');
    }
  };

  // 회원 탈퇴 함수
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
      window._replit = false;
      localStorage.removeItem('dummyUser');

      alert('계정이 성공적으로 삭제되었습니다.');
      setLocation("/login");
    } catch (error) {
      console.error('❌ 계정 삭제 실패:', error);
      setError(`계정 삭제 실패: ${error.message}`);
    } finally {
      setDeleteLoading(false);
    }
  };

  // Menu items data for the list
  const menuItems = [
    { icon: "💬", text: "챗봇 대화", onClick: () => setLocation("/main") },
    { icon: "⚙️", text: "챗봇 레벨 설정" },
    { icon: "📅", text: "증권 캘린더", onClick: () => setLocation("/calendar") },
  ];

  // Progress bar data
  const progressItems = [
    { label: "서비스 방문", value: 62 },
    { label: "챗봇 대화", value: 53 },
    { label: "일정 조회", value: 70 },
  ];

  return (
    <div className="relative w-full max-w-[393px] min-h-screen bg-white mx-auto">
      {/* Background with blur effects */}
      <div className="absolute w-full h-full top-0 left-0 rounded-lg">
        <div className="absolute w-full h-full top-0 left-0 bg-[#f5f6fa] rounded-lg overflow-hidden">
          <div className="relative w-[887px] h-[1160px] top-[-89px] left-[-162px]">
            {/* Background blur images */}
            <div className="absolute w-[612px] h-[659px] top-[165px] left-0 bg-gradient-to-r from-blue-200/30 to-purple-200/30 rounded-full blur-3xl" />
            <div className="absolute w-[441px] h-[334px] top-[116px] left-[183px] bg-gradient-to-r from-pink-200/30 to-blue-200/30 rounded-full blur-3xl" />
            <div className="absolute w-[427px] h-[315px] top-0 left-[190px] bg-gradient-to-r from-white/50 to-gray-200/30 rounded-full blur-3xl" />
            <div className="absolute w-[755px] h-[772px] top-[388px] left-[131px] bg-gradient-to-r from-purple-300/30 to-pink-300/30 rounded-full blur-3xl" />
            <div className="absolute w-[439px] h-[496px] top-[325px] left-[191px] bg-gradient-to-r from-blue-300/30 to-cyan-300/30 rounded-full blur-3xl" />
            
            <div className="absolute w-full h-full top-[89px] left-[162px] bg-white/55 backdrop-blur-sm" />
          </div>
        </div>

        {/* Menu items */}
        {menuItems.map((item, index) => (
          <div
            key={`menu-item-${index}`}
            className={`flex w-[345px] items-center justify-between px-[18px] py-2.5 absolute left-6 cursor-pointer hover:bg-white/20 rounded-lg transition-colors ${
              index === 0
                ? "top-[440px]"
                : index === 1
                  ? "top-[484px]"
                  : "top-[528px]"
            }`}
            onClick={item.onClick}
          >
            <div className="inline-flex items-center gap-3">
              <div className="text-lg">
                {item.icon}
              </div>
              <div className="[font-family:'Pretendard-Medium',Helvetica] font-medium text-[#1a1a1a] text-sm">
                {item.text}
              </div>
            </div>
            <div className="relative w-6 h-6">
              <ChevronRightIcon className="h-4 w-4 absolute top-1 left-1 text-[#1a1a1a]" />
            </div>
          </div>
        ))}

        {/* User level card */}
        <Card className="absolute w-[345px] h-[310px] top-[129px] left-6 bg-white rounded-[10px] shadow-[0px_4px_4px_#00000003] border-none">
          <CardContent className="p-0">
            {/* Level icon and title */}
            <div className="absolute w-[100px] h-[124px] top-[13px] left-[123px]">
              <div className="relative h-[123px]">
                <div className="absolute w-[100px] h-[100px] top-0 left-0 flex items-center justify-center">
                  <Level2GemLarge />
                </div>
                <div className="absolute top-[99px] left-6 [font-family:'Pretendard-Bold',Helvetica] font-bold text-[#1a1a1a] text-xl tracking-[0] leading-[normal] whitespace-nowrap">
                  관심러
                </div>
              </div>
            </div>

            {/* Progress bars */}
            <div className="flex flex-col w-[301px] items-start gap-3 absolute top-[151px] left-[22px]">
              {progressItems.map((item, index) => (
                <div
                  key={`progress-${index}`}
                  className="flex items-center gap-2.5 relative self-stretch w-full flex-[0_0_auto]"
                >
                  <div className="inline-flex items-center justify-center gap-2.5 relative flex-[0_0_auto]">
                    <div className="relative w-20 [font-family:'Pretendard-Medium',Helvetica] font-medium text-[#1a1a1a] text-sm tracking-[0] leading-[normal]">
                      {item.label}
                    </div>
                  </div>
                  <div className="relative w-[208px] h-2.5">
                    <Progress
                      value={item.value}
                      className="h-2.5 bg-[#e8e8e8] rounded-[10px]"
                    />
                  </div>
                </div>
              ))}
            </div>

            <Separator className="absolute w-[302px] h-px top-[258px] left-[22px]" />

            {/* InfoIcon text */}
            <div className="absolute w-[301px] h-[34px] top-[270px] left-[22px]">
              <div className="absolute w-[279px] -top-px left-[22px] [font-family:'Pretendard-Regular',Helvetica] font-normal text-[#1a1a1acc] text-xs tracking-[0] leading-[16.8px]">
                레벨이 오르면 더 많은 시장 일정과 전문적인 해설을 <br />
                확인할 수 있어요.
              </div>
              <div className="absolute w-4 h-4 top-px left-0">
                <InfoIcon className="h-4 w-4 text-[#1a1a1acc]" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error message */}
        {error && (
          <div className="absolute top-[720px] left-6 w-[345px] p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Logout and Delete Account buttons */}
        <div className="absolute top-[760px] left-6 w-[345px] flex flex-col gap-3">
          <Button
            variant="secondary"
            className="bg-[#f1f3f7] rounded-[100px] px-4 py-2.5 h-auto"
            onClick={handleLogout}
          >
            <span className="[font-family:'Pretendard-SemiBold',Helvetica] font-semibold text-[#444445] text-lg">
              로그아웃
            </span>
          </Button>
          
          <Button
            variant="destructive"
            className="rounded-[100px] px-4 py-2.5 h-auto"
            onClick={handleDeleteAccount}
            disabled={deleteLoading}
          >
            <span className="[font-family:'Pretendard-SemiBold',Helvetica] font-semibold text-white text-lg">
              {deleteLoading ? '🗑️ 삭제 중...' : '🗑️ 회원 탈퇴'}
            </span>
          </Button>
        </div>
      </div>

      {/* Header */}
      <header className="fixed w-full max-w-[393px] h-[50px] top-[54px] left-0 right-0 mx-auto bg-white border-b border-[#0000001a] z-40">
        <div className="absolute top-0.5 left-[153px] [font-family:'Micro_5',Helvetica] font-normal text-[#1a1a1a] text-[44px] tracking-[0] leading-[normal] whitespace-nowrap">
          CAFFY
        </div>
        <Button
          variant="ghost"
          className="absolute top-[13px] left-6 p-0 h-6 w-6"
          onClick={() => setLocation("/main")}
        >
          <ChevronLeftIcon className="h-5 w-5 text-[#1a1a1a]" />
        </Button>
      </header>

      {/* Status bar placeholder - removed time display per user request */}
      <div className="fixed w-full max-w-[393px] h-[54px] top-0 left-0 right-0 mx-auto bg-white z-50">
        <div className="relative h-[54px]">
          {/* Battery and signal indicators would go here */}
        </div>
      </div>
    </div>
  );
};