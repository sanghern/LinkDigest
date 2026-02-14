import axios from 'axios';

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

// FastAPI 배열 쿼리 파라미터 형식에 맞게 변환하는 함수
// tags=AI&tags=코딩 형식으로 변환 (기본값: tags[]=AI&tags[]=코딩)
const paramsSerializer = (params) => {
    const searchParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
        const value = params[key];
        if (value === null || value === undefined) {
            return; // null/undefined 값은 제외
        }
        
        if (Array.isArray(value)) {
            // 배열인 경우 각 요소를 반복하여 추가 (tags=AI&tags=코딩 형식)
            value.forEach(item => {
                if (item !== null && item !== undefined) {
                    searchParams.append(key, item);
                }
            });
        } else {
            // 일반 값인 경우 그대로 추가
            searchParams.append(key, value);
        }
    });
    
    return searchParams.toString();
};

const axiosInstance = axios.create({
    baseURL: getApiBaseURL(),
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true,
    paramsSerializer: paramsSerializer
});

// API 에러 처리 함수 정의
const handleApiError = (error) => {
    if (error.response) {
        // 서버 응답이 있는 경우
        console.error('API Error:', error.response.data);
        throw new Error(error.response.data.detail || '요청 처리 중 오류가 발생했습니다.');
    } else if (error.request) {
        // 요청은 보냈지만 응답을 받지 못한 경우
        console.error('API Request Error:', error.request);
        throw new Error('서버에서 응답을 받지 못했습니다.');
    } else {
        // 요청 설정 중 오류 발생
        console.error('API Setup Error:', error.message);
        throw error;
    }
};

// 요청 인터셉터
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

const api = {
    // Auth
    auth: {
        login: async (username, password) => {
            try {
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('password', password);
                
                const response = await axiosInstance.post('/auth/login', formData, {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                });

                // 토큰 저장
                if (response.data.access_token) {
                    localStorage.setItem('token', response.data.access_token);
                    // Authorization 헤더 설정
                    axiosInstance.defaults.headers.common['Authorization'] = 
                        `Bearer ${response.data.access_token}`;
                }

                return response.data;
            } catch (error) {
                console.error('Login failed:', error.response?.data || error.message);
                
                // 에러 메시지 개선
                if (error.response) {
                    // 서버 응답이 있는 경우
                    const errorMessage = error.response.data?.detail || 
                                       error.response.data?.message || 
                                       '로그인에 실패했습니다.';
                    throw new Error(errorMessage);
                } else if (error.request) {
                    // 요청은 보냈지만 응답을 받지 못한 경우 (네트워크 에러)
                    throw new Error('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.');
                } else {
                    // 요청 설정 중 오류 발생
                    throw new Error(error.message || '로그인 요청 중 오류가 발생했습니다.');
                }
            }
        },
        
        logout: async () => {
            try {
                const response = await axiosInstance.post('/auth/logout');
                // 토큰 제거
                localStorage.removeItem('token');
                delete axiosInstance.defaults.headers.common['Authorization'];
                return response.data;
            } catch (error) {
                console.error('Logout failed:', error.response?.data || error.message);
                throw error;
            }
        },
        
        me: async () => {
            try {
                const response = await axiosInstance.get('/auth/me');
                return response.data;
            } catch (error) {
                if (error.response?.status === 401) {
                    localStorage.removeItem('token');
                    delete axiosInstance.defaults.headers.common['Authorization'];
                }
                throw error;
            }
        }
    },

    // Bookmarks
    bookmarks: {
        create: async (data) => {
            const response = await axiosInstance.post('/bookmarks/', data);
            return response.data;
        },

        getList: async ({ page, per_page, tags }) => {
            const params = { page, per_page };
            // 여러 태그를 배열로 전달 (FastAPI Query 파라미터 배열 형식)
            if (tags && tags.length > 0) {
                params.tags = tags;
            }
            
            // 디버깅: 전달되는 파라미터 확인
            console.log('[Frontend API] getList 호출:', params);
            
            const response = await axiosInstance.get('/bookmarks/', {
                params
            });
            
            // 디버깅: 실제 요청 URL 확인
            console.log('[Frontend API] 실제 요청 URL:', response.config.url);
            
            return response.data;
        },

        update: async (id, data) => {
            try {
                // URL 문자열 정규화 및 검증
                let validUrl;
                try {
                    // URL 객체로 변환하여 유효성 검사
                    const urlObject = new URL(data.url.startsWith('http') ? data.url : `https://${data.url}`);
                    validUrl = urlObject.toString(); // 정규화된 URL 문자열로 변환
                } catch (urlError) {
                    throw new Error('올바른 URL 형식이 아닙니다.');
                }

                // 데이터 정제
                const bookmarkData = {
                    title: data.title.trim(),
                    url: validUrl,  // 검증된 URL 문자열
                    source_name: data.source_name?.trim() || '',
                    summary: data.summary?.trim() || '',
                    tags: Array.isArray(data.tags) ? data.tags : 
                        data.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                };

                const response = await axiosInstance.put(`/bookmarks/${id}`, bookmarkData);
                return response.data;
            } catch (error) {
                if (error.response?.status === 422) {
                    throw new Error(error.response.data.detail || '입력값이 올바르지 않습니다.');
                }
                console.error('북마크 수정 실패:', error);
                throw error;
            }
        },

        delete: async (id) => {
            const response = await axiosInstance.delete(`/bookmarks/${id}`);
            return response.data;
        },

        getDetail: async (id) => {
            const response = await axiosInstance.get(`/bookmarks/${id}`);
            return response.data;
        },

        getById: async (id) => {
            try {
                const response = await axiosInstance.get(`/bookmarks/${id}`);
                return response.data;
            } catch (error) {
                handleApiError(error);
            }
        },

        getBookmark: async (id) => {
            const response = await axiosInstance.get(`/bookmarks/${id}`);
            return response.data;
        },

        increaseReadCount: async (bookmarkId) => {
            try {
                const response = await axiosInstance.post(`/bookmarks/${bookmarkId}/increase-read-count`, {});
                return response.data;
            } catch (error) {
                throw error;
            }
        },
    },

    // Logs
    logs: {
        getList: async (params) => {
            const response = await axiosInstance.get('/logs/', { params });
            return response.data;
        },

        getStats: async () => {
            const response = await axiosInstance.get('/logs/stats');
            return response.data;
        },

        save: async (data) => {
            const response = await axiosInstance.post('/logs/', {
                ...data,
                timestamp: data.timestamp || new Date().toISOString()
            });
            return response.data;
        }
    }
};

export default api; 