import { ChevronLeftIcon } from "lucide-react";
import React from "react";
import { Button } from "@/components/ui/button";

export const HeaderSection = (): JSX.Element => {
  return (
    <header className="w-full h-[50px] bg-transparent border-b border-[#0000001a] flex items-center justify-between px-6">
      <Button variant="ghost" size="icon" className="p-0 h-6 w-6">
        <ChevronLeftIcon className="h-4 w-4" />
      </Button>

      <div className="[font-family:'Micro_5',Helvetica] font-normal text-[#1a1a1a] text-[44px] tracking-[0] leading-[normal]">
        CAFFY
      </div>

      <div className="flex items-center gap-1">
        <div className="relative w-[22px] h-[19px]">
          <svg viewBox="0 0 22 19" className="w-full h-full object-contain" fill="#1a1a1a">
            <path d="M11 0L14 7h8l-6.5 5L18 19l-7-5-7 5 2.5-7L0 7h8z"/>
          </svg>
          <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
            <span className="text-[9.6px] [font-family:'Anta',Helvetica] font-normal text-white tracking-[0] leading-[normal]">
              2
            </span>
          </div>
        </div>
        <span className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-black leading-[normal] text-sm tracking-[0]">
          관심러
        </span>
      </div>
    </header>
  );
};