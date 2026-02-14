import os
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

def get_article_content(url: str) -> str:
    """
    URL에서 기사 내용을 추출하는 함수
    
    Args:
        url: 기사 URL
        
    Returns:
        str: 추출된 기사 내용
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 본문 내용 추출
        article_text = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:  # 빈 텍스트가 아닌 경우만 추가
                article_text.append(text)
        
        return ' '.join(article_text)
        
    except Exception as e:
        print(f"Error extracting article: {str(e)}")
        return ""

def summarize_article(url: str) -> str:
    """
    URL의 기사를 요약하는 함수
    
    Args:
        url: 기사 URL
        
    Returns:
        str: 요약된 텍스트
    """
    # 기사 내용 추출
    article_text = get_article_content(url)
    if not article_text:
        return "기사 내용을 가져올 수 없습니다."

    # .env 파일 로드
    load_dotenv()

    # OpenAI 클라이언트 설정
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 기사를 간단하게 요약해주는 도우미야."},
                {"role": "user", "content": f"다음 기사를 3줄로 요약해줘:\n\n{article_text.strip()}"}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return "기사 요약 중 오류가 발생했습니다."

if __name__ == "__main__":
    url = input("기사 URL을 입력하세요: ")
    if url:
        summary = summarize_article(url)
        print("\n=== 기사 요약 결과 ===")
        print(summary)
    else:
        print("URL이 입력되지 않았습니다.") 