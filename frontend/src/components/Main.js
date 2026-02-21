import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import BookmarkList from './BookmarkList';

/**
 * 첫 화면: 공개 북마크 목록 (로그인 후 목록/상세와 동일 UI).
 * 로그인한 사용자는 / 로 리다이렉트.
 */
const Main = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    if (user) {
        navigate('/', { replace: true });
        return null;
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
            <BookmarkList isPublicMode />
        </div>
    );
};

export default Main;
