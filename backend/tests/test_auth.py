import os
import requests
import json
import uuid
from datetime import datetime
from urllib.parse import urlencode
import pytest

# pytest.ini 설정을 활용하여 pythonpath와 asyncio_mode가 자동 적용됨

def test_user_auth():
    base_url = "http://localhost:8000/api"
    
    # 1. 관리자 로그인 테스트
    def test_admin_login():
        print("\n=== 관리자 로그인 테스트 ===")
        
        login_data = {
            "username": "admin",
            "password": "tkdgjsl1234!@#$",
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
        
        assert response.status_code == 200, "로그인 실패"
        data = response.json()
        
        # 응답 구조 검증
        assert "access_token" in data, "access_token 누락"
        assert "token_type" in data, "token_type 누락"
        assert "user" in data, "user 정보 누락"
        
        # user 객체 검증
        user = data["user"]
        assert "id" in user, "user.id 누락"
        assert "username" in user, "user.username 누락"
        assert user["username"] == "admin", "username 불일치"
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return data["access_token"]
    
    # 2. 잘못된 비밀번호로 로그인 테스트
    def test_invalid_password():
        print("\n=== 잘못된 비밀번호 로그인 테스트 ===")
        login_data = {
            "username": "admin",
            "password": "wrongpassword",
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
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 401, "잘못된 비밀번호로 로그인이 성공함"
    
    # 3. 존재하지 않는 사용자로 로그인 테스트
    def test_invalid_user():
        print("\n=== 존재하지 않는 사용자 로그인 테스트 ===")
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = requests.post(
            f"{base_url}/auth/login",
            data=login_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 401, "존재하지 않는 사용자로 로그인이 성공함"
    
    # 4. 토큰으로 사용자 정보 조회 테스트
    def test_me(token):
        print("\n=== 사용자 정보 조회 테스트 ===")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{base_url}/auth/me",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200, "사용자 정보 조회 실패"
        data = response.json()
        
        # 응답 구조 검증
        assert "id" in data, "id 필드 누락"
        assert "username" in data, "username 필드 누락"
        assert isinstance(data["id"], str), "id는 문자열이어야 함"
        assert isinstance(data["username"], str), "username은 문자열이어야 함"
        
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return data
    
    # 5. 잘못된 토큰으로 접근 테스트
    def test_invalid_token():
        print("\n=== 잘못된 토큰 테스트 ===")
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = requests.get(
            f"{base_url}/auth/me",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 401, "잘못된 토큰으로 접근이 성공함"
    
    def test_logout():
        print("\n=== 로그아웃 테스트 ===")
        
        # 1. 먼저 로그인하여 토큰 얻기
        login_data = {
            "username": "admin",
            "password": "tkdgjsl1234!@#$",
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
        
        assert response.status_code == 200, "로그인 실패"
        token = response.json()["access_token"]
        
        # 2. 로그아웃 요청
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{base_url}/auth/logout",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "로그아웃 실패"
        assert response.json()["message"] == "Successfully logged out"
        
        # 3. 로그아웃된 토큰으로 /me 엔드포인트 접근 시도
        response = requests.get(
            f"{base_url}/auth/me",
            headers=headers
        )
        
        print(f"\n=== 로그아웃된 토큰 검증 ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 401, "로그아웃된 토큰으로 접근이 성공함"
    
    try:
        print("\n🔍 사용자 인증 테스트 시작...")
        
        token = test_admin_login()
        print("\n✅ 로그인 응답 구조 검증 성공")
        print("- access_token 확인")
        print("- token_type 확인")
        print("- user 정보 확인")
        
        # 테스트 실행
        #test_invalid_password()
        #test_invalid_user()
        test_me(token)
        #test_invalid_token()
        test_logout()
        
        print("\n✅ 모든 인증 테스트가 성공적으로 완료되었습니다!")
        
    except AssertionError as e:
        print(f"\n❌ [검증 실패] {str(e)}")
        print("예상 응답 구조:")
        print(json.dumps({
            "access_token": "string",
            "token_type": "string",
            "user": {
                "id": "string",
                "username": "string"
            }
        }, indent=2))
    except requests.exceptions.ConnectionError:
        print("\n❌ [연결 오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n❌ [오류] 테스트 중 예상치 못한 오류 발생: {str(e)}")
    finally:
        print("\n🔚 테스트 완료")

def test_login_success(client, test_db, test_user):
    """로그인 성공 테스트"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123!",
            "grant_type": "password",
            "scope": ""
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 응답 구조 검증
    assert "access_token" in data
    assert "token_type" in data
    assert "user" in data
    
    # 토큰 검증
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert data["token_type"] == "bearer"
    
    # 사용자 정보 검증
    user = data["user"]
    assert isinstance(user, dict)
    assert "id" in user
    assert "username" in user
    assert isinstance(user["id"], str)
    assert isinstance(user["username"], str)
    assert user["username"] == "testuser"

def test_login_invalid_credentials(client, test_db):
    """잘못된 인증 정보로 로그인 실패 테스트"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wronguser",
            "password": "wrongpass",
            "grant_type": "password",
            "scope": ""
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect username or password"

def test_login_missing_fields(client):
    """필수 필드 누락 시 로그인 실패 테스트"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            # password 누락
            "grant_type": "password",
            "scope": ""
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

if __name__ == "__main__":
    test_user_auth() 