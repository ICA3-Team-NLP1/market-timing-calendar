import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { AppHeader } from "@/components/common/AppHeader";
import { ChatInput } from "@/components/common/ChatInput";
import { useLocation } from "wouter";
import { explainEvent, getCalendarEvents, chatConversation } from "@/utils/api";

interface ChatMessage {
  type: "user" | "assistant";
  content: string;
}

export const ChatPage = (): JSX.Element => {
  const [, setLocation] = useLocation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentEvent, setCurrentEvent] = useState<any>(null);

  // URL에서 파라미터 추출
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get('eventId');
  const question = urlParams.get('question');

  // 전역 세션 ID 저장
  const getStoredSessionId = () => window.sessionStorage.getItem('chatSessionId');
  const setStoredSessionId = (sessionId: string) => window.sessionStorage.setItem('chatSessionId', sessionId);

  const handleBackClick = () => {
    setLocation("/main");
  };

  // 페이지 로드 시 스크롤 맨 위로 이동
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // 이벤트 정보 로드 및 설명 요청 또는 일반 질문 처리
  useEffect(() => {
    if (eventId) {
      loadEventAndExplain(parseInt(eventId));
    } else if (question) {
      handleRecommendedQuestion(decodeURIComponent(question));
    }
  }, [eventId, question]);

  // 새로운 질문 처리 (연속 대화)
  const handleNewQuestion = async (questionText: string) => {
    try {
      setIsLoading(true);

      // 사용자 메시지 추가
      const userMessage: ChatMessage = {
        type: "user",
        content: questionText
      };
      const newMessages = [...messages, userMessage];
      setMessages(newMessages);

      // AI 응답 시작
      let assistantMessage: ChatMessage = {
        type: "assistant",
        content: ""
      };
      setMessages([...newMessages, assistantMessage]);

      // 현재 대화 내역을 API 형식으로 변환
      const history = newMessages.slice(0, -1).map(msg => ({
        role: msg.type === "user" ? "user" : "assistant",
        content: msg.content
      }));

      // 챗봇 대화 API 호출
      const response = await chatConversation(
        questionText,
        history,
        getStoredSessionId(),
        true,
        "moderate"
      );

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      const finalMessages = [...newMessages];

      if (reader) {
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  assistantMessage.content += parsed.content;
                  setMessages([...finalMessages, { ...assistantMessage }]);
                }
              } catch (e) {
                // 일반 텍스트로 처리
                if (data.trim()) {
                  assistantMessage.content += data;
                  setMessages([...finalMessages, { ...assistantMessage }]);
                }
              }
            } else if (line.includes('SESSION_ID:')) {
              // 세션 ID 추출 및 저장
              const sessionIdMatch = line.match(/SESSION_ID:\s*([a-f0-9-]+)/);
              if (sessionIdMatch) {
                setStoredSessionId(sessionIdMatch[1]);
                console.log('세션 ID 저장됨:', sessionIdMatch[1]);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('챗봇 대화 요청 실패:', error);
      setMessages(prev => [...prev, {
        type: "assistant",
        content: "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecommendedQuestion = async (questionText: string) => {
    try {
      setIsLoading(true);

      // 사용자 메시지 추가
      const userMessage: ChatMessage = {
        type: "user",
        content: questionText
      };
      setMessages([userMessage]);

      // AI 응답 시작
      let assistantMessage: ChatMessage = {
        type: "assistant",
        content: ""
      };
      setMessages([userMessage, assistantMessage]);

      // 챗봇 대화 API 호출
      const response = await chatConversation(
        questionText,
        [], // 빈 히스토리
        getStoredSessionId(), // 저장된 세션 ID 사용
        true, // use_memory
        "moderate" // safety_level
      );

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      const newMessages = [userMessage];


      if (reader) {
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  assistantMessage.content += parsed.content;
                  setMessages([...newMessages, { ...assistantMessage }]);
                }
              } catch (e) {
                // 일반 텍스트로 처리
                if (data.trim()) {
                  assistantMessage.content += data;
                  setMessages([...newMessages, { ...assistantMessage }]);
                }
              }
            } else if (line.includes('SESSION_ID:')) {
              // 세션 ID 추출 및 저장
              const sessionIdMatch = line.match(/SESSION_ID:\s*([a-f0-9-]+)/);
              if (sessionIdMatch) {
                setStoredSessionId(sessionIdMatch[1]);
                console.log('세션 ID 저장됨:', sessionIdMatch[1]);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('챗봇 대화 요청 실패:', error);
      setMessages(prev => [...prev, {
        type: "assistant",
        content: "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadEventAndExplain = async (eventId: number) => {
    try {
      setIsLoading(true);

      // 더 넓은 날짜 범위로 이벤트 검색 (6개월 전후)
      const today = new Date();
      const pastDate = new Date();
      pastDate.setMonth(today.getMonth() - 6);
      const futureDate = new Date();
      futureDate.setMonth(today.getMonth() + 6);

      const startDate = pastDate.toISOString().split('T')[0];
      const endDate = futureDate.toISOString().split('T')[0];

      console.log(`이벤트 ID ${eventId} 검색 중... (날짜 범위: ${startDate} ~ ${endDate})`);

      const events = await getCalendarEvents(startDate, endDate);
      console.log('검색된 이벤트들:', events);
      
      const event = events.find((e: any) => e.id === eventId);

      if (!event) {
        console.error(`이벤트 ID ${eventId}를 찾을 수 없습니다.`);
        setMessages([{
          type: "assistant",
          content: "죄송합니다. 요청하신 이벤트를 찾을 수 없습니다. 다시 시도해주세요."
        }]);
        return;
      }

      console.log('찾은 이벤트:', event);
      setCurrentEvent(event);

      // 사용자 메시지 추가
      const userMessage: ChatMessage = {
        type: "user",
        content: `${event.title}에 대해 설명해주세요.`
      };
      setMessages([userMessage]);

      // AI 응답 시작
      let assistantMessage: ChatMessage = {
        type: "assistant",
        content: ""
      };
      setMessages([userMessage, assistantMessage]);
      const newMessages = [userMessage];

      // 스트리밍 응답 처리
      const response = await explainEvent(eventId);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  assistantMessage.content += parsed.content;
                  setMessages([...newMessages, { ...assistantMessage }]);
                }
              } catch (e) {
                // 일반 텍스트로 처리
                if (data.trim()) {
                  assistantMessage.content += data;
                  setMessages([...newMessages, { ...assistantMessage }]);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('이벤트 설명 요청 실패:', error);
      setMessages([{
        type: "assistant",
        content: "죄송합니다. 이벤트 설명을 가져오는 중 오류가 발생했습니다."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full max-w-[393px] h-[852px] bg-white mx-auto">
      <div className="absolute w-full h-[calc(852px-104px-90px)] top-[104px] left-0 rounded-lg pb-[90px] overflow-y-auto">
        <div className="absolute w-full h-[852px] top-0 left-0 bg-[#f5f6fa] rounded-lg overflow-hidden border-[none] before:content-[''] before:absolute before:inset-0 before:p-px before:rounded-lg before:[background:linear-gradient(180deg,rgba(31,31,51,0.04)_0%,rgba(31,31,51,0)_100%)] before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:z-[1] before:pointer-events-none">
          <div className="relative w-[887px] h-[1160px] top-[-89px] left-[-162px]">
            {/* Background blur circles */}
            <div className="absolute w-[612px] h-[659px] top-[165px] left-0 bg-gradient-radial from-blue-200/30 to-transparent rounded-full blur-3xl" />
            <div className="absolute w-[441px] h-[334px] top-[116px] left-[183px] bg-gradient-radial from-purple-200/20 to-transparent rounded-full blur-2xl" />
            <div className="absolute w-[427px] h-[315px] top-0 left-[190px] bg-gradient-radial from-white/40 to-transparent rounded-full blur-xl" />
            <div className="absolute w-[755px] h-[772px] top-[388px] left-[131px] bg-gradient-radial from-purple-300/25 to-transparent rounded-full blur-3xl" />
            <div className="absolute w-[439px] h-[496px] top-[325px] left-[191px] bg-gradient-radial from-blue-300/30 to-transparent rounded-full blur-2xl" />
            <div className="absolute w-full h-[852px] top-[89px] left-[162px] bg-[#ffffff8c] backdrop-blur-sm backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(4px)_brightness(100%)]" />
          </div>
        </div>

        {/* Chat messages */}
        <div className="relative z-10 p-6 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <Card className={`max-w-[280px] ${
                message.type === 'user' 
                  ? 'bg-[#1a1a1a] text-white' 
                  : 'bg-white text-gray-900'
              }`}>
                <CardContent className="p-3">
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <Card className="max-w-[280px] bg-white">
                <CardContent className="p-3">
                  <div className="text-sm text-gray-500">
                    설명을 생성하고 있습니다...
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="fixed w-full max-w-[393px] h-[54px] top-0 left-0 right-0 mx-auto z-50 bg-white/95 backdrop-blur-md">
        <div className="relative h-[54px]">
          {/* Empty status bar space */}
        </div>
      </div>

      {/* Fixed Header with back button */}
      <AppHeader showBackButton={true} onBackClick={handleBackClick} />

      {/* Fixed Chat Input */}
      <ChatInput 
        readOnly={false} 
        placeholder="CAFFY에게 물어보기"
        onSubmit={handleNewQuestion}
      />
    </div>
  );
};