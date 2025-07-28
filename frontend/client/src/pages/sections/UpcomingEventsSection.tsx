import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Level1Gem } from "@/components/icons/Level1Gem";
import { Level2Gem } from "@/components/icons/Level2Gem";
import { useLocation } from "wouter";
import { handleLevelUpdate } from "@/utils/levelUpHelper";
import { useLevelUp } from "@/contexts/LevelUpContext";
import { getCalendarEvents, generateRecommendQuestion } from "@/utils/api";

export const UpcomingEventsSection = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const { showLevelUpModal } = useLevelUp();
  const [recommendedQuestions, setRecommendedQuestions] = useState<string[]>([
    "금리 인하가 왜 중요한가요?",
    "FOMC가 뭐예요?",
    "연준이 뭐예요?",
  ]);
  const [loading, setLoading] = useState(false);

  // 이벤트 데이터와 추천 질문 생성
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    const loadEventsAndQuestions = async () => {
      try {
        setLoading(true);

        // 오늘부터 7일 후까지의 이벤트 조회
        const today = new Date();
        const futureDate = new Date();
        futureDate.setDate(today.getDate() + 7);

        const startDate = today.toISOString().split("T")[0];
        const endDate = futureDate.toISOString().split("T")[0];

        const eventsData = await getCalendarEvents(startDate, endDate);
        
        if (eventsData && eventsData.length > 0) {
          // 이벤트 데이터 저장
          setEvents(eventsData);

          // 날짜순으로 정렬하고 가장 빠른 이벤트 선택
          const sortedEvents = eventsData.sort(
            (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
          );
          const nextEvent = sortedEvents[0];

          // D-day 계산
          const eventDate = new Date(nextEvent.date);
          const todayDate = new Date();
          todayDate.setHours(0, 0, 0, 0);
          eventDate.setHours(0, 0, 0, 0);

          const timeDiff = eventDate.getTime() - todayDate.getTime();
          const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

          const getDayText = () => {
            if (daysDiff === 0) return "오늘";
            if (daysDiff === 1) return "D-1";
            return `D-${daysDiff}`;
          };

          // 이벤트 설명 구성
          const eventDescription = `놓치지 마세요
'${nextEvent.title}' 일정이 다가와요! (${getDayText()})

${nextEvent.description_ko || nextEvent.description || "경제 지표 발표"}`;

          // 세션 ID 가져오기
          const sessionId = window.sessionStorage.getItem("chatSessionId");

          // 추천 질문 생성 API 호출
          const response = await generateRecommendQuestion(
            eventDescription,
            3, // 질문 개수
            15, // 문자열 길이 제한
            sessionId,
          );

          if (response.questions && response.questions.length > 0) {
            setRecommendedQuestions(response.questions);
            console.log("추천 질문 업데이트됨:", response.questions);
          }
        } else {
          setEvents([]);
        }
      } catch (error) {
        console.error("추천 질문 생성 실패:", error);
        // 에러 시 기본 질문 유지
      } finally {
        setLoading(false);
      }
    };

    loadEventsAndQuestions();
  }, []);

  const handleEventClick = async (eventId: number) => {
    // 레벨 업데이트 - 일정 조회 (다가오는 일정 클릭 시)
    await handleLevelUpdate("calendar_views", showLevelUpModal);

    setLocation(`/chat?eventId=${eventId}`);
  };

  const handleRecommendedQuestionClick = async (question: string) => {
    // 레벨 업데이트 - 추천 질문 클릭 시
    await handleLevelUpdate("chatbot_conversations", showLevelUpModal);
    setLocation(`/chat?question=${encodeURIComponent(question)}`);
  };

  const hasEvents = () => {
    if (loading) return false;
    return events && events.length > 0;
  };

  return (
    <section className="w-full pl-6 pr-6">
      {/* 하얀색 박스 - 이벤트 제목과 D-day */}
      {(loading || hasEvents()) && (
        <div className="bg-white rounded-[20px] p-0 mb-4">
          {loading ? (
            <div className="text-black">로딩 중...</div>
          ) : (
            <>
              {/* 다가오는 이벤트 표시 */}
              {(() => {
                if (events && events.length > 0) {
                  // 날짜순으로 정렬하고 가장 빠른 이벤트 선택
                  const sortedEvents = events.sort(
                    (a, b) =>
                      new Date(a.date).getTime() - new Date(b.date).getTime(),
                  );
                  const nextEvent = sortedEvents[0];

                  // D-day 계산
                  const eventDate = new Date(nextEvent.date);
                  const todayDate = new Date();
                  todayDate.setHours(0, 0, 0, 0);
                  eventDate.setHours(0, 0, 0, 0);

                  const timeDiff = eventDate.getTime() - todayDate.getTime();
                  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

                  const getDayText = () => {
                    if (daysDiff === 0) return "오늘";
                    if (daysDiff === 1) return "D-1";
                    return `D-${daysDiff}`;
                  };

                  return (
                    <>
                      <div className="mb-2">
                        <h2 className="[font-family:'Pretendard-Bold',Helvetica] font-bold text-black text-lg leading-normal">
                          놓치지 마세요
                        </h2>
                      </div>
                      <h3 className="[font-family:'Pretendard-Bold',Helvetica] font-bold text-black text-lg leading-normal">
                        {nextEvent.title} ({getDayText()})
                      </h3>
                    </>
                  );
                }

                return (
                  <div className="text-black">다가오는 일정이 없습니다.</div>
                );
              })()}
            </>
          )}
        </div>
      )}

      {/* 검은색 박스 - 이벤트 설명 */}
      {!loading &&
        hasEvents() &&
        (() => {
          if (events && events.length > 0) {
            const sortedEvents = events.sort(
              (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
            );
            const nextEvent = sortedEvents[0];

            return (
              <div className="bg-[#1a1a1a] text-white border-none rounded-md py-2.5 pl-6 pr-4">
                <p className="[font-family:'Pretendard-Regular',Helvetica] font-normal text-white text-base tracking-[0] leading-6">
                  {nextEvent.description_ko || nextEvent.description || "경제 지표 발표"}
                </p>
              </div>
            );
          }
          return null;
        })()}

      {/* 추천 질문 섹션 */}
      <section className="w-full py-6 pl-0 pr-0">
        <h3 className="font-bold text-[#1a1a1a] text-base mb-4 [font-family:'Pretendard-Bold',Helvetica]">
          추천 질문
        </h3>
        <div className="flex flex-col gap-2.5 items-start">
          {recommendedQuestions.map((question, index) => (
            <Button
              key={`question-${index}`}
              variant="outline"
              className="flex items-center gap-1 px-4 py-2.5 h-auto bg-[#e8f0ff] rounded-[100px] shadow-[0px_4px_4px_#00000005] border-none hover:bg-[#d8e5fa] w-fit"
              onClick={() => handleRecommendedQuestionClick(question)}
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
    </section>
  );
};
