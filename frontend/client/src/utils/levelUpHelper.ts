
import { updateUserLevel } from './api';

export interface LevelUpResult {
  success: boolean;
  level_up: boolean;
  current_level: string;
  message?: string;
  exp: Record<string, number>;
  next_level_conditions?: Record<string, number>;
}

export interface LevelUpModalData {
  newLevel: string;
  message?: string;
  exp: Record<string, number>;
}

export const handleLevelUpdate = async (
  eventType: string, 
  showLevelUpModal?: (data: LevelUpModalData) => void
): Promise<LevelUpResult | null> => {
  try {
    console.log(`레벨 업데이트 시작: ${eventType}`);
    const result = await updateUserLevel(eventType);
    
    console.log('레벨 업데이트 결과:', result);
    
    // 레벨업이 발생한 경우 모달 표시
    if (result.level_up && showLevelUpModal) {
      showLevelUpModal({
        newLevel: result.current_level,
        message: result.message,
        exp: result.exp
      });
      
      // 레벨업 이벤트 발생시켜 AppHeader 업데이트 트리거
      window.dispatchEvent(new CustomEvent('levelUp'));
    }
    
    return result;
  } catch (error) {
    console.error(`레벨 업데이트 실패 (${eventType}):`, error);
    return null;
  }
};
