#!/usr/bin/env python3
"""
등록된 API 라우트 목록 출력 (검증용).
backend 디렉토리에서 실행: python scripts/list_routes.py 또는 PYTHONPATH=. python scripts/list_routes.py
"""
import sys
from pathlib import Path

# backend 루트를 path에 추가
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.main import app


def list_routes():
    print("등록된 라우트 (path, methods):")
    print("-" * 60)
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "routes"):
            for r in route.routes:
                path = route.path + (r.path if r.path else "/")
                methods = getattr(r, "methods", set()) or set()
                if path and methods:
                    print(f"  {path:45} {methods}")
        elif hasattr(route, "path") and hasattr(route, "methods"):
            methods = route.methods or set()
            if route.path and methods:
                print(f"  {route.path:45} {methods}")
    print("-" * 60)
    print("공개 북마크 확인: GET /api/public/bookmarks 또는 GET /api/public/bookmarks/ 가 목록에 있어야 합니다.")


if __name__ == "__main__":
    list_routes()
