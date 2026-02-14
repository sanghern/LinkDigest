import React from 'react';

const AutoRefresh = ({ autoRefresh, refreshInterval, onAutoRefreshChange, onIntervalChange }) => {
    return (
        <div className="mb-4 flex items-center space-x-4">
            <div className="flex items-center">
                <input
                    type="checkbox"
                    id="autoRefresh"
                    checked={autoRefresh}
                    onChange={(e) => onAutoRefreshChange(e.target.checked)}
                    className="mr-2"
                />
                <label htmlFor="autoRefresh">자동 새로고침</label>
            </div>
            {autoRefresh && (
                <select
                    value={refreshInterval}
                    onChange={(e) => onIntervalChange(Number(e.target.value))}
                    className="border rounded px-2 py-1"
                >
                    <option value="10">10초</option>
                    <option value="30">30초</option>
                    <option value="60">1분</option>
                </select>
            )}
        </div>
    );
};

export default React.memo(AutoRefresh); 