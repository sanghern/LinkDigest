import os
import json
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

# 프롬프트 설정 파일 경로 (이 모듈과 같은 디렉터리의 prompt.conf)
_PROMPT_CONF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.conf")


def _normalize_prompt(value):  # str | list -> str (newline 유지)
    """문자열이면 그대로, 리스트면 줄 단위로 \\n 연결."""
    if isinstance(value, list):
        return "\n".join(str(line) for line in value)
    return value if isinstance(value, str) else ""


def _load_prompts() -> dict:
    """prompt.conf(JSON)에서 system/user_template 로드. 실패 시 기본 문자열 반환."""
    try:
        with open(_PROMPT_CONF_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {
            "system": _normalize_prompt(raw.get("system", "")),
            "user_template": _normalize_prompt(raw.get("user_template", "{text}")),
        }
    except Exception as e:
        logger.warning(f"prompt.conf 로드 실패, 기본 프롬프트 사용: {e}")
        return {
            "system": "당신은 입력한 웹 컨텐츠를 핵심만 추출하여 가독성 높은 마크다운 형식으로 정리하는 전문 편집자입니다.",
            "user_template": "다음 컨텐츠를 위 규칙에 맞게 정리하세요:\n\n{text}\n\n",
        }


def summarize_article(text: str, model: Optional[str] = None) -> str:
    """
    Ollama 모델을 사용하여 텍스트를 마크다운 형식으로 편집하는 함수
    
    Args:
        text (str): 편집할 텍스트 내용
        model (str, optional): 사용할 모델명. 미지정 시 OLLAMA_MODEL 사용
        
    Returns:
        str: 편집된 텍스트. 오류 발생 시 빈 문자열 반환
    """
    try:
        use_model = (model or "").strip() or OLLAMA_MODEL
        logger.info(f"Ollama API 요청 시작: 텍스트 편집 (모델: {use_model})")
        prompts = _load_prompts()
        system_content = prompts.get("system", "")
        user_content = (prompts.get("user_template", "{text}")).format(text=text)

        # Ollama API 요청
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": use_model,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ],
                "stream": False,
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
