import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { useLocation } from "wouter";

export const InsightsSection = (): JSX.Element => {
  const [, setLocation] = useLocation();
  // Data for upcoming events
  const upcomingEvents = [
    {
      id: 1,
      level: 1,
      label: "Today",
      labelStyle: "font-bold text-[#1a1a1a]",
      title: "소비자 물가지수 발표",
      description: "앞으로 미국의 경제\n상활을 예측할 수 있어요.",
    },
    {
      id: 2,
      level: 2,
      label: "D-2",
      labelStyle: "font-medium text-[#1e1f1f]",
      title: "소비자 물가지수 발표",
      description: "앞으로 미국의 경제\n상활을 예측할 수 있어요.",
    },
    {
      id: 3,
      level: 1,
      label: "D-3",
      labelStyle: "font-medium text-[#1e1f1f]",
      title: "소비자 물가지수 발표",
      description: "앞으로 미국의 경제\n상활을 예측할 수 있어요.",
    },
  ];

  return (
    <section className="w-full px-6 pb-32">
      <div className="flex justify-between items-center mb-[31px]">
        <h2 className="[font-family:'Pretendard-Bold',Helvetica] font-bold text-[#1a1a1a] text-base">
          다가오는 일정
        </h2>
        <button 
          className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-[#1a1a1acc] text-sm hover:text-[#1a1a1a] transition-colors"
          onClick={() => setLocation("/calendar")}
        >
          더보기
        </button>
      </div>

      <div className="flex items-center gap-2.5 overflow-x-auto">
        {upcomingEvents.map((event) => (
          <Card
            key={event.id}
            className="flex-shrink-0 bg-[#f1f3f7] rounded-md shadow-[0px_4px_4px_#00000005] border-none cursor-pointer hover:bg-[#e1e7f1] transition-colors"
            onClick={() => setLocation("/chat")}
          >
            <CardContent className="flex flex-col items-start gap-2.5 pt-4 pb-5 px-4">
              <div className="flex items-center justify-between w-full">
                <div className="relative w-5 h-5">
                  {event.level === 1 ? <Level1Gem /> : <Level2Gem />}
                </div>

                <div
                  className={`relative w-fit [font-family:'Pretendard-${event.id === 1 ? "Bold" : "Medium"}',Helvetica] ${event.labelStyle} text-xs whitespace-nowrap`}
                >
                  {event.label}
                </div>
              </div>

              <div className="flex flex-col w-[116px] items-start gap-2">
                <h3 className="self-stretch mt-[-1.00px] [font-family:'Pretendard-Bold',Helvetica] font-bold text-black leading-normal text-sm">
                  {event.title}
                </h3>

                <p className="self-stretch [font-family:'Pretendard-Regular',Helvetica] font-normal text-black leading-[19.6px] text-sm whitespace-pre-line">
                  {event.description}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
};