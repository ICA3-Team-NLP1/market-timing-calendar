
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { LevelUpModal } from '@/components/modals/LevelUpModal';

interface LevelUpContextType {
  showLevelUpModal: (levelUpData?: any) => void;
  hideLevelUpModal: () => void;
}

const LevelUpContext = createContext<LevelUpContextType | undefined>(undefined);

export const useLevelUp = (): LevelUpContextType => {
  const context = useContext(LevelUpContext);
  if (!context) {
    throw new Error('useLevelUp must be used within a LevelUpProvider');
  }
  return context;
};

interface LevelUpProviderProps {
  children: ReactNode;
}

export const LevelUpProvider = ({ children }: LevelUpProviderProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [levelUpData, setLevelUpData] = useState<any>(null);

  const showLevelUpModal = (data?: any) => {
    setLevelUpData(data);
    setIsModalOpen(true);
  };

  const hideLevelUpModal = () => {
    setIsModalOpen(false);
    setLevelUpData(null);
  };

  return (
    <LevelUpContext.Provider value={{ showLevelUpModal, hideLevelUpModal }}>
      {children}
      <LevelUpModal 
        isOpen={isModalOpen} 
        onClose={hideLevelUpModal}
        levelUpData={levelUpData}
      />
    </LevelUpContext.Provider>
  );
};
