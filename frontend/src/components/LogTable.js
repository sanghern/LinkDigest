import React, { useState } from 'react';
import { format } from 'date-fns';
import LogDetailModal from './LogDetailModal';

const LogTable = ({ logs, getLevelColor }) => {
    const [selectedLog, setSelectedLog] = useState(null);

    return (
        <>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                    <thead>
                        <tr className="bg-gray-100">
                            <th className="px-4 py-2">시간</th>
                            <th className="px-4 py-2">레벨</th>
                            <th className="px-4 py-2">소스</th>
                            <th className="px-4 py-2">메시지</th>
                            <th className="px-4 py-2">경로</th>
                            <th className="px-4 py-2">상태</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map((log) => (
                            <tr 
                                key={log.id} 
                                className="border-b hover:bg-gray-50 cursor-pointer"
                                onClick={() => setSelectedLog(log)}
                            >
                                <td className="px-4 py-2">
                                    {format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                                </td>
                                <td className={`px-4 py-2 ${getLevelColor(log.level)}`}>
                                    {log.level}
                                </td>
                                <td className="px-4 py-2">{log.source}</td>
                                <td className="px-4 py-2">{log.message}</td>
                                <td className="px-4 py-2">{log.request_path || '-'}</td>
                                <td className="px-4 py-2">
                                    {log.response_status ? 
                                        <span className={log.response_status < 400 ? 'text-green-600' : 'text-red-600'}>
                                            {log.response_status}
                                        </span> 
                                        : '-'
                                    }
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {selectedLog && (
                <LogDetailModal
                    log={selectedLog}
                    onClose={() => setSelectedLog(null)}
                />
            )}
        </>
    );
};

export default React.memo(LogTable); 