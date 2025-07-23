import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { AppHeader } from "@/components/common/AppHeader";
import { ChatInput } from "@/components/common/ChatInput";
import { useLocation } from "wouter";

export const ChatPage = (): JSX.Element => {
  const [, setLocation] = useLocation();

  const handleBackClick = () => {
    setLocation("/main");
  };

  // Chat messages data
  const chatMessages = [
    {
      type: "announcement",
      content: (
        <span className="text-[#1a1a1a] leading-[33.6px]">
          놓치지 마세요
          <br />
          내일 <span className="font-bold">FOMC 결과</span>를 발표해요!
        </span>
      ),
      className:
        "absolute w-[293px] top-[50px] left-6 font-normal text-[#1a1a1a] text-2xl tracking-[0] leading-8",
    },
    {
      type: "assistant",
      content:
        "5월 FOMC에서 금리를 동결했고 연준 위원들은 올해 두 번의 금리인하를 전망했어요",
      className:
        "w-[347px] top-[160px] left-6 bg-[#1a1a1a] flex items-center px-4 py-2.5 absolute rounded-md",
    },
    {
      type: "user",
      content: "금리 인하가 왜 중요한가요?",
      className:
        "w-[198px] top-[245px] left-[171px] bg-[#1a1a1a80] flex items-center px-4 py-2.5 absolute rounded-md",
    },
    {
      type: "assistant",
      content:
        "금리 인하는 돈 빌리는 데 드는 이자 비용이 줄어든다는 뜻이에요. 그래서, 기업은 투자를 더 많이 하고, 사람들은 대출을 쉽게 받아 소비를 늘려요!",
      className:
        "flex w-[345px] items-center px-4 py-2.5 absolute top-[320px] left-6 bg-[#1a1a1a] rounded-md",
    },
  ];

  return (
    <div className="relative w-full max-w-[393px] h-[852px] bg-white mx-auto">
      <div className="absolute w-full h-[calc(852px-104px-90px)] top-[104px] left-0 rounded-lg pb-[90px] overflow-y-auto">{/* adjusted for fixed header and chat input */}
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
        {chatMessages.map((message, index) => {
          if (message.type === "announcement") {
            return (
              <div key={`message-${index}`} className={message.className}>
                {message.content}
              </div>
            );
          } else {
            return (
              <Card key={`message-${index}`} className={message.className}>
                <CardContent className="p-0">
                  <div className="relative w-full mt-[-1.00px] [font-family:'Pretendard-Regular',Helvetica] font-normal text-white text-base tracking-[0] leading-6">
                    {message.content}
                  </div>
                </CardContent>
              </Card>
            );
          }
        })}
      </div>

      {/* Status bar - removed time and battery */}
      <div className="fixed w-full max-w-[393px] h-[54px] top-0 left-0 right-0 mx-auto z-50 bg-white/95 backdrop-blur-md">
        <div className="relative h-[54px]">
          {/* Empty status bar space */}
        </div>
      </div>

      {/* Fixed Header with back button */}
      <AppHeader showBackButton={true} onBackClick={handleBackClick} />

      {/* Fixed Chat Input */}
      <ChatInput />
    </div>
  );
};