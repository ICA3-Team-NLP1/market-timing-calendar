import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ChevronLeftIcon, ChevronRightIcon, LockIcon, ChevronRight } from "lucide-react";
import { AppHeader } from "@/components/common/AppHeader";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { useLocation } from "wouter";

export const CalendarPage = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [currentDate, setCurrentDate] = useState(new Date(2025, 6)); // July 2025 (month is 0-indexed)

  const handleBackClick = () => {
    setLocation("/main");
  };

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const formatDate = (date: Date) => {
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
  };

  // Data for tabs
  const tabItems = [
    { id: "all", label: "전체", isActive: true },
    { id: "level1", label: "레벨1", isActive: false },
    { id: "level2", label: "레벨2", isActive: false },
    { id: "level3", label: "레벨3", isActive: false, isLocked: true },
  ];

  // Calendar events grouped by date
  const calendarData = [
    {
      date: "6월 25일",
      events: [
        {
          level: 1,
          title: "소비자 물가지수 발표",
          difficulty: "⭐⭐⭐",
          description: "소비자가 구입하는 상품·서비스의 평균 물가 변동 지표로 시장이 주목하는 물가지수.",
          hasDetail: true
        },
        {
          level: 2,
          title: "소비자 물가지수 발표",
          difficulty: "⭐⭐⭐",
          description: "소비자가 구입하는 상품·서비스의 평균 물가 변동 지표로 시장이 주목하는 물가지수.",
          hasDetail: true
        }
      ]
    },
    {
      date: "22일 화요일",
      events: [
        {
          level: 1,
          title: "소비자 물가지수 발표",
          difficulty: "⭐⭐⭐",
          description: "소비자가 구입하는 상품·서비스의 평균 물가 변동 지표로 시장이 주목하는 물가지수.",
          hasDetail: true
        }
      ]
    }
  ];

  return (
    <div className="relative w-full max-w-[393px] h-[852px] bg-white mx-auto">
      <Card className="relative w-full h-full rounded-lg overflow-hidden border-none">
        {/* Navigation Tab Section - Fixed at top */}
        <div className="absolute w-full h-[50px] top-[104px] left-0 bg-white/95 backdrop-blur-md border-b border-[#0000001a] z-30">
          <div className="px-6 py-2">
            <Tabs defaultValue="all" className="w-full">
              <TabsList className="flex h-10 w-full justify-start bg-transparent p-0 gap-0">
                {tabItems.map((tab) => (
                  <TabsTrigger
                    key={tab.id}
                    value={tab.id}
                    className={`h-10 px-3 py-1 relative rounded-none data-[state=active]:shadow-none ${
                      tab.isLocked
                        ? "text-[#1a1a1a33] [font-family:'Pretendard-Medium',Helvetica] font-medium"
                        : tab.isActive
                          ? "text-[#1a1a1a] [font-family:'Pretendard-Bold',Helvetica] font-bold data-[state=active]:border-b-2 data-[state=active]:border-[#1a1a1a]"
                          : "text-[#1a1a1a99] [font-family:'Pretendard-Medium',Helvetica] font-medium"
                    }`}
                    disabled={tab.isLocked}
                  >
                    {tab.label}
                    {tab.isLocked && (
                      <div className="ml-1">
                        <LockIcon className="w-4 h-4" />
                      </div>
                    )}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        </div>

        {/* Main content container */}
        <div className="absolute w-full h-[calc(852px-154px)] top-[154px] left-0 bg-white rounded-lg overflow-y-auto">
          {/* Date Navigation Section */}
          <div className="px-6 py-4">
            <div className="w-[142px] h-[36px]">
              <div className="relative w-full h-full bg-[#E8F0FF] rounded-[18px] shadow-[0px_4px_4px_rgba(0,0,0,0.02)] flex items-center justify-between px-3">
                <Button variant="ghost" size="icon" className="p-0 h-4 w-4" onClick={handlePrevMonth}>
                  <ChevronLeftIcon className="h-4 w-4 text-[#1A1A1A]" />
                </Button>
                <div className="flex items-center">
                  <span className="[font-family:'Pretendard-Medium',Helvetica] font-medium text-[#1A1A1A] text-sm tracking-[0] leading-[normal] whitespace-nowrap">
                    {formatDate(currentDate)}
                  </span>
                </div>
                <Button variant="ghost" size="icon" className="p-0 h-4 w-4" onClick={handleNextMonth}>
                  <ChevronRightIcon className="h-4 w-4 text-[#1A1A1A]" />
                </Button>
              </div>
            </div>
          </div>

          {/* Calendar Items List - Grouped by Date */}
          <div className="px-6 space-y-6">
            {calendarData.map((dateGroup, dateIndex) => (
              <div key={dateIndex} className="space-y-4">
                {/* Date Header */}
                <div className="text-sm font-medium text-[#666666] mb-3">
                  {dateGroup.date}
                </div>
                
                {/* Events for this date */}
                <div className="space-y-3">
                  {dateGroup.events.map((event, eventIndex) => (
                    <div key={eventIndex} className="bg-white rounded-xl p-4 border border-[#e5e7eb] shadow-sm">
                      {/* Event Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {event.level === 1 ? <Level1Gem /> : <Level2Gem />}
                          <span className="font-bold text-[#1a1a1a] text-[18px]">{event.title}</span>
                        </div>
                        {event.hasDetail && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-[12px] text-[#666666] p-0 h-auto font-normal hover:bg-transparent"
                            onClick={() => setLocation("/chat")}
                          >
                            자세히 보기
                            <ChevronRight className="w-3 h-3 ml-1" />
                          </Button>
                        )}
                      </div>

                      {/* Difficulty Rating */}
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-[12px] text-[#666666]">주가영향도</span>
                        <span className="text-[12px]">{event.difficulty}</span>
                      </div>

                      {/* Description */}
                      <p className="text-[14px] text-[#666666] leading-relaxed">
                        {event.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Bottom padding for scroll */}
          <div className="h-6"></div>
        </div>
      </Card>

      {/* Status bar */}
      <div className="fixed w-full max-w-[393px] h-[54px] top-0 left-0 right-0 mx-auto z-50 bg-white/95 backdrop-blur-md">
        <div className="relative h-[54px]">
          {/* Empty status bar space */}
        </div>
      </div>

      {/* Fixed Header with back button */}
      <AppHeader showBackButton={true} onBackClick={handleBackClick} />
    </div>
  );
};