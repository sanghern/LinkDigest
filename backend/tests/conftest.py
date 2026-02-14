import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import requests

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app

# pytest.ini 설정을 활용하여 pythonpath와 asyncio_mode가 자동 적용됨

@pytest.fixture
async def async_client():
    """비동기 HTTP 클라이언트 fixture"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def db_session():
    """데이터베이스 세션 fixture"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def normal_user_token_headers():
    """일반 사용자 토큰 헤더 fixture"""
    return {"Authorization": f"Bearer test-token"}

@pytest.fixture
def base_url():
    """API 기본 URL fixture"""
    return "http://localhost:8000/api"

@pytest.fixture
def admin_token(base_url):
    """관리자 로그인 토큰 fixture"""
    login_data = {
        "username": "admin",
        "password": os.getenv("ADMIN_PASSWORD", "tkdgjsl1234!@#$"),
        "grant_type": "password",
        "scope": ""
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(
        f"{base_url}/auth/login",
        data=urlencode(login_data),
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        pytest.skip("관리자 로그인 실패 - 서버가 실행 중이지 않거나 인증 정보가 잘못됨")

@pytest.fixture
def auth_headers(admin_token):
    """인증 헤더 fixture"""
    return {"Authorization": f"Bearer {admin_token}"} 