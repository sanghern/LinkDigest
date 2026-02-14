import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import api from '../utils/api';
import LogStats from './LogStats';
import logger from '../utils/logger';
import LogFilter from './LogFilter';
import LogTable from './LogTable';
import Pagination from './Pagination';
import AutoRefresh from './AutoRefresh';
import LoadingSpinner from './LoadingSpinner';
import ErrorDisplay from './ErrorDisplay';

const LogViewer = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filter, setFilter] = useState({
        level: 'all',
        source: 'all',
        search: ''
    });
    const [autoRefresh, setAutoRefresh] = useState(false);
    const [refreshInterval, setRefreshInterval] = useState(30);
    const [page, setPage] = useState(1);
    const PAGE_SIZE = 10;
    const [totalCount, setTotalCount] = useState(0);
    const [stats, setStats] = useState(null);

    const fetchLogs = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.logs.getList({
                page,
                per_page: PAGE_SIZE,
                level: filter.level,
                source: filter.source,
                search: filter.search
            });
            setLogs(response.items);
            setTotalCount(response.total);
        } catch (error) {
            console.error('로그 조회 실패:', error);
            setError('로그를 불러오는데 실패했습니다.');
        } finally {
            setLoading(false);
        }
    }, [page, filter]);

    const fetchStats = useCallback(async () => {
        try {
            const stats = await api.logs.getStats();
            setStats(stats);
        } catch (error) {
            console.error('통계 조회 실패:', error);
            setError('통계를 불러오는데 실패했습니다.');
        }
    }, []);

    useEffect(() => {
        fetchLogs();
        fetchStats();
    }, [fetchLogs, fetchStats]);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchLogs, refreshInterval * 1000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, refreshInterval, fetchLogs]);

    const handleFilterChange = useCallback((newFilter) => {
        setFilter(newFilter);
        setPage(1);
    }, []);

    const handlePageChange = useCallback((newPage) => {
        setPage(newPage);
    }, []);

    const handleAutoRefreshChange = useCallback((enabled) => {
        setAutoRefresh(enabled);
    }, []);

    const handleIntervalChange = useCallback((interval) => {
        setRefreshInterval(interval);
    }, []);

    const getLevelColor = useCallback((level) => {
        switch (level.toLowerCase()) {
            case 'error': return 'text-red-600';
            case 'warn': return 'text-yellow-600';
            case 'info': return 'text-blue-600';
            default: return 'text-gray-600';
        }
    }, []);

    const handleDownload = async () => {
        try {
            const { logs } = await api.logs.getList({ limit: totalCount });
            
            const csvContent = [
                ['시간', '레벨', '소스', '메시지', '경로', '상태'].join(','),
                ...logs.map(log => [
                    format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss'),
                    log.level,
                    log.source,
                    `"${log.message.replace(/"/g, '""')}"`,
                    log.request_path || '',
                    log.response_status || ''
                ].join(','))
            ].join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `logs_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
            link.click();
            
            logger.info('로그 CSV 다운로드 완료', { count: logs.length });
        } catch (err) {
            const errorMessage = 'CSV 다운로드에 실패했습니다.';
            setError(errorMessage);
            logger.error(errorMessage, err);
        }
    };

    const totalPages = Math.ceil(totalCount / PAGE_SIZE);

    const handleRetry = useCallback(async () => {
        setError(null);
        try {
            await Promise.all([fetchLogs(), fetchStats()]);
        } catch (err) {
            await api.logs.save({
                level: 'ERROR',
                message: '로그 재시도 실패',
                meta_data: {
                    error: err.message
                }
            });
        }
    }, [fetchLogs, fetchStats]);

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <LoadingSpinner message="로그 데이터를 불러오는 중입니다..." />
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <ErrorDisplay error={error} onRetry={handleRetry} />
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">시스템 로그</h2>
                <button
                    onClick={handleDownload}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                    CSV 다운로드
                </button>
            </div>
            
            {stats === null && (
                <div className="mb-6">
                    <LoadingSpinner message="통계 데이터를 불러오는 중..." />
                </div>
            )}
            
            <LogStats stats={stats} />
            
            <LogFilter 
                filter={filter} 
                onFilterChange={handleFilterChange} 
            />
            
            <AutoRefresh
                autoRefresh={autoRefresh}
                refreshInterval={refreshInterval}
                onAutoRefreshChange={handleAutoRefreshChange}
                onIntervalChange={handleIntervalChange}
            />

            <LogTable 
                logs={logs} 
                getLevelColor={getLevelColor} 
            />

            <Pagination
                page={page}
                totalPages={totalPages}
                onPageChange={handlePageChange}
            />
        </div>
    );
};

export default LogViewer; 