import React, { useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { useLocation } from "wouter";

export const Element = (): JSX.Element => {
  const [, setLocation] = useLocation();

  // 페이지 로드 시 스크롤 맨 위로 이동
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const handleClick = () => {
    setLocation("/login");
  };

  return (
    <Card 
      className="relative w-full max-w-[393px] h-[852px] bg-[#1a1a1a] rounded-none mx-auto cursor-pointer transition-transform hover:scale-105"
      onClick={handleClick}
    >
      <CardContent className="flex items-center justify-center h-full p-0">
        <h1 className="[font-family:'Micro_5',Helvetica] font-normal text-white text-[100px] tracking-[0] leading-normal select-none">
          CAFFY
        </h1>
      </CardContent>
    </Card>
  );
};