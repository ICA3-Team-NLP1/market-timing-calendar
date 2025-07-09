import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebase';
import Login from './components/Login';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Firebase 인증 상태 변화 감지
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      console.log('인증 상태 변화:', currentUser);
      setUser(currentUser);
      setLoading(false);
    });

    // 컴포넌트 언마운트 시 리스너 제거
    return () => unsubscribe();
  }, []);

  // 로딩 중
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <Login user={user} setUser={setUser} />
    </div>
  );
}

export default App;
