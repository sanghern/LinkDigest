import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkAuth = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                setLoading(false);
                return;
            }

            const userData = await api.auth.me();
            setUser(userData);
        } catch (error) {
            localStorage.removeItem('token');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async (username, password) => {
        try {
            const response = await api.auth.login(username, password);
            if (response.user) {
                setUser(response.user);
                return true;
            }
            throw new Error('사용자 정보를 받지 못했습니다.');
        } catch (error) {
            throw error;
        }
    };

    const logout = async () => {
        try {
            await api.auth.logout();
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            localStorage.removeItem('token');
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 