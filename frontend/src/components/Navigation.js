import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logger from '../utils/logger';

const Navigation = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        logger.info('로그아웃 성공');
        navigate('/login');
    };

    if (!user) return null;

    return (
        <nav className="bg-gray-800 text-white p-4">
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="text-xl font-bold">
                    Link_Digest:북마크 요약
                </Link>
                <div className="flex items-center space-x-4">
                    <span>{user.username}</span>
                    <button
                        onClick={handleLogout}
                        className="p-1.5 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
                        title="로그아웃"
                    >
                        <svg 
                            className="w-5 h-5" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                        >
                            <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth="2" 
                                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" 
                            />
                        </svg>
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navigation; 