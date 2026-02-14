/**
 * Docker 백엔드 연결 검증 스크립트
 * 사용법: node scripts/verify-backend.js [BASE_URL]
 * 기본 BASE_URL: http://localhost:8000/api
 * 예: node scripts/verify-backend.js http://localhost:8080/api
 */

const http = require('http');
const https = require('https');

const BASE_URL = process.argv[2] || 'http://localhost:8000/api';

function request(url, options = {}) {
    return new Promise((resolve, reject) => {
        const u = new URL(url);
        const lib = u.protocol === 'https:' ? https : http;
        const req = lib.request(
            url,
            { method: options.method || 'GET', timeout: 5000 },
            (res) => {
                let data = '';
                res.on('data', (ch) => (data += ch));
                res.on('end', () => {
                    try {
                        resolve({ status: res.statusCode, data: data ? JSON.parse(data) : null });
                    } catch {
                        resolve({ status: res.statusCode, data });
                    }
                });
            }
        );
        req.on('error', reject);
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('timeout'));
        });
        if (options.body) {
            req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
            req.write(options.body);
        }
        req.end();
    });
}

async function main() {
    console.log('=== Docker 백엔드 연결 검증 ===');
    console.log('대상 URL:', BASE_URL);
    console.log('');

    let ok = true;

    // 1. Health
    try {
        const health = await request(`${BASE_URL}/health`);
        if (health.status === 200) {
            console.log('[OK] GET /api/health:', health.status, health.data || '');
        } else {
            console.log('[FAIL] GET /api/health:', health.status, health.data);
            ok = false;
        }
    } catch (e) {
        console.log('[FAIL] GET /api/health - 연결 실패:', e.message);
        ok = false;
    }

    // 2. Root (API 정보)
    try {
        const root = await request(BASE_URL.replace(/\/api\/?$/, '') + '/');
        if (root.status === 200 && root.data && root.data.message) {
            console.log('[OK] GET /:', root.status, root.data.message);
        } else {
            console.log('[INFO] GET /:', root.status, root.data || '');
        }
    } catch (e) {
        console.log('[WARN] GET / -', e.message);
    }

    // 3. Login (실제 프론트 연결과 동일한 방식)
    const adminUser = process.env.ADMIN_USERNAME || 'admin';
    const adminPass = process.env.ADMIN_PASSWORD || process.env.REACT_APP_ADMIN_PASSWORD || '';
    if (adminPass) {
        try {
            const body = new URLSearchParams({ username: adminUser, password: adminPass }).toString();
            const login = await request(`${BASE_URL}/auth/login`, { method: 'POST', body });
            if (login.status === 200 && login.data && login.data.access_token) {
                console.log('[OK] POST /api/auth/login: 토큰 발급 성공');
            } else {
                console.log('[FAIL] POST /api/auth/login:', login.status, login.data?.detail || login.data);
                ok = false;
            }
        } catch (e) {
            console.log('[FAIL] POST /api/auth/login - 연결 실패:', e.message);
            ok = false;
        }
    } else {
        console.log('[SKIP] POST /api/auth/login (ADMIN_PASSWORD 미설정)');
    }

    console.log('');
    if (ok) {
        console.log('결과: Docker 백엔드에 정상 연결됩니다.');
        process.exit(0);
    } else {
        console.log('결과: 일부 검증 실패. 백엔드가 실행 중인지, URL이 맞는지 확인하세요.');
        process.exit(1);
    }
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
