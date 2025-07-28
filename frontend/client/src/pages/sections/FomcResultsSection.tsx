
import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { getCalendarEvents } from "@/utils/api";

export const FomcResultsSection = (): JSX.Element => {
  const [upcomingEvent, setUpcomingEvent] = useState(null);
  const [daysUntil, setDaysUntil] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUpcomingEvent = async () => {
      try {
        // 오늘부터 7일 후까지의 이벤트 조회
        const today = new Date();
        const futureDate = new Date();
        futureDate.setDate(today.getDate() + 7);

        const startDate = today.toISOString().split('T')[0];
        const endDate = futureDate.toISOString().split('T')[0];

        const events = await getCalendarEvents(startDate, endDate);

        if (events && events.length > 0) {
          // 날짜순으로 정렬하고 가장 빠른 이벤트 선택
          const sortedEvents = events.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
          const nextEvent = sortedEvents[0];
          
          // D-day 계산
          const eventDate = new Date(nextEvent.date);
          const todayDate = new Date();
          todayDate.setHours(0, 0, 0, 0);
          eventDate.setHours(0, 0, 0, 0);
          
          const timeDiff = eventDate.getTime() - todayDate.getTime();
          const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
          
          setUpcomingEvent(nextEvent);
          setDaysUntil(daysDiff);
        }
      } catch (error) {
        console.error('이벤트 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUpcomingEvent();
  }, []);

  if (loading) {
    return (
      <section className="w-full px-6 pb-8">
        <Card className="bg-[#4b42ff] rounded-[20px] shadow-[0px_4px_4px_#00000040] border-none">
          <CardContent className="flex flex-col items-start gap-2 px-6 py-6">
            <div className="text-white">로딩 중...</div>
          </CardContent>
        </Card>
      </section>
    );
  }

  if (!upcomingEvent) {
    return (
      <section className="w-full px-6 pb-8">
        <Card className="bg-[#4b42ff] rounded-[20px] shadow-[0px_4px_4px_#00000040] border-none">
          <CardContent className="flex flex-col items-start gap-2 px-6 py-6">
            <div className="text-white">다가오는 일정이 없습니다.</div>
          </CardContent>
        </Card>
      </section>
    );
  }

  const getDayText = () => {
    if (daysUntil === 0) return "오늘";
    if (daysUntil === 1) return "D-1";
    return `D-${daysUntil}`;
  };

  return (
    <section className="w-full px-6 pb-8">
      <Card className="bg-[#4b42ff] rounded-[20px] shadow-[0px_4px_4px_#00000040] border-none">
        <CardContent className="flex flex-col items-start gap-2 px-6 py-6">
          <h2 className="[font-family:'Pretendard-Bold',Helvetica] font-bold text-white text-base leading-normal">
            놓치지 마세요
          </h2>
          
          <h3 className="[font-family:'Pretendard-Bold',Helvetica] font-bold text-white text-lg leading-normal">
            '{upcomingEvent.title}' 일정이 다가와요! ({getDayText()})
          </h3>
          
          <p className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-white text-sm leading-relaxed">
            {upcomingEvent.description_ko || upcomingEvent.description || "경제 지표 발표"}
          </p>
        </CardContent>
      </Card>
    </section>
  );
};
