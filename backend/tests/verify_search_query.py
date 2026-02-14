#!/usr/bin/env python3
"""
필터 검색 쿼리 검증 스크립트
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# 환경 변수 로드
load_dotenv()

# DB 연결 설정
DB_PASSWORD = "tkdgjsl1234!@#$"
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)
DATABASE_URL = os.getenv('AIGROUND_DB_URL', 
    f"postgresql://aiground:{ENCODED_PASSWORD}@192.168.7.89:5432/aiscrap?sslmode=disable")

def verify_search_queries():
    """검색 쿼리 검증"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("=" * 80)
            print("필터 검색 쿼리 검증")
            print("=" * 80)
            print()
            
            # 1. 샘플 데이터 확인
            print("[1] 샘플 데이터 확인")
            print("-" * 80)
            sample_query = text("""
                SELECT 
                    id,
                    title,
                    tags,
                    array_to_string(tags, ',') as tags_string
                FROM bookmarks 
                WHERE tags IS NOT NULL 
                  AND array_length(tags, 1) > 0
                LIMIT 5
            """)
            
            result = conn.execute(sample_query)
            rows = result.fetchall()
            
            if not rows:
                print("⚠️  tags가 있는 북마크가 없습니다.")
                return
            
            for idx, row in enumerate(rows, 1):
                print(f"  [{idx}] ID: {row[0]}")
                print(f"      제목: {row[1][:50]}...")
                print(f"      tags: {row[2]}")
                print(f"      tags 문자열: {row[3]}")
                print()
            
            # 2. 단일 태그 검색 쿼리 테스트
            print("[2] 단일 태그 검색 쿼리 테스트")
            print("-" * 80)
            
            # 실제 tags에서 키워드 추출
            if rows:
                sample_tags = rows[0][2]  # 첫 번째 북마크의 tags
                if sample_tags and len(sample_tags) > 0:
                    test_keyword = sample_tags[0]  # 첫 번째 태그 사용
                    print(f"테스트 키워드: '{test_keyword}'")
                    print()
                    
                    # unnest를 사용한 검색 쿼리
                    search_query = text("""
                        SELECT 
                            id,
                            title,
                            tags,
                            array_to_string(tags, ',') as tags_string
                        FROM bookmarks 
                        WHERE tags IS NOT NULL 
                          AND array_length(tags, 1) > 0
                          AND EXISTS (
                              SELECT 1 
                              FROM unnest(bookmarks.tags) AS tag 
                              WHERE tag LIKE :keyword
                          )
                        LIMIT 10
                    """)
                    
                    search_result = conn.execute(
                        search_query.bindparams(keyword=f'%{test_keyword}%')
                    )
                    search_rows = search_result.fetchall()
                    
                    print(f"검색 결과: {len(search_rows)}개")
                    for idx, row in enumerate(search_rows, 1):
                        print(f"  [{idx}] {row[1][:50]}...")
                        print(f"      tags: {row[3]}")
                    print()
                    
                    # 부분 일치 테스트
                    if len(test_keyword) > 2:
                        partial_keyword = test_keyword[:len(test_keyword)//2]
                        print(f"부분 일치 테스트 (키워드: '{partial_keyword}')")
                        partial_result = conn.execute(
                            search_query.bindparams(keyword=f'%{partial_keyword}%')
                        )
                        partial_rows = partial_result.fetchall()
                        print(f"검색 결과: {len(partial_rows)}개")
                        print()
            
            # 3. 다중 태그 검색 쿼리 테스트 (AND 조건)
            print("[3] 다중 태그 검색 쿼리 테스트 (AND 조건)")
            print("-" * 80)
            
            if rows:
                # 여러 북마크에서 태그 추출
                all_tags = []
                for row in rows[:3]:  # 처음 3개 북마크
                    if row[2]:
                        all_tags.extend(row[2])
                
                if len(all_tags) >= 2:
                    test_tags = list(set(all_tags))[:2]  # 중복 제거 후 2개 선택
                    print(f"테스트 태그: {test_tags}")
                    print()
                    
                    # AND 조건으로 검색
                    multi_search_query = text("""
                        SELECT 
                            id,
                            title,
                            tags,
                            array_to_string(tags, ',') as tags_string
                        FROM bookmarks 
                        WHERE tags IS NOT NULL 
                          AND array_length(tags, 1) > 0
                          AND EXISTS (
                              SELECT 1 
                              FROM unnest(bookmarks.tags) AS tag 
                              WHERE tag LIKE :keyword_0
                          )
                          AND EXISTS (
                              SELECT 1 
                              FROM unnest(bookmarks.tags) AS tag 
                              WHERE tag LIKE :keyword_1
                          )
                        LIMIT 10
                    """)
                    
                    multi_result = conn.execute(
                        multi_search_query.bindparams(
                            keyword_0=f'%{test_tags[0]}%',
                            keyword_1=f'%{test_tags[1]}%'
                        )
                    )
                    multi_rows = multi_result.fetchall()
                    
                    print(f"AND 조건 검색 결과: {len(multi_rows)}개")
                    for idx, row in enumerate(multi_rows, 1):
                        print(f"  [{idx}] {row[1][:50]}...")
                        print(f"      tags: {row[3]}")
                    print()
            
            # 4. 쿼리 성능 확인
            print("[4] 쿼리 성능 확인")
            print("-" * 80)
            
            explain_query = text("""
                EXPLAIN ANALYZE
                SELECT 
                    id,
                    title,
                    tags
                FROM bookmarks 
                WHERE tags IS NOT NULL 
                  AND array_length(tags, 1) > 0
                  AND EXISTS (
                      SELECT 1 
                      FROM unnest(bookmarks.tags) AS tag 
                      WHERE tag LIKE '%AI%'
                  )
                LIMIT 10
            """)
            
            explain_result = conn.execute(explain_query)
            explain_rows = explain_result.fetchall()
            
            print("EXPLAIN ANALYZE 결과:")
            for row in explain_rows:
                print(f"  {row[0]}")
            print()
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    verify_search_queries()
