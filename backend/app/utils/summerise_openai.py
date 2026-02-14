import os
import requests
from dotenv import load_dotenv
import logging
from typing import Optional
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# Ollama API 설정 (config.py의 settings에서 가져옴)
OLLAMA_API_URL = settings.OLLAMA_API_URL
OLLAMA_MODEL = settings.OLLAMA_MODEL

def summarize_article(text: str) -> str:
    """
    Ollama Mistral:7b 모델을 사용하여 텍스트를 마크다운 형식으로 편집하는 함수
    
    Args:
        text (str): 편집할 텍스트 내용
        
    Returns:
        str: 편집된 텍스트. 오류 발생 시 빈 문자열 반환
        
    Note:
        - Ollama 로컬 모델(Mistral:7b)을 사용하여 마크다운 형식으로 편집
        - 컨텐츠 분류와 키워드 추출
        - 중요 내용을 강조하고 가독성 높은 포맷 사용
    """
    try:
        logger.info("Ollama API 요청 시작: 텍스트 편집")
        
        # Ollama API 요청
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 입력한 컨텐츠를 가독성 좋게 마크다운 형식으로 편집하는 전문가입니다. \
                        마크다운 형식으로 편집하며, 제목(`##`), 소제목(`###`), 리스트(`-` 또는 `1.`)을 적절히 사용하여 가독성을 높이세요. \
                        중요한 통계 및 인용문을 **굵은 글씨**로 강조하세요., \
                        또한 비교가 가능한 내용을 비교표를 만들어 주세요.\
                        참조 링크는 항상 포함하세요. \
                        이미지 링크는 컨텐츠 내에 적절하게 배치하세요. \
                        첫부문에 컨텐츠에 대한 기사,블로그,논문 등과 같은 분류기준으로 `📌️ 분류`와 `📌 키워드`를 한라인씩 추가하고, \
                        다음에 5줄 `📌 핵심요약`을 각각 라인으로 구분하여 추가하세요."
                    },
                    {
                        "role": "user",
                        "content": f"다음 컨텐츠가 한글이 아닌경우 한글로 번역한 후 가독성 좋게 나열식으로 편집해 주세요:\n\n{text}\n\n"
                    }
                ],
                "stream": False
            },
            timeout=300  # 5분 타임아웃 (대용량 텍스트 처리 고려)
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Ollama 응답 형식: {"message": {"content": "..."}}
        edited_content = result.get('message', {}).get('content', '')
        
        if not edited_content:
            logger.warning("Ollama API 응답에 컨텐츠가 없습니다.")
            return ""
        
        logger.info("텍스트 편집 완료")
        return edited_content
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API 요청 실패: {str(e)}", exc_info=True)
        return ""
    except Exception as e:
        logger.error(f"텍스트 편집 실패: {str(e)}", exc_info=True)
        return ""

def get_api_key() -> Optional[str]:
    """
    더 이상 사용하지 않는 함수 (Ollama는 API 키가 필요 없음)
    
    Returns:
        None: 항상 None 반환
    """
    logger.info("Ollama는 API 키가 필요하지 않습니다.")
    return None

# 테스트 코드
if __name__ == "__main__":
    test_article = """
    [테스트 컨텐츠]
    인공지능(AI) 기술이 빠르게 발전하면서 다양한 산업 분야에서 혁신을 이끌고 있다.
    특히 자연어 처리 분야에서는 GPT와 같은 대규모 언어 모델이 등장하여 텍스트 생성, 번역, 요약 등 다양한 작업을 수행할 수 있게 되었다.
    이러한 AI 기술의 발전은 업무 효율성을 높이고 새로운 서비스를 창출하는 데 기여하고 있으며, 앞으로도 계속해서 발전할 것으로 전망된다.
    """
    
    edited = summarize_article(test_article)
    print("\n=== 편집 결과 ===")
    print(edited)
