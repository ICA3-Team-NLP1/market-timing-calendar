#!/usr/bin/env python3
"""Langfuse Factory - Dependency Inversion Principle 적용"""

from typing import Optional, Dict, Any
from app.core.llm import LangfuseManager


class LangfuseFactory:
    """Langfuse Manager Factory (Factory Pattern + DIP)"""
    
    @staticmethod
    def create_app_manager(user=None, session_id: Optional[str] = None) -> LangfuseManager:
        """App용 LangfuseManager 생성 (session_id는 반드시 외부에서 받아야 함)"""
        return LangfuseManager.create_for_app(user=user, session_id=session_id)
    
    @staticmethod
    def create_background_manager(task_metadata: Optional[Dict[str, Any]] = None) -> LangfuseManager:
        """Background용 LangfuseManager 생성 (session_id는 반드시 외부에서 받아야 함)"""
        return LangfuseManager.create_for_background(task_metadata=task_metadata)
    
    @staticmethod
    def create_custom_manager(
        service_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> LangfuseManager:
        """커스텀 LangfuseManager 생성 (session_id는 반드시 외부에서 받아야 함)"""
        return LangfuseManager(
            service_name=service_name,
            user_id=user_id,
            session_id=session_id
        ) 