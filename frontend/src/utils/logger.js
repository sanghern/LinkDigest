// import api from './axios'; // 제거
import api from './api';

class Logger {
    constructor() {
        this.logFile = null;
        this.initLogFile();
    }

    async initLogFile() {
        try {
            // 로그 파일 생성 (브라우저의 File System Access API 사용)
            const fileHandle = await window.showSaveFilePicker({
                suggestedName: 'frontend.log',
                types: [{
                    description: 'Log Files',
                    accept: { 'text/plain': ['.log'] },
                }],
            });
            this.logFile = fileHandle;
        } catch (error) {
            console.warn('로그 파일 생성 실패:', error);
        }
    }

    async writeToFile(logMessage) {
        if (!this.logFile) return;
        
        try {
            const writable = await this.logFile.createWritable();
            await writable.write(logMessage + '\n');
            await writable.close();
        } catch (error) {
            console.error('로그 파일 쓰기 실패:', error);
        }
    }

    formatLogMessage(level, message, data = {}) {
        const timestamp = new Date().toISOString();
        const userId = localStorage.getItem('userId') || 'anonymous';
        return `${timestamp} [${level}] [user:${userId}] frontend: ${message}`;
    }

    async saveToDb(level, message, data = {}) {
        try {
            const userId = localStorage.getItem('userId');
            const logData = {
                level: level.toUpperCase(),
                message,
                source: 'frontend',
                timestamp: new Date().toISOString(),
                user_id: userId || null,
                meta_data: {
                    ...data,
                    url: window.location.href,
                    userAgent: navigator.userAgent
                }
            };

            if (userId) {
                await api.logs.save(logData);
            }
        } catch (error) {
            console.error('DB 로그 저장 실패:', error);
        }
    }

    async log(level, message, data = {}) {
        const logMessage = this.formatLogMessage(level, message, data);
        
        // 콘솔 출력
        if (level.toLowerCase() === 'error') {
            console.error(logMessage, data);
        } else if (level.toLowerCase() === 'warn') {
            console.warn(logMessage, data);
        } else {
            console.log(logMessage, data);
        }

        // 파일 저장
        await this.writeToFile(logMessage);
        
        // DB 저장
        await this.saveToDb(level, message, data);
    }

    async info(message, data = {}) {
        console.info(message, data);
        
        try {
            await api.logs.save({
                level: "INFO",
                message: message,
                source: "frontend",
                meta_data: {
                    ...data,
                    url: window.location.href,
                    userAgent: navigator.userAgent
                }
            });
        } catch (logError) {
            console.error('로그 저장 실패:', logError);
        }
    }

    async warn(message, data = {}) {
        await this.log('WARN', message, data);
    }

    async error(message, error) {
        console.error(message, error);
        
        try {
            await api.logs.save({
                level: "ERROR",
                message: message,
                source: "frontend",
                meta_data: {
                    error: error.message,
                    errorDetail: error.response?.data?.detail,
                    errorStack: error.stack,
                    url: window.location.href,
                    userAgent: navigator.userAgent
                }
            });
        } catch (logError) {
            console.error('로그 저장 실패:', logError);
        }
    }
}

const logger = new Logger();
export default logger; 

// logAPI.saveLog -> api.logs.save
export const logError = async (error, context = {}) => {
    try {
        await api.logs.save({
            level: 'ERROR',
            message: error.message,
            // ...
        });
    } catch (logError) {
        console.error('로그 저장 실패:', logError);
    }
}; 