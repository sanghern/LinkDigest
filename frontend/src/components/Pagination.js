import React from 'react';

const Pagination = ({ 
    page, 
    pageSize, 
    totalCount, 
    onPageChange, 
    onPageSizeChange 
}) => {
    const totalPages = Math.ceil(totalCount / pageSize);

    return (
        <div className="mt-4 flex justify-between items-center">
            <div className="text-sm text-gray-700">
                {totalCount}개 중 {(page - 1) * pageSize + 1}-
                {Math.min(page * pageSize, totalCount)}개 표시
            </div>
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                    onClick={() => onPageChange(page - 1)}
                    disabled={page === 1}
                    className={`relative inline-flex items-center px-2 py-2 rounded-l-md border text-sm font-medium ${
                        page === 1
                            ? 'bg-gray-100 text-gray-400'
                            : 'bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                >
                    이전
                </button>
                {[...Array(totalPages)].map((_, i) => (
                    <button
                        key={i + 1}
                        onClick={() => onPageChange(i + 1)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === i + 1
                                ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                    >
                        {i + 1}
                    </button>
                ))}
                <button
                    onClick={() => onPageChange(page + 1)}
                    disabled={page === totalPages}
                    className={`relative inline-flex items-center px-2 py-2 rounded-r-md border text-sm font-medium ${
                        page === totalPages
                            ? 'bg-gray-100 text-gray-400'
                            : 'bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                >
                    다음
                </button>
            </nav>
            <select
                value={pageSize}
                onChange={(e) => onPageSizeChange(Number(e.target.value))}
                className="border rounded px-2 py-1"
            >
                <option value="10">10개씩</option>
                <option value="20">20개씩</option>
                <option value="50">50개씩</option>
            </select>
        </div>
    );
};

export default React.memo(Pagination); 