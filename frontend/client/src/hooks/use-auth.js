import { useEffect, useState } from 'react';
import { useLocation } from 'wouter';
import { auth } from '../firebase.js';
import { onAuthStateChanged } from 'firebase/auth';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [, setLocation] = useLocation();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const redirectToLogin = () => {
    setLocation('/login');
  };

  return { user, loading, redirectToLogin };
}; 