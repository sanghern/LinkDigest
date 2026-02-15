from bs4 import BeautifulSoup
import requests
import logging
from urllib.parse import urlparse, urljoin
from typing import Dict, Optional, Tuple, List
import re
import urllib3
from ..utils.summerise_openai import summarize_article
from ..utils.translate import translate_text, detect_language

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """웹 페이지 내용 가져오기"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"페이지 로딩 실패: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """페이지 제목 추출"""
        if not soup:
            return ''
            
        # 1. og:title 메타 태그 확인 (가장 정확한 제목 정보)
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
            
        # 2. article 태그 내 h1 태그 확인
        article = soup.find('article')
        if article:
            h1 = article.find('h1')
            if h1:
                return h1.get_text().strip()
            
        # 3. 첫 번째 h1 태그 확인
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        # 4. title 태그 확인
        if soup.title:
            title = soup.title.string
            if title:
                # 불필요한 접미사 제거 (예: " - 사이트명")
                return title.split('|')[0].split('-')[0].strip()
            
        return ''

    def _extract_content(self, soup: BeautifulSoup, url: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        웹 페이지에서 컨텐츠, 참조 링크, 이미지를 추출하는 함수
        
        Args:
            soup: BeautifulSoup 파싱된 HTML 객체
            url: 원본 웹페이지 URL
            
        Returns:
            Tuple[str, List[Dict[str, str]]]: 
                - 추출된 컨텐츠 문자열 (마크다운 형식)
                - 참조 링크 목록 (텍스트와 URL 포함)
        """
        # 결과를 저장할 리스트 초기화
        content = []  # 추출된 텍스트 컨텐츠를 저장
        reference_links = []  # 참조 링크 정보를 저장
        seen_texts = set()  # 중복 텍스트 방지를 위한 집합
        seen_urls = set()   # 중복 URL 방지를 위한 집합
        seen_images = set() # 중복 이미지 방지를 위한 집합

        # 1. 메인 컨텐츠 영역 찾기
        main_content = None
        for selector in ['article', 'main', '.post-content', '.article-content', '.entry-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        target = main_content if main_content else soup

        # 2. 불필요한 요소 제거
        for tag in target.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()

        # 3. 컨텐츠 추출
        paragraphs = target.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
        for p in paragraphs:
            # 3.1 텍스트 정규화 (공백, 줄바꿈 등 처리)
            text = ' '.join(p.get_text().strip().split())
            
            # 3.2 의미 있는 텍스트만 추가 (중복 제거)
            if text and len(text) > 20 and text not in seen_texts:
                seen_texts.add(text)
                content.append(text)

                # 참조 링크 추출
                for link in p.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(url, href)
                        if absolute_url not in seen_urls:
                            link_text = ' '.join(link.get_text().strip().split())
                            if link_text and len(link_text) > 5:
                                seen_urls.add(absolute_url)
                                reference_links.append({
                                    'text': link_text,
                                    'url': absolute_url
                                })

                # 이미지 추출
                for img in p.find_all('img', src=True):
                    src = img.get('src')
                    if src and not src.startswith('data:'):  # base64 이미지 제외
                        img_url = urljoin(url, src)
                        if img_url not in seen_images:
                            seen_images.add(img_url)
                            alt_text = img.get('alt', '이미지') or '이미지'
                            content.append(f"![{alt_text}]({img_url})")

        # 4. 참조 링크 정보를 컨텐츠 끝에 마크다운 형식으로 추가
        if reference_links:
            content.append("\n### 참조 링크")
            for ref in reference_links:
                content.append(f"- [{ref['text']}]({ref['url']})")

        # 최종 결과 반환 (컨텐츠는 줄바꿈으로 구분)
        return '\n\n'.join(content), reference_links

    def _extract_source_name(self, soup: BeautifulSoup, url: str) -> str:
        """출처 이름 추출"""
        # og:site_name 메타 태그 확인
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            return og_site['content'].strip()
            
        # 도메인에서 추출
        domain = urlparse(url).netloc
        return domain.replace('www.', '')

    # def _extract_link_content(self, url: str) -> str:
    #     """참조 링크의 내용 추출 - 주석 처리"""
    #     try:
    #         response = requests.get(url, headers=self.headers, timeout=5)
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         return soup.get_text()[:500] + "..."  # 첫 500자만 추출
    #     except Exception as e:
    #         logger.warning(f"링크 내용 추출 실패: {url} - {str(e)}")
    #         return ""

    def scrape(self, url: str) -> Dict[str, str]:
        """URL에서 컨텐츠를 스크랩"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = self._extract_title(soup)
            
            # title이 있으면 영어인 경우에만 한글로 번역하여 한글(영문) 형태로 변환
            if title:
                try:
                    detected_lang = detect_language(title)
                    # 영어인 경우에만 한글로 번역
                    if detected_lang == 'en':
                        translated_title = translate_text(title, source_lang='en', target_lang='ko')
                        # 번역 성공 시 한글(영문) 형태로 변환
                        if translated_title and translated_title != title:
                            title = f"{translated_title}({title})"
                            logger.info(f"제목 번역 완료: {title}")
                    # 한글인 경우는 그대로 유지
                    else:
                        logger.info(f"제목이 한글이므로 번역하지 않음: {title}")
                except Exception as e:
                    logger.warning(f"제목 번역 실패: {str(e)}, 원본 제목 사용")
            
            content, reference_links = self._extract_content(soup, url)
            source_name = self._extract_source_name(soup, url)

            return {
                'title': title,
                'content': content,
                'source_name': source_name,
                'reference_links': reference_links
            }

        except Exception as e:
            logger.error(f"스크랩 실패: {str(e)}")
            return {
                'title': '',
                'content': '',
                'source_name': '',
                'reference_links': []
            }

def generate_summary(text: str, model: str = None) -> str:
    """텍스트 요약 생성 (model 미지정 시 기본 모델 사용)."""
    try:
        return summarize_article(text, model=model)
    except Exception as e:
        logger.error(f"요약 생성 실패: {str(e)}")
        return "" 