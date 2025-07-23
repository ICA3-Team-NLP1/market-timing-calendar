import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export const FomcResultsSection = (): JSX.Element => {
  return (
    <Card className="border-none shadow-none w-full">
      <CardContent className="p-0 pt-6 pl-6">
        <div className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-[#1a1a1a] text-2xl">
          <p className="leading-[33.6px] mb-0">놓치지 마세요</p>
          <p className="leading-[33.6px] mt-0">
            내일 &apos;
            <span className="[font-family:'Pretendard-Bold',Helvetica] font-bold">
              FOMC 결과
            </span>
            &apos;를 발표해요!
          </p>
        </div>
      </CardContent>
    </Card>
  );
};