import React from 'react';
import logger from '../utils/logger';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        logger.error('React Error Boundary caught an error:', {
            error: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            location: window.location.href
        });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-lg">
                        <h2 className="text-2xl font-bold text-red-600 mb-4">
                            오류가 발생했습니다
                        </h2>
                        <p className="text-gray-600 mb-4">
                            죄송합니다. 예상치 못한 오류가 발생했습니다.
                            페이지를 새로고침하거나 나중에 다시 시도해주세요.
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            페이지 새로고침
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary; 