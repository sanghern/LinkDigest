import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pytest

# pytest.ini 설정을 활용하여 pythonpath와 asyncio_mode가 자동 적용됨

def test_logs():
    base_url = "http://localhost:8000/api"
    token = None  # 전역 토큰 변수

    def login():
        """관리자로 로그인하여 토큰 얻기"""
        print("\n=== 로그인 테스트 ===")
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
        return response.json()["access_token"]

    def test_create_log():
        """로그 생성 테스트"""
        print("\n=== 로그 생성 테스트 ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        log_data = {
            "level": "INFO",
            "message": "Test log message",
            "source": "backend",
            "request_path": "/api/test",
            "request_method": "GET",
            "response_status": 200,
            "execution_time": 0.5,
            "ip_address": "127.0.0.1",
            "user_agent": "test-client",
            "meta_data": {"test": "data"}
        }
        
        response = requests.post(
            f"{base_url}/logs/",
            headers=headers,
            json=log_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "로그 생성 실패"
        assert response.json()["message"] == log_data["message"]
        assert "user_id" in response.json(), "user_id가 응답에 없음"
        assert response.json()["user_id"] is not None, "user_id가 None임"

    def test_get_logs():
        """로그 목록 조회 테스트"""
        print("\n=== 로그 목록 조회 테스트 ===")
        
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(
                f"{base_url}/logs",
                headers=headers,
                params={"page": 1, "per_page": 10}
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert response.status_code == 200, "로그 목록 조회 실패"
            assert "items" in data, "items 필드 누락"
            assert "total" in data, "total 필드 누락"
            assert "page" in data, "page 필드 누락"
            assert "per_page" in data, "per_page 필드 누락"
            
            if data["items"]:
                log = data["items"][0]
                assert "id" in log, "로그 ID 누락"
                assert "level" in log, "로그 레벨 누락"
                assert "message" in log, "로그 메시지 누락"
                assert "timestamp" in log, "타임스탬프 누락"
            
            return data
            
        except Exception as e:
            print(f"\n❌ [오류] 로그 조회 중 예외 발생: {str(e)}")
            print(f"응답 내용: {response.text}")
            raise

    def test_get_log_stats():
        """로그 통계 조회 테스트"""
        print("\n=== 로그 통계 조회 테스트 ===")
        
        # 1. 먼저 로그인하여 토큰 얻기
        token = login()
        
        # 2. 토큰을 헤더에 포함하여 요청
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{base_url}/logs/stats",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "로그 통계 조회 실패"
        stats = response.json()
        
        # 필수 통계 필드 확인
        required_fields = [
            "total_logs",
            "error_count",
            "last_24h",
            "by_level",
            "by_source"
        ]
        for field in required_fields:
            assert field in stats, f"통계에 {field} 필드가 없음"
        
        # 레벨별 통계 확인
        assert "INFO" in stats["by_level"], "INFO 레벨 통계 없음"
        assert "ERROR" in stats["by_level"], "ERROR 레벨 통계 없음"
        
        # 소스별 통계 확인
        assert "frontend" in stats["by_source"], "프론트엔드 통계 없음"
        assert "backend" in stats["by_source"], "백엔드 통계 없음"
        
        return stats

    try:
        print("\n🔍 로그 테스트 시작...")
        
        # 테스트 실행 순서
        token = login()  # 먼저 로그인하여 토큰 얻기
        test_create_log()
        test_get_logs()
        test_get_log_stats()
        
        print("\n✅ 모든 로그 테스트가 성공적으로 완료되었습니다!")
        
    except AssertionError as e:
        print(f"\n❌ [검증 실패] {str(e)}")
    except Exception as e:
        print(f"\n❌ [오류] 테스트 중 예상치 못한 오류 발생: {str(e)}")
    finally:
        print("\n🔚 테스트 완료")

# pytest 형식의 테스트 함수들 (기존 로직 재사용)
def test_log_create(base_url, auth_headers):
    """로그 생성 테스트 (pytest 형식)"""
    log_data = {
        "level": "INFO",
        "message": "Test log message",
        "source": "backend",
        "request_path": "/api/test",
        "request_method": "GET",
        "response_status": 200,
        "execution_time": 0.5,
        "ip_address": "127.0.0.1",
        "user_agent": "test-client",
        "meta_data": {"test": "data"}
    }
    
    response = requests.post(
        f"{base_url}/logs/",
        headers=auth_headers,
        json=log_data
    )
    
    assert response.status_code == 200, "로그 생성 실패"
    assert response.json()["message"] == log_data["message"]
    assert "user_id" in response.json(), "user_id가 응답에 없음"

def test_log_get_list(base_url, auth_headers):
    """로그 목록 조회 테스트 (pytest 형식)"""
    response = requests.get(
        f"{base_url}/logs",
        headers=auth_headers,
        params={"page": 1, "per_page": 10}
    )
    
    assert response.status_code == 200, "로그 목록 조회 실패"
    data = response.json()
    assert "items" in data, "items 필드 누락"
    assert "total" in data, "total 필드 누락"
    assert "page" in data, "page 필드 누락"
    assert "per_page" in data, "per_page 필드 누락"

def test_log_get_stats(base_url, auth_headers):
    """로그 통계 조회 테스트 (pytest 형식)"""
    response = requests.get(
        f"{base_url}/logs/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 200, "로그 통계 조회 실패"
    stats = response.json()
    
    required_fields = [
        "total_logs",
        "error_count",
        "last_24h",
        "by_level",
        "by_source"
    ]
    for field in required_fields:
        assert field in stats, f"통계에 {field} 필드가 없음"

if __name__ == "__main__":
    # 기존 독립 실행 방식 유지
    test_logs() 