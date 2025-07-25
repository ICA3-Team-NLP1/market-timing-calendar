import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ChevronLeftIcon, ChevronRightIcon, LockIcon, ChevronRight } from "lucide-react";
import { AppHeader } from "@/components/common/AppHeader";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { Level3Gem } from "@/components/icons/Level3Gem";
import { useLocation } from "wouter";
import { getCalendarEvents, getCurrentUser } from "@/utils/api";

export const CalendarPage = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [currentDate, setCurrentDate] = useState(new Date(2025, 6)); // July 2025 (month is 0-indexed)
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [userLevel, setUserLevel] = useState("BEGINNER");

  // 페이지 로드 시 스크롤 맨 위로 이동
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

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

  // API에서 이벤트 데이터 로드
  const loadEvents = async () => {
    try {
      setLoading(true);
      const startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];

      // 모든 이벤트를 가져와서 프론트엔드에서 필터링
      const eventsData = await getCalendarEvents(startDateStr, endDateStr, null);
      setEvents(eventsData);
    } catch (error) {
      console.error('이벤트 로드 실패:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  // 사용자 정보 로드
  useEffect(() => {
    const loadUserInfo = async () => {
      try {
        const user = await getCurrentUser();
        setUserLevel(user.level);
      } catch (error) {
        console.error('사용자 정보 로드 실패:', error);
        setUserLevel("BEGINNER"); // 기본값
      }
    };

    loadUserInfo();
  }, []);

  useEffect(() => {
    loadEvents();
  }, [currentDate]); // activeTab 의존성 제거 - 프론트엔드에서 필터링하므로

  // activeTab이 변경될 때만 리렌더링 (API 재호출 없이)
  useEffect(() => {
    // 탭 변경 시 추가 로직이 필요하면 여기에 작성
  }, [activeTab]);

  // 사용자 레벨에 따른 탭 잠금 여부 결정
  const getTabLockStatus = (tabLevel) => {
    switch (userLevel) {
      case "BEGINNER":
        return tabLevel === "level2" || tabLevel === "level3";
      case "INTERMEDIATE":
        return tabLevel === "level3";
      case "ADVANCED":
        return false;
      default:
        return tabLevel !== "all" && tabLevel !== "level1";
    }
  };

  // Data for tabs - 사용자 레벨에 따른 탭 활성화
  const tabItems = [
    { id: "all", label: "전체", isActive: activeTab === "all", isLocked: false },
    { id: "level1", label: "레벨1", isActive: activeTab === "level1", isLocked: false },
    { id: "level2", label: "레벨2", isActive: activeTab === "level2", isLocked: getTabLockStatus("level2") },
    { id: "level3", label: "레벨3", isActive: activeTab === "level3", isLocked: getTabLockStatus("level3") },
  ];

  // 이벤트를 날짜별로 그룹핑하고 popularity 순으로 정렬
  const groupEventsByDate = (events) => {
    const grouped = {};

    // 탭에 따른 이벤트 필터링
    let filteredEvents = events;
    if (activeTab === "level1") {
      filteredEvents = events.filter(event => event.level === "BEGINNER");
    } else if (activeTab === "level2") {
      filteredEvents = events.filter(event => event.level === "INTERMEDIATE");
    } else if (activeTab === "level3") {
      filteredEvents = events.filter(event => event.level === "ADVANCED");
    }
    // activeTab === "all"인 경우는 모든 이벤트를 표시

    filteredEvents.forEach(event => {
      const eventDate = new Date(event.date);
      const dateKey = eventDate.getDate(); // 날짜만 숫자로 저장
      const displayDateKey = `${eventDate.getMonth() + 1}월 ${eventDate.getDate()}일`;

      if (!grouped[dateKey]) {
        grouped[dateKey] = {
          displayDate: displayDateKey,
          actualDate: eventDate,
          events: []
        };
      }

      grouped[dateKey].events.push({
        id: event.id,
        level: event.level === "BEGINNER" ? 1 : event.level === "INTERMEDIATE" ? 2 : 3,
        title: event.title,
        difficulty: getImpactStars(event.impact),
        description: event.description_ko || event.description,
        hasDetail: true,
        popularity: event.popularity || 1
      });
    });

    // 각 날짜별로 popularity 순으로 정렬 (높은 순)
    Object.keys(grouped).forEach(dateKey => {
      grouped[dateKey].events.sort((a, b) => b.popularity - a.popularity);
    });

    // 날짜 순으로 정렬된 배열로 변환
    return Object.entries(grouped)
      .map(([dateKey, dateData]) => ({ 
        date: dateData.displayDate, 
        events: dateData.events,
        sortDate: dateData.actualDate
      }))
      .sort((a, b) => a.sortDate.getTime() - b.sortDate.getTime());
  };

  // impact를 별표로 변환하는 함수
  const getImpactStars = (impact) => {
    switch(impact) {
      case "HIGH": return "⭐⭐⭐";
      case "MEDIUM": return "⭐⭐";
      case "LOW": return "⭐";
      default: return "⭐⭐";
    }
  };

  const calendarData = groupEventsByDate(events);

  return (
    <div className="relative w-full max-w-[393px] h-[852px] bg-white mx-auto">
      <Card className="relative w-full h-full rounded-lg overflow-hidden border-none">
        {/* Navigation Tab Section - Fixed at top */}
        <div className="absolute w-full h-[50px] top-[104px] left-0 bg-white/95 backdrop-blur-md border-b border-[#0000001a] z-30">
          <div className="px-6 py-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="flex h-10 w-full justify-start bg-transparent p-0 gap-0">
                {tabItems.map((tab) => (
                  <TabsTrigger
                    key={tab.id}
                    value={tab.id}
                    className={`h-10 px-3 py-1 relative rounded-none data-[state=active]:shadow-none ${
                      tab.isLocked
                        ? "text-[#1a1a1a33] [font-family:'Pretendard-Medium',Helvetica] font-medium cursor-not-allowed"
                        : tab.isActive
                          ? "text-[#1a1a1a] [font-family:'Pretendard-Bold',Helvetica] font-bold data-[state=active]:border-b-2 data-[state=active]:border-[#1a1a1a]"
                          : "text-[#1a1a1a99] [font-family:'Pretendard-Medium',Helvetica] font-medium"
                    }`}
                    disabled={tab.isLocked}
                    onClick={tab.isLocked ? (e) => e.preventDefault() : undefined}
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
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="text-[#666666]">로딩 중...</div>
              </div>
            ) : calendarData.length === 0 ? (
              <div className="flex flex-col items-center py-8">
                <div className="text-[#666666] mb-2">이 기간에는 등록된 이벤트가 없습니다.</div>
                <div className="text-[#999999] text-sm">다른 월을 선택해보세요.</div>
              </div>
            ) : (
              calendarData.map((dateGroup, dateIndex) => (
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
                          {event.level === 1 ? <Level1Gem /> : event.level === 2 ? <Level2Gem /> : <Level3Gem />}
                          <span className="font-bold text-[#1a1a1a] text-[18px]">{event.title}</span>
                        </div>
                        {event.hasDetail && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-[12px] text-[#666666] p-0 h-auto font-normal hover:bg-transparent"
                            onClick={() => setLocation(`/chat?eventId=${event.id}`)}
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
              ))
            )}
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