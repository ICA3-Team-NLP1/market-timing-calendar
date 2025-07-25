import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { AppHeader } from "@/components/common/AppHeader";
import { ChatInput } from "@/components/common/ChatInput";
import { useLocation } from "wouter";
import { explainEvent, getCalendarEvents, chatConversation } from "@/utils/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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

  // 메시지 업데이트 공통 함수
  const updateMessages = (initialMessages: ChatMessage[], assistantMessage: ChatMessage, useDynamicUpdate: boolean) => {
    if (useDynamicUpdate) {
      setMessages(prevMessages => {
        const updatedMessages = [...prevMessages];
        updatedMessages[updatedMessages.length - 1] = { ...assistantMessage };
        return updatedMessages;
      });
    } else {
      setMessages([...initialMessages, { ...assistantMessage }]);
    }
  };

  // 공통 스트리밍 처리 함수
  const processStreamingResponse = async (
    response: Response,
    initialMessages: ChatMessage[],
    assistantMessage: ChatMessage,
    useDynamicUpdate: boolean = false
  ) => {
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullResponseText = ''; // 전체 응답 텍스트 저장

    if (reader) {
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        fullResponseText += chunk; // 전체 응답에 추가
        
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              break;
            }

            if (data) {
              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  assistantMessage.content += parsed.content;
                  updateMessages(initialMessages, assistantMessage, useDynamicUpdate);
                }
              } catch (e) {
                assistantMessage.content += data;
                updateMessages(initialMessages, assistantMessage, useDynamicUpdate);
              }
            }
          } else if (line.includes('SESSION_ID:')) {
            const sessionIdMatch = line.match(/SESSION_ID:\s*([a-f0-9\-]+)/i);
            if (sessionIdMatch && sessionIdMatch[1]) {
              const extractedSessionId = sessionIdMatch[1].trim();
              setStoredSessionId(extractedSessionId);
              console.log('스트리밍 중 세션 ID 저장됨:', extractedSessionId);
            }
          } else if (line.trim() && !line.startsWith('data:') && !line.includes('SESSION_ID:')) {
            assistantMessage.content += line.trim() + ' ';
            updateMessages(initialMessages, assistantMessage, useDynamicUpdate);
          }
        }
      }

      // 스트리밍 완료 후 전체 응답에서 SESSION_ID 재확인
      const finalSessionIdMatch = fullResponseText.match(/SESSION_ID:\s*([a-f0-9\-]+)/i);
      if (finalSessionIdMatch && finalSessionIdMatch[1]) {
        const finalSessionId = finalSessionIdMatch[1].trim();
        const currentStoredId = getStoredSessionId();
        
        if (currentStoredId !== finalSessionId) {
          setStoredSessionId(finalSessionId);
          console.log('스트리밍 완료 후 세션 ID 저장됨:', finalSessionId);
        }
      }
    }
  };

  // 공통 에러 처리 함수
  const handleChatError = (error: any, functionName: string) => {
    console.error(`${functionName} 요청 실패:`, error);
    
    let errorMessage = "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다.";
    if (error.message) {
      errorMessage += ` (${error.message})`;
    }

    setMessages(prev => [...prev, {
      type: "assistant",
      content: errorMessage
    }]);
  };

  // 새로운 질문 처리 (연속 대화)
  const handleNewQuestion = async (questionText: string) => {
    console.log('🔄 handleNewQuestion');
    
    try {
      setIsLoading(true);

      const userMessage: ChatMessage = { type: "user", content: questionText };
      const newMessages = [...messages, userMessage];
      setMessages(newMessages);

      const assistantMessage: ChatMessage = { type: "assistant", content: "" };
      setMessages([...newMessages, assistantMessage]);

      const history = newMessages.slice(0, -1).map(msg => ({
        role: msg.type === "user" ? "user" : "assistant",
        content: msg.content
      }));

      const response = await chatConversation(questionText, history, getStoredSessionId(), true, "moderate");
      await processStreamingResponse(response, newMessages, assistantMessage, true);
    } catch (error) {
      handleChatError(error, 'handleNewQuestion');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecommendedQuestion = async (questionText: string) => {
    console.log('📋 handleRecommendedQuestion');
    
    try {
      setIsLoading(true);

      const userMessage: ChatMessage = { type: "user", content: questionText };
      setMessages([userMessage]);

      const assistantMessage: ChatMessage = { type: "assistant", content: "" };
      setMessages([userMessage, assistantMessage]);

      const response = await chatConversation(questionText, [], getStoredSessionId(), true, "moderate");
      await processStreamingResponse(response, [userMessage], assistantMessage, false);
    } catch (error) {
      handleChatError(error, 'handleRecommendedQuestion');
    } finally {
      setIsLoading(false);
    }
  };

  const loadEventAndExplain = async (eventId: number) => {
    console.log('📅 loadEventAndExplain');
    
    try {
      setIsLoading(true);

      const today = new Date();
      const pastDate = new Date();
      pastDate.setMonth(today.getMonth() - 6);
      const futureDate = new Date();
      futureDate.setMonth(today.getMonth() + 6);

      const startDate = pastDate.toISOString().split('T')[0];
      const endDate = futureDate.toISOString().split('T')[0];

      const events = await getCalendarEvents(startDate, endDate);
      const event = events.find((e: any) => e.id === eventId);

      if (!event) {
        setMessages([{
          type: "assistant",
          content: "죄송합니다. 요청하신 이벤트를 찾을 수 없습니다. 다시 시도해주세요."
        }]);
        return;
      }

      setCurrentEvent(event);

      const userMessage: ChatMessage = { type: "user", content: `${event.title}에 대해 설명해주세요.` };
      setMessages([userMessage]);

      const assistantMessage: ChatMessage = { type: "assistant", content: "" };
      setMessages([userMessage, assistantMessage]);

      const response = await explainEvent(eventId);
      await processStreamingResponse(response, [userMessage], assistantMessage, false);
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
                  <div className="text-sm leading-relaxed">
                    {message.type === 'assistant' ? (
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // 모든 요소에 적절한 스타일 클래스 적용
                          h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mb-2">{children}</h1>,
                          h2: ({children}) => <h2 className="text-base font-semibold text-gray-900 mb-2">{children}</h2>,
                          h3: ({children}) => <h3 className="text-sm font-medium text-gray-900 mb-1">{children}</h3>,
                          p: ({children}) => <p className="text-gray-900 mb-2 leading-relaxed whitespace-pre-wrap">{children}</p>,
                          strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                          em: ({children}) => <em className="italic text-gray-900">{children}</em>,
                          code: ({children}) => <code className="bg-gray-100 text-gray-900 px-1 py-0.5 rounded text-xs">{children}</code>,
                          pre: ({children}) => <pre className="bg-gray-100 text-gray-900 p-2 rounded text-xs overflow-x-auto whitespace-pre-wrap">{children}</pre>,
                          ul: ({children}) => <ul className="list-disc list-inside text-gray-900 mb-2">{children}</ul>,
                          ol: ({children}) => <ol className="list-decimal list-inside text-gray-900 mb-2">{children}</ol>,
                          li: ({children}) => <li className="text-gray-900 mb-1">{children}</li>,
                          blockquote: ({children}) => <blockquote className="border-l-4 border-gray-300 pl-3 text-gray-700 italic">{children}</blockquote>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    )}
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