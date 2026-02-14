import os
import requests
import logging
import re
from typing import Optional
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# Ollama API 설정 (config.py의 settings에서 가져옴)
OLLAMA_API_URL = settings.OLLAMA_API_URL
TRANSLATE_MODEL = settings.TRANSLATE_MODEL


def detect_language(text: str) -> str:
    """
    텍스트의 언어를 자동으로 감지하는 함수
    
    Args:
        text: 감지할 텍스트
        
    Returns:
        str: 'ko' (한글) 또는 'en' (영어)
    """
    if not text or not text.strip():
        return 'en'  # 기본값은 영어
    
    # 한글 유니코드 범위 확인
    # 한글: 가-힣 (0xAC00-0xD7A3), ㄱ-ㅎ (0x3131-0x318E), ㅏ-ㅣ (0x314F-0x3163)
    korean_pattern = re.compile(r'[가-힣ㄱ-ㅎㅏ-ㅣ]')
    
    # 텍스트에서 한글이 포함되어 있는지 확인
    korean_count = len(korean_pattern.findall(text))
    total_chars = len(re.findall(r'[가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z]', text))
    
    # 한글이 30% 이상이면 한글로 판단
    if total_chars > 0 and korean_count / total_chars > 0.3:
        return 'ko'
    else:
        return 'en'


def translate_text(text: str, source_lang: Optional[str] = None, target_lang: Optional[str] = None) -> str:
    """
    텍스트를 번역하는 함수
    
    Args:
        text: 번역할 텍스트
        source_lang: 원본 언어 ('ko' 또는 'en'). None이면 자동 감지
        target_lang: 목표 언어 ('ko' 또는 'en'). None이면 자동 결정 (영어->한글, 한글->영어)
        
    Returns:
        str: 번역된 텍스트. 오류 발생 시 원본 텍스트 반환
    """
    if not text or not text.strip():
        return text
    
    try:
        # 언어 자동 감지
        if source_lang is None:
            detected_lang = detect_language(text)
            source_lang = detected_lang
            logger.info(f"언어 자동 감지: {source_lang}")
        
        # 목표 언어 결정
        if target_lang is None:
            if source_lang == 'ko':
                target_lang = 'en'
            else:
                target_lang = 'ko'
        
        # 같은 언어면 번역하지 않음
        if source_lang == target_lang:
            logger.info(f"원본 언어와 목표 언어가 동일하여 번역하지 않습니다: {source_lang}")
            return text
        
        logger.info(f"번역 시작: {source_lang} -> {target_lang}")
        
        # 번역 방향에 따른 프롬프트 설정
        if source_lang == 'en' and target_lang == 'ko':
            system_prompt = "You are a professional translator. Translate the given English text into Korean. Provide only the translated text without any additional explanations or notes."
            user_prompt = f"Translate the following English text to Korean:\n\n{text}"
        else:  # ko -> en
            system_prompt = "You are a professional translator. Translate the given Korean text into English. Provide only the translated text without any additional explanations or notes."
            user_prompt = f"Translate the following Korean text to English:\n\n{text}"
        
        # Ollama API 요청
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": TRANSLATE_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "stream": False
            },
            timeout=300  # 5분 타임아웃
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Ollama 응답 형식: {"message": {"content": "..."}}
        translated_text = result.get('message', {}).get('content', '')
        
        if not translated_text:
            logger.warning("Ollama API 응답에 번역된 텍스트가 없습니다.")
            return text
        
        logger.info(f"번역 완료: {source_lang} -> {target_lang}")
        return translated_text.strip()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API 요청 실패: {str(e)}", exc_info=True)
        return text
    except Exception as e:
        logger.error(f"번역 실패: {str(e)}", exc_info=True)
        return text


def translate_to_korean(text: str) -> str:
    """
    영어 텍스트를 한글로 번역하는 함수
    
    Args:
        text: 번역할 영어 텍스트
        
    Returns:
        str: 번역된 한글 텍스트
    """
    return translate_text(text, source_lang='en', target_lang='ko')


def translate_to_english(text: str) -> str:
    """
    한글 텍스트를 영어로 번역하는 함수
    
    Args:
        text: 번역할 한글 텍스트
        
    Returns:
        str: 번역된 영어 텍스트
    """
    return translate_text(text, source_lang='ko', target_lang='en')


# 테스트 코드
if __name__ == "__main__":
    # 영어 -> 한글 테스트
    english_text = "Hello, this is a test message for translation."
    print(f"\n원본 (영어): {english_text}")
    korean_result = translate_to_korean(english_text)
    print(f"번역 (한글): {korean_result}")
    
    # 한글 -> 영어 테스트
    korean_text = "안녕하세요, 이것은 번역을 위한 테스트 메시지입니다."
    print(f"\n원본 (한글): {korean_text}")
    english_result = translate_to_english(korean_text)
    print(f"번역 (영어): {english_result}")
    
    # 자동 감지 테스트
    auto_text = "This is an automatic language detection test."
    print(f"\n자동 감지 테스트 (영어): {auto_text}")
    auto_result = translate_text(auto_text)
    print(f"번역 결과: {auto_result}")
