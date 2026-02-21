import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logger from '../utils/logger';

const Navigation = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout().then(() => {
            try { logger.info('로그아웃 성공'); } catch (e) { /* 로그 실패해도 무시 */ }
            navigate('/main');
        }).catch(() => {
            navigate('/main');
        });
    };

    // 상단 바: 짙은 회색
    const navClassName = 'text-white p-4 bg-gray-800';

    // 로그인 전: 좌측 Link Digest, 우측 로그인 버튼
    if (!user) {
        const showLoginForm = () => navigate('/login?form=1');
        return (
            <nav className={navClassName}>
                <div className="container mx-auto flex justify-between items-center">
                    <Link to="/main" className="flex items-center gap-2 text-xl font-bold">
                        <img src="/favicon.svg" alt="" className="w-8 h-8 flex-shrink-0" />
                        Link Digest
                    </Link>
                    <button
                        type="button"
                        onClick={showLoginForm}
                        className="text-sm font-medium text-blue-300 hover:text-white px-3 py-1.5 rounded"
                    >
                        로그인
                    </button>
                </div>
            </nav>
        );
    }

    return (
        <nav className={navClassName}>
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="flex items-center gap-2 text-xl font-bold">
                    <img src="/favicon.svg" alt="" className="w-8 h-8 flex-shrink-0" />
                    Link Digest
                </Link>
                <div className="flex items-center space-x-4">
                    <span>{user.username}</span>
                    <button
                        onClick={handleLogout}
                        className="p-1.5 text-gray-300 hover:text-white rounded-full hover:bg-white/10"
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