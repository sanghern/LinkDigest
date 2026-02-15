# 데일리시큐(dailysecu.com) 스크래핑 미동작 원인 분석

## 대상 URL
- `https://www.dailysecu.com/news/articleView.html?idxno=205216` (fbclid 등 쿼리 파라미터 포함 가능)

## 분석 결과 요약

| 항목 | 내용 |
|------|------|
| **HTTP 응답** | 200 OK, 약 122KB HTML 정상 수신 (curl 검증) |
| **본문 위치** | `#article-view-content-div` (class: `article-veiw-body view-page`, itemprop="articleBody") 또는 그 상위 `.article-body` |
| **원인** | 메인 컨텐츠 선택자에 데일리시큐/일부 뉴스 사이트용 선택자가 없어, **첫 번째 `article`**만 사용함. 해당 사이트는 본문이 **중첩된 article 내부의 div**에 있어, 선택한 영역에서 본문이 누락되거나 노이즈가 많을 수 있음. |

## 상세 분석

### 1. 사이트 HTML 구조 (요약)
- **제목**: `og:title`, `<title>` 태그에 정상 존재.
- **본문 영역**:
  - 최상위: `<article class="atlview-grid-body">` (레이아웃 래퍼)
  - 그 안: `<div class="article-body">` → `<div id="article-view-content-div" class="article-veiw-body view-page" itemprop="articleBody">` 안에 실제 기사 `<p>` 태그들이 있음.
- 현재 스크래퍼는 `article`, `main`, `.post-content`, `.article-content`, `.entry-content` 순으로 **첫 번째로 매칭되는 것**만 사용. `article`이 먼저 매칭되면 `atlview-grid-body`가 선택됨.
- 이론상 해당 article 하위에 본문 div와 `<p>`가 있으므로 추출은 가능하나, **같은 article 안에 툴바·드롭다운(글자크기 설정 등)**이 포함되어 있어, 선택자를 더 구체화하면 본문만 안정적으로 추출 가능.

### 2. 가능한 추가 원인
- **긴 URL(fbclid 등)**: 서버가 동일 본문을 반환하는지, 리다이렉트/차단 여부는 서버 설정에 따름. curl로 긴 URL 요청 시 200이면 동일하게 수신되는 경우가 많음.
- **User-Agent / 봇 차단**: 일부 사이트는 단순 User-Agent로 차단할 수 있음. 현재 `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`만 사용 중.
- **타임아웃**: 기본 10초. 페이지가 무거우면 실패할 수 있음.

## 조치 사항 (구현 반영)

1. **메인 컨텐츠 선택자 확장**  
   본문 영역을 더 정확히 잡기 위해 아래 선택자를 **기존 선택자보다 앞**에 추가함.
   - `#article-view-content-div` (데일리시큐 등)
   - `[itemprop="articleBody"]`
   - `.article-body`
   - `.article_view` (일부 뉴스 사이트)

2. **User-Agent 보강**  
   Chrome 브라우저와 유사한 전체 User-Agent 문자열로 변경하여 차단 가능성을 줄임.

3. **(선택) 타임아웃**  
   필요 시 `scrape()` 호출 시 타임아웃을 15초 등으로 늘릴 수 있음.

## 참고
- 수정 파일: `backend/app/services/scraping_service.py`
  - `_extract_content`: 메인 컨텐츠 선택자에 `#article-view-content-div`, `[itemprop="articleBody"]`, `.article-body`, `.article_view` 추가.
  - `self.headers`: User-Agent를 Chrome 유사 문자열로, Accept / Accept-Language 헤더 추가.
