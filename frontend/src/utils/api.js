import { auth } from '../firebase';

// 🔑 API 호출 시 자동으로 Firebase 토큰 포함
export const apiCall = async (url, options = {}) => {
    try {
        // 현재 로그인된 사용자 확인
        const currentUser = auth.currentUser;
        if (!currentUser) {
            throw new Error('로그인이 필요합니다');
        }

        // Firebase ID Token 자동 획득
        const idToken = await currentUser.getIdToken();

        // Authorization 헤더 자동 추가
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`, // 🔑 토큰 자동 포함
            ...options.headers
        };

        // API 호출
        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('❌ API 호출 실패:', error);
        throw error;
    }
};

// 🔧 백엔드 API 기본 URL
const API_BASE_URL = 'http://localhost:8000';

// 🔧 보호된 API 호출 함수들 (토큰 자동 포함)
export const getCurrentUser = async () => {
    return await apiCall(`${API_BASE_URL}/api/v1/users/me`);
};

export const getUserByUid = async (uid) => {
    return await apiCall(`${API_BASE_URL}/api/v1/auth/user/${uid}`);
};

// 🔧 사용자 탈퇴 API
export const deleteUser = async () => {
    return await apiCall(`${API_BASE_URL}/api/v1/users/me`, {
        method: 'DELETE'
    });
};
