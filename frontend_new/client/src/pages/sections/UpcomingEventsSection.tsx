import React from "react";
import { Button } from "@/components/ui/button";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { useLocation } from "wouter";

export const UpcomingEventsSection = (): JSX.Element => {
  const [, setLocation] = useLocation();
  // Data for recommended questions
  const recommendedQuestions = [
    "금리 인하가 왜 중요한가요?",
    "FOMC가 뭐예요?",
    "연준이 뭐예요?",
  ];

  return (
    <section className="w-full py-8 px-6">
      <h3 className="font-bold text-[#1a1a1a] text-base mb-4 [font-family:'Pretendard-Bold',Helvetica]">
        추천 질문
      </h3>

      <div className="flex flex-col gap-2.5 items-start">
        {recommendedQuestions.map((question, index) => (
          <Button
            key={`question-${index}`}
            variant="outline"
            className="flex items-center gap-1 px-4 py-2.5 h-auto bg-[#e8f0ff] rounded-[100px] shadow-[0px_4px_4px_#00000005] border-none hover:bg-[#d8e5fa] w-fit"
            onClick={() => setLocation("/chat")}
          >
            <div className="relative w-[15px] h-[15px] flex-shrink-0">
              <svg viewBox="0 0 15 15" className="w-full h-full" fill="#444445">
                <path d="M7.5 0C3.364 0 0 3.364 0 7.5S3.364 15 7.5 15 15 11.636 15 7.5 11.636 0 7.5 0zm0 12c-.828 0-1.5-.672-1.5-1.5S6.672 9 7.5 9s1.5.672 1.5 1.5S8.328 12 7.5 12zm1.5-4.5h-3V6c0-1.657 1.343-3 3-3s3 1.343 3 3v1.5z"/>
              </svg>
            </div>
            <span className="[font-family:'Pretendard-Medium',Helvetica] font-medium text-[#444445] text-sm whitespace-nowrap">
              {question}
            </span>
          </Button>
        ))}
      </div>
    </section>
  );
};