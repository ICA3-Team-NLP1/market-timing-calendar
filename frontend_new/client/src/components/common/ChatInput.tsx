import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CalendarIcon } from "lucide-react";
import { useLocation } from "wouter";

interface ChatInputProps {
  onClick?: () => void;
  readOnly?: boolean;
  placeholder?: string;
  onSubmit?: (message: string) => void;
}

export const ChatInput = ({ 
  onClick, 
  readOnly = false, 
  placeholder = "CAFFY에게 물어보기",
  onSubmit
}: ChatInputProps): JSX.Element => {
  const [, setLocation] = useLocation();
  const [inputValue, setInputValue] = useState("");

  const handleCalendarClick = () => {
    setLocation("/calendar");
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!readOnly) {
      setInputValue(e.target.value);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim() && !readOnly) {
      if (onSubmit) {
        // 현재 페이지에서 메시지 전송
        onSubmit(inputValue.trim());
        setInputValue("");
      } else {
        // 질문과 함께 /chat으로 이동
        setLocation(`/chat?question=${encodeURIComponent(inputValue.trim())}`);
        setInputValue("");
      }
    }
  };

  const handleInputClick = () => {
    if (readOnly && onClick) {
      onClick();
    }
  };

  return (
    <div className="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-[393px] h-[70px] z-50 bg-white/95 backdrop-blur-md pt-4 pb-4">
      <div className="relative w-[345px] h-9 mx-auto">
        <div className="flex w-[305px] items-center gap-2.5 px-3 py-2 absolute top-0 left-10 bg-white rounded-[100px] border border-solid border-[#1a1a1a80] shadow-[0px_4px_4px_#00000008]">
          <Input
            className="border-none shadow-none bg-transparent h-auto p-0 text-[#1a1a1a] text-base [font-family:'Pretendard-Regular',Helvetica] placeholder:text-[#1a1a1a4c] cursor-pointer"
            placeholder={placeholder}
            onClick={handleInputClick}
            readOnly={readOnly}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyPress}
          />
        </div>

        <Button 
          className="absolute w-9 h-9 top-0 left-0 p-0 bg-transparent hover:bg-transparent"
          onClick={handleCalendarClick}
        >
          <CalendarIcon className="w-5 h-5 text-[#1a1a1a]" />
        </Button>
      </div>
    </div>
  );
};