import axios from 'axios';
import logger from './logger';

/**
 * API Base URL 설정
 * 
 * React 앱은 다음 순서로 환경 변수를 로드합니다:
 * 1. 시스템 환경 변수 (최우선)
 * 2. .env 파일의 값
 * 3. 기본값 (fallback)
 * 
 * .env 파일에서 REACT_APP_API_URL을 설정하면 그 값을 사용합니다.
 * 없으면 기본값 '/api'를 사용합니다.
 */
const getApiBaseURL = () => {
    const url = process.env.REACT_APP_API_URL;
    if (url) {
        return url.trim();
    }
    return '/api';  // .env 파일에 값이 없을 때만 기본값 사용
};

const api = axios.create({
    baseURL: getApiBaseURL(),  // .env 파일의 REACT_APP_API_URL 값 사용
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        logger.info('API Request', {
            url: config.url,
            method: config.method,
            data: config.data
        });
        
        return config;
    },
    (error) => {
        logger.error('API Request Error', error);
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // 서버 응답이 있는 경우
            logger.error('API Error', {
                status: error.response.status,
                data: error.response.data,
                url: error.config.url
            });

            if (error.response.status === 401) {
                // 인증 에러 처리
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
        } else if (error.request) {
            // 서버 응답이 없는 경우
            logger.error('Network Error', {
                message: 'No response from server',
                url: error.config.url
            });
        } else {
            // 요청 설정 중 에러
            logger.error('Request Error', {
                message: error.message
            });
        }
        return Promise.reject(error);
    }
);

export default api; 