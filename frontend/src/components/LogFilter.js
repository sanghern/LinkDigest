import React, { useCallback, useEffect } from 'react';
import { useDebounce } from '../hooks/useDebounce';

const LogFilter = ({ filter, onFilterChange }) => {
    // 검색어에 디바운스 적용
    const debouncedSearch = useDebounce(filter.search, 500);

    // 필터 변경 핸들러를 useCallback으로 래핑
    const handleFilterChange = useCallback((key, value) => {
        const newFilter = { ...filter, [key]: value };
        onFilterChange(newFilter);
    }, [filter, onFilterChange]);

    // 디바운스된 검색어 처리
    useEffect(() => {
        if (debouncedSearch !== filter.search) {
            handleFilterChange('search', debouncedSearch);
        }
    }, [debouncedSearch, filter.search, handleFilterChange]);

    useEffect(() => {
        // 필터 변경 시 상위 컴포넌트에 알림
        onFilterChange(filter);
    }, [filter, onFilterChange]);

    return (
        <div className="mb-4 space-y-4">
            <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        로그 레벨
                    </label>
                    <select
                        value={filter.level}
                        onChange={(e) => handleFilterChange('level', e.target.value)}
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">모든 레벨</option>
                        <option value="info">Info</option>
                        <option value="warn">Warning</option>
                        <option value="error">Error</option>
                    </select>
                </div>
                
                <div className="flex-1 min-w-[200px]">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        소스
                    </label>
                    <select
                        value={filter.source}
                        onChange={(e) => handleFilterChange('source', e.target.value)}
                        className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">모든 소스</option>
                        <option value="frontend">Frontend</option>
                        <option value="backend">Backend</option>
                    </select>
                </div>
            </div>

            <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    검색
                </label>
                <input
                    type="text"
                    placeholder="메시지 또는 경로로 검색..."
                    value={filter.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="w-full border rounded px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {filter.search && (
                    <button
                        onClick={() => handleFilterChange('search', '')}
                        className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                    >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
};

export default React.memo(LogFilter); 