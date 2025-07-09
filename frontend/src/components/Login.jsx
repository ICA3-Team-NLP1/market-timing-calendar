import React, { useState } from 'react';
import {
    // signInWithEmailAndPassword,
    // createUserWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
    signOut
} from 'firebase/auth';
import { auth } from '../firebase';
import { getCurrentUser } from '../utils/api'; // 🔧 API 함수 import
import './Login.css';

const Login = ({ user, setUser }) => {
    // const [email, setEmail] = useState('');
    // const [password, setPassword] = useState('');
    // const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [apiResult, setApiResult] = useState(null); // 🔧 API 결과 저장
    const [apiLoading, setApiLoading] = useState(false); // 🔧 API 호출 로딩

    // 이메일/비밀번호 로그인
    // const handleEmailLogin = async (e) => {
    //     e.preventDefault();
    //     setLoading(true);
    //     setError('');
    //
    //     try {
    //         let result;
    //         if (isLogin) {
    //             result = await signInWithEmailAndPassword(auth, email, password);
    //         } else {
    //             result = await createUserWithEmailAndPassword(auth, email, password);
    //         }
    //
    //         console.log('로그인 성공:', result.user);
    //         setUser(result.user);
    //     } catch (error) {
    //         console.error('로그인 실패:', error);
    //         setError(error.message);
    //     } finally {
    //         setLoading(false);
    //     }
    // };

    // Google 로그인
    const handleGoogleLogin = async () => {
        setLoading(true);
        setError('');

        try {
            const provider = new GoogleAuthProvider();
            const result = await signInWithPopup(auth, provider);

            console.log('Google 로그인 성공:', result.user);
            setUser(result.user);
        } catch (error) {
            console.error('Google 로그인 실패:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    // 🔧 백엔드 API 테스트 함수
    const testBackendAPI = async () => {
        setApiLoading(true);
        setApiResult(null);
        setError('');

        try {
            console.log('🔑 백엔드 API 호출 시작...');
            const result = await getCurrentUser(); // 🔑 토큰 자동 포함됨

            console.log('✅ 백엔드 API 호출 성공:', result);
            setApiResult(result);

        } catch (error) {
            console.error('❌ 백엔드 API 호출 실패:', error);
            setError(`API 호출 실패: ${error.message}`);
        } finally {
            setApiLoading(false);
        }
    };

    // 로그아웃
    const handleLogout = async () => {
        try {
            await signOut(auth);
            setUser(null);
            setApiResult(null); // 🔧 API 결과도 초기화
            console.log('✅ 로그아웃 성공');
        } catch (error) {
            console.error('로그아웃 실패:', error);
        }
    };

    // 이미 로그인된 경우
    if (user) {
        return (
            <div className="login-container">
                <div className="login-box">
                    <h2>환영합니다! 👋</h2>
                    <div className="user-info">
                        <img
                            src={user.photoURL || '/default-avatar.png'}
                            alt="프로필"
                            className="user-avatar"
                        />
                        <p><strong>{user.displayName || user.email}</strong></p>
                        <p>{user.email}</p>
                        <p>이메일 인증: {user.emailVerified ? '✅' : '❌'}</p>
                    </div>

                    {/* 🔧 API 테스트 버튼 */}
                    <button
                        onClick={testBackendAPI}
                        disabled={apiLoading}
                        className="submit-btn"
                        style={{
                            marginBottom: '15px',
                            backgroundColor: apiLoading ? '#ccc' : '#28a745',
                            cursor: apiLoading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {apiLoading ? '🔄 API 호출 중...' : '🔑 백엔드 API 테스트'}
                    </button>

                    {/* 🔧 API 결과 표시 */}
                    {apiResult && (
                        <div style={{
                            marginBottom: '15px',
                            padding: '15px',
                            backgroundColor: '#d4edda',
                            border: '1px solid #c3e6cb',
                            borderRadius: '8px',
                            fontSize: '12px',
                            textAlign: 'left'
                        }}>
                            <p><strong>✅ 백엔드 API 호출 성공!</strong></p>
                            <p><strong>응답 데이터:</strong></p>
                            <pre style={{
                                backgroundColor: '#f8f9fa',
                                padding: '8px',
                                borderRadius: '4px',
                                overflow: 'auto',
                                fontSize: '11px'
                            }}>
                                {JSON.stringify(apiResult, null, 2)}
                            </pre>
                        </div>
                    )}

                    {/* 에러 메시지 */}
                    {error && (
                        <div className="error-message" style={{ marginBottom: '15px' }}>
                            {error}
                        </div>
                    )}

                    <button onClick={handleLogout} className="logout-btn">
                        로그아웃
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Market Timing Calendar</h2>
                <p className="subtitle">로그인하여 시작하세요</p>

                {error && <div className="error-message">{error}</div>}

                {/*<form onSubmit={handleEmailLogin} className="login-form">*/}
                {/*    <input*/}
                {/*        type="email"*/}
                {/*        placeholder="이메일"*/}
                {/*        value={email}*/}
                {/*        onChange={(e) => setEmail(e.target.value)}*/}
                {/*        required*/}
                {/*        className="form-input"*/}
                {/*    />*/}
                {/*    <input*/}
                {/*        type="password"*/}
                {/*        placeholder="비밀번호"*/}
                {/*        value={password}*/}
                {/*        onChange={(e) => setPassword(e.target.value)}*/}
                {/*        required*/}
                {/*        className="form-input"*/}
                {/*    />*/}

                {/*    <button*/}
                {/*        type="submit"*/}
                {/*        disabled={loading}*/}
                {/*        className="submit-btn"*/}
                {/*    >*/}
                {/*        {loading ? '처리 중...' : (isLogin ? '로그인' : '회원가입')}*/}
                {/*    </button>*/}
                {/*</form>*/}

                {/*<div className="divider">*/}
                {/*    <span>또는</span>*/}
                {/*</div>*/}

                <button
                    onClick={handleGoogleLogin}
                    disabled={loading}
                    className="google-btn"
                    style={{ color: "#333" }}
                >
                    🔍 Google로 로그인
                </button>

                {/*<div className="toggle-form">*/}
                {/*    <button*/}
                {/*        type="button"*/}
                {/*        onClick={() => setIsLogin(!isLogin)}*/}
                {/*        className="toggle-btn"*/}
                {/*    >*/}
                {/*        {isLogin ? '회원가입하기' : '로그인하기'}*/}
                {/*    </button>*/}
                {/*</div>*/}
            </div>
        </div>
    );
};

export default Login; 