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

/** 공개 API 경로 prefix (인증 불필요). baseURL에 /api 없을 때 /api 붙임 */
const getPublicApiPrefix = () => {
    const base = getApiBaseURL();
    return (base.endsWith('/api') || base.endsWith('/api/')) ? '' : '/api';
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
        if (config.skipAuth) return config;
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
        if (error.response?.status === 401 && !error.config?.skipAuth) {
            localStorage.removeItem('token');
            window.location.href = '/main';
        }
        return Promise.reject(error);
    }
);

const api = {
    // ---------- 공개용 API (인증 불필요, skipAuth) ----------
    publicBookmarks: {
        getList: async ({ page = 1, per_page = 10 } = {}) => {
            const prefix = getPublicApiPrefix();
            const response = await axiosInstance.get(`${prefix}/public/bookmarks/`, {
                params: { page, per_page },
                skipAuth: true
            });
            return response.data;
        },
        getById: async (id) => {
            const prefix = getPublicApiPrefix();
            const response = await axiosInstance.get(`${prefix}/public/bookmarks/${id}`, {
                skipAuth: true
            });
            return response.data;
        },
    },

    // ---------- 인증용 API (토큰 필요) ----------
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

        getSummaryModels: async () => {
            const response = await axiosInstance.get('/bookmarks/summary-models');
            return response.data;
        },

        getList: async ({ page, per_page, tags }) => {
            const params = { page, per_page };
            if (tags && tags.length > 0) {
                params.tags = tags;
            }
            const response = await axiosInstance.get('/bookmarks/', { params });
            return response.data;
        },

        update: async (id, data) => {
            try {
                // URL이 있는 경우에만 형식 검증 (미등록/빈 URL은 검증 생략)
                const urlRaw = data.url != null ? String(data.url).trim() : '';
                let validUrl = urlRaw;
                if (urlRaw) {
                    try {
                        const urlObject = new URL(urlRaw.startsWith('http') ? urlRaw : `https://${urlRaw}`);
                        validUrl = urlObject.toString();
                    } catch (urlError) {
                        throw new Error('올바른 URL 형식이 아닙니다.');
                    }
                }

                // 데이터 정제
                const bookmarkData = {
                    title: data.title.trim(),
                    url: validUrl,
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

        share: async (bookmarkId, target, publicValue = undefined) => {
            const body = { target };
            if (target === 'users' && publicValue !== undefined) body.public = publicValue;
            const response = await axiosInstance.post(`/bookmarks/${bookmarkId}/share`, body);
            return response.data;
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