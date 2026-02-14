import React from 'react';

const LoadingSpinner = ({ message = '로딩 중...' }) => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[200px]">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">{message}</p>
        </div>
    );
};

export default React.memo(LoadingSpinner); 