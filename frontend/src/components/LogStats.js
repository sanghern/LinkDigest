import React from 'react';

const LogStats = ({ stats }) => {
    if (!stats) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* 전체 통계 */}
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-2">전체 통계</h3>
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <span>총 로그 수:</span>
                        <span className="font-medium">{stats.total_logs}</span>
                    </div>
                    <div className="flex justify-between">
                        <span>최근 24시간:</span>
                        <span className="font-medium">{stats.last_24h}</span>
                    </div>
                </div>
            </div>

            {/* 레벨별 통계 */}
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-2">레벨별 통계</h3>
                <div className="space-y-2">
                    {Object.entries(stats.by_level).map(([level, count]) => (
                        <div key={level} className="flex justify-between">
                            <span>{level}:</span>
                            <span className={`font-medium ${
                                level === 'ERROR' ? 'text-red-600' :
                                level === 'WARN' ? 'text-yellow-600' : 'text-blue-600'
                            }`}>
                                {count}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* 소스별 통계 */}
            <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-2">소스별 통계</h3>
                <div className="space-y-2">
                    {Object.entries(stats.by_source).map(([source, count]) => (
                        <div key={source} className="flex justify-between">
                            <span>{source}:</span>
                            <span className="font-medium">{count}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default LogStats; 