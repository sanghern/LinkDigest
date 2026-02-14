import React from 'react';
import { format } from 'date-fns';

const LogDetailModal = ({ log, onClose }) => {
    if (!log) return null;

    // timestamp 포맷팅 예시
    const formattedDate = format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss');

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl">
                <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="text-lg font-semibold">로그 상세 정보</h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div className="p-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm font-medium text-gray-500">시간</label>
                            <p>{formattedDate}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-500">레벨</label>
                            <p className={`font-medium ${
                                log.level === 'ERROR' ? 'text-red-600' :
                                log.level === 'WARN' ? 'text-yellow-600' : 'text-blue-600'
                            }`}>{log.level}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-500">소스</label>
                            <p>{log.source}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-500">상태 코드</label>
                            <p>{log.response_status || '-'}</p>
                        </div>
                    </div>

                    <div>
                        <label className="text-sm font-medium text-gray-500">메시지</label>
                        <p className="mt-1 p-2 bg-gray-50 rounded">{log.message}</p>
                    </div>

                    {log.request_path && (
                        <div>
                            <label className="text-sm font-medium text-gray-500">요청 경로</label>
                            <p className="mt-1 font-mono text-sm">{log.request_path}</p>
                        </div>
                    )}

                    {log.trace && (
                        <div>
                            <label className="text-sm font-medium text-gray-500">스택 트레이스</label>
                            <pre className="mt-1 p-2 bg-gray-50 rounded overflow-x-auto text-sm">
                                {log.trace}
                            </pre>
                        </div>
                    )}

                    {log.meta_data && (
                        <div>
                            <label className="text-sm font-medium text-gray-500">메타데이터</label>
                            <pre className="mt-1 p-2 bg-gray-50 rounded overflow-x-auto text-sm">
                                {JSON.stringify(log.meta_data, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default React.memo(LogDetailModal); 