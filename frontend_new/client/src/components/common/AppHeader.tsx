import { ChevronLeftIcon } from "lucide-react";
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { Level3Gem } from "@/components/icons/Level3Gem";
import { LevelUpModal } from "@/components/modals/LevelUpModal";
import { useLocation } from "wouter";
import { getCurrentUser } from "@/utils/api";

interface AppHeaderProps {
  showBackButton?: boolean;
  onBackClick?: () => void;
}

export const AppHeader = ({ showBackButton = false, onBackClick }: AppHeaderProps): JSX.Element => {
  const [isLevelUpModalOpen, setIsLevelUpModalOpen] = useState(false);
  const [userLevel, setUserLevel] = useState("INTERMEDIATE"); // 기본값
  const [levelDisplayName, setLevelDisplayName] = useState("관심러"); // 기본값
  const [, setLocation] = useLocation();

  // 사용자 레벨 정보 로드
  useEffect(() => {
    const loadUserLevel = async () => {
      try {
        const user = await getCurrentUser();
        setUserLevel(user.level);
        
        // 레벨에 따른 표시명 설정
        switch (user.level) {
          case "BEGINNER":
            setLevelDisplayName("주린이");
            break;
          case "INTERMEDIATE":
            setLevelDisplayName("관심러");
            break;
          case "ADVANCED":
            setLevelDisplayName("전문가");
            break;
          default:
            setLevelDisplayName("관심러");
        }
      } catch (error) {
        console.error('사용자 레벨 로드 실패:', error);
        // 에러 시 기본값 유지
        setUserLevel("INTERMEDIATE");
        setLevelDisplayName("관심러");
      }
    };

    loadUserLevel();
  }, []);

  const handleCaffyClick = () => {
    setIsLevelUpModalOpen(true);
  };

  const handleInterestClick = () => {
    setLocation("/profile");
  };

  // 레벨에 따른 보석 아이콘 렌더링
  const renderLevelGem = () => {
    switch (userLevel) {
      case "BEGINNER":
        return <Level1Gem />;
      case "INTERMEDIATE":
        return <Level2Gem />;
      case "ADVANCED":
        return <Level3Gem />;
      default:
        return <Level2Gem />;
    }
  };

  return (
    <>
      <LevelUpModal 
        isOpen={isLevelUpModalOpen} 
        onClose={() => setIsLevelUpModalOpen(false)} 
      />
    <header className="fixed w-full max-w-[393px] h-[50px] top-[54px] left-0 right-0 mx-auto bg-white/95 backdrop-blur-md [border-top-style:none] [border-right-style:none] border-b [border-bottom-style:solid] [border-left-style:none] border-[#0000001a] z-40">
      {showBackButton && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute w-6 h-6 top-[13px] left-6 p-0 hover:bg-transparent"
          onClick={onBackClick}
        >
          <ChevronLeftIcon className="h-4 w-4" />
        </Button>
      )}

      <button 
        className="absolute top-0.5 left-[153px] [font-family:'Micro_5',Helvetica] font-normal text-[#1a1a1a] text-[44px] tracking-[0] leading-[normal] whitespace-nowrap cursor-pointer hover:opacity-80 transition-opacity"
        onClick={handleCaffyClick}
      >
        CAFFY
      </button>

      <button 
        className="absolute w-[80px] h-[30px] top-2.5 left-[290px] cursor-pointer hover:opacity-80 transition-opacity"
        onClick={handleInterestClick}
      >
        <div className="absolute w-6 h-6 top-[3px] left-0">
          {renderLevelGem()}
        </div>
        <div className="absolute top-1 left-7 text-black text-sm leading-[normal] [font-family:'Pretendard-Regular',Helvetica] font-normal tracking-[0] whitespace-nowrap">
          {levelDisplayName}
        </div>
      </button>
    </header>
    </>
  );
};