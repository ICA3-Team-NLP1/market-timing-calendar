import React from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Level2Gem_LevelUp } from "@/components/icons/Level2Gem_LevelUp";
import { Level3Gem_LevelUp } from "@/components/icons/Level3Gem_LevelUp";

interface LevelUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  levelUpData?: {
    newLevel: string;
    message?: string;
    exp?: Record<string, number>;
  };
}

export const LevelUpModal = ({ isOpen, onClose, levelUpData }: LevelUpModalProps): JSX.Element => {
  const levelMessage = levelUpData?.message || "레벨업을 축하합니다!";
  
  // 레벨에 따른 레벨업 아이콘 렌더링
  const renderLevelUpGem = () => {
    switch (levelUpData?.newLevel) {
      case "INTERMEDIATE":
        return <Level2Gem_LevelUp />;
      case "ADVANCED":
        return <Level3Gem_LevelUp />;
      default:
        return <Level2Gem_LevelUp />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="fixed w-[346px] h-[328px] top-[270px] left-1/2 -translate-x-1/2 bg-white rounded-[10px] p-0 border-none max-w-none">
        <DialogTitle className="sr-only">Level Up</DialogTitle>
        <DialogDescription className="sr-only">You have reached level 3! Your insights and interpretations are now richer.</DialogDescription>
        <div className="absolute w-[220px] h-[219px] top-[53px] left-[65px]">
          <div className="absolute w-[134px] h-[136px] top-0 left-[41px]">
            {renderLevelUpGem()}
          </div>
          <div className="absolute top-[148px] left-[23px] [font-family:'Pretendard-Bold',Helvetica] font-bold text-[#1a1a1a] text-[32px] tracking-[0] leading-[normal] whitespace-nowrap">
            LEVEL UP !
          </div>
          <div className="absolute top-[197px] left-0 [font-family:'Pretendard-Medium',Helvetica] font-medium text-[#1a1a1a] text-lg tracking-[0] leading-[normal] text-center">
            {levelMessage}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};