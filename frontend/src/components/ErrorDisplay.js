import React from 'react';

const ErrorDisplay = ({ error, onRetry }) => {
    return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 my-4">
            <div className="flex items-center">
                <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <h3 className="text-red-800 font-medium">오류 발생</h3>
            </div>
            <p className="text-red-700 mt-2">{error}</p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="mt-3 bg-red-100 text-red-800 px-4 py-2 rounded hover:bg-red-200"
                >
                    다시 시도
                </button>
            )}
        </div>
    );
};

export default React.memo(ErrorDisplay); 