import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { Level3Gem } from "@/components/icons/Level3Gem";
import { useLocation } from "wouter";
import { getCalendarEvents } from "@/utils/api";

export const InsightsSection = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // 날짜 포맷 함수
  const formatEventDate = (eventDate: string) => {
    const today = new Date();
    const event = new Date(eventDate);

    // 날짜만 비교하기 위해 시간을 0으로 설정
    today.setHours(0, 0, 0, 0);
    event.setHours(0, 0, 0, 0);

    const diffTime = event.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return { label: "Today", style: "font-bold text-[#ff6b35]" };
    } else if (diffDays > 0) {
      return { label: `D-${diffDays}`, style: "font-medium text-[#666666]" };
    } else {
      return { label: `D+${Math.abs(diffDays)}`, style: "font-medium text-[#999999]" };
    }
  };

  // 레벨에 따른 아이콘 렌더링
  const getLevelGem = (level: string) => {
    switch (level) {
      case "BEGINNER":
        return <Level1Gem />;
      case "INTERMEDIATE":
        return <Level2Gem />;
      case "ADVANCED":
        return <Level3Gem />;
      default:
        return <Level1Gem />;
    }
  };

  // 레벨 숫자 변환
  const getLevelNumber = (level: string) => {
    switch (level) {
      case "BEGINNER":
        return 1;
      case "INTERMEDIATE":
        return 2;
      case "ADVANCED":
        return 3;
      default:
        return 1;
    }
  };

  // 이벤트 데이터 로드
  useEffect(() => {
    const loadUpcomingEvents = async () => {
      try {
        setLoading(true);

        // 오늘부터 7일 후까지의 날짜 범위 설정
        const today = new Date();
        const endDate = new Date();
        endDate.setDate(today.getDate() + 7);

        const startDateStr = today.toISOString().split('T')[0];
        const endDateStr = endDate.toISOString().split('T')[0];

        const eventsData = await getCalendarEvents(startDateStr, endDateStr, null);

        // 이벤트를 날짜 순으로 정렬하고 처리
        const processedEvents = eventsData
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          .slice(0, 3) // 최대 3개만 표시
          .map((event, index) => {
            const dateInfo = formatEventDate(event.date);
            return {
              id: event.id,
              level: getLevelNumber(event.level),
              label: dateInfo.label,
              labelStyle: dateInfo.style,
              title: event.title,
              description: event.description_ko || event.description || "경제 지표 발표",
              originalEvent: event
            };
          });

        setUpcomingEvents(processedEvents);
      } catch (error) {
        console.error('이벤트 로드 실패:', error);
        // 에러 시 빈 배열로 설정
        setUpcomingEvents([]);
      } finally {
        setLoading(false);
      }
    };

    loadUpcomingEvents();
  }, []);

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

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="text-[#666666]">로딩 중...</div>
        </div>
      ) : upcomingEvents.length === 0 ? (
        <div className="flex justify-center py-8">
          <div className="text-[#666666]">다가오는 일정이 없습니다.</div>
        </div>
      ) : (
        <div className="flex items-center gap-2.5 overflow-x-auto">
          {upcomingEvents.map((event) => (
            <Card
              key={event.id}
              className="flex-shrink-0 bg-[#f1f3f7] rounded-md shadow-[0px_4px_4px_#00000005] border-none cursor-pointer hover:bg-[#e1e7f1] transition-colors"
              onClick={() => setLocation(`/chat?eventId=${event.id}`)}
            >
              <CardContent className="flex flex-col items-start gap-2.5 pt-4 pb-5 px-4">
                <div className="flex items-center justify-between w-full">
                  <div className="relative w-5 h-5">
                    {getLevelGem(event.originalEvent?.level || "BEGINNER")}
                  </div>

                  <div
                    className={`relative w-fit [font-family:'Pretendard-${event.label === "Today" ? "Bold" : "Medium"}',Helvetica] ${event.labelStyle} text-xs whitespace-nowrap`}
                  >
                    {event.label}
                  </div>
                </div>

                <div className="flex flex-col w-[116px] items-start gap-2">
                  <h3 className="self-stretch mt-[-1.00px] [font-family:'Pretendard-Bold',Helvetica] font-bold text-black leading-normal text-sm">
                    {event.title}
                  </h3>

                  <p className="self-stretch [font-family:'Pretendard-Regular',Helvetica] font-normal text-black leading-[19.6px] text-sm whitespace-pre-line">
                    {event.description.length > 50 
                      ? event.description.substring(0, 50) + "..." 
                      : event.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </section>
  );
};