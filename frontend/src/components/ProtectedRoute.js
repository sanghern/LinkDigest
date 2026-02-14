import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();

    // 로그인 전에는 항상 로그인 화면(/login)으로
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    if (loading) {
        return <div>Loading...</div>;
    }

    return children;
};

export default ProtectedRoute; 