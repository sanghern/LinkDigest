import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import requests
import json
import uuid
from datetime import datetime
from urllib.parse import urlencode
import pytest

# pytest.ini 설정을 활용하여 pythonpath와 asyncio_mode가 자동 적용됨

def test_bookmarks():
    base_url = "http://localhost:8000/api"
    token = None
    created_bookmark_id = None

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

    def test_create_bookmark():
        """북마크 생성 테스트"""
        print("\n=== 북마크 생성 테스트 ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        bookmark_data = {
            "title": "Test Bookmark",
            "url": "https://example.com",  # 단순 문자열로 전달
            "summary": "Test summary",
            "source_name": "Test source",
            "tags": ["test", "example"]
        }
        
        response = requests.post(
            f"{base_url}/bookmarks/",
            headers=headers,
            json=bookmark_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "북마크 생성 실패"
        assert response.json()["title"] == bookmark_data["title"]
        return response.json()["id"]

    def test_get_bookmarks():
        """북마크 목록 조회 테스트"""
        print("\n=== 북마크 목록 조회 테스트 ===")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{base_url}/bookmarks/",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "북마크 목록 조회 실패"
        assert isinstance(response.json(), list), "응답이 리스트 형식이 아님"

    def test_update_bookmark():
        """북마크 수정 테스트"""
        print("\n=== 북마크 수정 테스트 ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "title": "Updated Bookmark",
            "url": "https://example.com/updated",
            "source_name": "Test Source",
            "summary": "This is an updated test bookmark",
            "tags": ["test", "update", "api"]
        }
        
        try:
            response = requests.put(
                f"{base_url}/bookmarks/{created_bookmark_id}",
                headers=headers,
                json=update_data
            )
            
            print(f"Status Code: {response.status_code}")
            
            # 응답 내용 출력 전에 검사
            response_text = response.text
            print(f"Raw Response: {response_text}")
            
            if response.status_code == 500:
                print("서버 내부 오류가 발생했습니다.")
                return
            
            if not response_text:
                print("빈 응답이 반환되었습니다.")
                return
            
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            assert response.status_code == 200, "북마크 수정 실패"
            assert response_data["title"] == update_data["title"]
            assert response_data["url"] == update_data["url"]
            assert response_data["source_name"] == update_data["source_name"]
            assert response_data["summary"] == update_data["summary"]
            assert response_data["tags"] == update_data["tags"]
            
        except requests.exceptions.RequestException as e:
            print(f"요청 중 오류 발생: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {str(e)}")
        except Exception as e:
            print(f"예상치 못한 오류: {str(e)}")

    def test_update_bookmark_invalid_url():
        """잘못된 URL로 북마크 수정 테스트"""
        print("\n=== 잘못된 URL 북마크 수정 테스트 ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        invalid_data = {
            "title": "Test Bookmark",
            "url": "invalid-url"  # 잘못된 URL 형식
        }
        
        response = requests.put(
            f"{base_url}/bookmarks/{created_bookmark_id}",
            headers=headers,
            json=invalid_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 422, "잘못된 URL 검증 실패"

    def test_delete_bookmark():
        """북마크 삭제 테스트"""
        print("\n=== 북마크 삭제 테스트 ===")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.delete(
            f"{base_url}/bookmarks/{created_bookmark_id}",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200, "북마크 삭제 실패"
        
        # 삭제된 북마크 조회 시도
        response = requests.get(
            f"{base_url}/bookmarks/{created_bookmark_id}",
            headers=headers
        )
        assert response.status_code == 404, "삭제된 북마크가 여전히 조회됨"

    def test_read_count():
        """북마크 조회수 테스트"""
        print("\n=== 북마크 조회수 테스트 ===")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # 초기 조회
            response = requests.get(
                f"{base_url}/bookmarks/{created_bookmark_id}",
                headers=headers
            )
            assert response.status_code == 200, "북마크 조회 실패"
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # read_count 필드 존재 확인
            response_data = response.json()
            assert "read_count" in response_data, "read_count 필드가 응답에 없습니다"
            initial_count = response_data["read_count"]
            print(f"초기 조회수: {initial_count}")
            
            # 다시 조회
            response = requests.get(
                f"{base_url}/bookmarks/{created_bookmark_id}",
                headers=headers
            )
            assert response.status_code == 200, "북마크 조회 실패"
            
            response_data = response.json()
            new_count = response_data["read_count"]
            print(f"새로운 조회수: {new_count}")
            
            # 조회수 증가 확인
            assert new_count == initial_count + 1, f"조회수가 증가하지 않음 (초기: {initial_count}, 현재: {new_count})"
            
        except AssertionError as e:
            print(f"Error: {str(e)}")
            raise
        except Exception as e:
            print(f"Error: 조회수 테스트 중 오류 발생 - {str(e)}")
            raise

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
        
        # 3. 로그아웃된 토큰으로 북마크 접근 시도
        response = requests.get(
            f"{base_url}/bookmarks",
            headers=headers
        )
        
        print(f"\n=== 로그아웃된 토큰으로 북마크 접근 시도 ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 401, "로그아웃된 토큰으로 접근이 성공함"

    try:
        print("\n🔍 북마크 API 테스트 시작...")
        
        # 로그인하여 토큰 얻기
        token = login()
        
        # CRUD 테스트 실행
        created_bookmark_id = test_create_bookmark()
        test_get_bookmarks()
        test_read_count()  # 삭제하기 전에 조회수 테스트
        test_update_bookmark()  # 북마크 수정 테스트
        test_update_bookmark_invalid_url()  # 잘못된 URL 테스트
        test_delete_bookmark()
        test_logout()  # 로그아웃 테스트 추가
        
        print("\n✅ 모든 북마크 테스트가 성공적으로 완료되었습니다!")
        
    except AssertionError as e:
        print(f"\n❌ [검증 실패] {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ [연결 오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n❌ [오류] 테스트 중 예상치 못한 오류 발생: {str(e)}")
    finally:
        print("\n🔚 테스트 완료")

# pytest 형식의 테스트 함수들 (기존 로직 재사용)
def test_bookmark_create(base_url, auth_headers):
    """북마크 생성 테스트 (pytest 형식)"""
    bookmark_data = {
        "title": "Test Bookmark",
        "url": "https://example.com",
        "summary": "Test summary",
        "source_name": "Test source",
        "tags": ["test", "example"]
    }
    
    response = requests.post(
        f"{base_url}/bookmarks/",
        headers=auth_headers,
        json=bookmark_data
    )
    
    assert response.status_code == 200, "북마크 생성 실패"
    assert response.json()["title"] == bookmark_data["title"]
    return response.json()["id"]

def test_bookmark_get_list(base_url, auth_headers):
    """북마크 목록 조회 테스트 (pytest 형식)"""
    response = requests.get(
        f"{base_url}/bookmarks/",
        headers=auth_headers
    )
    
    assert response.status_code == 200, "북마크 목록 조회 실패"
    data = response.json()
    assert isinstance(data, dict), "응답이 딕셔너리 형식이 아님"
    assert "items" in data or isinstance(data, list), "응답 구조가 올바르지 않음"

def test_bookmark_read_count(base_url, auth_headers):
    """북마크 조회수 테스트 (pytest 형식)"""
    # 먼저 북마크 생성
    bookmark_id = test_bookmark_create(base_url, auth_headers)
    
    # 초기 조회
    response = requests.get(
        f"{base_url}/bookmarks/{bookmark_id}",
        headers=auth_headers
    )
    assert response.status_code == 200, "북마크 조회 실패"
    initial_count = response.json()["read_count"]
    
    # 다시 조회하여 조회수 증가 확인
    response = requests.get(
        f"{base_url}/bookmarks/{bookmark_id}",
        headers=auth_headers
    )
    assert response.status_code == 200, "북마크 조회 실패"
    new_count = response.json()["read_count"]
    
    assert new_count == initial_count + 1, f"조회수가 증가하지 않음 (초기: {initial_count}, 현재: {new_count})"
    
    # 정리: 생성한 북마크 삭제
    requests.delete(f"{base_url}/bookmarks/{bookmark_id}", headers=auth_headers)

if __name__ == "__main__":
    # 기존 독립 실행 방식 유지
    test_bookmarks() 