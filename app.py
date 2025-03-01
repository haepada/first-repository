import streamlit as st
import random
import time
from PIL import Image
import numpy as np
import io
import base64
import threading
import google.generativeai as genai
import re
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="TRPG 주사위 기반 스토리텔링",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 기본 스타일 */
    .main {
        background-color: #151a28;
        color: #d0d0d0;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #4b5d78;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    /* 캐릭터 패널 스타일 */
    .character-panel {
        background-color: #1e2636;
        padding: 15px;
        border-radius: 5px;
        height: 100%;
        margin-bottom: 15px;
    }
    
    /* 스탯 박스 스타일 */
    .stat-box {
        background-color: #2a3549;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stat-name {
        font-weight: bold;
        color: #e0e0ff;
    }
    
    .stat-value {
        font-weight: bold;
        color: #ffcc00;
        font-size: 1.2rem;
    }
    
    /* 카드 스타일 */
    .theme-card {
        background-color: #2a3549;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    .theme-card:hover {
        transform: scale(1.05);
    }
    
    /* 옵션 카드 스타일 */
    .option-card {
        background-color: #2a3549;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.2s;
        border-left: 3px solid #4a90e2;
    }
    
    .option-card:hover {
        transform: translateX(5px);
        background-color: #344261;
    }
    
    h1, h2, h3 {
        color: #e0e0ff;
    }
    .dice-result {
        font-size: 3rem;
        text-align: center;
        color: #ffcc00;
        font-weight: bold;
        margin: 10px 0;
    }
    .player-section {
        border-top: 2px solid #3d4c63;
        padding-top: 10px;
        margin-top: 15px;
    }
    .suggested-action {
        margin: 5px 0;
        padding: 10px;
        background-color: #2a3549;
        border-radius: 5px;
        cursor: pointer;
    }
    .suggested-action:hover {
        background-color: #344261;
    }
    
    .item-action {
        margin: 5px 0;
        padding: 10px;
        background-color: #2a3549;
        border-radius: 5px;
        cursor: pointer;
        border-left: 4px solid #ffcc00;
    }
    .item-notification {
        background-color: #2a3549;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        border-left: 4px solid #ffcc00;
        animation: fadeIn 1s;
    }
    .item-action:hover {
        background-color: #344261;
    }
    .qa-section {
        margin-top: 15px;
        padding: 10px;
        background-color: #1e2636;
        border-radius: 5px;
    }
    .question {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .answer {
        margin-left: 10px;
        margin-bottom: 15px;
    }
    .theme-box {
        width: 300px;
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .check-result {
        background-color: #2a3549;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success {
        color: #4CAF50;
        font-weight: bold;
    }
    .failure {
        color: #F44336;
        font-weight: bold;
    }
    /* 상태창 UI 개선 */
    .stat-box {
        background-color: #2a3549;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stat-name {
        font-weight: bold;
        color: #e0e0ff;
    }
    .stat-value {
        font-weight: bold;
        color: #ffcc00;
        font-size: 1.2rem;
    }
    .inventory-item {
        background-color: #2a3549;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        align-items: center;
    }
    .inventory-item:before {
        content: "•";
        color: #4a90e2;
        font-size: 1.2rem;
        margin-right: 8px;
    }
    .location-button {
        margin: 5px 0;
        padding: 8px 12px;
        background-color: #3d4c63;
        color: white;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
        text-align: center;
    }
    .location-button:hover {
        background-color: #4b5d78;
    }
    /* 주사위 애니메이션 개선 */
    @keyframes dice-roll {
        0% { transform: rotate(0deg) translateY(0px); }
        25% { transform: rotate(90deg) translateY(-20px); }
        50% { transform: rotate(180deg) translateY(0px); }
        75% { transform: rotate(270deg) translateY(-10px); }
        100% { transform: rotate(360deg) translateY(0px); }
    }
    .dice-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 150px;
    }
    .dice-rolling {
        font-size: 4rem;
        color: #ffcc00;
        animation: dice-roll 1s ease-out;
    }
    .previous-story {
        background-color: #1e2636;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #6b8afd;
        opacity: 0.8;
    }
    .continuation-box {
        background-color: #2d3748;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
        border: 2px solid #6b8afd;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .item-action {
        margin: 5px 0;
        padding: 10px;
        background-color: #2a3549;
        border-radius: 5px;
        cursor: pointer;
    }
    .item-acquire {
        border-left: 4px solid #ffcc00;
    }
    .item-use {
        border-left: 4px solid #4CAF50;
    }
    .item-action:hover {
        background-color: #344261;
    }
    .action-number {
        font-weight: bold;
        display: inline-block;
        margin-right: 10px;
        color: #ffcc00;
    }
    .action-text {
        display: inline-block;
    }
    .story-continuation {
        background-color: #1e2636;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .world-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
    .world-action-button {
        flex-grow: 1;
        min-width: 150px;
    }
    .question-box {
        background-color: #2a3549;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #ffcc00;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        margin: 20px 0;
    }
    .loading-text {
        color: #6b8afd;
        font-weight: bold;
        margin-left: 10px;
    }
    
    /* 선택된 버튼 스타일 */
    .selected-button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-left: 4px solid #FFFFFF !important;
        transform: translateX(5px);
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }
    
    /* 질문/선택지 선택 후 표시되는 버튼 강조 */
    .action-button {
        background-color: #4b5d78 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.8rem !important;
        border-radius: 5px !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .action-button:hover {
        background-color: #3a4a5e !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    .primary-action-button {
        background-color: #6b8afd !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.8rem !important;
        border-radius: 5px !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(107, 138, 253, 0.3) !important;
    }
    
    .primary-action-button:hover {
        background-color: #5a79ec !important;
        box-shadow: 0 6px 8px rgba(107, 138, 253, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* 선택된 질문/옵션 스타일 */
    .selected-option {
        background-color: #344261 !important;
        border-left: 4px solid #6b8afd !important;
        transform: translateX(5px);
        transition: all 0.3s ease;
    }
    
    /* 선택된 행동 스타일 */
    .selected-action {
        background-color: #344261 !important;
        border-left: 4px solid #ffcc00 !important;
        transform: translateX(5px);
    }
</style>
""", unsafe_allow_html=True)

# 테마별 이미지 생성 함수
def create_theme_image(theme):
    """테마별 이미지/박스 생성"""
    if theme == "fantasy":
        color = "#4b5d78"
        text = "판타지"
    elif theme == "sci-fi":
        color = "#3a7b9c"
        text = "SF"
    else:  # dystopia
        color = "#8b4045"
        text = "디스토피아"
    
    # HTML로 색상 박스 표시
    return f"""
    <div class="theme-box" style="background-color: {color};">
        {text}
    </div>
    """

# 인벤토리 업데이트 함수
def update_inventory(action, item):
    """인벤토리 아이템 추가/제거"""
    if action == "add":
        if item not in st.session_state.character['inventory']:
            st.session_state.character['inventory'].append(item)
    elif action == "remove":
        if item in st.session_state.character['inventory']:
            st.session_state.character['inventory'].remove(item)

# 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.stage = 'theme_selection'
    st.session_state.world_description = ""
    st.session_state.character = {
        'profession': '',
        'stats': {'STR': 0, 'INT': 0, 'DEX': 0, 'CON': 0, 'WIS': 0, 'CHA': 0},
        'backstory': '',
        'inventory': ['기본 의류', '작은 주머니 (5 골드)']
    }
    st.session_state.story_log = []
    st.session_state.current_location = ""
    # 백업 모드 플래그 추가
    st.session_state.use_backup_mode = False
    # 단일 생성 제어를 위한 키
    st.session_state.world_generated = False
    st.session_state.world_accepted = False
    st.session_state.question_answers = []
    st.session_state.question_count = 0
    st.session_state.question_submitted = False
    st.session_state.question_answered = False
    st.session_state.question_current = ""
    st.session_state.answer_current = ""
    
    st.session_state.background_options_generated = False
    st.session_state.character_backgrounds = []
    
    st.session_state.dice_rolled = False
    st.session_state.dice_result = 0
    st.session_state.dice_rolling_animation = False
    
    st.session_state.action_submitted = False
    st.session_state.action_processed = False
    st.session_state.current_action = ""
    st.session_state.action_response = ""
    st.session_state.ability_check_done = False
    
    st.session_state.suggestions_generated = False
    st.session_state.action_suggestions = []
    
    st.session_state.master_question_submitted = False
    st.session_state.master_question_answered = False
    st.session_state.master_question = ""
    st.session_state.master_answer = ""
    
    # 이동 기능 관련 상태 (중복 제거를 위해 하나만 유지)
    st.session_state.move_submitted = False
    st.session_state.move_processed = False
    st.session_state.move_destination = ""
    st.session_state.move_response = ""
    
    # 가능한 위치 목록 추가
    st.session_state.available_locations = []
    
    # 행동 단계 관련 상태 추가
    st.session_state.action_phase = 'suggestions'
    
    # 이어서 작성하기 관련 상태 추가
    st.session_state.continuation_mode = False
    st.session_state.continuation_text = ""
    
    # 아이템 알림 관련 상태 추가
    st.session_state.item_notification = ""
    st.session_state.show_item_notification = False
    
    # 세계관 질문 관련 상태 추가
    st.session_state.world_questions = []
    st.session_state.world_question_count = 0
    
    # 세계관 페이지 활성 섹션 추가
    st.session_state.active_section = None
    
    st.session_state.master_message = "어서 오세요, 모험가님. 어떤 세계를 탐험하고 싶으신가요?"
    
    st.session_state.initialized = True

@st.cache_resource(ttl=3600)  # 1시간 캐싱
def setup_gemini():
    """Gemini API 초기화 - 캐싱 및 오류 처리 개선"""
    try:
        # Streamlit Secrets에서 API 키 가져오기 
        api_key = st.secrets.get("GEMINI_NEW_0226", None)
        
        if not api_key:
            st.sidebar.error("API 키가 설정되지 않음")
            st.session_state.use_backup_mode = True
            return None
        
        # Gemini API 초기화
        genai.configure(api_key=api_key)
        
        # 최신 모델 이름으로 시도
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            return model
        except Exception as e:
            # 이전 모델 이름으로 시도
            try:
                model = genai.GenerativeModel("gemini-pro")
                return model
            except Exception as inner_e:
                st.error(f"사용 가능한 Gemini 모델을 찾을 수 없습니다. 백업 응답을 사용합니다.")
                st.session_state.use_backup_mode = True
                return None
                
    except Exception as e:
        st.error(f"Gemini 모델 초기화 오류: {e}")
        st.session_state.use_backup_mode = True
        return None
    
# 백업 응답 준비
backup_responses = {
    "world": "당신이 선택한 세계는 신비로운 곳으로, 다양한 인종과 마법이 공존합니다. 북쪽의 산맥에는 고대 종족이 살고 있으며, 남쪽의 숲에는 미지의 생물이 서식합니다. 중앙 평원에는 인간 문명이 발달했으며, 동쪽 바다에는 무역 항로가 발달했습니다. 세계의 균형은 최근 어둠의 세력으로 인해 위협받고 있습니다.",
    "character": "당신은 멀리서 온 여행자로 특별한 재능을 가지고 있습니다. 어린 시절 신비로운 사건을 경험한 후, 그 진실을 찾아 여행하게 되었습니다. 길을 떠나는 동안 다양한 기술을 익혔고, 이제는 자신의 운명을 찾아 나서고 있습니다.",
    "story": "당신은 조심스럽게 앞으로 나아갔습니다. 주변 환경을 잘 살피며 위험 요소를 확인합니다. 다행히 위험은 발견되지 않았고, 앞길이 열렸습니다. 계속해서 탐험을 이어나갈 수 있습니다.",
    "question": "흥미로운 질문입니다! 이 세계의 그 부분은 아직 완전히 탐험되지 않았지만, 전설에 따르면 그곳에는 고대의 지식이 숨겨져 있다고 합니다. 더 알고 싶다면 직접 탐험해보는 것이 좋겠습니다."
}

# Gemini API 호출 개선 - 오류 처리 및 재시도 로직 추가
def generate_gemini_text(prompt, max_tokens=500, retries=2, timeout=10):
    """
    Gemini API를 사용하여 텍스트 생성 - 오류 처리 및 재시도 로직 추가
    """
    # 백업 모드 확인
    if getattr(st.session_state, 'use_backup_mode', False):
        # 백업 모드면 즉시 백업 응답 반환
        if "world" in prompt.lower():
            return backup_responses["world"]
        elif "character" in prompt.lower():
            return backup_responses["character"]
        elif "질문" in prompt.lower() or "question" in prompt.lower():
            return backup_responses["question"]
        else:
            return backup_responses["story"]
    
    # 재시도 로직
    for attempt in range(retries + 1):
        try:
            model = setup_gemini()
            
            if not model:
                # 모델 초기화 실패 시 백업 응답 사용
                if "world" in prompt.lower():
                    return backup_responses["world"]
                elif "character" in prompt.lower():
                    return backup_responses["character"]
                elif "질문" in prompt.lower() or "question" in prompt.lower():
                    return backup_responses["question"]
                else:
                    return backup_responses["story"]
            
            # 안전 설정
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
            
            # 모델 생성 구성
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
                "stop_sequences": ["USER:", "ASSISTANT:"]
            }
            
            # 텍스트 생성
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # 응답 텍스트 추출 및 길이 제한
            text = response.text
            if len(text) > max_tokens * 4:
                text = text[:max_tokens * 4] + "..."
            
            return text
            
        except Exception as e:
            if attempt < retries:
                st.warning(f"API 호출 오류, 재시도 중... ({attempt+1}/{retries})")
                time.sleep(1)  # 잠시 대기 후 재시도
                continue
            else:
                st.error(f"Gemini API 호출 오류: {e}")
                st.session_state.use_backup_mode = True
                
                # 오류 발생 시 백업 응답 사용
                if "world" in prompt.lower():
                    return backup_responses["world"]
                elif "character" in prompt.lower():
                    return backup_responses["character"]
                elif "질문" in prompt.lower() or "question" in prompt.lower():
                    return backup_responses["question"]
                else:
                    return backup_responses["story"]
    
    # 이 코드는 실행되지 않음 (위에서 항상 반환함)
    return backup_responses["story"]


def display_dice_animation(placeholder, dice_expression='1d20', duration=1.0):
    """주사위 굴리기 애니메이션 표시 - 개선된 버전"""
    import re
    
    # 주사위 표현식 파싱
    pattern = r'(\d+)d(\d+)([+-]\d+)?'
    match = re.match(pattern, dice_expression.lower().replace(' ', ''))
    
    if match:
        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier = match.group(3) or "+0"
        modifier_value = int(modifier)
    else:
        # 기본값
        num_dice = 1
        dice_type = 20
        modifier_value = 0
        modifier = "+0"
    
    # 굴리기 시작 시간
    start_time = time.time()
    
    # 주사위 아이콘 선택
    dice_icons = {
        4: "🎲 (d4)",
        6: "🎲 (d6)",
        8: "🎲 (d8)",
        10: "🎲 (d10)",
        12: "🎲 (d12)",
        20: "🎲 (d20)",
        100: "🎲 (d%)"
    }
    dice_icon = dice_icons.get(dice_type, "🎲")
    
    # 애니메이션 표시 (간략화)
    while time.time() - start_time < duration:
        # 임시 주사위 결과 생성
        temp_rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        temp_total = sum(temp_rolls) + modifier_value
        
        # 간소화된 애니메이션 표시
        dice_html = f"""
        <div class='dice-animation'>
            <div class='dice-rolling'>
                {dice_icon}<br>
                <span style='font-size: 1rem;'>{' + '.join([str(r) for r in temp_rolls])}{modifier if modifier_value != 0 else ""}</span><br>
                <span style='font-weight: bold;'>= {temp_total}</span>
            </div>
        </div>
        """
        placeholder.markdown(dice_html, unsafe_allow_html=True)
        time.sleep(0.1)
    
    # 최종 주사위 결과 계산
    result = calculate_dice_result(dice_expression)
    
    # 간소화된 결과 표시
    final_html = f"""
    <div class='dice-result-container'>
        <div style='font-size: 2rem;'>{dice_icon}</div>
        <div>{dice_expression.upper()}</div>
        <div style='margin: 10px 0;'>
    """
    
    # 각 주사위 결과를 간소화하여 표시
    for roll in result['rolls']:
        color = "#4CAF50" if roll == dice_type else "#F44336" if roll == 1 else "#e0e0ff"
        final_html += f"<span style='display:inline-block; margin:0 5px; color:{color};'>{roll}</span>"
    
    # 수정자 및 총점
    if result['modifier'] != 0:
        modifier_sign = "+" if result['modifier'] > 0 else ""
        final_html += f"<br><span>수정자: {modifier_sign}{result['modifier']}</span>"
    
    final_html += f"<br><div style='font-size: 1.8rem; font-weight: bold; color: #FFD700;'>{result['total']}</div></div></div>"
    
    placeholder.markdown(final_html, unsafe_allow_html=True)
    return result

# 위치 이미지 생성 함수 (임시)
def get_location_image(location, theme):
    """위치 이미지 생성 함수 (플레이스홀더)"""
    colors = {
        'fantasy': (100, 80, 200),
        'sci-fi': (80, 180, 200),
        'dystopia': (200, 100, 80)
    }
    color = colors.get(theme, (150, 150, 150))
    
    # 색상 이미지 생성
    img = Image.new('RGB', (400, 300), color)
    return img

# 테마별 직업 생성 함수
def generate_professions(theme):
    """테마에 따른 직업 목록 반환"""
    professions = {
        'fantasy': ['마법사', '전사', '도적', '성직자', '음유시인', '연금술사'],
        'sci-fi': ['우주 파일럿', '사이버 해커', '생체공학자', '보안 요원', '외계종족 전문가', '기계공학자'],
        'dystopia': ['정보 브로커', '밀수업자', '저항군 요원', '엘리트 경비원', '스카운터', '의료 기술자']
    }
    return professions.get(theme, ['모험가', '전문가', '기술자'])

# 테마별 위치 생성 함수
def generate_locations(theme):
    """테마에 따른 위치 목록 반환"""
    locations = {
        'fantasy': ["왕국의 수도", "마법사의 탑", "고대 숲", "상인 거리", "지하 미궁"],
        'sci-fi': ["중앙 우주 정거장", "연구 시설", "거주 구역", "우주선 정비소", "외계 식민지"],
        'dystopia': ["지하 피난처", "통제 구역", "폐허 지대", "저항군 은신처", "권력자 거주구"]
    }
    return locations.get(theme, ["시작 지점", "미지의 땅", "중심부", "외곽 지역", "비밀 장소"])

# 마스터(AI)가 세계관 생성하는 함수
def generate_world_description(theme):
    """선택한 테마에 기반한 세계관 생성 - 개선된 버전"""
    
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. '{theme}' 테마의 몰입감 있는 세계를 한국어로 만들어주세요.
    다음 구조에 따라 체계적으로 세계관을 구축해주세요:

    # 1. 기본 골격 수립
    ## 핵심 테마와 분위기
    - '{theme}'의 특성이 뚜렷하게 드러나는 세계의 중심 이념이나 분위기
    
    ## 세계의 독창적 규칙
    - 이 세계만의 특별한 물리법칙이나 마법/기술 체계
    
    # 2. 구조적 요소
    ## 주요 지역 (3~5개)
    - 각 지역의 특성과 분위기
    
    ## 주요 세력 (2~3개)
    - 세력 간의 관계와 갈등 구조
    
    # 3. 현재 상황
    ## 중심 갈등 
    - 플레이어가 직면하게 될 세계의 주요 문제나 갈등
    
    ## 잠재적 위협
    - 세계를 위협하는 요소나 임박한 위기
    
    # 4. 플레이어 개입 지점
    - 플레이어가 이 세계에서 영향력을 행사할 수 있는 방법
    - 탐험 가능한 비밀이나 수수께끼

    모든 문장은 반드시 완성된 형태로 작성하세요. 중간에 문장이 끊기지 않도록 해주세요.
    전체 내용은 약 400-500단어로 작성해주세요.
    """
    
    return generate_gemini_text(prompt, 800)

# 마스터(AI)가 세계관 질문에 대답하는 함수
def master_answer_question(question, world_desc, theme):
    """세계관에 대한 질문에 마스터가 답변 - 개선된 버전"""
    try:
        prompt = f"""
        당신은 TRPG 게임 마스터입니다. 플레이어가 '{theme}' 테마의 다음 세계에 대해 질문했습니다:
        
        세계 설명:
        {world_desc[:500]}...
        
        플레이어 질문:
        {question}
        
        ## 응답 지침:
        1. 게임 마스터로서 이 질문에 대한 답변을 한국어로 작성해주세요.
        2. 세계관을 풍부하게 하면서 플레이어의 상상력을 자극하는 답변을 제공하세요.
        3. 플레이어가 알 수 없는 신비한 요소를 한두 가지 남겨두세요.
        4. 질문에 관련된 세계의 역사, 전설, 소문 등을 포함하세요.
        5. 150단어 이내로 간결하게 답변하세요.
        
        모든 문장은 완결된 형태로 작성하세요.
        """
        
        return generate_gemini_text(prompt, 400)
    except Exception as e:
        st.error(f"질문 응답 생성 중 오류: {e}")
        return backup_responses["question"]  # 백업 응답 반환

def generate_character_options(profession, theme):
    """직업과 테마에 기반한 캐릭터 배경 옵션 생성 - 개선된 버전"""
    
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. '{theme}' 테마의 세계에서 '{profession}' 직업을 가진 
    캐릭터의 3가지 다른 배경 스토리 옵션을 한국어로 제안해주세요. 

    각 옵션은 다음 요소를 포함해야 합니다:

    ## 삼위일체 구조
    1. **배경 서사**: 캐릭터가 겪은 결정적 사건 3개
    2. **도덕적 축**: 캐릭터의 행동을 결정하는 2가지 가치관이나 신념
    3. **동기 구조**: 표면적 목표, 개인적 욕망, 그리고 숨겨진 공포

    ## 개성화를 위한 요소
    - 캐릭터만의 독특한 특성이나 버릇
    - 관계망 (가족, 멘토, 적대자 등)
    - 물리적 특징이나 외형적 특성

    ## 직업 연계성
    - 이 캐릭터가 해당 직업을 가지게 된 이유
    - 직업 관련 전문 기술이나 지식

    각 옵션을 120단어 내외로 작성해주세요.
    모든 문장은 완결된 형태로 작성하세요.
    
    다음 형식으로 반환해주세요:
    
    #옵션 1:
    (첫 번째 배경 스토리)
    
    #옵션 2:
    (두 번째 배경 스토리)
    
    #옵션 3:
    (세 번째 배경 스토리)
    """
    
    response = generate_gemini_text(prompt, 800)
    
    # 옵션 분리
    options = []
    current_option = ""
    for line in response.split('\n'):
        if line.startswith('#옵션') or line.startswith('# 옵션') or line.startswith('옵션'):
            if current_option:
                options.append(current_option.strip())
            current_option = ""
        else:
            current_option += line + "\n"
    
    if current_option:
        options.append(current_option.strip())
    
    # 옵션이 3개 미만이면 백업 옵션 추가
    while len(options) < 3:
        options.append(f"당신은 {profession}으로, 험난한 세계에서 살아남기 위해 기술을 연마했습니다. 특별한 재능을 가지고 있으며, 자신의 운명을 개척하고자 합니다.")
    
    return options[:3]  # 최대 3개까지만 반환

# 스탯별 색상 및 설명 함수 구현
def get_stat_info(stat, value, profession=""):
    """능력치 값에 따른 색상과 설명 반환 - 안전하게 처리"""
    # 값이 None이거나 숫자가 아닌 경우 기본값 처리
    try:
        value = int(value) if value is not None else 0
    except (ValueError, TypeError):
        value = 0
    
    # 스탯별 색상 설정 (낮음 - 중간 - 높음)
    if value < 8:
        color = "#F44336"  # 빨강 (낮음)
        level = "낮음"
    elif value < 12:
        color = "#FFC107"  # 노랑 (보통)
        level = "보통"
    elif value < 16:
        color = "#4CAF50"  # 초록 (높음)
        level = "높음"
    else:
        color = "#3F51B5"  # 파랑 (매우 높음)
        level = "매우 높음"
    
    # 직업별 스탯 적합성 설명
    profession_stat_match = {
        '마법사': {'INT': '핵심', 'WIS': '중요', 'CON': '생존용'},
        '전사': {'STR': '핵심', 'CON': '중요', 'DEX': '유용'},
        '도적': {'DEX': '핵심', 'INT': '유용', 'CHA': '보조'},
        '성직자': {'WIS': '핵심', 'CHA': '중요', 'CON': '유용'},
        '음유시인': {'CHA': '핵심', 'DEX': '중요', 'WIS': '유용'},
        '연금술사': {'INT': '핵심', 'CON': '중요', 'WIS': '유용'},
        '우주 파일럿': {'DEX': '핵심', 'INT': '중요', 'WIS': '유용'},
        '사이버 해커': {'INT': '핵심', 'DEX': '유용', 'WIS': '보조'},
        '생체공학자': {'INT': '핵심', 'WIS': '중요', 'DEX': '유용'},
        '보안 요원': {'STR': '핵심', 'DEX': '중요', 'CON': '유용'},
        '외계종족 전문가': {'INT': '핵심', 'CHA': '중요', 'WIS': '유용'},
        '기계공학자': {'INT': '핵심', 'DEX': '중요', 'STR': '유용'},
        '정보 브로커': {'INT': '핵심', 'CHA': '중요', 'WIS': '유용'},
        '밀수업자': {'DEX': '핵심', 'CHA': '중요', 'CON': '유용'},
        '저항군 요원': {'DEX': '핵심', 'STR': '중요', 'INT': '유용'},
        '엘리트 경비원': {'STR': '핵심', 'DEX': '중요', 'CON': '유용'},
        '스카운터': {'DEX': '핵심', 'WIS': '중요', 'CON': '유용'},
        '의료 기술자': {'INT': '핵심', 'DEX': '중요', 'WIS': '유용'}
    }
    
    # 현재 직업에 대한 스탯 적합성 확인 (안전하게 처리)
    if profession and isinstance(profession, str) and profession in profession_stat_match and stat in profession_stat_match[profession]:
        match = profession_stat_match[profession][stat]
        description = f"{level} - {match} 스탯"
    else:
        description = f"{level}"
    
    return color, description


# 개선된 스토리 응답 생성 함수
def generate_story_response(action, dice_result, theme, location, character_info, success=None, ability=None, total=None, difficulty=None):
    """행동 결과에 따른 스토리 응답 생성 - 개선된 버전"""
    
    # 아이템 관련 행동인지 확인
    item_acquisition = "[아이템 획득]" in action or "아이템" in action.lower() or "주워" in action or "발견" in action
    item_usage = "[아이템 사용]" in action or "사용" in action.lower()
    
    # 캐릭터 정보 안전하게 가져오기
    stats = character_info.get('stats', {})
    profession = character_info.get('profession', '모험가')
    race = character_info.get('race', '인간')
    inventory = character_info.get('inventory', [])
    backstory = character_info.get('backstory', '')
    special_trait = character_info.get('special_trait', '')
    
    # 결과 판정 요약
    result_status = success if success is not None else (dice_result >= 15)
    result_text = "성공" if result_status else "실패"
    
    # 능력치 관련 정보
    ability_names = {
        'STR': '근력', 'INT': '지능', 'DEX': '민첩', 
        'CON': '체력', 'WIS': '지혜', 'CHA': '매력'
    }
    ability_full_name = ability_names.get(ability, '능력치')
    
    # 안전한 인벤토리 문자열 변환
    inventory_text = ', '.join([
        item.name if hasattr(item, 'name') else str(item) 
        for item in inventory
    ])
    
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어의 행동 결과에 대한 스토리를 생성해주세요.

    ## 상황 정보
    - 테마: {theme}
    - 현재 위치: {location}
    - 플레이어 종족: {race}
    - 플레이어 직업: {profession}
    - 플레이어 능력치: {', '.join([f"{k}: {v}" for k, v in stats.items()]) if stats else "기본 능력치"}
    - 특별한 특성: {special_trait}
    - 인벤토리: {inventory_text}
    - 캐릭터 배경: {backstory[:150]}...
    
    ## 행동 및 판정 결과
    - 행동: {action}
    - 판정 능력: {ability if ability else '없음'} ({ability_full_name})
    - 주사위 결과: {dice_result}
    - 총점: {total if total else dice_result}
    - 난이도: {difficulty if difficulty else 15}
    - 판정 결과: {result_text}
    
    ## 스토리텔링 지침
    1. 감각적 몰입을 위해 시각, 청각, 후각, 촉각 등 다양한 감각적 묘사를 포함해주세요.
    2. 캐릭터의 감정과 내면 상태를 반영해주세요.
    3. 행동의 결과를 극적으로 표현하되, 성공과 실패에 따른 차별화된 결과를 묘사해주세요.
    4. 결과가 세계관에 영향을 미치는 느낌을 주세요.
    5. 모든 문장은 완결되어야 합니다. 중간에 끊기지 않도록 해주세요.
    6. '어떻게 할까요?', '무엇을 할까요?', '선택하세요' 등의 질문 형태는 포함하지 마세요.
    7. 중요한 개념이나 이름은 굵게 표시해주세요 (예: **중요한 단어**).
    8. {profession}과 {race}의 특성을 반영한 묘사를 포함하세요.
    """
    
    # 아이템 관련 행동인 경우 추가 지시사항
    if item_acquisition:
        prompt += f"""
    ## 아이템 획득 지침
    - 플레이어가 획득할 수 있는 아이템을 생성하고, 해당 아이템을 굵게(**아이템명**) 표시해주세요.
    - 아이템에 대한 설명(용도, 품질, 특징)을 포함하세요.
    - 주사위 결과가 좋을수록 더 가치 있는 아이템을 획득하게 해주세요.
    - 소비성 아이템인 경우 수량을 명시하세요. (예: "**물약** 3개")
    - 장비형 아이템인 경우 내구도를 언급하세요. (예: "내구도가 높은 **검**")
        """
    elif item_usage:
        prompt += f"""
    ## 아이템 사용 지침
    - 플레이어가 사용할 아이템을 굵게(**아이템명**) 표시해주세요.
    - 사용 가능한 인벤토리 아이템: {inventory_text}
    - 아이템 사용의 효과를 자세히 설명해주세요.
    - 주사위 결과가 좋을수록 더 효과적으로 아이템을 사용하게 해주세요.
    - 소비성 아이템은 사용 후 소모됨을 설명하세요.
    - 장비형 아이템은 계속 사용 가능함을 설명하세요.
        """
    
    # 테마별 묘사 스타일 가이드 추가
    if theme == 'fantasy':
        prompt += """
    ## 판타지 세계 묘사 가이드
    - 마법적 요소와, 신비로운 분위기를 강조하세요.
    - 판타지 세계의 독특한 종족, 생물, 정신적 특성을 언급하세요.
    - 고대의 힘, 예언, 운명과 같은 테마를 활용하세요.
        """
    elif theme == 'sci-fi':
        prompt += """
    ## SF 세계 묘사 가이드
    - 첨단 기술, 미래적 환경, 외계 존재를 강조하세요.
    - 과학적 원리, 인공지능, 우주 탐험 등의 요소를 활용하세요.
    - 인류의 미래, 기술 발전의 영향과 같은 테마를 반영하세요.
        """
    else:  # dystopia
        prompt += """
    ## 디스토피아 세계 묘사 가이드
    - 암울한 미래, 억압적 사회, 환경 파괴의 흔적을 강조하세요.
    - 생존을 위한 투쟁, 자원 부족, 사회적 긴장감을 묘사하세요.
    - 희망과 절망의 대비, 저항의 불씨와 같은 테마를 활용하세요.
        """
    
    # 스토리 길이 및 스타일 지침
    prompt += """
    ## 스타일 및 형식 지침
    - 약 250-300단어 분량으로 생생하게 묘사해주세요.
    - 중요한 부분은 굵게(**단어**) 강조하세요.
    - 단락을 적절히 나누어 가독성을 높이세요.
    - 다양한 문장 구조를 사용하여 리듬감 있는 서술을 해주세요.
    - 캐릭터와 환경의 상호작용을 강조하여 현장감을 높이세요.
    """
    
    try:
        response = generate_gemini_text(prompt, 600)
        
        # 응답이 너무 짧거나 없는 경우 백업 응답 사용
        if not response or len(response.strip()) < 20:
            success_text = "성공" if (success or dice_result >= 15) else "실패"
            return f"당신은 {action}을(를) 시도했고, 주사위 결과 {dice_result}로 {success_text}했습니다. {success_text}한 결과로 상황이 변화했고, 이제 다음 행동을 결정할 수 있습니다."
        
        return response
    
    except Exception as e:
        # 오류 발생 시 백업 응답
        st.error(f"스토리 생성 중 오류 발생: {e}")
        success_text = "성공" if (success or dice_result >= 15) else "실패"
        return f"당신은 {action}을(를) 시도했습니다. 주사위 결과 {dice_result}가 나왔고, {success_text}했습니다. 다음 행동을 선택할 수 있습니다."

# 스토리 응답에서 아이템 추출 함수 개선
def extract_used_items_from_story(story_text, inventory):
    """스토리 텍스트에서 사용한 아이템 추출 - 개선된 버전"""
    # 인벤토리 아이템 이름 목록 생성
    inventory_names = [item.name if hasattr(item, 'name') else str(item) for item in inventory]
    
    try:
        # 굵게 표시된 텍스트를 우선 추출 (** 사이의 내용)
        import re
        import json
        
        # 굵게 표시된 아이템 이름 추출
        bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
        
        # 사용 관련 키워드
        use_keywords = ["사용", "소비", "마시", "적용", "꺼내", "휘두", "착용"]
        
        # 기본 데이터 생성
        used_items_data = []
        
        # 1. 굵게 표시된 아이템을 우선 처리
        for item_name in bold_items:
            if item_name in inventory_names:
                # 아이템이 사용되었는지 확인 (주변 30자 이내)
                for part in story_text.split(f"**{item_name}**"):
                    # 아이템 이름 앞뒤 30자 검사
                    nearby_text = (part[-30:] if part else "") + (part[:30] if part else "")
                    if any(keyword in nearby_text for keyword in use_keywords):
                        used_items_data.append({
                            "name": item_name,
                            "quantity": 1
                        })
                        break
        
        # 2. 그 외 인벤토리에 있는 아이템이 사용되었는지 검사
        for item_name in inventory_names:
            if not any(item["name"] == item_name for item in used_items_data):
                # 아이템 이름이 스토리에 포함되어 있는지 확인
                if item_name in story_text:
                    # 아이템이 사용되었는지 확인 (주변 30자 이내)
                    for part in story_text.split(item_name):
                        # 아이템 이름 앞뒤 30자 검사
                        nearby_text = (part[-30:] if part else "") + (part[:30] if part else "")
                        if any(keyword in nearby_text for keyword in use_keywords):
                            used_items_data.append({
                                "name": item_name,
                                "quantity": 1
                            })
                            break
        
        # 중복 제거 (같은 아이템이 여러 번 추출된 경우)
        unique_items = {}
        for item in used_items_data:
            name = item["name"]
            if name in unique_items:
                unique_items[name]["quantity"] += item["quantity"]
            else:
                unique_items[name] = item
        
        return list(unique_items.values())
    
    except Exception as e:
        st.error(f"사용된 아이템 추출 오류: {e}")
        # 오류 시 기본 처리
        # 굵게 표시된 아이템 중 인벤토리에 있는 것만 처리
        used_items = []
        bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
        for item_name in bold_items:
            if item_name in inventory_names:
                used_items.append({
                    "name": item_name,
                    "quantity": 1
                })
        return used_items
    
# 아이템 클래스 구조 정의
class Item:
    """게임 내 아이템 기본 클래스"""
    def __init__(self, name, description, type="일반", consumable=False, durability=None, max_durability=None, quantity=1, rarity="일반"):
        self.name = name                    # 아이템 이름
        self.description = description      # 아이템 설명
        self.type = type                    # 아이템 유형 (무기, 방어구, 소비품, 도구, 일반)
        self.consumable = consumable        # 소비성 여부 (사용 후 사라짐)
        self.durability = durability        # 현재 내구도 (None이면 내구도 없음)
        self.max_durability = max_durability or durability  # 최대 내구도
        self.quantity = quantity            # 수량
        self.rarity = rarity                # 희귀도 (일반, 희귀, 영웅, 전설)
        
    def to_dict(self):
        """아이템을 사전 형태로 변환"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'consumable': self.consumable,
            'durability': self.durability,
            'max_durability': self.max_durability,
            'quantity': self.quantity,
            'rarity': self.rarity
        }
    
    @classmethod
    def from_dict(cls, data):
        """사전 형태에서 아이템 객체 생성"""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            type=data.get('type', '일반'),
            consumable=data.get('consumable', False),
            durability=data.get('durability', None),
            max_durability=data.get('max_durability', None),
            quantity=data.get('quantity', 1),
            rarity=data.get('rarity', '일반')
        )
    
    def use(self):
        """아이템 사용"""
        if self.consumable:
            if self.quantity > 1:
                self.quantity -= 1
                return f"{self.name}을(를) 사용했습니다. 남은 수량: {self.quantity}"
            else:
                return f"{self.name}을(를) 사용했습니다. 모두 소진되었습니다."
        elif self.durability is not None:
            self.durability -= 1
            if self.durability <= 0:
                return f"{self.name}의 내구도가 다 되어 사용할 수 없게 되었습니다."
            else:
                return f"{self.name}을(를) 사용했습니다. 남은 내구도: {self.durability}/{self.max_durability}"
        else:
            return f"{self.name}을(를) 사용했습니다."
    
    def get_icon(self):
        """아이템 유형에 따른 아이콘 반환"""
        icons = {
            "무기": "⚔️",
            "방어구": "🛡️",
            "소비품": "🧪",
            "도구": "🔧",
            "마법": "✨",
            "기술": "🔌",
            "일반": "📦"
        }
        return icons.get(self.type, "📦")
    
    def get_rarity_color(self):
        """아이템 희귀도에 따른 색상 코드 반환"""
        colors = {
            "일반": "#AAAAAA",  # 회색
            "고급": "#4CAF50",  # 녹색
            "희귀": "#2196F3",  # 파란색
            "영웅": "#9C27B0",  # 보라색
            "전설": "#FFC107"   # 노란색
        }
        return colors.get(self.rarity, "#AAAAAA")
    
    def get_durability_percentage(self):
        """내구도 백분율 계산"""
        if self.durability is None or self.max_durability is None or self.max_durability <= 0:
            return 100
        return (self.durability / self.max_durability) * 100


def initialize_inventory(theme):
    """테마별 기본 인벤토리 초기화 - 개선된 버전"""
    inventory = []
    
    if theme == 'fantasy':
        inventory = [
            Item("기본 의류", "일반적인 모험가 복장입니다.", type="방어구", consumable=False),
            Item("여행용 가방", "다양한 물건을 담을 수 있는 가방입니다.", type="도구", consumable=False),
            Item("횃불", "어두운 곳을 밝힐 수 있습니다. 약 1시간 정도 사용 가능합니다.", type="소비품", consumable=True, quantity=3),
            Item("단검", "기본적인 근접 무기입니다.", type="무기", consumable=False, durability=20, max_durability=20),
            Item("물통", "물을 담아 갈 수 있습니다.", type="도구", consumable=False),
            Item("식량", "하루치 식량입니다.", type="소비품", consumable=True, quantity=5),
            Item("치유 물약", "체력을 회복시켜주는 물약입니다.", type="소비품", consumable=True, quantity=2, rarity="고급")
        ]
    elif theme == 'sci-fi':
        inventory = [
            Item("기본 의류", "표준 우주 여행자 복장입니다.", type="방어구", consumable=False),
            Item("휴대용 컴퓨터", "간단한 정보 검색과 해킹에 사용할 수 있습니다.", type="도구", consumable=False, durability=30, max_durability=30),
            Item("에너지 셀", "장비 작동에 필요한 에너지 셀입니다.", type="소비품", consumable=True, quantity=3),
            Item("레이저 포인터", "기본적인 레이저 도구입니다.", type="도구", consumable=False, durability=15, max_durability=15),
            Item("통신 장치", "다른 사람과 통신할 수 있습니다.", type="도구", consumable=False, durability=25, max_durability=25),
            Item("비상 식량", "우주 여행용 압축 식량입니다.", type="소비품", consumable=True, quantity=5),
            Item("의료 키트", "부상을 치료할 수 있는 기본 의료 키트입니다.", type="소비품", consumable=True, quantity=2, rarity="고급")
        ]
    else:  # dystopia
        inventory = [
            Item("작업용 의류", "튼튼하고 방호력이 있는 작업복입니다.", type="방어구", consumable=False, durability=15, max_durability=15),
            Item("가스 마스크", "유해 가스를 걸러냅니다.", type="방어구", consumable=False, durability=20, max_durability=20),
            Item("필터", "가스 마스크에 사용하는 필터입니다.", type="소비품", consumable=True, quantity=3),
            Item("생존 나이프", "다용도 생존 도구입니다.", type="무기", consumable=False, durability=25, max_durability=25),
            Item("정수 알약", "오염된 물을 정화할 수 있습니다.", type="소비품", consumable=True, quantity=5),
            Item("식량 배급 카드", "배급소에서 식량을 받을 수 있는 카드입니다.", type="도구", consumable=False),
            Item("응급 주사기", "위급 상황에서 생명 유지에 도움이 됩니다.", type="소비품", consumable=True, quantity=1, rarity="희귀")
        ]
    
    return inventory
# 인벤토리 표시 함수
def display_inventory(inventory):
    """인벤토리 아이템을 시각적으로 표시하는 함수 - 개선된 버전"""
    # 인벤토리가 비어있는 경우 처리
    if not inventory:
        st.write("인벤토리가 비어있습니다.")
        return
    
    # 아이템 유형별 분류
    categorized_items = {
        "무기": [],
        "방어구": [],
        "소비품": [],
        "도구": [],
        "마법": [],
        "기술": [],
        "일반": []
    }
    
    # 아이템을 카테고리별로 분류
    for item in inventory:
        try:
            item_type = item.type if hasattr(item, 'type') else "일반"
            if item_type in categorized_items:
                categorized_items[item_type].append(item)
            else:
                categorized_items["일반"].append(item)
        except:
            # 문자열이나 다른 형태의 아이템은 일반으로 분류
            categorized_items["일반"].append(item)
    
    # 카테고리별로 아이템 표시
    for category, items in categorized_items.items():
        if items:  # 해당 카테고리에 아이템이 있는 경우에만 표시
            # 카테고리 아이콘 선택
            category_icons = {
                "무기": "⚔️",
                "방어구": "🛡️",
                "소비품": "🧪",
                "도구": "🔧",
                "마법": "✨",
                "기술": "🔌",
                "일반": "📦"
            }
            category_icon = category_icons.get(category, "📦")
            
            st.write(f"{category_icon} **{category}**")
            
            # 카테고리 내 아이템 표시 - 간소화된 버전
            for item in items:
                try:
                    # 아이템 정보 안전하게 추출
                    if hasattr(item, 'name'):
                        item_name = item.name
                        item_desc = getattr(item, 'description', '설명 없음')
                        item_quantity = getattr(item, 'quantity', 1)
                        
                        # 아이콘 가져오기
                        icon = getattr(item, 'get_icon', lambda: "📦")
                        if callable(icon):
                            icon = icon()
                            
                        # 수량 표시
                        quantity_text = f" x{item_quantity}" if item_quantity > 1 else ""
                        
                        # 단순화된 표시 방식
                        st.markdown(f"{icon} **{item_name}**{quantity_text} - {item_desc}")
                    else:
                        # 문자열 아이템
                        st.markdown(f"📦 {str(item)}")
                except Exception as e:
                    st.markdown(f"📦 {str(item)} (표시 오류: {str(e)})")

def get_durability_color(percentage):
    """내구도 퍼센트에 따른 색상 반환"""
    if percentage > 66:
        return "#4CAF50"  # 녹색 (양호)
    elif percentage > 33:
        return "#FFC107"  # 노란색 (경고)
    else:
        return "#F44336"  # 빨간색 (위험)

# 스토리 응답에서 아이템 추출 함수 개선
def extract_items_from_story(story_text):
    """스토리 텍스트에서 획득한 아이템을 자동 추출"""
    prompt = f"""
    다음 TRPG 스토리 텍스트를 분석하여 플레이어가 획득했거나 발견한 모든 아이템을 추출해주세요.
    일반적인 배경 요소가 아닌, 플레이어가 실제로 소지하거나 사용할 수 있는 아이템만 추출하세요.
    특히 굵게 표시된 아이템(**, ** 사이의 텍스트)에 주목하세요.
    
    스토리 텍스트:
    {story_text}
    
    다음 JSON 형식으로 반환해주세요:
    [
      {{
        "name": "아이템 이름",
        "description": "아이템 설명 (없으면 빈 문자열)",
        "consumable": true/false (소비성 여부, 기본값 false),
        "durability": 숫자 (내구도, 없으면 null),
        "quantity": 숫자 (수량, 기본값 1)
      }},
      ...
    ]
    
    아이템이 없으면 빈 배열 []을 반환하세요.
    """
    
    try:
        response = generate_gemini_text(prompt, 300)
        
        # 굵게 표시된 텍스트를 우선 추출 (** 사이의 내용)
        import re
        import json
        
        # 굵게 표시된 아이템 이름 추출
        bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
        
        # 응답에서 JSON 구조 추출 시도
        try:
            # 응답 텍스트에서 JSON 부분만 추출 시도
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                items_data = json.loads(json_match.group(0))
            else:
                # 전체 응답을 JSON으로 파싱 시도
                items_data = json.loads(response)
        except:
            # JSON 파싱 실패 시 기본 아이템 생성
            items_data = []
            for item_name in bold_items:
                items_data.append({
                    "name": item_name,
                    "description": "발견한 아이템입니다.",
                    "consumable": False,
                    "durability": None,
                    "quantity": 1
                })
        
        # Item 객체 목록 생성
        items = []
        for item_data in items_data:
            items.append(Item.from_dict(item_data))
        
        # 굵게 표시된 아이템이 있지만 JSON에 포함되지 않은 경우 추가
        existing_names = [item.name for item in items]
        for bold_item in bold_items:
            if bold_item not in existing_names:
                items.append(Item(
                    name=bold_item,
                    description="발견한 아이템입니다.",
                    consumable=False,
                    quantity=1
                ))
        
        return items
    
    except Exception as e:
        st.error(f"아이템 추출 오류: {e}")
        # 오류 시 기본 아이템 생성
        items = []
        for item_name in bold_items:
            items.append(Item(
                name=item_name,
                description="발견한 아이템입니다.",
                consumable=False,
                quantity=1
            ))
        return items

# 사용된 아이템 추출 함수 개선
def extract_used_items_from_story(story_text, inventory):
    """스토리 텍스트에서 사용한 아이템 추출"""
    # 인벤토리 아이템 이름 목록 생성
    inventory_names = [item.name for item in inventory]
    
    prompt = f"""
    다음 TRPG 스토리 텍스트를 분석하여 플레이어가 사용한 아이템을 추출해주세요.
    특히 굵게 표시된 아이템(**, ** 사이의 텍스트)에 주목하세요.
    
    인벤토리에 있는 아이템: {', '.join(inventory_names)}
    
    스토리 텍스트:
    {story_text}
    
    다음 JSON 형식으로 반환해주세요:
    [
      {{
        "name": "아이템 이름",
        "quantity": 사용한 수량 (기본값 1)
      }},
      ...
    ]
    
    아무 아이템도 사용하지 않았다면 빈 배열 []을 반환하세요.
    """
    
    try:
        response = generate_gemini_text(prompt, 200)
        
        # 굵게 표시된 텍스트를 우선 추출 (** 사이의 내용)
        import re
        import json
        
        # 굵게 표시된 아이템 이름 추출
        bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
        
        # 응답에서 JSON 구조 추출 시도
        try:
            # 응답 텍스트에서 JSON 부분만 추출 시도
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                used_items_data = json.loads(json_match.group(0))
            else:
                # 전체 응답을 JSON으로 파싱 시도
                used_items_data = json.loads(response)
        except:
            # JSON 파싱 실패 시 기본 데이터 생성
            used_items_data = []
            for item_name in bold_items:
                if item_name in inventory_names:
                    used_items_data.append({
                        "name": item_name,
                        "quantity": 1
                    })
        
        # 사용된 아이템 데이터 필터링 (인벤토리에 있는 아이템만)
        filtered_items_data = []
        for item_data in used_items_data:
            if item_data["name"] in inventory_names:
                filtered_items_data.append(item_data)
        
        # 굵게 표시된 아이템이 있지만 JSON에 포함되지 않은 경우 추가
        existing_names = [item["name"] for item in filtered_items_data]
        for bold_item in bold_items:
            if bold_item in inventory_names and bold_item not in existing_names:
                filtered_items_data.append({
                    "name": bold_item,
                    "quantity": 1
                })
        
        return filtered_items_data
    
    except:
        # 오류 시 기본 데이터 생성
        used_items_data = []
        for item_name in bold_items:
            if item_name in inventory_names:
                used_items_data.append({
                    "name": item_name,
                    "quantity": 1
                })
        return used_items_data

# 인벤토리 업데이트 함수
def update_inventory(action, item_data, inventory):
    """인벤토리 아이템 추가/제거/사용 - 개선된 버전"""
    if action == "add":
        # 새 아이템인 경우
        if isinstance(item_data, Item):
            item = item_data
        else:
            # 딕셔너리 형태로 전달된 경우
            if isinstance(item_data, dict):
                item = Item.from_dict(item_data)
            else:
                # 문자열인 경우
                item = Item(name=str(item_data), description="획득한 아이템입니다.")
        
        # 기존 아이템인지 확인
        for existing_item in inventory:
            if hasattr(existing_item, 'name') and existing_item.name == item.name:
                # 유형이 같은지 확인 (다른 유형이면 별도 아이템으로 처리)
                existing_type = getattr(existing_item, 'type', '일반')
                new_type = getattr(item, 'type', '일반')
                
                if existing_type == new_type:
                    # 수량 증가
                    existing_item.quantity += item.quantity
                    return f"**{item.name}** {item.quantity}개가 추가되었습니다. (총 {existing_item.quantity}개)"
        
        # 새 아이템 추가
        inventory.append(item)
        quantity_text = f" {item.quantity}개" if item.quantity > 1 else ""
        return f"새 아이템 **{item.name}**{quantity_text}을(를) 획득했습니다!"
    
    elif action == "use":
        # 아이템 사용 (소비성 아이템 소모 또는 내구도 감소)
        if isinstance(item_data, dict):
            item_name = item_data.get("name", "")
            quantity = item_data.get("quantity", 1)
        else:
            item_name = str(item_data)
            quantity = 1
        
        for i, item in enumerate(inventory):
            item_n = item.name if hasattr(item, 'name') else str(item)
            if item_n == item_name:
                # 소비성 아이템인지 확인
                if hasattr(item, 'consumable') and item.consumable:
                    # 소비성 아이템 수량 감소
                    if item.quantity <= quantity:
                        # 모두 소모
                        removed_item = inventory.pop(i)
                        return f"**{removed_item.name}**을(를) 모두 사용했습니다."
                    else:
                        # 일부 소모
                        item.quantity -= quantity
                        return f"**{item.name}** {quantity}개를 사용했습니다. (남은 수량: {item.quantity})"
                
                # 내구도 있는 아이템인지 확인
                elif hasattr(item, 'durability') and item.durability is not None:
                    # 내구도 감소
                    item.durability -= 1
                    if item.durability <= 0:
                        # 내구도 소진으로 파괴
                        removed_item = inventory.pop(i)
                        return f"**{removed_item.name}**의 내구도가 다 되어 사용할 수 없게 되었습니다."
                    else:
                        # 내구도 감소
                        max_durability = getattr(item, 'max_durability', item.durability)
                        return f"**{item.name}**의 내구도가 감소했습니다. (남은 내구도: {item.durability}/{max_durability})"
                else:
                    # 일반 아이템 사용 (변화 없음)
                    return f"**{item.name}**을(를) 사용했습니다."
        
        return f"**{item_name}**이(가) 인벤토리에 없습니다."
    
    elif action == "remove":
        # 아이템 제거
        if isinstance(item_data, dict):
            item_name = item_data.get("name", "")
        else:
            item_name = str(item_data)
        
        for i, item in enumerate(inventory):
            item_n = item.name if hasattr(item, 'name') else str(item)
            if item_n == item_name:
                removed_item = inventory.pop(i)
                item_name = removed_item.name if hasattr(removed_item, 'name') else str(removed_item)
                return f"**{item_name}**을(를) 인벤토리에서 제거했습니다."
        
        return f"**{item_name}**이(가) 인벤토리에 없습니다."
    
    return "아이템 작업에 실패했습니다."

def process_acquired_items():
    """스토리에서 획득한 아이템 처리 및 인벤토리 업데이트"""
    if not hasattr(st.session_state, 'acquired_items') or not st.session_state.acquired_items:
        return
    
    items_added = []
    
    # 획득한 아이템을 인벤토리에 추가
    for item in st.session_state.acquired_items:
        if isinstance(item, Item):
            # Item 객체인 경우
            item_name = item.name
            update_result = update_inventory("add", item, st.session_state.character['inventory'])
            items_added.append(item_name)
        else:
            # 단순 문자열인 경우
            item_name = item.strip()
            if item_name and item_name not in st.session_state.character['inventory']:
                st.session_state.character['inventory'].append(item_name)
                items_added.append(item_name)
    
    # 획득 알림 표시 설정
    if items_added:
        items_text = ", ".join(items_added)
        st.session_state.item_notification = f"🎁 획득한 아이템: {items_text}"
        st.session_state.show_item_notification = True
    
    # 처리 완료 후 상태 초기화
    st.session_state.acquired_items = []
    
# 아이템 처리 및 스토리 생성 함수 개선
def process_items_and_generate_story(action, dice_result, theme, location, character):
    """행동에 따른 아이템 처리 및 스토리 생성 - 개선된 버전"""
    # 아이템 관련 행동인지 확인
    item_acquisition = "[아이템 획득]" in action or "아이템" in action.lower() or "주워" in action or "발견" in action
    item_usage = "[아이템 사용]" in action or "사용" in action.lower()
    
    # 스토리 생성
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어의 행동 결과에 대한 스토리를 생성해주세요.

    ## 상황 정보
    - 테마: {theme}
    - 현재 위치: {location}
    - 플레이어 직업: {character['profession']}
    - 플레이어 종족: {character.get('race', '인간')}
    - 주사위 결과: {dice_result}
    
    ## 행동 및 판정 결과
    - 행동: {action}
    - 판정 성공 여부: {'성공' if dice_result >= 15 else '실패'}
    """
    
    # 아이템 관련 행동인 경우 추가 지시사항
    if item_acquisition:
        prompt += f"""
    ## 아이템 획득 지침
    - 플레이어가 획득할 수 있는 아이템을 생성하고, 해당 아이템을 굵게(**아이템명**) 표시해주세요.
    - 아이템에 대한 설명(용도, 품질, 특징)을 포함하세요.
    - 주사위 결과가 좋을수록 더 가치 있는 아이템을 획득하게 해주세요.
    - 소비성 아이템인 경우 수량을 명시하세요. (예: "**물약** 3개")
    - 장비형 아이템인 경우 내구도를 언급하세요. (예: "내구도가 높은 **검**")
    
    ## 아이템 희귀도 지침
    - 주사위 결과: {dice_result}
    - 10 이하: 일반 아이템 (허름한, 낡은, 기본적인)
    - 11-15: 고급 아이템 (좋은 품질의, 견고한, 정교한)
    - 16-20: 희귀 아이템 (희귀한, 특별한, 특화된)
    - 21-25: 영웅급 아이템 (강력한, 전설적인, 고대의)
    - 26 이상: 전설급 아이템 (신화적인, 불가능한, 시대를 초월한)
        """
    elif item_usage:
        # 인벤토리에서 아이템 이름 추출
        inventory_items = []
        for item in character['inventory']:
            if hasattr(item, 'name'):
                inventory_name = item.name
                item_type = getattr(item, 'type', '일반')
                item_consumable = getattr(item, 'consumable', False)
                inventory_items.append(f"{inventory_name} ({item_type}, {'소비성' if item_consumable else '장비'})")
            else:
                inventory_items.append(str(item))
        
        prompt += f"""
    ## 아이템 사용 지침
    - 플레이어가 사용할 아이템을 굵게(**아이템명**) 표시해주세요.
    - 사용 가능한 인벤토리 아이템: {', '.join(inventory_items)}
    - 아이템 사용의 효과를 자세히 설명해주세요.
    - 주사위 결과가 좋을수록 더 효과적으로 아이템을 사용하게 해주세요.
    - 소비성 아이템은 사용 후 소모됨을 설명하세요.
    - 장비형 아이템은 계속 사용 가능함을 설명하세요.
        """
    
    prompt += """
    ## 중요 지시사항
    1. 감각적 몰입을 위해 시각, 청각, 후각, 촉각 등 다양한 감각적 묘사를 포함해주세요.
    2. 캐릭터의 감정과 내면 상태를 반영해주세요.
    3. 행동 결과를 극적으로 표현하되, 성공과 실패에 따른 차별화된 결과를 묘사해주세요.
    4. 선택지나 다음 행동 제안을 포함하지 마세요.
    5. 모든 문장은 완결되어야 합니다. 중간에 끊기지 않도록 해주세요.
    6. '어떻게 할까요?', '무엇을 할까요?', '선택하세요' 등의 문구를 사용하지 마세요.
    7. 응답은 250단어 이내로 간결하게 작성해주세요.
    """
    
    # 스토리 생성
    story = generate_gemini_text(prompt, 350)
    
    # 아이템 처리
    notification = ""
    
    # 1. 아이템 획득 처리
    if item_acquisition and dice_result >= 10:  # 10 이상이면 아이템 획득 성공
        # 스토리에서 아이템 추출
        acquired_items = extract_items_from_story(story)
        
        # 인벤토리에 아이템 추가
        if acquired_items:
            notifications = []
            for item in acquired_items:
                result = update_inventory("add", item, character['inventory'])
                notifications.append(result)
            
            notification = "🎁 " + " / ".join(notifications)
    
    # 2. 아이템 사용 처리
    elif item_usage:
        # 스토리에서 사용된 아이템 추출
        used_items_data = extract_used_items_from_story(story, character['inventory'])
        
        # 인벤토리에서 아이템 사용/제거
        if used_items_data:
            notifications = []
            for item_data in used_items_data:
                result = update_inventory("use", item_data, character['inventory'])
                notifications.append(result)
            
            notification = "🔄 " + " / ".join(notifications)
    
    return story, notification

# 캐릭터 생성 시 인벤토리 초기화 통합
def initialize_character(profession, backstory, stats, theme):
    """캐릭터 초기화 및 인벤토리 설정"""
    # 아이템 객체 리스트로 인벤토리 초기화
    inventory = initialize_inventory(theme)
    
    character = {
        'profession': profession,
        'backstory': backstory,
        'stats': stats,
        'inventory': inventory,
        'special_trait': None
    }
    
    return character

# 왼쪽 패널에 캐릭터 정보 표시 함수
def display_character_panel(character, location):
    """캐릭터 정보를 왼쪽 패널에 표시"""
    st.markdown("<div class='character-panel'>", unsafe_allow_html=True)
    st.write(f"## {character['profession']}")
    
    # 능력치 표시
    st.write("### 능력치")
    for stat, value in character['stats'].items():
        # 직업 정보 가져오기
        prof = character['profession']
        color, description = get_stat_info(stat, value, prof)
        
        st.markdown(f"""
        <div class='stat-box' style="border-left: 4px solid {color};">
            <span class='stat-name'>{stat}</span>
            <span class='stat-value'>{value}</span>
            <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 2px;">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 인벤토리 표시 (개선된 버전)
    st.write("### 인벤토리")
    # 기존 인벤토리 표시 코드 대신 display_inventory 함수 호출
    display_inventory(character['inventory'])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 위치 정보
    st.markdown(f"""
    <div class='location-box' style='margin-bottom: 15px; padding: 12px; background-color: #2d3748; border-radius: 5px; text-align: center;'>
        <h3 style='margin: 0; color: #e0e0ff;'>현재 위치</h3>
        <div style='font-size: 1.2rem; font-weight: bold; margin-top: 8px;'>{location}</div>
    </div>
    """, unsafe_allow_html=True)
    
# 게임플레이 페이지에서 아이템 알림 표시
def display_item_notification(notification):
    """아이템 관련 알림 표시 - 더 눈에 띄게 개선"""
    if notification:
        # 아이템 이름 강조를 위한 정규식 처리
        import re
        # 아이템 이름을 추출하여 강조 처리
        highlighted_notification = notification
        item_names = re.findall(r'아이템: (.*?)(,|$|\))', notification)
        
        for item_name in item_names:
            # 아이템 이름에 강조 스타일 적용 (더 눈에 띄게 수정)
            highlighted_notification = highlighted_notification.replace(
                item_name[0], 
                f'<span style="color: #FFD700; font-weight: bold; background-color: rgba(255, 215, 0, 0.2); padding: 3px 6px; border-radius: 3px; box-shadow: 0 0 5px rgba(255, 215, 0, 0.3);">{item_name[0]}</span>'
            )
        
        # 획득/사용 키워드에 더 눈에 띄는 스타일 적용
        highlighted_notification = highlighted_notification.replace(
            "획득한 아이템", 
            '<span style="color: #4CAF50; font-weight: bold; background-color: rgba(76, 175, 80, 0.1); padding: 2px 5px; border-radius: 3px;">🆕 획득한 아이템</span>'
        ).replace(
            "사용한 아이템", 
            '<span style="color: #FF9800; font-weight: bold; background-color: rgba(255, 152, 0, 0.1); padding: 2px 5px; border-radius: 3px;">⚙️ 사용한 아이템</span>'
        )
        
        st.markdown(f"""
        <div class='item-notification' style="animation: pulse 2s infinite; background-color: #2a3549; padding: 18px; border-radius: 8px; margin: 18px 0; border-left: 8px solid #FFD700; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 15px;">🎁</div>
                <div style="font-size: 1.1rem;">{highlighted_notification}</div>
            </div>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
            50% {{ box-shadow: 0 0 10px 3px rgba(255, 215, 0, 0.2); transform: scale(1.01); }}
            100% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
        }}
        </style>
        """, unsafe_allow_html=True)

# 행동 처리 및 스토리 진행 개선 함수
def handle_action_and_story(action, dice_result, theme, location, character):
    """행동 처리 및 스토리 진행"""
    # 아이템 처리 및 스토리 생성
    story, notification = process_items_and_generate_story(
        action, dice_result, theme, location, character
    )
    
    # 스토리 로그에 추가
    if story and len(story) > 10:  # 유효한 응답인지 확인
        st.session_state.story_log.append(story)
    else:
        # 백업 응답 사용
        backup_response = f"당신은 {action}을(를) 시도했습니다. 주사위 결과 {dice_result}가 나왔습니다."
        st.session_state.story_log.append(backup_response)
    
    # 알림 저장
    if notification:
        st.session_state.item_notification = notification
        st.session_state.show_item_notification = True
    
    # 행동 단계 초기화
    st.session_state.action_phase = 'suggestions'
    st.session_state.suggestions_generated = False
    st.session_state.dice_rolled = False
    
    # 임시 상태 초기화
    for key in ['suggested_ability', 'dice_result', 'current_action']:
        if key in st.session_state:
            del st.session_state[key]
    
    return story, notification



def handle_ability_check(action_phase, current_action, character_info):
    """능력치 판정 과정을 처리하는 함수 - 완전히 새로 작성"""
    with st.spinner("주사위를 굴리고 있습니다..."):
        # 로딩 표시
        loading_placeholder = st.empty()
        loading_placeholder.info("주사위를 굴려 스토리의 진행을 판단하는 중... 잠시만 기다려주세요.")
    
    st.subheader("능력치 판정")
    
    # 행동 표시
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <h4 style='margin-top: 0; margin-bottom: 10px; color: #e0e0ff;'>선택한 행동:</h4>
        <p style='margin: 0;'>{current_action}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 마스터가 능력치와 난이도 제안
    if 'suggested_ability' not in st.session_state:
        with st.spinner("마스터가 판정 방식을 결정 중..."):
            # 행동 분석을 위한 프롬프트
            prompt = f"""
            당신은 TRPG 게임 마스터입니다. 플레이어의 다음 행동에 가장 적합한 능력치와 난이도를 결정해주세요.
            
            플레이어 행동: {current_action}
            플레이어 직업: {character_info['profession']}
            현재 위치: {st.session_state.current_location}
            
            다음 능력치 중 하나를 선택하세요:
            - STR (근력): 물리적 힘이 필요한 행동
            - INT (지능): 지식, 분석, 추론이 필요한 행동
            - DEX (민첩): 손재주, 반사신경, 정확성이 필요한 행동
            - CON (체력): 지구력, 내구성이 필요한 행동
            - WIS (지혜): 직관, 통찰력, 인식이 필요한 행동
            - CHA (매력): 설득, 위협, 속임수가 필요한 행동
            
            난이도는 다음 기준으로 설정하세요:
            - 쉬움(10): 일상적인 행동, 실패 가능성이 낮음
            - 보통(15): 약간의 전문성이 필요한 행동, 보통 수준의 도전
            - 어려움(20): 전문적 기술이 필요한 행동, 실패 가능성이 높음
            - 매우 어려움(25): 극도로 어려운 행동, 전문가도 실패할 확률이 높음
            - 거의 불가능(30): 역사적으로 몇 번 성공한 적 있는 수준의 행동
            
            다음 형식으로 응답해주세요:
            능력치: [능력치 코드]
            난이도: [숫자]
            이유: [간략한 설명]
            성공 결과: [성공했을 때 일어날 일에 대한 간략한 설명]
            실패 결과: [실패했을 때 일어날 일에 대한 간략한 설명]
            추천 주사위: [추천 주사위 표현식, 예: 1d20+능력치]
            """
            
            # 마스터의 판정 제안 생성
            response = generate_gemini_text(prompt, 300)
            
            # 응답에서 능력치와 난이도 추출
            ability_code = "STR"  # 기본값
            difficulty = 15  # 기본값
            reason = "이 행동에는 근력이 필요합니다."  # 기본값
            success_outcome = "행동에 성공합니다."  # 기본값
            failure_outcome = "행동에 실패합니다."  # 기본값
            recommended_dice = "1d20"  # 기본값
            
            for line in response.split('\n'):
                if '능력치:' in line.lower():
                    for code in ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']:
                        if code in line:
                            ability_code = code
                            break
                elif '난이도:' in line.lower():
                    try:
                        difficulty_str = line.split(':')[1].strip()
                        difficulty = int(''.join(filter(str.isdigit, difficulty_str)))
                        # 범위 제한
                        difficulty = max(5, min(30, difficulty))
                    except:
                        pass
                elif '이유:' in line.lower():
                    reason = line.split(':', 1)[1].strip()
                elif '성공 결과:' in line.lower():
                    success_outcome = line.split(':', 1)[1].strip()
                elif '실패 결과:' in line.lower():
                    failure_outcome = line.split(':', 1)[1].strip()
                elif '추천 주사위:' in line.lower():
                    recommended_dice = line.split(':', 1)[1].strip()
                    # 기본값이 없는 경우 기본값 설정
                    if not recommended_dice or 'd' not in recommended_dice.lower():
                        recommended_dice = "1d20"
            
            # 능력치 전체 이름 매핑
            ability_names = {
                'STR': '근력', 'INT': '지능', 'DEX': '민첩', 
                'CON': '체력', 'WIS': '지혜', 'CHA': '매력'
            }
            
            # 세션에 저장
            st.session_state.suggested_ability = {
                'code': ability_code,
                'name': ability_names.get(ability_code, ''),
                'difficulty': difficulty,
                'reason': reason,
                'success_outcome': success_outcome,
                'failure_outcome': failure_outcome,
                'recommended_dice': recommended_dice
            }
        
        st.rerun()
    
    # 마스터의 제안 표시 - 향상된 UI
    ability = st.session_state.suggested_ability
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
        <h4 style='margin-top: 0;'>마스터의 판정 제안</h4>
        <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #6b8afd;'>능력치</div>
                <div style='font-size: 1.2rem;'>{ability['code']} ({ability['name']})</div>
            </div>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #FFC107;'>난이도</div>
                <div style='font-size: 1.2rem;'>{ability['difficulty']}</div>
            </div>
        </div>
        <div style='margin-top: 10px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
            <div style='font-weight: bold; margin-bottom: 5px;'>이유</div>
            <div>{ability['reason']}</div>
        </div>
        <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
            <div style='flex: 1; min-width: 200px; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #4CAF50;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #4CAF50;'>성공 시</div>
                <div>{ability['success_outcome']}</div>
            </div>
            <div style='flex: 1; min-width: 200px; background-color: rgba(244, 67, 54, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #F44336;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #F44336;'>실패 시</div>
                <div>{ability['failure_outcome']}</div>
            </div>
        </div>
        <div style='margin-top: 10px; text-align: center; font-size: 0.9rem; color: #aaaaaa;'>
            추천 주사위: {ability['recommended_dice']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 주사위 굴리기 자동 실행
    if not st.session_state.get('dice_rolled', False):
        # 주사위 애니메이션을 위한 플레이스홀더
        dice_placeholder = st.empty()
        
        # 주사위 표현식 결정
        dice_expression = ability.get('recommended_dice', "1d20")
        
        # 능력치 수정자 적용 (표현식에 이미 능력치가 포함되어 있지 않은 경우)
        ability_code = ability['code']
        ability_value = character_info['stats'][ability_code]
        
        if "+" not in dice_expression and "-" not in dice_expression:
            # 능력치 수정자 적용
            dice_expression = f"{dice_expression}+{ability_value}"
        
        with st.spinner("주사위 굴리는 중..."):
            # 주사위 굴리기 애니메이션 및 결과 표시
            dice_result = display_dice_animation(dice_placeholder, dice_expression, 1.0)
            
            st.session_state.dice_rolled = True
            st.session_state.dice_result = dice_result
    else:
        # 이미 굴린 주사위 결과 표시
        dice_placeholder = st.empty()
        dice_result = st.session_state.dice_result
        
        # 주사위 결과 재표시 로직...
        
    # 판정 결과 계산
    difficulty = ability['difficulty']
    success = dice_result['total'] >= difficulty
    
    # 결과 표시 (더 풍부하게 개선)
    result_color = "#1e3a23" if success else "#3a1e1e"
    result_border = "#4CAF50" if success else "#F44336"
    result_text = "성공" if success else "실패"
    outcome_text = ability['success_outcome'] if success else ability['failure_outcome']
    
    st.markdown(f"""
    <div style='background-color: {result_color}; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid {result_border};'>
        <h3 style='margin-top: 0;'>판정 결과: <span style='color: {result_border};'>{result_text}</span></h3>
        <div style='display: flex; align-items: center; margin: 10px 0;'>
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; text-align: center; margin-right: 10px;'>
                <span style='font-size: 0.8rem;'>주사위 + 능력치</span>
                <div style='font-size: 1.2rem; font-weight: bold;'>{dice_result['total']}</div>
            </div>
            <div style='font-size: 1.5rem; margin: 0 10px;'>VS</div>
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; text-align: center;'>
                <span style='font-size: 0.8rem;'>난이도</span>
                <div style='font-size: 1.2rem; font-weight: bold;'>{difficulty}</div>
            </div>
        </div>
        <div style='background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; margin-top: 10px;'>
            <p><strong>결과:</strong> {outcome_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 스토리 진행 버튼 - 더 매력적인 UI
    if st.button("스토리 진행", key="continue_story_button", use_container_width=True):
        handle_story_progression(current_action, dice_result['total'], success, ability['code'], dice_result['total'], difficulty)
        
    return success, dice_result['total'], ability['code'], dice_result['total'], difficulty


def handle_story_progression(action, dice_result, success, ability, total, difficulty):
    """주사위 결과에 따른 스토리 진행을 처리하는 함수 - 개선된 버전"""
    with st.spinner("마스터가 결과를 계산 중..."):
        # 로딩 표시
        loading_placeholder = st.empty()
        loading_placeholder.info("마스터가 스토리를 생성하는 중... 잠시만 기다려주세요.")
        
        # 능력치 판정 결과에 따른 스토리 응답 생성
        response = generate_story_response(
            action,
            dice_result,
            st.session_state.theme,
            st.session_state.current_location,
            st.session_state.character,
            success=success,
            ability=ability,
            total=total,
            difficulty=difficulty
        )
        
        # 스토리 로그에 추가
        if response and len(response) > 10:  # 유효한 응답인지 확인
            st.session_state.story_log.append(response)
        else:
            # 백업 응답 사용
            backup_response = f"{'성공적으로' if success else '아쉽게도'} {action}을(를) {'완료했습니다' if success else '실패했습니다'}. 다음 행동을 선택할 수 있습니다."
            st.session_state.story_log.append(backup_response)
        
        # 아이템 처리 및 스토리 생성
        story, notification = process_items_and_generate_story(
            action, 
            dice_result, 
            st.session_state.theme, 
            st.session_state.current_location, 
            st.session_state.character
        )
        
        # 아이템 알림이 있으면 표시 설정
        if notification:
            st.session_state.item_notification = notification
            st.session_state.show_item_notification = True
        
        # 다음 행동 제안으로 바로 전환 (인벤토리 관리 단계 제거)
        st.session_state.action_phase = 'suggestions'
        st.session_state.suggestions_generated = False
        
        # 임시 상태 초기화
        if 'suggested_ability' in st.session_state:
            del st.session_state.suggested_ability
        if 'dice_result' in st.session_state:
            del st.session_state.dice_result
        st.session_state.dice_rolled = False
        
        # 로딩 메시지 제거
        loading_placeholder.empty()
    
    st.rerun()
# 마스터(AI)가 행동 제안하는 함수 수정

def generate_action_suggestions(location, theme, context):
    """현재 상황에 맞는 행동 제안 생성 - 개선된 버전"""
    
    # 플레이어 인벤토리 확인
    inventory_items = []
    character_info = {}
    if 'character' in st.session_state:
        if 'inventory' in st.session_state.character:
            inventory_items = st.session_state.character['inventory']
        character_info = st.session_state.character
    
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어에게 현재 상황에서 취할 수 있는 5가지 행동을 제안해주세요.
    
    ## 상황 정보
    - 테마: {theme}
    - 현재 위치: {location}
    - 최근 상황: {context}
    - 플레이어 직업: {character_info.get('profession', '모험가')}
    - 플레이어 인벤토리: {', '.join([item.name if hasattr(item, 'name') else str(item) for item in inventory_items])}
    
    ## 제안 지침
    1. 각 행동은 매력적이고 흥미로운 결과로 이어질 수 있어야 합니다.
    2. 다양한 플레이 스타일(탐험, 전투, 사회적 상호작용, 수집 등)을 고려해주세요.
    3. 위험과 보상의 균형을 고려하세요.
    4. "어떻게 하시겠습니까?", "무엇을 선택하시겠습니까?" 등의 질문은 포함하지 마세요.
    5. 각 행동은 간결하고 명확한 서술로 작성하세요.
    
    반드시 다음 형식으로 5가지 행동을 제안해주세요:
    1. [일반] 일반적인 행동 제안 (환경 탐색 등)
    2. [위험] 위험하지만 보상이 큰 행동
    3. [상호작용] NPC나 환경과 상호작용하는 행동
    4. [아이템 획득] 새로운 아이템을 얻을 수 있는 행동 (어떤 아이템을 얻을 수 있는지 암시)
    5. [아이템 사용] 인벤토리의 아이템을 사용하는 행동 (사용할 아이템 명시)
    
    [아이템 사용]의 경우, 플레이어 인벤토리에 있는 아이템 중 하나를 사용하는 행동을 제안하세요.
    인벤토리가 비어있다면 다른 유형의 행동을 제안하세요.
    """
    
    response = generate_gemini_text(prompt, 400)
    
    # 응답 파싱
    suggestions = []
    temp_suggestions = []
    
    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 카테고리 태그가 있는 행동 찾기
        for tag in ['[일반]', '[위험]', '[상호작용]', '[아이템 획득]', '[아이템 사용]']:
            if tag in line:
                # 행에서 번호와 점(.)을 제거하여 깔끔하게 만듦
                temp_line = re.sub(r'^\d+\.\s*', '', line)
                temp_suggestions.append(temp_line)
                break
    
    # 카테고리별 기본 행동
    default_actions = {
        '[일반]': "주변을 자세히 살펴본다.",
        '[위험]': "수상한 소리가 나는 방향으로 탐색한다.",
        '[상호작용]': "근처에 있는 인물에게 말을 건다.",
        '[아이템 획득]': "근처에서 빛나는 물체를 발견하고 주워든다.",
        '[아이템 사용]': "가방에서 유용한 도구를 꺼내 사용한다."
    }
    
    # 각 카테고리별로 제안이 있는지 확인
    categories = ['[일반]', '[위험]', '[상호작용]', '[아이템 획득]', '[아이템 사용]']
    for i, category in enumerate(categories):
        found = False
        for suggestion in temp_suggestions:
            if category in suggestion:
                suggestions.append(f"{i+1}. {suggestion}")
                found = True
                break
        
        if not found:
            # 기본 행동 추가
            action = f"{i+1}. {category} {default_actions[category]}"
            suggestions.append(action)
    
    return suggestions[:5]  # 최대 5개까지 반환



# 개선된 주사위 굴리기 함수
# 주사위 굴리기 기본 함수
def roll_dice(dice_type=20, num_dice=1):
    """주사위 굴리기 함수 - 개선된 버전"""
    results = [random.randint(1, dice_type) for _ in range(num_dice)]
    return results

# 주사위 결과 계산 함수
def calculate_dice_result(dice_expression):
    """주사위 표현식 계산 (예: '2d6+3', '1d20-2', '3d8' 등)"""
    import re
    
    # 표현식 분석
    pattern = r'(\d+)d(\d+)([+-]\d+)?'
    match = re.match(pattern, dice_expression.lower().replace(' ', ''))
    
    if not match:
        raise ValueError(f"유효하지 않은 주사위 표현식: {dice_expression}")
    
    num_dice = int(match.group(1))
    dice_type = int(match.group(2))
    modifier = match.group(3)
    
    # 주사위 굴리기
    rolls = roll_dice(dice_type, num_dice)
    
    # 보정값 적용
    total = sum(rolls)
    modifier_value = 0
    
    if modifier:
        modifier_value = int(modifier)
        total += modifier_value
    
    return {
        'rolls': rolls,
        'total': total,
        'modifier': modifier_value,
        'num_dice': num_dice,
        'dice_type': dice_type
    }

def handle_action_phase():
    """행동 선택 및 처리 부분을 관리하는 함수 - 개선된 버전"""
    # 행동 단계 관리
    action_phase = st.session_state.get('action_phase', 'suggestions')
    
    # 1. 이동 처리
    if action_phase == "moving":
        with st.spinner(f"{st.session_state.move_destination}(으)로 이동 중..."):
            # 로딩 표시
            loading_placeholder = st.empty()
            loading_placeholder.info(f"{st.session_state.move_destination}(으)로 이동하는 중... 잠시만 기다려주세요.")
            
            # 이동 스토리 생성
            movement_story = generate_movement_story(
                st.session_state.current_location,
                st.session_state.move_destination,
                st.session_state.theme
            )
            
            # 스토리 로그에 추가
            st.session_state.story_log.append(movement_story)
            
            # 현재 위치 업데이트
            st.session_state.current_location = st.session_state.move_destination
            
            # 이동 상태 초기화
            st.session_state.move_destination = ""
            st.session_state.action_phase = 'suggestions'
            st.session_state.suggestions_generated = False
            
            # 로딩 메시지 제거
            loading_placeholder.empty()
        
        st.rerun()
    
    # 2. 능력치 판정 단계
    elif action_phase == "ability_check":
        st.subheader("능력치 판정")
        
        # 행동 표시 - 가독성 개선
        st.info(f"선택한 행동: {st.session_state.current_action}")
        
        # 마스터가 능력치와 난이도 제안
        if 'suggested_ability' not in st.session_state:
            with st.spinner("마스터가 판정 방식을 결정 중..."):
                # 로딩 표시
                loading_placeholder = st.empty()
                loading_placeholder.info("마스터가 판정 방식을 결정하는 중... 잠시만 기다려주세요.")
                
                # 행동 분석을 위한 프롬프트
                prompt = f"""
                당신은 TRPG 게임 마스터입니다. 플레이어의 다음 행동에 가장 적합한 능력치와 난이도를 결정해주세요.
                
                플레이어 행동: {st.session_state.current_action}
                플레이어 직업: {st.session_state.character['profession']}
                현재 위치: {st.session_state.current_location}
                
                다음 능력치 중 하나를 선택하세요:
                - STR (근력): 물리적 힘이 필요한 행동
                - INT (지능): 지식, 분석, 추론이 필요한 행동
                - DEX (민첩): 손재주, 반사신경, 정확성이 필요한 행동
                - CON (체력): 지구력, 내구성이 필요한 행동
                - WIS (지혜): 직관, 통찰력, 인식이 필요한 행동
                - CHA (매력): 설득, 위협, 속임수가 필요한 행동
                
                난이도는 다음 기준으로 설정하세요:
                - 쉬움(10): 일상적인 행동, 실패 가능성이 낮음
                - 보통(15): 약간의 전문성이 필요한 행동, 보통 수준의 도전
                - 어려움(20): 전문적 기술이 필요한 행동, 실패 가능성이 높음
                - 매우 어려움(25): 극도로 어려운 행동, 전문가도 실패할 확률이 높음
                - 거의 불가능(30): 역사적으로 몇 번 성공한 적 있는 수준의 행동
                
                다음 형식으로 응답해주세요:
                능력치: [능력치 코드]
                난이도: [숫자]
                이유: [간략한 설명]
                성공 결과: [성공했을 때 일어날 일에 대한 간략한 설명]
                실패 결과: [실패했을 때 일어날 일에 대한 간략한 설명]
                """
                
                # 마스터의 판정 제안 생성
                response = generate_gemini_text(prompt, 250)
                
                # 응답에서 능력치와 난이도 추출
                ability_code = "STR"  # 기본값
                difficulty = 15  # 기본값
                reason = "이 행동에는 근력이 필요합니다."  # 기본값
                success_outcome = "행동에 성공합니다."  # 기본값
                failure_outcome = "행동에 실패합니다."  # 기본값
                
                for line in response.split('\n'):
                    if '능력치:' in line.lower():
                        for code in ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']:
                            if code in line:
                                ability_code = code
                                break
                    elif '난이도:' in line.lower():
                        try:
                            difficulty_str = line.split(':')[1].strip()
                            difficulty = int(''.join(filter(str.isdigit, difficulty_str)))
                            # 범위 제한
                            difficulty = max(5, min(30, difficulty))
                        except:
                            pass
                    elif '이유:' in line.lower():
                        reason = line.split(':')[1].strip()
                    elif '성공 결과:' in line.lower():
                        success_outcome = line.split(':', 1)[1].strip()
                    elif '실패 결과:' in line.lower():
                        failure_outcome = line.split(':', 1)[1].strip()
                
                # 능력치 전체 이름 매핑
                ability_names = {
                    'STR': '근력', 'INT': '지능', 'DEX': '민첩', 
                    'CON': '체력', 'WIS': '지혜', 'CHA': '매력'
                }
                
                # 세션에 저장
                st.session_state.suggested_ability = {
                    'code': ability_code,
                    'name': ability_names.get(ability_code, ''),
                    'difficulty': difficulty,
                    'reason': reason,
                    'success_outcome': success_outcome,
                    'failure_outcome': failure_outcome
                }
                
                # 로딩 메시지 제거
                loading_placeholder.empty()
            
            st.rerun()
        
        # 마스터의 제안 표시 - 간소화된 UI
        ability = st.session_state.suggested_ability
        
        # 레이아웃 분리
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**사용 능력치:** {ability['code']} ({ability['name']})")
            st.write(f"**난이도:** {ability['difficulty']}")
        with col2:
            st.write(f"**이유:** {ability['reason']}")
        
        # 성공/실패 결과 표시
        st.success(f"**성공 시:** {ability['success_outcome']}")
        st.error(f"**실패 시:** {ability['failure_outcome']}")
        
        # 주사위 굴리기 자동 실행
        if not st.session_state.get('dice_rolled', False):
            # 주사위 애니메이션을 위한 플레이스홀더
            dice_placeholder = st.empty()
            
            with st.spinner("주사위 굴리는 중..."):
                # 주사위 굴리기
                dice_result = random.randint(1, 20)
                dice_placeholder.markdown(f"<div class='dice-result'>🎲 {dice_result}</div>", unsafe_allow_html=True)
                
                st.session_state.dice_rolled = True
                st.session_state.dice_result = dice_result
        else:
            # 주사위 결과 표시
            dice_result = st.session_state.dice_result
            st.markdown(f"<div class='dice-result'>🎲 {dice_result}</div>", unsafe_allow_html=True)
        
        # 능력치 값 가져오기
        ability_code = st.session_state.suggested_ability['code']
        ability_value = st.session_state.character['stats'][ability_code]
        difficulty = st.session_state.suggested_ability['difficulty']
        
        # 판정 결과 계산
        total_result = dice_result + ability_value
        success = total_result >= difficulty
        
        # 결과 표시 (간소화된 버전)
        result_color = "green" if success else "red"
        result_text = "성공" if success else "실패"
        
        st.write(f"### 판정 결과: {result_text}")
        st.write(f"주사위 결과: {dice_result}")
        st.write(f"능력치 보너스: +{ability_value} ({ability_code})")
        st.write(f"총합: {total_result} vs 난이도: {difficulty}")
        
        # 결과 설명
        if success:
            st.success(ability['success_outcome'])
        else:
            st.error(ability['failure_outcome'])
        
        # 스토리 진행 버튼
        if st.button("스토리 진행", key="continue_story_button", use_container_width=True):
            handle_story_progression(st.session_state.current_action, dice_result, success, ability_code, total_result, difficulty)
            
    # 3. 행동 제안 및 선택 단계
    elif action_phase == 'suggestions':
        st.subheader("행동 선택")
        
        # 위치 이동 옵션
        if 'available_locations' in st.session_state and len(st.session_state.available_locations) > 1:
            with st.expander("다른 장소로 이동", expanded=False):
                st.write("이동할 장소를 선택하세요:")
                
                # 현재 위치를 제외한 장소 목록 생성
                other_locations = [loc for loc in st.session_state.available_locations 
                                  if loc != st.session_state.current_location]
                
                # 장소 버튼 표시
                location_cols = st.columns(2)
                for i, location in enumerate(other_locations):
                    with location_cols[i % 2]:
                        if st.button(f"{location}로 이동", key=f"move_to_{i}", use_container_width=True):
                            st.session_state.move_destination = location
                            st.session_state.action_phase = 'moving'
                            st.rerun()
        
        # 행동 제안 표시
        if st.session_state.get('suggestions_generated', False):
            # 행동 제안 표시 (간소화된 방식)
            st.write("### 제안된 행동")
            for i, action in enumerate(st.session_state.action_suggestions):
                # 행동 유형 아이콘 결정
                if "[아이템 획득]" in action:
                    icon = "🔍"
                elif "[아이템 사용]" in action:
                    icon = "🧰"
                elif "[위험]" in action:
                    icon = "⚠️"
                elif "[상호작용]" in action:
                    icon = "💬"
                else:  # [일반]
                    icon = "🔎"
                
                # 선택지 표시
                expander = st.expander(f"{icon} {action}")
                with expander:
                    if st.button(f"이 행동 선택", key=f"action_{i}", use_container_width=True):
                        st.session_state.current_action = action
                        st.session_state.action_phase = 'ability_check'
                        # 초기화
                        st.session_state.dice_rolled = False
                        if 'dice_result' in st.session_state:
                            del st.session_state.dice_result
                        if 'suggested_ability' in st.session_state:
                            del st.session_state.suggested_ability
                        st.rerun()
            
            # 직접 행동 입력 옵션
            st.markdown("---")
            st.write("### 직접 행동 입력")
            custom_action = st.text_input("행동 설명:", key="custom_action_input")
            if st.button("실행", key="custom_action_button") and custom_action:
                # 행동 선택 시 주사위 굴림 상태 초기화
                st.session_state.current_action = custom_action
                st.session_state.action_phase = 'ability_check'
                # 초기화
                st.session_state.dice_rolled = False
                if 'dice_result' in st.session_state:
                    del st.session_state.dice_result
                if 'suggested_ability' in st.session_state:
                    del st.session_state.suggested_ability
                st.rerun()
        
        # 행동 제안 생성
        else:
            with st.spinner("마스터가 행동을 제안 중..."):
                # 로딩 표시
                loading_placeholder = st.empty()
                loading_placeholder.info("마스터가 행동을 제안하는 중... 잠시만 기다려주세요.")
                
                if st.session_state.story_log:
                    last_entry = st.session_state.story_log[-1]
                else:
                    last_entry = "모험의 시작"
                
                st.session_state.action_suggestions = generate_action_suggestions(
                    st.session_state.current_location,
                    st.session_state.theme,
                    last_entry
                )
                st.session_state.suggestions_generated = True
                
                # 로딩 메시지 제거
                loading_placeholder.empty()
            
            st.rerun()

def master_answer_game_question(question, theme, location, world_description):
    """게임 중 질문에 마스터가 답변 - 개선된 버전"""
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어가 게임 중에 다음과 같은 질문을 했습니다:
    
    {question}
    
    ## 게임 정보
    세계 테마: {theme}
    현재 위치: {location}
    세계 설명: {world_description[:300]}...
    
    ## 응답 지침
    1. 게임의 흐름을 유지하되, 플레이어에게 유용한 정보를 제공하세요.
    2. 세계관의 신비함과 일관성을 유지하세요.
    3. 필요하다면 플레이어의 캐릭터가 알지 못하는 정보는 "소문에 따르면..." 또는 "전설에 의하면..."과 같은 형식으로 제공하세요.
    4. 직접적인 답변보다는 플레이어가 스스로 발견하고 탐험할 수 있는 힌트를 제공하세요.
    5. 150단어 이내로 답변하세요.
    6. 모든 문장은 완결된 형태로 작성하세요.
    """
    
    return generate_gemini_text(prompt, 400)

# 이동 스토리 생성 함수
def generate_movement_story(current_location, destination, theme):
    """장소 이동 시 스토리 생성 - 개선된 버전"""
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어가 {current_location}에서 {destination}으로 이동하려고 합니다.
    
    ## 이동 스토리 지침
    1. 이동 과정과 새로운 장소에 도착했을 때의 상황을 생생하게 묘사해주세요.
    2. 이동 중 발생하는 작은 사건이나 만남을 포함하세요.
    3. 출발지와 목적지의 대비되는 분위기나 환경적 차이를 강조하세요.
    4. 다양한 감각적 묘사(시각, 청각, 후각, 촉각)를 포함하세요.
    5. 도착 장소에서 플레이어가 볼 수 있는 주요 랜드마크나 특징적 요소를 설명하세요.
    6. 현지 주민이나 생물의 반응이나 활동을 포함하세요.
    
    ## 정보
    세계 테마: {theme}
    출발 위치: {current_location}
    목적지: {destination}
    
    약 200단어 내외로 작성해주세요.
    모든 문장은 완결된 형태로 작성하세요.
    """
    
    return generate_gemini_text(prompt, 500)

def get_theme_description(theme):
    """테마에 대한 상세 설명 제공"""
    theme_descriptions = {
        "fantasy": """
        <p><strong>판타지 세계</strong>는 마법, 신화적 생물, 영웅적 모험이 가득한 세계입니다.</p>
        <p>중세 시대를 연상시키는 배경에 마법과 신비로운 존재들이 공존하며, 
        고대의 유물, 잊혀진 주문서, 드래곤과 같은 전설적 생물들이 있습니다.</p>
        <p>당신은 이 세계에서 마법사, 전사, 도적, 성직자 등 다양한 직업을 가진 모험가가 될 수 있습니다.</p>
        """,
        
        "sci-fi": """
        <p><strong>SF(공상과학) 세계</strong>는 미래 기술, 우주 탐험, 외계 생명체가 존재하는 세계입니다.</p>
        <p>첨단 기술, 우주선, 인공지능, 외계 행성 등이 배경이 되며, 
        인류의 미래 또는 다른 행성계의 이야기를 다룹니다.</p>
        <p>당신은 우주 파일럿, 사이버 해커, 외계종족 전문가 등 미래 지향적인 직업을 가진 캐릭터가 될 수 있습니다.</p>
        """,
        
        "dystopia": """
        <p><strong>디스토피아 세계</strong>는 암울한 미래, 억압적인 사회 체제, 환경 재앙 이후의 세계를 그립니다.</p>
        <p>종종 파괴된 문명의 폐허, 독재 정권, 자원 부족, 계급 사회 등을 배경으로 하며, 
        생존과 자유를 위한 투쟁이 중심 주제입니다.</p>
        <p>당신은 저항군 요원, 밀수업자, 정보 브로커 등 어두운 세계에서 살아남기 위한 직업을 가진 캐릭터가 될 수 있습니다.</p>
        """
    }
    
    return theme_descriptions.get(theme, "")

def world_description_page():
    st.header("2️⃣ 세계관 설명")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 세계관 설명 표시 - 단락 구분 개선
    world_desc_paragraphs = st.session_state.world_description.split("\n\n")
    formatted_desc = ""
    for para in world_desc_paragraphs:
        formatted_desc += f"<p>{para}</p>\n"
    
    st.markdown(f"<div class='story-text'>{formatted_desc}</div>", unsafe_allow_html=True)
    
    # "다른 세계 탐험하기" 버튼 추가 - 새로운 기능
    if st.button("🌍 다른 세계 탐험하기", key="explore_other_world", use_container_width=True):
        # 세션 상태 초기화 (일부만)
        for key in ['theme', 'world_description', 'world_generated', 'world_accepted', 
                   'question_answers', 'question_count', 'current_location']:
            if key in st.session_state:
                del st.session_state[key]
        
        # 테마 선택 화면으로 돌아가기
        st.session_state.stage = 'theme_selection'
        st.session_state.master_message = "새로운 세계를 탐험해보세요!"
        st.rerun()
    
    # 탭 기반 UI로 변경 - 더 매끄러운 사용자 경험
    tabs = st.tabs(["세계관 확장", "질문하기", "탐험 시작"])
    
    # 세계관 확장 탭
    with tabs[0]:
        st.subheader("세계관 이어서 작성")
        
        # 설명 추가 - 가독성 개선
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>세계관을 더 풍부하게 만들어보세요. AI 마스터에게 특정 부분을 확장해달라고 요청하거나, 직접 내용을 추가할 수 있습니다.</p>
            <p>추가된 내용은 기존 세계관과 자연스럽게 통합되어 더 깊이 있는 세계를 만들어갑니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 직접 입력 옵션 추가
        expand_method = st.radio(
            "확장 방법 선택:",
            ["AI 마스터에게 맡기기", "직접 작성하기"],
            horizontal=True
        )
        
        # AI 확장 선택 시
        if expand_method == "AI 마스터에게 맡기기":
            # 확장할 주제 선택 (더 구체적인 세계관 생성 유도)
            expansion_topics = {
                "역사와 전설": "세계의 역사적 사건, 신화, 전설적 영웅 등에 대한 이야기를 확장합니다.",
                "마법/기술 체계": "세계의 마법 시스템이나 기술 체계의 작동 방식과 한계를 자세히 설명합니다.",
                "종족과 문화": "세계에 존재하는 다양한 종족들과 그들의 문화, 관습, 생활 방식을 확장합니다.",
                "정치 체계와 세력": "권력 구조, 주요 세력 간의 관계, 정치적 갈등 등을 더 자세히 설명합니다.",
                "지리와 환경": "세계의 지리적 특성, 주요 지역, 기후, 자연환경에 대해 확장합니다.",
                "현재 갈등과 위기": "세계에서 진행 중인 갈등, 위기, 중요한 문제에 대해 자세히 설명합니다."
            }
            
            topic_options = list(expansion_topics.keys())
            topic_descriptions = list(expansion_topics.values())
            
            # 설명과 함께 확장 주제 선택
            expansion_topic_idx = st.selectbox(
                "확장할 세계관 요소를 선택하세요:",
                range(len(topic_options)),
                format_func=lambda i: topic_options[i]
            )
            
            expansion_topic = topic_options[expansion_topic_idx]
            
            # 선택한 주제에 대한 설명 표시
            st.markdown(f"""
            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <p>{topic_descriptions[expansion_topic_idx]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 이전 세계관 설명의 마지막 부분만 표시
            last_paragraph = st.session_state.world_description.split("\n\n")[-1]
            
            # 확장 버튼 누르기 전과 후의 상태 관리
            if 'continuation_generated' not in st.session_state:
                st.session_state.continuation_generated = False
                
            if not st.session_state.continuation_generated:
                if st.button("세계관 확장하기", key="expand_world"):
                    with st.spinner("이어질 내용을 생성 중..."):
                        try:
                            continuation_prompt = f"""
                            당신은 TRPG 게임 마스터입니다. 다음 세계관 설명을 이어서 작성해주세요.
                            이전 세계관 내용을 기반으로 "{expansion_topic}" 측면을 더 상세히 확장해주세요.
                            
                            테마: {st.session_state.theme}
                            현재 세계관 설명의 일부:
                            {st.session_state.world_description[:500]}...
                            
                            ## 확장 지침:
                            1. 선택한 주제({expansion_topic})에 초점을 맞추어 세계관을 확장하세요.
                            2. 플레이어가 탐험하거나 상호작용할 수 있는 구체적인 요소를 추가하세요.
                            3. 이전 내용과 일관성을 유지하면서 세계를 더 풍부하게 만드세요.
                            4. 비밀, 갈등, 또는 미스터리 요소를 하나 이상 포함하세요.
                            5. 200-300단어 내외로 작성하세요.
                            6. 단락을 나누어 가독성을 높이세요.
                            
                            모든 문장은 완결된 형태로 작성하세요.
                            """
                            
                            # 로딩 표시 확실히 하기
                            loading_placeholder = st.empty()
                            loading_placeholder.info("AI 마스터가 세계관을 확장하고 있습니다... 잠시만 기다려주세요.")
                            
                            # 확장 내용 생성
                            st.session_state.continuation_text = generate_gemini_text(continuation_prompt, 500)
                            st.session_state.continuation_generated = True
                            
                            # 로딩 메시지 제거
                            loading_placeholder.empty()
                        except Exception as e:
                            st.error(f"내용 생성 중 오류 발생: {e}")
                            # 오류 발생 시 백업 응답
                            st.session_state.continuation_text = "이 세계는 더 많은 비밀과 모험으로 가득 차 있습니다. 숨겨진 장소와 만날 수 있는 흥미로운 캐릭터들이 여러분을 기다리고 있습니다."
                            st.session_state.continuation_generated = True
                    st.rerun()
                    
            # 생성된 내용이 있으면 표시
            if st.session_state.continuation_generated:
                # 사용성 개선: 생성된 내용과 어떻게 반영되는지 시각적으로 표시
                st.subheader("확장된 세계관 내용:")
                st.info("다음 내용이 세계관에 추가됩니다. '이 내용으로 적용하기'를 클릭하면 세계관에 반영됩니다.")
                
                # 단락 나누기 - 가독성 개선
                continuation_paragraphs = st.session_state.continuation_text.split("\n\n")
                formatted_continuation = ""
                for para in continuation_paragraphs:
                    formatted_continuation += f"<p>{para}</p>\n"
                
                st.markdown(f"<div class='story-text' style='border-left: 4px solid #4CAF50;'>{formatted_continuation}</div>", unsafe_allow_html=True)
                
                # 적용 버튼과 다시 생성 버튼 병렬 배치
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("이 내용으로 적용하기", key="apply_expansion"):
                        # 세계 설명에 추가
                        st.session_state.world_description += "\n\n## " + expansion_topic + "\n" + st.session_state.continuation_text
                        
                        # 상태 초기화
                        st.session_state.continuation_generated = False
                        if "continuation_text" in st.session_state:
                            del st.session_state.continuation_text
                        
                        st.session_state.master_message = "세계관이 더욱 풍부해졌습니다! 이 세계에 대해 더 궁금한 점이 있으신가요?"
                        st.success("세계관이 성공적으로 확장되었습니다!")
                        st.rerun()
                
                with col2:
                    if st.button("다시 생성하기", key="regenerate_expansion"):
                        # 내용 다시 생성하도록 상태 초기화
                        st.session_state.continuation_generated = False
                        if "continuation_text" in st.session_state:
                            del st.session_state.continuation_text
                        st.rerun()
        
        # 직접 작성 선택 시
        else:  # "직접 작성하기"
            st.write("세계관에 추가하고 싶은 내용을 직접 작성해보세요:")
            user_continuation = st.text_area("세계관 추가 내용:", height=200)
            
            # 사용성 개선: 무한 추가 방지를 위한 확인 메시지
            if user_continuation and st.button("내용 추가하기", key="add_user_content"):
                # 미리보기 표시
                st.subheader("추가될 내용:")
                st.info("다음 내용이 세계관에 추가됩니다. 내용이 올바른지 확인하세요.")
                
                # 단락 나누기 - 가독성 개선
                user_paragraphs = user_continuation.split("\n\n")
                formatted_user_content = ""
                for para in user_paragraphs:
                    formatted_user_content += f"<p>{para}</p>\n"
                
                st.markdown(f"<div class='story-text' style='border-left: 4px solid #4CAF50;'>{formatted_user_content}</div>", unsafe_allow_html=True)
                
                # 확인 후 추가 (한 번만 추가되도록 확인)
                confirm = st.checkbox("위 내용을 세계관에 추가하시겠습니까?", key="confirm_add_content")
                if confirm and st.button("확인 후 추가하기", key="confirm_add_user_content"):
                    # 작성한 내용 추가
                    st.session_state.world_description += "\n\n## 직접 추가한 세계관 내용\n" + user_continuation
                    st.session_state.master_message = "직접 작성하신 내용이 세계관에 추가되었습니다! 이 세계가 더욱 풍부해졌습니다."
                    st.success("세계관에 내용이 성공적으로 추가되었습니다!")
                    st.rerun()
    
    # 질문하기 탭 - 개선된 선택 시각화
    with tabs[1]:
        st.subheader("세계관에 대한 질문")
        
        # 설명 추가 - 가독성 개선
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>세계에 대해 궁금한 점을 마스터에게 질문해보세요. 세계의 역사, 문화, 종족, 마법/기술 체계 등에 대한 질문을 할 수 있습니다.</p>
            <p>마스터의 답변은 세계관에 추가되어 더 풍부한 배경을 만들어갑니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 질문 제안 목록
        suggested_questions = [
            "이 세계의 마법/기술 체계는 어떻게 작동하나요?",
            "가장 위험한 지역은 어디이며 어떤 위협이 있나요?",
            "주요 세력들 간의 관계는 어떻게 되나요?",
            "일반적인 사람들의 생활 방식은 어떠한가요?",
            "이 세계에서 가장 귀중한 자원은 무엇인가요?",
            "최근에 일어난 중요한 사건은 무엇인가요?",
            "전설적인 인물이나 영웅은 누구인가요?",
        ]
        
        # 질문 처리 상태 관리
        if 'question_processing' not in st.session_state:
            st.session_state.question_processing = False
        
        if 'selected_suggested_question' not in st.session_state:
            st.session_state.selected_suggested_question = None
            
        if 'world_questions_history' not in st.session_state:
            st.session_state.world_questions_history = []
        
        # 제안된 질문 표시 - 토글 방식으로 개선
        st.write("제안된 질문:")
        question_cols = st.columns(2)
        
        for i, q in enumerate(suggested_questions):
            with question_cols[i % 2]:
                # 토글 버튼으로 질문 선택
                is_selected = st.checkbox(q, key=f"toggle_q_{i}", value=(st.session_state.selected_suggested_question == q))
                
                if is_selected:
                    st.session_state.selected_suggested_question = q
                elif st.session_state.selected_suggested_question == q:
                    st.session_state.selected_suggested_question = None
        
        # 선택된 질문이 있으면 질문하기 버튼 표시
        if st.session_state.selected_suggested_question:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.success(f"'{st.session_state.selected_suggested_question}' 질문이 선택되었습니다.")
        
        # 직접 질문 입력 섹션
        st.markdown("<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid #3d4c63;'></div>", unsafe_allow_html=True)
        st.write("### 직접 질문 입력")
        
        # 기본값 설정 (선택된 질문이 있으면 해당 질문 표시)
        default_question = st.session_state.get('custom_question_value', st.session_state.get('selected_suggested_question', ''))
        
        # 폼 사용으로 무한 생성 방지
        with st.form(key="world_question_form"):
            custom_question = st.text_input("질문 내용:", value=default_question, key="custom_world_question")
            submit_question = st.form_submit_button("질문하기", use_container_width=True, disabled=st.session_state.question_processing)
        
        # 질문이 제출되었을 때
        if submit_question and (custom_question or st.session_state.selected_suggested_question):
            question_to_ask = custom_question or st.session_state.selected_suggested_question
            
            # 이미 처리 중이 아닐 때만 실행
            if not st.session_state.question_processing:
                st.session_state.question_processing = True
                
                # 응답 표시할 플레이스홀더 생성
                response_placeholder = st.empty()
                response_placeholder.info("마스터가 답변을 작성 중입니다... 잠시만 기다려주세요.")
                
                # 질문 처리 및 답변 생성
                try:
                    prompt = f"""
                    당신은 TRPG 마스터입니다. 플레이어가 당신이 만든 세계에 대해 질문했습니다.
                    세계관 설명: {st.session_state.world_description}
                    
                    플레이어의 질문: {question_to_ask}
                    
                    이 질문에 대한 답변을 세계관에 맞게 상세하게 제공해주세요. 
                    답변은 마크다운 형식으로 작성하고, 중요한 개념이나 용어는 **굵게** 표시해주세요.
                    """
                    
                    # 답변 생성
                    with st.spinner("마스터가 질문에 대한 답변을 생각하고 있습니다..."):
                        answer = generate_gemini_text(prompt, 800)
                    
                    # 질문과 답변을 세션 상태에 저장
                    qa_pair = {
                        "question": question_to_ask,
                        "answer": answer,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.world_questions_history.append(qa_pair)
                    
                    # 세계관에 질문과 답변 추가
                    st.session_state.world_description += f"\n\n## 질문: {question_to_ask}\n{answer}"
                    
                    # 단락 구분 적용
                    answer_paragraphs = answer.split("\n\n")
                    formatted_answer = ""
                    for para in answer_paragraphs:
                        formatted_answer += f"<p>{para}</p>\n"
                    
                    # 응답 표시 - 페이지 새로고침 없이 표시
                    response_placeholder.markdown(f"""
                    <div style='background-color: #2d3748; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
                        <div style='font-weight: bold; margin-bottom: 5px;'>질문: {question_to_ask}</div>
                        <div>{formatted_answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 상태 초기화
                    st.session_state.master_message = "질문에 답변했습니다. 더 궁금한 점이 있으신가요?"
                
                except Exception as e:
                    st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
                    response_placeholder.error("질문 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
                
                finally:
                    # 처리 완료 상태로 변경
                    st.session_state.question_processing = False
                    st.session_state.selected_suggested_question = None
                    st.session_state.custom_question_value = ''
        
        # 이전 질문 및 답변 표시
        if st.session_state.world_questions_history:
            st.markdown("<div style='margin-top: 30px; padding-top: 10px; border-top: 1px solid #3d4c63;'></div>", unsafe_allow_html=True)
            st.write("### 이전 질문 및 답변")
            
            for i, qa in enumerate(reversed(st.session_state.world_questions_history)):
                with st.expander(f"Q: {qa['question']} ({qa['timestamp']})"):
                    st.markdown(qa['answer'])
    # 탐험 시작 탭
    with tabs[2]:
        st.subheader("탐험 시작하기")
        
        # 설명 추가 - 가독성 개선
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>모험을 시작할 지역을 선택하고 캐릭터 생성으로 진행하세요.</p>
            <p>선택한 지역은 캐릭터가 모험을 시작하는 첫 장소가 됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 시작 지점 선택
        if 'available_locations' in st.session_state and st.session_state.available_locations:
            st.write("#### 시작 지점 선택")
            st.write("모험을 시작할 위치를 선택하세요:")
            
            # 사용성 개선: 선택된 위치를 표시
            selected_location = st.session_state.get('current_location', '')
            
            # 시작 지점 그리드 표시
            location_cols = st.columns(3)
            for i, location in enumerate(st.session_state.available_locations):
                with location_cols[i % 3]:
                    # 현재 선택된 위치인 경우 다른 스타일로 표시
                    if location == selected_location:
                        st.markdown(f"""
                        <div style='background-color: #4CAF50; color: white; padding: 10px; 
                                    border-radius: 5px; text-align: center; margin-bottom: 10px;'>
                            ✓ {location} (선택됨)
                        </div>
                        """, unsafe_allow_html=True)
                        # 선택 취소 버튼
                        if st.button("선택 취소", key=f"unselect_loc_{i}"):
                            st.session_state.current_location = ""
                            st.rerun()
                    else:
                        if st.button(location, key=f"start_loc_{i}", use_container_width=True):
                            st.session_state.current_location = location
                            st.session_state.master_message = f"{location}에서 모험을 시작합니다. 이제 캐릭터를 생성할 차례입니다."
                            st.rerun()
        
        # 캐릭터 생성으로 이동 버튼
        st.write("#### 캐릭터 생성")
        st.write("세계를 충분히 탐색했다면, 이제 당신의 캐릭터를 만들어 모험을 시작할 수 있습니다.")
        
        # 선택된 시작 위치 없으면 경고
        if not st.session_state.get('current_location'):
            st.warning("캐릭터 생성으로 진행하기 전에 시작 지점을 선택해주세요!")
            proceed_button = st.button("캐릭터 생성으로 진행", key="to_character_creation", 
                                     use_container_width=True, disabled=True)
        else:
            proceed_button = st.button("캐릭터 생성으로 진행", key="to_character_creation", 
                                     use_container_width=True)
            if proceed_button:
                st.session_state.stage = 'character_creation'
                st.session_state.master_message = "이제 이 세계에서 모험을 떠날 당신의 캐릭터를 만들어 볼까요?"
                st.rerun()
                
# 질문 처리 함수
def process_question(question):
    with st.spinner("마스터가 응답 중..."):
        answer = master_answer_question(
            question,
            st.session_state.world_description,
            st.session_state.theme
        )
        
        # 질문과 답변 저장
        if 'question_answers' not in st.session_state:
            st.session_state.question_answers = []
        
        st.session_state.question_answers.append({
            "question": question,
            "answer": answer
        })
        
        st.session_state.question_count = len(st.session_state.question_answers)
        st.session_state.question_submitted = True
        st.session_state.question_current = question
        st.session_state.answer_current = answer
    
    st.rerun()

def generate_races(theme):
    """테마에 따른 종족 목록 반환"""
    races = {
        'fantasy': ['인간', '엘프', '드워프', '하플링', '오크', '고블린', '드라코니안'],
        'sci-fi': ['인간', '안드로이드', '외계인 하이브리드', '변형 인류', '네뷸런', '크로노스피어', '우주 유목민'],
        'dystopia': ['인간', '변이체', '강화인류', '생체기계', '숙주', '정신감응자', '저항자']
    }
    return races.get(theme, ['인간', '비인간', '신비종족'])

# 개선된 능력치 주사위 굴리기 함수
# 개선된 주사위 굴리기 함수 (세션에서 사용)
def ability_roll_section_improved(ability_col):
    """능력치 주사위 굴리기 기능을 개선한 함수 - 다시 굴리기 한번만 가능"""
    with ability_col:
        # 주사위 굴리기 관련 상태 초기화
        if 'dice_rolled' not in st.session_state:
            st.session_state.dice_rolled = False
        
        if 'reroll_used' not in st.session_state:
            st.session_state.reroll_used = False
            
        # 주사위 굴리기 설명 추가
        st.markdown("""
        <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
            <p>능력치는 각각 3D6(6면체 주사위 3개) 방식으로 결정됩니다.</p>
            <p>각 능력치는 3~18 사이의 값을 가지며, 평균값은 10-11입니다.</p>
            <p>14 이상은 뛰어난 능력, 16 이상은 탁월한 능력입니다.</p>
            <p><strong>다시 굴리기는 1번만 가능합니다.</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 주사위 굴리기 버튼
        if not st.session_state.dice_rolled and st.button("주사위 굴리기", use_container_width=True, key="roll_ability_dice"):
            st.session_state.dice_rolled = True
            
            # 능력치 목록
            ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
            rolled_abilities = {}
            
            # 각 능력치별 주사위 굴리기 결과 애니메이션으로 표시
            ability_placeholders = {}
            for ability in ability_names:
                ability_placeholders[ability] = st.empty()
            
            # 순차적으로 각 능력치 굴리기
            for ability in ability_names:
                with st.spinner(f"{ability} 굴리는 중..."):
                    # 주사위 애니메이션 표시
                    dice_result = display_dice_animation(ability_placeholders[ability], "3d6", 0.5)
                    rolled_abilities[ability] = dice_result['total']
                    time.sleep(0.2)  # 약간의 딜레이
            
            # 세션에 저장
            st.session_state.rolled_abilities = rolled_abilities
            st.rerun()
        
        # 굴린 결과 표시
        if st.session_state.dice_rolled and 'rolled_abilities' in st.session_state:
            st.write("#### 주사위 결과:")
            cols = st.columns(3)
            i = 0
            
            # 직업 정보를 미리 가져옴
            prof = st.session_state.selected_profession if 'selected_profession' in st.session_state else ""
            
            # 직업별 중요 능력치 정보
            profession_key_stats = {
                '마법사': ['INT', 'WIS'], 
                '전사': ['STR', 'CON'], 
                '도적': ['DEX', 'CHA'],
                '성직자': ['WIS', 'CHA'],
                '음유시인': ['CHA', 'DEX'],
                '연금술사': ['INT', 'DEX'],
                '우주 파일럿': ['DEX', 'INT'],
                '사이버 해커': ['INT', 'DEX'],
                '외계종족 전문가': ['WIS', 'CHA'],
                '정보 브로커': ['INT', 'CHA'],
                '밀수업자': ['DEX', 'CHA'],
                '저항군 요원': ['DEX', 'CON']
            }
            
            # 직업에 중요한 능력치 강조
            key_stats = profession_key_stats.get(prof, [])
            
            # 능력치 총점 계산 (나중에 보여주기 위함)
            total_points = sum(st.session_state.rolled_abilities.values())
            
            # 결과를 정렬하여 먼저 중요 능력치를 표시
            sorted_abilities = sorted(
                st.session_state.rolled_abilities.items(),
                key=lambda x: (x[0] not in key_stats, key_stats.index(x[0]) if x[0] in key_stats else 999)
            )
            
            for ability, value in sorted_abilities:
                with cols[i % 3]:
                    # 직업에 중요한 능력치인지 확인
                    is_key_stat = ability in key_stats
                    
                    # 색상 및 설명 가져오기
                    color, description = get_stat_info(ability, value, prof)
                    
                    # 중요 능력치 강조 스타일을 HTML 문자열 내부에 직접 적용
                    # bar_width 계산
                    bar_width = min(100, (value / 18) * 100)
                    
                    # 전체 HTML을 하나의 st.markdown() 호출로 렌더링
                    stat_html = f"""
                    <div class='stat-box' style="border-left: 4px solid {color}; {("border: 2px solid gold; background-color: rgba(255, 215, 0, 0.1);" if is_key_stat else "")}">
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span class='stat-name'>{ability}{(" <span style='background-color: #FFD700; color: #000; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>" if is_key_stat else "")}</span>
                            <span class='stat-value'>{value}</span>
                        </div>
                        <div style='margin-top: 5px; background-color: #1e2636; height: 8px; border-radius: 4px;'>
                            <div style='background-color: {color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 5px;">{description}</div>
                    </div>
                    """
                    st.markdown(stat_html, unsafe_allow_html=True)
                i += 1            
            # 능력치 총점 표시
            avg_total = 63  # 3d6 6개의 평균
            
            # 총점 평가 (낮음, 평균, 높음)
            if total_points < avg_total - 5:
                total_rating = "낮음"
                total_color = "#F44336"  # 빨간색
            elif total_points > avg_total + 5:
                total_rating = "높음"
                total_color = "#4CAF50"  # 녹색
            else:
                total_rating = "평균"
                total_color = "#FFC107"  # 노란색
            
            st.markdown(f"""
            <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center;'>
                <div style='font-weight: bold;'>능력치 총점:</div>
                <div style='display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 5px;'>
                    <span style='color: {total_color}; font-size: 1.5rem; font-weight: bold;'>{total_points}</span>
                    <span style='background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
                </div>
                <div style='font-size: 0.8rem; margin-top: 5px;'>(평균 63, 70+ 우수, 80+ 탁월)</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 버튼 열 생성
            col1, col2 = st.columns(2)
            with col1:
                if st.button("이 능력치로 진행하기", use_container_width=True, key="use_these_stats"):
                    st.session_state.character['stats'] = st.session_state.rolled_abilities
                    st.session_state.character['profession'] = st.session_state.selected_profession
                    st.session_state.character['race'] = st.session_state.selected_race
                    st.session_state.character['backstory'] = st.session_state.selected_background
                    st.session_state.character_creation_step = 'review'
                    st.session_state.master_message = "좋습니다! 캐릭터가 거의 완성되었습니다. 최종 확인을 해 볼까요?"
                    
                    # 다시 굴리기 관련 상태 초기화
                    st.session_state.dice_rolled = False
                    st.session_state.reroll_used = False
                    st.rerun()
            
            with col2:
                # 다시 굴리기 버튼 - 한번만 사용 가능하도록 제한
                if st.button("다시 굴리기", 
                            use_container_width=True, 
                            key="reroll_ability_dice",
                            disabled=st.session_state.reroll_used):
                    if not st.session_state.reroll_used:
                        # 다시 굴리기 사용 표시
                        st.session_state.reroll_used = True
                        
                        # 능력치 목록
                        ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
                        rerolled_abilities = {}
                        
                        # 각 능력치별 재굴림 결과 표시
                        reroll_placeholders = {}
                        for ability in ability_names:
                            reroll_placeholders[ability] = st.empty()
                        
                        # 순차적으로 각 능력치 다시 굴리기
                        for ability in ability_names:
                            with st.spinner(f"{ability} 다시 굴리는 중..."):
                                # 다시 굴림 애니메이션 표시
                                dice_result = display_dice_animation(reroll_placeholders[ability], "3d6", 0.5)
                                rerolled_abilities[ability] = dice_result['total']
                                time.sleep(0.1)  # 약간의 딜레이
                        
                        # 결과 저장 및 상태 업데이트
                        st.session_state.rolled_abilities = rerolled_abilities
                        st.session_state.reroll_message = "다시 굴리기 기회를 사용했습니다."
                        st.rerun()
                
                # 다시 굴리기 사용 여부 표시
                if st.session_state.reroll_used:
                    st.info("다시 굴리기 기회를 이미 사용했습니다.")

def reset_game_session():
    """게임 세션을 완전히 초기화하고 첫 화면으로 돌아가는 함수"""
    # 세션 상태의 모든 키 리스트 가져오기
    all_keys = list(st.session_state.keys())
    
    # 'initialized'를 제외한 모든 키 삭제
    for key in all_keys:
        if key != 'initialized':
            if key in st.session_state:
                del st.session_state[key]
    
    # 기본 상태 다시 설정
    st.session_state.stage = 'theme_selection'
    st.session_state.master_message = "어서 오세요, 모험가님. 어떤 세계를 탐험하고 싶으신가요?"
    
    # 이 함수가 호출된 후에는 반드시 st.rerun()을 호출해야 함

def set_stage_to_character_creation():
    st.session_state.stage = 'character_creation'
    st.session_state.master_message = "이제 이 세계에서 모험을 떠날 당신의 캐릭터를 만들어 볼까요?"
    




def is_mobile():
    """현재 기기가 모바일인지 확인"""
    # 간단한 추정 - Streamlit에서 직접 기기 타입을 얻기 어려움
    # 실제로는 브라우저 window.innerWidth를 체크하는 JavaScript가 필요할 수 있음
    # 여기서는 세션 상태에 설정된 값을 사용
    return st.session_state.get('is_mobile', False)

# 개선된 반응형 레이아웃 - 모바일 지원
def setup_responsive_layout():
    """반응형 레이아웃 설정"""
    # 이 함수는 실제로는 JavaScript를 통해 화면 너비를 감지하고
    # 모바일 여부를 설정할 수 있지만, 여기서는 간단히 버튼으로 전환
    
    # 디스플레이 모드 토글 버튼
    display_mode = st.sidebar.radio(
        "디스플레이 모드:",
        ["데스크톱", "모바일"],
        horizontal=True
    )
    
    # 모바일 모드 설정
    st.session_state.is_mobile = (display_mode == "모바일")
    
    # 모바일 모드일 때 사이드바에 추가 메뉴
    if st.session_state.is_mobile:
        st.sidebar.markdown("### 모바일 네비게이션")
        
        # 게임 플레이 단계에서만 패널 선택 옵션 표시
        if st.session_state.get('stage') == 'game_play':
            panel_options = ["스토리", "캐릭터 정보", "게임 도구"]
            current_panel = st.session_state.get('mobile_panel', "스토리")
            
            selected_panel = st.sidebar.radio(
                "표시할 패널:",
                panel_options,
                index=panel_options.index(current_panel)
            )
            
            if selected_panel != current_panel:
                st.session_state.mobile_panel = selected_panel
                st.rerun()
                
def extract_background_tags(background_text):
    """배경 텍스트에서 태그를 추출하는 함수 (개선된 버전)"""
    import re
    tags = []
    keyword_map = {
        "영웅": "영웅적", "구원": "영웅적", "정의": "영웅적", 
        "비극": "비극적", "상실": "비극적", "슬픔": "비극적", "고통": "비극적",
        "신비": "신비로운", "마법": "신비로운", "초자연": "신비로운", 
        "학자": "학자", "연구": "학자", "지식": "학자", "서적": "학자",
        "범죄": "범죄자", "도둑": "범죄자", "불법": "범죄자", "암흑가": "범죄자",
        "전사": "전사", "전투": "전사", "군인": "전사", "검술": "전사",
        "귀족": "귀족", "왕족": "귀족", "부유": "귀족", "상류층": "귀족",
        "서민": "서민", "평민": "서민", "일반인": "서민", "농부": "서민",
        "이방인": "이방인", "외지인": "이방인", "여행자": "이방인", "이주민": "이방인",
        "운명": "운명적", "예언": "운명적", "선택받은": "운명적"
    }
    
    # 디버깅을 위한 출력
    print(f"분석할 배경 텍스트: {background_text[:100]}...")
    
    background_text_lower = background_text.lower()
    
    for keyword, tag in keyword_map.items():
        # 단어 경계를 확인하는 정규식 패턴
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, background_text_lower):
            print(f"키워드 '{keyword}' 발견 -> 태그 '{tag}' 추가")
            if tag not in tags:
                tags.append(tag)
    
    # 태그가 없으면 디버깅 메시지 출력
    if not tags:
        print("추출된 태그가 없습니다. 기본 태그 '신비로운'을 사용합니다.")
    
    # 최대 3개 태그 제한
    result_tags = tags[:3] if tags else ["신비로운"]  # 기본 태그 추가
    print(f"최종 추출된 태그: {result_tags}")
    return result_tags

def character_creation_page():
    st.header("2️⃣ 캐릭터 생성")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    if 'character_creation_step' not in st.session_state:
        st.session_state.character_creation_step = 'race'  # 이제 종족 선택이 첫 단계
    
    # 종족 선택 단계
    if st.session_state.character_creation_step == 'race':
        st.subheader("종족 선택")
        
        # 종족 선택 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>캐릭터의 종족은 당신의 모험에 큰 영향을 미칩니다. 각 종족은 고유한 특성과 문화적 배경을 가지고 있습니다.</p>
            <p>종족에 따라 특정 능력치에 보너스가 부여될 수 있으며, 스토리텔링에도 영향을 줍니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 종족 목록
        races = generate_races(st.session_state.theme)
        
        # 종족별 아이콘 매핑
        race_icons = {
            '인간': '👨‍🦰', '엘프': '🧝', '드워프': '🧔', '하플링': '🧒', '오크': '👹', 
            '고블린': '👺', '드라코니안': '🐉', '안드로이드': '🤖', '외계인 하이브리드': '👽',
            '변형 인류': '🧬', '네뷸런': '✨', '크로노스피어': '⏱️', '우주 유목민': '🚀',
            '변이체': '☢️', '강화인류': '🦾', '생체기계': '🔌', '숙주': '🦠',
            '정신감응자': '🔮', '저항자': '⚔️', '비인간': '❓', '신비종족': '🌟'
        }
        
        # 종족 능력치 보너스 매핑
        race_bonuses = {
            '인간': {'모든 능력치': '+1'},
            '엘프': {'DEX': '+2', 'INT': '+1'},
            '드워프': {'CON': '+2', 'STR': '+1'},
            '하플링': {'DEX': '+2', 'CHA': '+1'},
            '오크': {'STR': '+2', 'CON': '+1'},
            '고블린': {'DEX': '+2', 'INT': '+1'},
            '드라코니안': {'STR': '+2', 'CHA': '+1'},
            '안드로이드': {'INT': '+2', 'STR': '+1'},
            '외계인 하이브리드': {'WIS': '+2', 'CHA': '+1'},
            '변형 인류': {'DEX': '+2', 'CON': '+1'},
            '네뷸런': {'INT': '+2', 'WIS': '+1'},
            '크로노스피어': {'INT': '+2', 'DEX': '+1'},
            '우주 유목민': {'WIS': '+2', 'INT': '+1'},
            '변이체': {'CON': '+2', 'STR': '+1'},
            '강화인류': {'STR': '+2', 'INT': '+1'},
            '생체기계': {'CON': '+2', 'INT': '+1'},
            '숙주': {'CON': '+2', 'WIS': '+1'},
            '정신감응자': {'WIS': '+2', 'CHA': '+1'},
            '저항자': {'WIS': '+2', 'DEX': '+1'},
            '비인간': {'CHA': '+2', 'DEX': '+1'},
            '신비종족': {'WIS': '+2', 'CHA': '+1'}
        }
        
        # 종족별 특수 능력 매핑
        race_abilities = {
            '인간': '적응력: 모든 기술 판정에 +1 보너스',
            '엘프': '암시야: 어두운 곳에서도 시각적 판정에 불이익 없음',
            '드워프': '내구력: 독성 및 질병 저항에 +2 보너스',
            '하플링': '행운: 하루에 한 번 주사위를 다시 굴릴 수 있음',
            '오크': '위협: 협박 관련 판정에 +2 보너스',
            '고블린': '교활함: 함정 및 장치 관련 판정에 +2 보너스',
            '드라코니안': '용의 숨결: 하루에 한 번 약한 화염 공격 가능',
            '안드로이드': '기계 저항: 전기 및 해킹 공격에 +2 방어',
            '외계인 하이브리드': '텔레파시: 간단한 감정을 마음으로 전달 가능',
            '변형 인류': '환경 적응: 극단적 환경에서 생존 판정에 +2 보너스',
            '네뷸런': '에너지 조작: 작은 전자 장치를 맨손으로 작동 가능',
            '크로노스피어': '시간 감각: 선제 행동 판정에 +2 보너스',
            '우주 유목민': '우주 적응: 무중력 및 저산소 환경에서 유리함',
            '변이체': '돌연변이 능력: 스트레스 상황에서 무작위 능력 발현',
            '강화인류': '기계 장착: 특정 도구를 체내에 내장 가능',
            '생체기계': '자가 수리: 휴식 중 추가 체력 회복',
            '숙주': '공생체 감지: 숨겨진 생명체 감지에 +2 보너스',
            '정신감응자': '사고 읽기: 단순한 생각을 감지할 확률 25%',
            '저항자': '시스템 면역: 모든 정신 제어에 저항 가능',
            '비인간': '이질적 존재감: 처음 만나는 NPC에게 강한 인상 남김',
            '신비종족': '고대의 지식: 역사 및 마법 관련 지식에 +2 보너스'
        }
        
        # 종족 선택 버튼 표시 (개선된 카드 형식)
        race_cols = st.columns(3)
        for i, race in enumerate(races):
            with race_cols[i % 3]:
                icon = race_icons.get(race, '👤')  # 기본 아이콘
                bonus = race_bonuses.get(race, {'??': '+?'})  # 기본 보너스
                ability = race_abilities.get(race, '특수 능력 없음')  # 기본 특수 능력
                
                # 종족 카드 생성 (개선된 UI)
                st.markdown(f"""
                <div class='option-card' style='padding: 15px; position: relative;'>
                    <div style='position: absolute; top: 10px; right: 10px; font-size: 2rem;'>{icon}</div>
                    <h3 style='margin-bottom: 10px;'>{race}</h3>
                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                        <strong>능력치 보너스:</strong> <br>
                        {"<br>".join([f"{k}: {v}" for k, v in bonus.items()])}
                    </div>
                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                        <strong>특수 능력:</strong> <br>
                        {ability}
                    </div>
                """, unsafe_allow_html=True)
                
                # 종족별 간단한 설명
                race_descriptions = {
                    '인간': "적응력이 뛰어나고 다재다능한 종족",
                    '엘프': "장수하며 마법적 친화력과 우아함을 지님",
                    '드워프': "강인한 체력과 대장장이 기술을 가진 산악 거주민",
                    '하플링': "작지만 민첩하고 운이 좋은 종족",
                    '오크': "강력한 근력과 전투 기술을 지닌 전사 종족",
                    '고블린': "꾀가 많고 기계에 능통한 작은 종족",
                    '드라코니안': "용의 피를 이어받은 강력한 혼혈 종족",
                    '안드로이드': "인공지능과 합성 신체를 가진 인조 생명체",
                    '외계인 하이브리드': "인간과 외계 종족의 유전적 결합체",
                    '변형 인류': "유전적 개조를 통해 진화된 인류",
                    '네뷸런': "성운에서 태어난 에너지 기반 존재",
                    '크로노스피어': "시간 감각이 다른 차원의 존재",
                    '우주 유목민': "세대를 넘어 우주선에서 살아온 인류",
                    '변이체': "환경 오염으로 변이된 인류",
                    '강화인류': "기계적 향상을 받은 인류",
                    '생체기계': "기계와 유기체의 완전한 결합체",
                    '숙주': "외계 공생체와 결합한 인류",
                    '정신감응자': "초능력을 가진 인류의 새로운 진화",
                    '저항자': "통제 시스템에 영향받지 않는 희귀 유전자 보유자",
                    '비인간': "인간이 아닌 다양한 존재들",
                    '신비종족': "기원이 불분명한 신비로운 능력을 가진 종족"
                }
                
                if race in race_descriptions:
                    st.markdown(f"""
                    <div style='margin-top: 10px; font-size: 0.9rem; color: #aaaaaa;'>
                        {race_descriptions[race]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button(f"선택", key=f"race_{race}"):
                    st.session_state.selected_race = race
                    st.session_state.race_bonus = bonus
                    st.session_state.race_ability = ability
                    st.session_state.race_icon = icon
                    st.session_state.character_creation_step = 'profession'
                    st.session_state.master_message = f"{race} 종족을 선택하셨군요! 이제 당신의 직업을 선택해보세요."
                    st.rerun()
        
        # 직접 입력 옵션
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.write("### 다른 종족 직접 입력")
        st.write("원하는 종족이 목록에 없다면, 직접 입력할 수 있습니다.")
        custom_race = st.text_input("종족 이름:")
        custom_icon = st.selectbox("아이콘 선택:", ['👤', '🧙', '🧝', '🧟', '👻', '👽', '🤖', '🦊', '🐲', '🌟'])
        
        # 능력치 보너스 선택 (최대 2개)
        st.write("능력치 보너스 선택 (최대 2개):")
        bonus_cols = st.columns(3)
        
        all_stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        custom_bonuses = {}
        
        for i, stat in enumerate(all_stats):
            with bonus_cols[i % 3]:
                bonus_value = st.selectbox(f"{stat} 보너스:", ['+0', '+1', '+2'], key=f"custom_bonus_{stat}")
                if bonus_value != '+0':
                    custom_bonuses[stat] = bonus_value
        
        # 특수 능력 입력
        custom_ability = st.text_area("특수 능력 (선택사항):", 
                                      placeholder="예: 어둠 속에서도 잘 볼 수 있는 능력")
        
        if custom_race and st.button("이 종족으로 선택"):
            st.session_state.selected_race = custom_race
            st.session_state.race_bonus = custom_bonuses if custom_bonuses else {'없음': '+0'}
            st.session_state.race_ability = custom_ability if custom_ability else "특수 능력 없음"
            st.session_state.race_icon = custom_icon
            st.session_state.character_creation_step = 'profession'
            st.session_state.master_message = f"{custom_race} 종족을 선택하셨군요! 이제 당신의 직업을 선택해보세요."
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 직업 선택 단계
    elif st.session_state.character_creation_step == 'profession':
        st.subheader("직업 선택")
        
        # 직업 선택 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>직업은 캐릭터가 세계에서 수행하는 역할과 전문 기술을 결정합니다.</p>
            <p>각 직업마다 중요한 능력치가 다르며, 독특한 기술과 성장 경로를 가집니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 선택된 종족 표시 (개선된 UI)
        race_icon = st.session_state.get('race_icon', '👤')
        race_bonuses = st.session_state.get('race_bonus', {})
        race_ability = st.session_state.get('race_ability', "특수 능력 없음")
        
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 15px; display: flex; align-items: center;'>
            <div style='font-size: 2.5rem; margin-right: 15px;'>{race_icon}</div>
            <div style='flex-grow: 1;'>
                <h3 style='margin: 0; color: #4CAF50;'>선택한 종족: {st.session_state.selected_race}</h3>
                <div style='margin-top: 5px; font-size: 0.9rem;'>
                    <strong>능력치 보너스:</strong> {', '.join([f"{k} {v}" for k, v in race_bonuses.items()])}
                </div>
                <div style='margin-top: 5px; font-size: 0.9rem;'>
                    <strong>특수 능력:</strong> {race_ability}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 직업 선택 방식
        profession_method = st.radio(
            "직업 선택 방식:",
            ["기본 직업 선택", "직접 직업 만들기"],
            horizontal=True
        )
        
        if profession_method == "기본 직업 선택":
            # 직업 목록
            professions = generate_professions(st.session_state.theme)
            
            # 직업별 아이콘 매핑
            profession_icons = {
                # 판타지 직업
                '마법사': '🧙', '전사': '⚔️', '도적': '🗡️', '성직자': '✝️', 
                '음유시인': '🎭', '연금술사': '⚗️',
                # SF 직업
                '우주 파일럿': '🚀', '사이버 해커': '💻', '생체공학자': '🧬', 
                '보안 요원': '🛡️', '외계종족 전문가': '👽', '기계공학자': '⚙️',
                # 디스토피아 직업
                '정보 브로커': '📡', '밀수업자': '📦', '저항군 요원': '⚔️', 
                '엘리트 경비원': '👮', '스카운터': '🔭', '의료 기술자': '💉'
            }
            
            # 직업별 주요 능력치 매핑
            profession_stats = {
                # 판타지 직업
                '마법사': ['INT', 'WIS'], '전사': ['STR', 'CON'], '도적': ['DEX', 'CHA'],
                '성직자': ['WIS', 'CHA'], '음유시인': ['CHA', 'DEX'], '연금술사': ['INT', 'DEX'],
                # SF 직업
                '우주 파일럿': ['DEX', 'INT'], '사이버 해커': ['INT', 'DEX'], 
                '생체공학자': ['INT', 'WIS'], '보안 요원': ['STR', 'DEX'], 
                '외계종족 전문가': ['INT', 'CHA'], '기계공학자': ['INT', 'DEX'],
                # 디스토피아 직업
                '정보 브로커': ['INT', 'CHA'], '밀수업자': ['DEX', 'CHA'], 
                '저항군 요원': ['DEX', 'CON'], '엘리트 경비원': ['STR', 'CON'], 
                '스카운터': ['DEX', 'WIS'], '의료 기술자': ['INT', 'DEX']
            }
            
            # 직업별 시작 장비 및 특수 기술
            profession_equipment = {
                # 판타지 직업
                '마법사': ['마법서', '마법 지팡이', '마법 주머니', '초보자용 주문 2개'],
                '전사': ['검 또는 도끼', '갑옷', '방패', '생존 도구 세트'],
                '도적': ['단검 2개', '도둑 도구 세트', '후드 망토', '독약 제조 키트'],
                '성직자': ['신성한 상징', '치유 물약 3개', '의식용 로브', '기도서'],
                '음유시인': ['악기', '화려한 옷', '매력 향수', '이야기 모음집'],
                '연금술사': ['연금술 키트', '약초 가방', '실험 도구', '공식 노트'],
                # SF 직업
                '우주 파일럿': ['개인 통신기', '비상 우주복', '항법 장치', '우주선 접근 키'],
                '사이버 해커': ['고급 컴퓨터', '해킹 장치', '신경 연결 케이블', '데이터 칩'],
                '생체공학자': ['생체 스캐너', '미니 실험실', '표본 수집 키트', '의학 참고서'],
                '보안 요원': ['에너지 무기', '방어 슈트', '감시 장치', '신분 위조 키트'],
                '외계종족 전문가': ['번역기', '종족 백과사전', '접촉 프로토콜 가이드', '외계 유물'],
                '기계공학자': ['다용도 공구 세트', '소형 드론', '수리 매뉴얼', '예비 부품'],
                # 디스토피아 직업
                '정보 브로커': ['암호화된 단말기', '신원 위장 키트', '비밀 금고', '정보 데이터베이스'],
                '밀수업자': ['은닉 가방', '위조 서류', '지도 컬렉션', '거래 연락망'],
                '저항군 요원': ['숨겨진 무기', '위장 도구', '암호화 통신기', '안전가옥 접근권'],
                '엘리트 경비원': ['최신형 방호구', '감시 장비', '접근 배지', '진압 무기'],
                '스카운터': ['원거리 스캐너', '야간 투시경', '생존 키트', '지형 기록기'],
                '의료 기술자': ['응급 의료 키트', '진단 장비', '약물 합성기', '의학 데이터뱅크']
            }
            
            # 직업별 특수 기술
            profession_skills = {
                # 판타지 직업
                '마법사': '마법 감지: 주변의 마법적 현상을 감지할 수 있음',
                '전사': '전투 기술: 모든 무기 사용에 +1 보너스',
                '도적': '그림자 이동: 은신 및 잠입 판정에 +2 보너스',
                '성직자': '신성한 보호: 하루에 한 번 약한 치유 마법 사용 가능',
                '음유시인': '매혹: 설득 및 교섭 판정에 +2 보너스',
                '연금술사': '물약 식별: 알 수 없는 물약의 효과를 판별 가능',
                # SF 직업
                '우주 파일럿': '회피 기동: 위험한 상황에서의 회피 판정에 +2 보너스',
                '사이버 해커': '시스템 침투: 전자 장치 해킹 시도에 +2 보너스',
                '생체공학자': '생명체 분석: 생물학적 특성을 빠르게 파악 가능',
                '보안 요원': '위협 감지: 잠재적 위험을 사전에 감지할 확률 +25%',
                '외계종족 전문가': '외계어 이해: 처음 접하는 언어라도 기본 의사소통 가능',
                '기계공학자': '즉석 수리: 손상된 장비를 임시로 빠르게 수리 가능',
                # 디스토피아 직업
                '정보 브로커': '정보망: 지역 정보를 얻는 판정에 +2 보너스',
                '밀수업자': '은밀한 거래: 불법 물품 거래 및 운송에 +2 보너스',
                '저항군 요원': '생존 본능: 생명을 위협하는 상황에서 반사 판정 +2',
                '엘리트 경비원': '경계: 잠복 중 적 발견 확률 +25%',
                '스카운터': '지형 파악: 새로운 지역 탐색 시 +2 보너스',
                '의료 기술자': '응급 처치: 중상을 입은 대상을 안정시키는 능력'
            }
            
            # 직업 선택 버튼 표시 (개선된 카드 형식)
            profession_cols = st.columns(3)
            for i, profession in enumerate(professions):
                with profession_cols[i % 3]:
                    icon = profession_icons.get(profession, '👤')  # 기본 아이콘
                    key_stats = profession_stats.get(profession, ['??', '??'])  # 주요 능력치
                    equipment = profession_equipment.get(profession, ['기본 장비'])  # 시작 장비
                    skill = profession_skills.get(profession, '특수 기술 없음')  # 특수 기술
                    
                    # 직업 카드 생성 (개선된 UI)
                    st.markdown(f"""
                    <div class='option-card' style='padding: 15px; position: relative;'>
                        <div style='position: absolute; top: 10px; right: 10px; font-size: 2rem;'>{icon}</div>
                        <h3 style='margin-bottom: 10px;'>{profession}</h3>
                        <div style='margin-top: 10px; font-size: 0.9rem;'>
                            <strong>주요 능력치:</strong> {' & '.join(key_stats)}
                        </div>
                        <div style='margin-top: 10px; font-size: 0.9rem;'>
                            <strong>시작 장비:</strong>
                            <ul style='margin-top: 5px; padding-left: 20px; margin-bottom: 5px;'>
                                {"".join([f"<li>{item}</li>" for item in equipment[:3]])}
                                {"" if len(equipment) <= 3 else "<li>...</li>"}
                            </ul>
                        </div>
                        <div style='margin-top: 10px; font-size: 0.9rem;'>
                            <strong>특수 기술:</strong> <br>
                            {skill}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"선택", key=f"prof_{profession}"):
                        st.session_state.selected_profession = profession
                        st.session_state.profession_icon = icon
                        st.session_state.profession_stats = key_stats
                        st.session_state.profession_equipment = equipment
                        st.session_state.profession_skill = skill
                        
                        # 배경 옵션 생성 상태 확인
                        if not st.session_state.background_options_generated:
                            with st.spinner("캐릭터 배경 옵션을 생성 중..."):
                                st.session_state.character_backgrounds = generate_character_options(
                                    profession, st.session_state.theme
                                )
                                st.session_state.background_options_generated = True
                        
                        st.session_state.character_creation_step = 'background'
                        st.session_state.master_message = f"{profession} 직업을 선택하셨군요! 이제 캐릭터의 배경 이야기를 선택해보세요."
                        st.rerun()
        else:  # 직접 직업 만들기
            st.markdown("<div class='option-card'>", unsafe_allow_html=True)
            st.write("### 나만의 직업 만들기")
            st.write("세계관에 맞는 독특한 직업을 직접 만들어보세요")
            custom_profession = st.text_input("직업 이름:")
            custom_icon = st.selectbox("아이콘 선택:", ['🧙', '⚔️', '🗡️', '🧪', '📚', '🔮', '🎭', '⚗️', '🛡️', '🚀', '💻', '🧬', '👽', '⚙️', '📡', '📦', '💉', '🔭'])
            
            # 주요 능력치 선택 (최대 2개)
            st.write("주요 능력치 선택 (최대 2개):")
            stat_cols = st.columns(3)
            
            all_stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
            selected_stats = []
            
            for i, stat in enumerate(all_stats):
                with stat_cols[i % 3]:
                    if st.checkbox(f"{stat}", key=f"custom_prof_stat_{stat}"):
                        selected_stats.append(stat)
            
            # 3개 이상 선택 시 경고
            if len(selected_stats) > 2:
                st.warning("주요 능력치는 최대 2개까지만 선택할 수 있습니다. 처음 2개만 적용됩니다.")
                selected_stats = selected_stats[:2]
            elif len(selected_stats) == 0:
                st.info("주요 능력치를 1~2개 선택하세요.")
            
            # 시작 장비 입력
            st.write("시작 장비 (콤마로 구분):")
            equipment_input = st.text_area("예: 검, 방패, 물약 3개", height=100)
            
            # 특수 기술 입력
            special_skill = st.text_input("특수 기술 (예: 숨기: 은신 판정에 +2 보너스):")
            
            # 직업 설명
            profession_desc = st.text_area("직업 설명:", 
                                          placeholder="이 직업의 역할, 행동 방식, 세계관에서의 위치 등을 설명해주세요.",
                                          height=100)
            
            if st.button("이 직업으로 선택", use_container_width=True):
                if custom_profession and len(selected_stats) > 0 and special_skill:
                    # 사용자 정의 직업 정보 저장
                    st.session_state.selected_profession = custom_profession
                    st.session_state.profession_icon = custom_icon
                    st.session_state.profession_stats = selected_stats
                    
                    # 장비 파싱
                    equipment_list = [item.strip() for item in equipment_input.split(',') if item.strip()]
                    if not equipment_list:
                        equipment_list = ["기본 장비"]
                    st.session_state.profession_equipment = equipment_list
                    
                    st.session_state.profession_skill = special_skill
                    st.session_state.profession_description = profession_desc
                    
                    # 배경 옵션 생성 상태 확인
                    if not st.session_state.background_options_generated:
                        with st.spinner("캐릭터 배경 옵션을 생성 중..."):
                            st.session_state.character_backgrounds = generate_character_options(
                                custom_profession, st.session_state.theme
                            )
                            st.session_state.background_options_generated = True
                    
                    st.session_state.character_creation_step = 'background'
                    st.session_state.master_message = f"{custom_profession} 직업을 선택하셨군요! 이제 캐릭터의 배경 이야기를 선택해보세요."
                    st.rerun()
                else:
                    st.error("직업 이름, 최소 1개의 주요 능력치, 특수 기술은 필수 입력사항입니다.")
            st.markdown("</div>", unsafe_allow_html=True)
# 배경 선택 단계
    elif st.session_state.character_creation_step == 'background':
        st.subheader("캐릭터 배경 선택")
        
        # 배경 선택 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>캐릭터의 배경 스토리는 당신이 누구이고, 어떻게 모험을 시작하게 되었는지를 결정합니다.</p>
            <p>세계관 속에서 당신의 위치와 동기, 인간관계를 형성하는 중요한 요소입니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 선택된 종족과 직업 표시 (개선된 UI)
        race_icon = st.session_state.get('race_icon', '👤')
        profession_icon = st.session_state.get('profession_icon', '👤')
        key_stats = st.session_state.get('profession_stats', ['??', '??'])
        special_skill = st.session_state.get('profession_skill', '특수 기술 없음')
        
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 15px; display: flex; align-items: center;'>
            <div style='font-size: 2.5rem; margin-right: 15px;'>{race_icon}</div>
            <div style='flex-grow: 1;'>
                <h3 style='margin: 0; color: #4CAF50;'>선택한 종족: {st.session_state.selected_race}</h3>
                <div style='margin-top: 5px; font-size: 0.9rem;'>
                    <strong>특수 능력:</strong> {st.session_state.get('race_ability', '특수 능력 없음')}
                </div>
            </div>
            <div style='font-size: 2.5rem; margin: 0 15px;'>➕</div>
            <div style='font-size: 2.5rem; margin-right: 15px;'>{profession_icon}</div>
            <div style='flex-grow: 1;'>
                <h3 style='margin: 0; color: #4CAF50;'>선택한 직업: {st.session_state.selected_profession}</h3>
                <div style='margin-top: 5px; font-size: 0.9rem;'>
                    <strong>주요 능력치:</strong> {' & '.join(key_stats)}
                </div>
                <div style='margin-top: 5px; font-size: 0.9rem;'>
                    <strong>특수 기술:</strong> {special_skill}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 배경 태그 색상
        background_tags = {
            "영웅적": "#4CAF50",  # 녹색
            "비극적": "#F44336",  # 빨간색
            "신비로운": "#9C27B0",  # 보라색
            "학자": "#2196F3",  # 파란색
            "범죄자": "#FF9800",  # 주황색
            "전사": "#795548",  # 갈색
            "귀족": "#FFC107",  # 노란색
            "서민": "#607D8B",  # 회색
            "이방인": "#009688",  # 청록색
            "운명적": "#E91E63"   # 분홍색
        }
        
        # 배경 옵션 표시
        for i, background in enumerate(st.session_state.character_backgrounds):
            # 배경에서 태그 추출 (간단한 키워드 기반)
            bg_tags = []
            for tag, _ in background_tags.items():
                if tag.lower() in background.lower():
                    bg_tags.append(tag)
            
            if not bg_tags:
                bg_tags = ["신비로운"]  # 기본 태그
                
            st.markdown(f"<div class='option-card'>", unsafe_allow_html=True)
            
            # 태그 표시
            tags_html = ""
            for tag in bg_tags[:3]:  # 최대 3개 태그만
                tag_color = background_tags.get(tag, "#607D8B")  # 기본값은 회색
                tags_html += f"""
                <span style='background-color: {tag_color}; color: white; 
                           padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; 
                           margin-right: 5px; display: inline-block; margin-bottom: 5px;'>
                    {tag}
                </span>
                """
            
            st.markdown(f"""
            <div style='margin-bottom: 10px;'>
                {tags_html}
            </div>
            <h3>배경 옵션 {i+1}</h3>
            """, unsafe_allow_html=True)
            
            # 배경 내용 강조 처리
            # 중요 키워드 강조
            formatted_bg = background
            
            # 단락 나누기
            paragraphs = formatted_bg.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    st.markdown(f"<p>{para}</p>", unsafe_allow_html=True)
            
            if st.button(f"이 배경 선택", key=f"bg_{i}", 
                         use_container_width=True, 
                         help="이 배경 스토리로 캐릭터를 생성합니다"):
                st.session_state.selected_background = background
                st.session_state.background_tags = bg_tags
                st.session_state.character_creation_step = 'abilities'
                st.session_state.master_message = "좋은 선택입니다! 이제 캐릭터의 능력치를 결정해 봅시다."
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 직접 작성 옵션
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.write("### 직접 작성")
        st.write("자신만의 독특한 배경 스토리를 작성하고 싶다면 직접 입력할 수 있습니다.")
        
        # 태그 선택
        st.write("배경 태그 선택 (최대 3개):")
        tag_cols = st.columns(3)
        selected_tags = []
        i = 0
        for tag, color in background_tags.items():
            with tag_cols[i % 3]:
                if st.checkbox(tag, key=f"tag_{tag}"):
                    selected_tags.append(tag)
            i += 1
        
        # 선택된 태그가 3개 초과면 경고
        if len(selected_tags) > 3:
            st.warning("태그는 최대 3개까지만 선택할 수 있습니다. 초과된 태그는 무시됩니다.")
            selected_tags = selected_tags[:3]
        
        # 직접 입력 필드
        custom_background = st.text_area("나만의 배경 스토리:", height=200,
                                         placeholder="당신의 캐릭터는 어떤 사람인가요? 어떤 경험을 했나요? 무엇을 위해 모험을 떠나게 되었나요?")
        
        if custom_background and st.button("직접 작성한 배경 사용", use_container_width=True):
            st.session_state.selected_background = custom_background
            st.session_state.background_tags = selected_tags if selected_tags else ["신비로운"]
            st.session_state.character_creation_step = 'abilities'
            st.session_state.master_message = "창의적인 배경 스토리군요! 이제 캐릭터의 능력치를 결정해 봅시다."
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 뒤로 가기 옵션
        if st.button("← 직업 선택으로 돌아가기", use_container_width=True):
            st.session_state.character_creation_step = 'profession'
            st.session_state.background_options_generated = False
            st.session_state.master_message = "직업을 다시 선택해 보세요!"
            st.rerun()
# 능력치 설정 단계
    elif st.session_state.character_creation_step == 'abilities':
        st.subheader("능력치 설정")
        
        # 능력치 설정 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>능력치는 캐릭터의 신체적, 정신적 역량을 수치화한 것입니다.</p>
            <p>주사위를 굴려 결정하거나, 기본값을 사용할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 선택된 종족, 직업, 배경 태그 표시 (개선된 UI)
        race_icon = st.session_state.get('race_icon', '👤')
        profession_icon = st.session_state.get('profession_icon', '👤')
        key_stats = st.session_state.get('profession_stats', ['??', '??'])
        race_bonuses = st.session_state.get('race_bonus', {})
        bg_tags = st.session_state.get('background_tags', ["신비로운"])
        
        # 태그 표시용 HTML 생성
        tags_html = ""
        background_tags = {
            "영웅적": "#4CAF50", "비극적": "#F44336", "신비로운": "#9C27B0", 
            "학자": "#2196F3", "범죄자": "#FF9800", "전사": "#795548", 
            "귀족": "#FFC107", "서민": "#607D8B", "이방인": "#009688", 
            "운명적": "#E91E63"
        }
        for tag in bg_tags:
            tag_color = background_tags.get(tag, "#607D8B")  # 기본값은 회색
            tags_html += f"""
            <span style='background-color: {tag_color}; color: white; 
                       padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; 
                       margin-right: 5px; display: inline-block;'>
                {tag}
            </span>
            """
            
        # 캐릭터 요약 표시
        # 캐릭터 요약 정보를 HTML로 렌더링
        character_summary_html = f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <div style='display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 10px;'>
                <div style='font-size: 2.5rem; margin-right: 15px;'>{race_icon}</div>
                <div style='flex-grow: 1; margin-right: 15px;'>
                    <h3 style='margin: 0; color: #4CAF50;'>{st.session_state.selected_race} {st.session_state.selected_profession}</h3>
                    <div style='font-size: 0.9rem; margin-top: 5px;'>
                        {tags_html}
                    </div>
                </div>
                <div style='font-size: 2.5rem;'>{profession_icon}</div>
            </div>
            <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
                <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>핵심 능력치</div>
                    <div>{"・".join(key_stats)}</div>
                </div>
                <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>종족 보너스</div>
                    <div>{"・".join([f"{k} {v}" for k, v in race_bonuses.items()])}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(character_summary_html, unsafe_allow_html=True)
        
        ability_col1, ability_col2 = st.columns([3, 1])
        
        with ability_col1:
            # 능력치 설정 방법 선택
            ability_method = st.radio(
                "능력치 설정 방법:",
                ["3D6 주사위 굴리기", "기본 능력치 사용"],
                horizontal=True
            )
            
            if ability_method == "3D6 주사위 굴리기":
                # 주사위 굴리기 관련 상태 초기화
                if 'dice_rolled' not in st.session_state:
                    st.session_state.dice_rolled = False
                
                if 'reroll_used' not in st.session_state:
                    st.session_state.reroll_used = False
                    
                # 주사위 굴리기 설명 추가
                st.markdown("""
                <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
                    <p>능력치는 각각 3D6(6면체 주사위 3개) 방식으로 결정됩니다.</p>
                    <p>각 능력치는 3~18 사이의 값을 가지며, 평균값은 10-11입니다.</p>
                    <p>14 이상은 뛰어난 능력, 16 이상은 탁월한 능력입니다.</p>
                    <p><strong>다시 굴리기는 1번만 가능합니다.</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # 주사위 굴리기 버튼
                if not st.session_state.dice_rolled and st.button("주사위 굴리기", use_container_width=True, key="roll_ability_dice"):
                    st.session_state.dice_rolled = True
                    
                    # 능력치 목록
                    ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
                    rolled_abilities = {}
                    
                    # 각 능력치별 주사위 굴리기 결과 애니메이션으로 표시
                    ability_placeholders = {}
                    for ability in ability_names:
                        ability_placeholders[ability] = st.empty()
                    
                    # 순차적으로 각 능력치 굴리기
                    for ability in ability_names:
                        with st.spinner(f"{ability} 굴리는 중..."):
                            # 3D6 주사위 결과 계산
                            dice_rolls = [random.randint(1, 6) for _ in range(3)]
                            total = sum(dice_rolls)
                            
                            # 결과 표시
                            ability_placeholders[ability].markdown(f"""
                            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>
                                <div style='display: flex; justify-content: space-between;'>
                                    <span><strong>{ability}</strong></span>
                                    <span>🎲 {dice_rolls[0]} + {dice_rolls[1]} + {dice_rolls[2]} = <strong>{total}</strong></span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            rolled_abilities[ability] = total
                            time.sleep(0.3)  # 약간의 딜레이
                    
                    # 세션에 저장
                    st.session_state.rolled_abilities = rolled_abilities
                    st.rerun()
                
                # 굴린 결과 표시
                if st.session_state.dice_rolled and 'rolled_abilities' in st.session_state:
                    st.write("#### 주사위 결과:")
                    cols = st.columns(3)
                    i = 0
                    
                    # 직업 정보를 미리 가져옴
                    prof = st.session_state.selected_profession if 'selected_profession' in st.session_state else ""
                    
                    # 직업별 중요 능력치 정보
                    profession_key_stats = st.session_state.get('profession_stats', [])
                    
                    # 능력치 총점 계산 (나중에 보여주기 위함)
                    total_points = sum(st.session_state.rolled_abilities.values())
                    
                    # 결과를 정렬하여 먼저 중요 능력치를 표시
                    sorted_abilities = sorted(
                        st.session_state.rolled_abilities.items(),
                        key=lambda x: (x[0] not in profession_key_stats, profession_key_stats.index(x[0]) if x[0] in profession_key_stats else 999)
                    )
                    
                    for ability, value in sorted_abilities:
                        with cols[i % 3]:
                            # 직업에 중요한 능력치인지 확인
                            is_key_stat = ability in profession_key_stats
                            
                            # 색상 및 설명 가져오기
                            color, description = get_stat_info(ability, value, prof)
                            
                            # 중요 능력치 강조 스타일
                            highlight = "border: 2px solid gold; background-color: rgba(255, 215, 0, 0.1);" if is_key_stat else ""
                            key_badge = "<span style='background-color: #FFD700; color: #000; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>" if is_key_stat else ""
                            
                            # 능력치 값에 따른 바 그래프 너비 계산 (백분율, 최대 18 기준)
                            bar_width = min(100, (value / 18) * 100)
                            
                            # 개선된 능력치 표시
                            st.markdown(f"""
                            <div class='stat-box' style="border-left: 4px solid {color}; {highlight}">
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <span class='stat-name'>{ability}{key_badge}</span>
                                    <span class='stat-value'>{value}</span>
                                </div>
                                <div style='margin-top: 5px; background-color: #1e2636; height: 8px; border-radius: 4px;'>
                                    <div style='background-color: {color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
                                </div>
                                <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 5px;">{description}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        i += 1
                    
                    # 능력치 총점 표시
                    avg_total = 63  # 3D6 6개의 평균
                    
                    # 총점 평가 (낮음, 평균, 높음)
                    if total_points < avg_total - 5:
                        total_rating = "낮음"
                        total_color = "#F44336"  # 빨간색
                    elif total_points > avg_total + 5:
                        total_rating = "높음"
                        total_color = "#4CAF50"  # 녹색
                    else:
                        total_rating = "평균"
                        total_color = "#FFC107"  # 노란색
                    
                    st.markdown(f"""
                    <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center;'>
                        <div style='font-weight: bold;'>능력치 총점:</div>
                        <div style='display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 5px;'>
                            <span style='color: {total_color}; font-size: 1.5rem; font-weight: bold;'>{total_points}</span>
                            <span style='background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
                        </div>
                        <div style='font-size: 0.8rem; margin-top: 5px;'>(평균 63, 70+ 우수, 80+ 탁월)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 버튼 열 생성
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("이 능력치로 진행하기", use_container_width=True, key="use_these_stats"):
                            st.session_state.character['stats'] = st.session_state.rolled_abilities
                            st.session_state.character['profession'] = st.session_state.selected_profession
                            st.session_state.character['race'] = st.session_state.selected_race
                            st.session_state.character['backstory'] = st.session_state.selected_background
                            st.session_state.character_creation_step = 'review'
                            st.session_state.master_message = "좋습니다! 캐릭터가 거의 완성되었습니다. 최종 확인을 해 볼까요?"
                            
                            # 다시 굴리기 관련 상태 초기화
                            st.session_state.dice_rolled = False
                            st.session_state.reroll_used = False
                            st.rerun()
                    
                    with col2:
                        # 다시 굴리기 버튼 - 한번만 사용 가능하도록 제한
                        if st.button("다시 굴리기", 
                                    use_container_width=True, 
                                    key="reroll_ability_dice",
                                    disabled=st.session_state.reroll_used):
                            if not st.session_state.reroll_used:
                                # 다시 굴리기 사용 표시
                                st.session_state.reroll_used = True
                                
                                # 능력치 목록
                                ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
                                rerolled_abilities = {}
                                
                                # 각 능력치별 재굴림 결과 표시
                                reroll_placeholders = {}
                                for ability in ability_names:
                                    reroll_placeholders[ability] = st.empty()
                                
                                # 순차적으로 각 능력치 다시 굴리기
                                for ability in ability_names:
                                    # 3D6 주사위 결과 계산
                                    dice_rolls = [random.randint(1, 6) for _ in range(3)]
                                    total = sum(dice_rolls)
                                    rerolled_abilities[ability] = total
                                
                                # 결과 저장 및 상태 업데이트
                                st.session_state.rolled_abilities = rerolled_abilities
                                st.session_state.reroll_message = "다시 굴리기 기회를 사용했습니다."
                                st.rerun()
                    
                    # 다시 굴리기 사용 여부 표시
                    if st.session_state.reroll_used:
                        st.info("다시 굴리기 기회를 이미 사용했습니다.")
            
            else:  # 기본 능력치 사용
                st.write("#### 기본 능력치:")
                base_abilities = {'STR': 10, 'INT': 10, 'DEX': 10, 'CON': 10, 'WIS': 10, 'CHA': 10}
                
                # 직업에 따른 추천 능력치 조정
                if 'selected_profession' in st.session_state:
                    profession = st.session_state.selected_profession
                    profession_key_stats = st.session_state.get('profession_stats', [])
                    
                    # 주요 능력치에 보너스 부여
                    for stat in profession_key_stats:
                        if stat in base_abilities:
                            base_abilities[stat] = 14  # 주요 능력치는 14로 설정
                
                # 종족에 따른 능력치 보너스 적용
                if 'race_bonus' in st.session_state:
                    for stat, bonus in st.session_state.race_bonus.items():
                        if stat in base_abilities:
                            # 보너스값에서 '+'를 제거하고 정수로 변환
                            bonus_value = int(bonus.replace('+', ''))
                            base_abilities[stat] += bonus_value
                        elif stat == "모든 능력치":
                            # 모든 능력치에 보너스 적용
                            bonus_value = int(bonus.replace('+', ''))
                            for ability in base_abilities:
                                base_abilities[ability] += bonus_value
                
                # 결과 표시 (향상된 시각적 표현)
                cols = st.columns(3)
                i = 0
                
                # 직업 정보 가져오기
                prof = st.session_state.selected_profession if 'selected_profession' in st.session_state else ""
                key_stats = st.session_state.get('profession_stats', [])
                
                # 정렬: 주요 능력치 먼저
                sorted_abilities = sorted(
                    base_abilities.items(),
                    key=lambda x: (x[0] not in key_stats, key_stats.index(x[0]) if x[0] in key_stats else 999)
                )
                
                for ability, value in sorted_abilities:
                    with cols[i % 3]:
                        color, description = get_stat_info(ability, value, prof)
                        is_key_stat = ability in key_stats
                        
                        # 중요 능력치 강조 스타일
                        highlight = "border: 2px solid gold; background-color: rgba(255, 215, 0, 0.1);" if is_key_stat else ""
                        key_badge = "<span style='background-color: #FFD700; color: #000; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>" if is_key_stat else ""
                        
                        # 종족 보너스 표시
                        race_bonus_badge = ""
                        for stat, bonus in st.session_state.race_bonus.items():
                            if stat == ability or stat == "모든 능력치":
                                race_bonus_badge = f"<span style='background-color: #4CAF50; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>{bonus}</span>"
                        
                        # 개선된 능력치 표시
                        st.markdown(f"""
                        <div class='stat-box' style="border-left: 4px solid {color}; {highlight}">
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span class='stat-name'>{ability}{key_badge}{race_bonus_badge}</span>
                                <span class='stat-value'>{value}</span>
                            </div>
                            <div style='margin-top: 5px;'>
                                <div style='background-color: #444; height: 4px; border-radius: 2px;'>
                                    <div style='background-color: {color}; width: {min(value * 5, 100)}%; height: 100%; border-radius: 2px;'></div>
                                </div>
                            </div>
                            <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 5px;">{description}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    i += 1
                
                # 능력치 총점 표시
                total_points = sum(base_abilities.values())
                avg_total = 60  # 평균 총점
                
                # 총점 평가 (낮음, 평균, 높음)
                if total_points < avg_total - 5:
                    total_rating = "낮음"
                    total_color = "#F44336"  # 빨간색
                elif total_points > avg_total + 5:
                    total_rating = "높음"
                    total_color = "#4CAF50"  # 녹색
                else:
                    total_rating = "평균"
                    total_color = "#FFC107"  # 노란색
                
                st.markdown(f"""
                <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center;'>
                    <span style='font-weight: bold;'>능력치 총점:</span> 
                    <span style='color: {total_color}; font-size: 1.2rem; font-weight: bold;'>{total_points}</span>
                    <span style='margin-left: 10px; background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
                    <div style='font-size: 0.8rem; margin-top: 5px;'>(평균 60-65, 70+ 우수, 80+ 탁월)</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("기본 능력치로 진행하기", use_container_width=True):
                    st.session_state.character['stats'] = base_abilities
                    st.session_state.character['profession'] = st.session_state.selected_profession
                    st.session_state.character['race'] = st.session_state.selected_race
                    st.session_state.character['backstory'] = st.session_state.selected_background
                    st.session_state.character_creation_step = 'review'
                    st.session_state.master_message = "좋습니다! 캐릭터가 거의 완성되었습니다. 최종 확인을 해 볼까요?"
                    st.rerun()
        
        with ability_col2:
            # 능력치 설명 및 정보 표시
            st.markdown("""
            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
                <h4 style='margin-top: 0;'>능력치 정보</h4>
                <table style='width: 100%; font-size: 0.9rem;'>
                    <tr><td><strong>STR</strong></td><td>근력, 물리적 공격력</td></tr>
                    <tr><td><strong>DEX</strong></td><td>민첩성, 회피/정확도</td></tr>
                    <tr><td><strong>CON</strong></td><td>체력, 생존력</td></tr>
                    <tr><td><strong>INT</strong></td><td>지능, 마법/기술 이해력</td></tr>
                    <tr><td><strong>WIS</strong></td><td>지혜, 직관/인식력</td></tr>
                    <tr><td><strong>CHA</strong></td><td>매력, 설득력/교섭력</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # 능력치 점수 해석
            st.markdown("""
            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
                <h4 style='margin-top: 0;'>능력치 점수 해석</h4>
                <table style='width: 100%; font-size: 0.9rem;'>
                    <tr><td>1-3</td><td>심각한 약점</td></tr>
                    <tr><td>4-6</td><td>약함</td></tr>
                    <tr><td>7-9</td><td>평균 이하</td></tr>
                    <tr><td>10-12</td><td>평균적</td></tr>
                    <tr><td>13-15</td><td>평균 이상</td></tr>
                    <tr><td>16-17</td><td>매우 뛰어남</td></tr>
                    <tr><td>18+</td><td>전설적 수준</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # 배경 요약
            st.markdown("""
            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px;'>
                <h4 style='margin-top: 0;'>배경 요약</h4>
                <div style='max-height: 200px; overflow-y: auto; font-size: 0.9rem;'>
            """, unsafe_allow_html=True)
            
            # 배경 텍스트에서 중요 부분만 추출 (첫 200자)
            bg_summary = st.session_state.selected_background[:200]
            if len(st.session_state.selected_background) > 200:
                bg_summary += "..."
                
            st.markdown(f"{bg_summary}", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # 뒤로 가기 옵션
        if st.button("← 배경 선택으로 돌아가기", use_container_width=True):
            st.session_state.character_creation_step = 'background'
            
            # 주사위 굴리기 관련 상태 초기화
            if 'dice_rolled' in st.session_state:
                del st.session_state.dice_rolled
            if 'reroll_used' in st.session_state:
                del st.session_state.reroll_used
            if 'rolled_abilities' in st.session_state:
                del st.session_state.rolled_abilities
                
            st.session_state.master_message = "배경을 다시 선택해 보세요!"
            st.rerun()
# 캐릭터 최종 확인 단계
    elif st.session_state.character_creation_step == 'review':
        st.subheader("캐릭터 최종 확인")
        
        # 마지막 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
            <p>당신의 캐릭터가 완성되었습니다! 최종 정보를 확인하고 모험을 시작하세요.</p>
            <p>능력치, 장비, 특수 능력을 확인하고 필요하다면 수정할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        review_col1, review_col2 = st.columns([2, 1])
        
        with review_col1:
            # 종족 및 직업 아이콘 가져오기
            race_icon = st.session_state.get('race_icon', '👤')
            profession_icon = st.session_state.get('profession_icon', '👤')
            bg_tags = st.session_state.get('background_tags', ["신비로운"])
            
            # 태그 표시용 HTML 생성
            tags_html = ""
            background_tags = {
                "영웅적": "#4CAF50", "비극적": "#F44336", "신비로운": "#9C27B0", 
                "학자": "#2196F3", "범죄자": "#FF9800", "전사": "#795548", 
                "귀족": "#FFC107", "서민": "#607D8B", "이방인": "#009688", 
                "운명적": "#E91E63"
            }
            for tag in bg_tags:
                tag_color = background_tags.get(tag, "#607D8B")  # 기본값은 회색
                tags_html += f"""
                <span style='background-color: {tag_color}; color: white; 
                           padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; 
                           margin-right: 5px; display: inline-block;'>
                    {tag}
                </span>
                """
            
            # 캐릭터 카드 생성 (화려한 디자인)
            st.markdown(f"""
            <div style='background-color: #2a3549; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                      border: 2px solid #6b8afd; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                    <div style='font-size: 3rem; margin-right: 15px;'>{race_icon}</div>
                    <div style='flex-grow: 1;'>
                        <h2 style='margin: 0; color: #e0e0ff;'>
                            {st.session_state.character['race']} {st.session_state.character['profession']}
                        </h2>
                        <div style='margin-top: 5px;'>
                            {tags_html}
                        </div>
                    </div>
                    <div style='font-size: 3rem;'>{profession_icon}</div>
                </div>
                
                <div style='margin: 15px 0 20px 0;'>
                    <div style='font-weight: bold; margin-bottom: 5px; color: #6b8afd;'>캐릭터 특성</div>
                    <div style='background-color: rgba(107, 138, 253, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #6b8afd;'>
                        {st.session_state.get('race_ability', '종족 특성 없음')}
                    </div>
                    <div style='margin-top: 10px; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #4CAF50;'>
                        {st.session_state.get('profession_skill', '직업 특성 없음')}
                    </div>
                </div>
                
                <div style='font-weight: bold; margin-bottom: 10px; color: #6b8afd;'>배경 스토리</div>
                <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; max-height: 200px; overflow-y: auto;'>
                    {st.session_state.character['backstory']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 인벤토리 표시 (개선된 버전)
            st.markdown("""
            <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                      border: 2px solid #FFD700; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin-top: 0; color: #FFD700;'>인벤토리</h3>
            """, unsafe_allow_html=True)
            
            # 인벤토리 아이템 정렬
            inventory_items = st.session_state.character['inventory']
            
            # 아이템 카테고리 정의
            categories = {
                "무기": [],
                "방어구": [],
                "소비품": [],
                "도구": [],
                "기타": []
            }
            
            # 아이템을 카테고리별로 분류
            for item in inventory_items:
                item_name = item.name if hasattr(item, 'name') else str(item)
                item_desc = getattr(item, 'description', '설명 없음')
                item_consumable = getattr(item, 'consumable', False)
                item_durability = getattr(item, 'durability', None)
                item_quantity = getattr(item, 'quantity', 1)
                
                # 아이템 아이콘 결정
                if hasattr(item, 'type'):
                    item_type = item.type
                    category = item_type if item_type in categories else "기타"
                    if item_type == "무기":
                        icon = "⚔️"
                    elif item_type == "방어구":
                        icon = "🛡️"
                    elif item_type == "소비품":
                        icon = "🧪"
                    elif item_type == "도구":
                        icon = "🔧"
                    else:
                        icon = "📦"
                else:
                    # 아이템 이름으로 유추
                    if "검" in item_name or "도끼" in item_name or "단검" in item_name or "활" in item_name or "무기" in item_name:
                        icon = "⚔️"
                        category = "무기"
                    elif "갑옷" in item_name or "방패" in item_name or "투구" in item_name or "방어" in item_name:
                        icon = "🛡️"
                        category = "방어구"
                    elif item_consumable or "물약" in item_name or "음식" in item_name or "포션" in item_name:
                        icon = "🧪"
                        category = "소비품"
                    elif "도구" in item_name or "키트" in item_name or "세트" in item_name:
                        icon = "🔧"
                        category = "도구"
                    else:
                        icon = "📦"
                        category = "기타"
                
                # 아이템 정보 저장
                categories[category].append({
                    "name": item_name,
                    "icon": icon,
                    "desc": item_desc,
                    "consumable": item_consumable,
                    "durability": item_durability,
                    "quantity": item_quantity
                })
            
            # 카테고리별로 아이템 표시
            for category, items in categories.items():
                if items:  # 해당 카테고리에 아이템이 있는 경우에만 표시
                    st.markdown(f"""
                    <div style='margin-top: 10px;'>
                        <div style='font-weight: bold; color: #e0e0ff; margin-bottom: 5px;'>{category}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for item in items:
                        # 내구도 또는 수량 표시
                        quantity_text = ""
                        if item["quantity"] > 1:
                            quantity_text = f"<span style='color: #FFD700;'>×{item['quantity']}</span>"
                        elif item["durability"] is not None:
                            quantity_text = f"<span style='color: #4CAF50;'>내구도: {item['durability']}</span>"
                        
                        # 소비성 아이템 표시
                        consumable_badge = ""
                        if item["consumable"]:
                            consumable_badge = "<span style='background-color: #FF9800; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>소비</span>"
                        
                        # 아이템 표시
                        st.markdown(f"""
                        <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 5px; display: flex; align-items: center;'>
                            <div style='font-size: 1.5rem; margin-right: 10px;'>{item['icon']}</div>
                            <div style='flex-grow: 1;'>
                                <div>
                                    <span style='font-weight: bold;'>{item['name']}</span>
                                    {consumable_badge}
                                    <span style='float: right;'>{quantity_text}</span>
                                </div>
                                <div style='font-size: 0.8rem; color: #aaaaaa; margin-top: 3px;'>{item['desc']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 특별한 특성 추가
            if 'special_trait' not in st.session_state:
                # 테마와 배경 태그에 따른 특성 선택
                theme = st.session_state.theme
                bg_tags = st.session_state.get('background_tags', ["신비로운"])
                
                fantasy_traits = [
                    "마법에 대한 직관: 마법 관련 판정에 +1 보너스",
                    "언어 재능: 하나의 추가 언어를 이해할 수 있음",
                    "생존 본능: 위험 감지 판정에 +2 보너스",
                    "전투 감각: 선제력 판정에 +1 보너스",
                    "비밀 감지: 숨겨진 문이나 함정 찾기에 +2 보너스"
                ]
                
                scifi_traits = [
                    "기계 친화력: 장치 조작 판정에 +1 보너스",
                    "우주 적응: 저중력 환경 적응에 +2 보너스",
                    "전술적 사고: 전투 전략 판정에 +1 보너스",
                    "네트워크 감각: 정보 검색에 +2 보너스",
                    "생체 회복: 휴식 시 추가 체력 회복"
                ]
                
                dystopia_traits = [
                    "생존자 본능: 위험한 상황 탈출에 +1 보너스",
                    "자원 절약: 소비품 사용 효율 +25%",
                    "야간 시력: 어두운 곳에서 시각 판정에 불이익 없음",
                    "불굴의 의지: 정신적 충격 저항에 +2 보너스",
                    "전술적 직감: 교전 시 선제 행동 확률 +15%"
                ]
                
                # 태그에 따른 특성 선택 확률 조정
                has_hero = "영웅적" in bg_tags
                has_scholarly = "학자" in bg_tags
                has_tragic = "비극적" in bg_tags
                has_criminal = "범죄자" in bg_tags
                has_mysterious = "신비로운" in bg_tags
                
                if theme == "fantasy":
                    traits = fantasy_traits
                    if has_hero:
                        traits.append("운명의 보호: 하루에 한 번 치명적 공격을 일반 공격으로 낮출 수 있음")
                    if has_scholarly:
                        traits.append("비전학자: 마법 관련 지식 판정에 +2 보너스")
                    if has_tragic:
                        traits.append("고통의 힘: 체력이 절반 이하일 때 공격력 +1")
                    if has_criminal:
                        traits.append("그림자 걷기: 은신 판정에 +2 보너스")
                    if has_mysterious:
                        traits.append("신비한 직감: 하루에 한 번 주사위를 다시 굴릴 수 있음")
                elif theme == "sci-fi":
                    traits = scifi_traits
                    if has_hero:
                        traits.append("영웅적 리더십: 아군 NPC 의사 결정에 영향력 +25%")
                    if has_scholarly:
                        traits.append("데이터 분석: 기술 장치 판독에 +2 보너스")
                    if has_tragic:
                        traits.append("역경의 경험: 위기 상황에서 판단력 +1")
                    if has_criminal:
                        traits.append("시스템 침투: 보안 해제 시도에 +2 보너스")
                    if has_mysterious:
                        traits.append("양자 직감: 확률적 사건 예측에 +15% 정확도")
                else:  # dystopia
                    traits = dystopia_traits
                    if has_hero:
                        traits.append("불굴의 영웅: 동료를 보호하는 행동에 +2 보너스")
                    if has_scholarly:
                        traits.append("생존 지식: 자원 활용 효율 +20%")
                    if has_tragic:
                        traits.append("상실의 분노: 개인적 원한에 관련된 행동에 +2 보너스")
                    if has_criminal:
                        traits.append("암시장 연결망: 희귀 물품 거래 시 15% 할인")
                    if has_mysterious:
                        traits.append("통제 면역: 정신 조작 시도에 대한 저항 +25%")
                
                # 무작위 특성 선택
                st.session_state.special_trait = random.choice(traits)
            
            # 특수 특성 표시
            st.markdown(f"""
            <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                      border: 2px solid #9C27B0; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin-top: 0; color: #9C27B0;'>특별한 특성</h3>
                <div style='background-color: rgba(156, 39, 176, 0.1); padding: 15px; border-radius: 5px; border-left: 3px solid #9C27B0;'>
                    <div style='font-weight: bold;'>🌟 {st.session_state.special_trait.split(":")[0]}</div>
                    <div style='margin-top: 5px;'>{":".join(st.session_state.special_trait.split(":")[1:])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with review_col2:
            # 능력치 표시
            st.markdown("""
            <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                      border: 2px solid #4CAF50; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin-top: 0; color: #4CAF50;'>능력치</h3>
            """, unsafe_allow_html=True)
            
            # 직업 정보 가져오기
            prof = st.session_state.character['profession']
            key_stats = st.session_state.get('profession_stats', [])
            
            # 능력치 값 총합 계산
            total_points = sum(st.session_state.character['stats'].values())
            
            # 능력치 설정
            for stat, value in st.session_state.character['stats'].items():
                # 색상 및 설명 가져오기
                color, description = get_stat_info(stat, value, prof)
                is_key_stat = stat in key_stats
                
                # 키 스탯 표시
                key_badge = ""
                if is_key_stat:
                    key_badge = f"<span style='background-color: #FFD700; color: black; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>"
                
                # 바 그래프 너비 계산 (백분율, 최대 18 기준)
                bar_width = min(100, (value / 18) * 100)
                
                # 능력치 바 생성
                st.markdown(f"""
                <div style='margin-bottom: 15px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: bold;'>{stat}</span>
                            {key_badge}
                        </div>
                        <span style='font-weight: bold; color: {color};'>{value}</span>
                    </div>
                    <div style='margin-top: 5px; background-color: #1e2636; height: 8px; border-radius: 4px;'>
                        <div style='background-color: {color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
                    </div>
                    <div style='font-size: 0.8rem; color: #aaaaaa; margin-top: 3px;'>{description}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 능력치 총점 표시
            avg_total = 60  # 평균 총점
            
            # 총점 평가 (낮음, 평균, 높음)
            if total_points < avg_total - 5:
                total_rating = "낮음"
                total_color = "#F44336"  # 빨간색
            elif total_points > avg_total + 5:
                total_rating = "높음"
                total_color = "#4CAF50"  # 녹색
            else:
                total_rating = "평균"
                total_color = "#FFC107"  # 노란색
            
            st.markdown(f"""
            <div style='text-align: center; margin-top: 10px; padding: 10px; background-color: rgba(0,0,0,0.2); border-radius: 5px;'>
                <span style='font-weight: bold;'>능력치 총점:</span> 
                <span style='color: {total_color}; font-size: 1.2rem; font-weight: bold;'>{total_points}</span>
                <span style='margin-left: 10px; background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
            </div>
            """, unsafe_allow_html=True)
            
            
            # 시작 위치 정보
            st.markdown(f"""
            <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                      border: 2px solid #2196F3; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin-top: 0; color: #2196F3;'>시작 위치</h3>
                <div style='background-color: rgba(33, 150, 243, 0.1); padding: 15px; border-radius: 5px; border-left: 3px solid #2196F3;'>
                    <div style='font-size: 1.2rem; font-weight: bold; text-align: center;'>{st.session_state.current_location}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 캐릭터 플레이 팁
            st.markdown(f"""
            <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; 
                      border: 2px solid #FF9800; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                <h3 style='margin-top: 0; color: #FF9800;'>플레이 팁</h3>
                <ul style='margin-top: 10px; padding-left: 20px;'>
                    <li>당신의 핵심 능력치({', '.join(key_stats)})를 활용하는 행동을 시도하세요.</li>
                    <li>"{st.session_state.special_trait.split(':')[0]}" 특성을 중요한 순간에 활용하세요.</li>
                    <li>배경 스토리와 일관된 캐릭터 플레이를 하면 더 몰입감 있는 경험을 할 수 있습니다.</li>
                    <li>마스터에게 세계관에 대한 궁금한 점을 자유롭게 질문하세요.</li>
                    <li>창의적인 문제 해결 방법을 시도해보세요.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # 최종 선택 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이 캐릭터로 게임 시작", use_container_width=True):
                # 특별한 특성 저장
                if 'special_trait' in st.session_state:
                    st.session_state.character['special_trait'] = st.session_state.special_trait
                
                # 게임 시작 준비
                with st.spinner("게임을 준비하는 중..."):
                    # 시작 메시지 생성
                    start_prompt = f"""
                    당신은 TRPG 게임 마스터입니다. 플레이어 캐릭터의 게임 시작 장면을 묘사해주세요.
                    
                    세계: {st.session_state.world_description[:200]}...
                    캐릭터: {st.session_state.character['race']} {st.session_state.character['profession']}
                    배경: {st.session_state.character['backstory'][:200]}...
                    현재 위치: {st.session_state.current_location}
                    특별한 특성: {st.session_state.character.get('special_trait', '특별한 특성 없음')}
                    
                    게임을 시작하는 첫 장면을 생생하게 묘사해주세요. 플레이어가 마주한 상황을 설명하되,
                    다양한 감각적 묘사(시각, 청각, 후각, 촉각)를 포함하세요.
                    플레이어의 특별한 특성이나 배경과 연결된 요소를 포함하면 좋습니다.
                    '당신은 어떻게 할 것인가요?' 등의 질문으로 끝내지 마세요.
                    
                    약 200단어 내외로 작성해주세요.
                    """
                    intro = generate_gemini_text(start_prompt, 500)
                    st.session_state.story_log.append(intro)
                    
                    # 행동 제안 생성 상태 설정
                    st.session_state.suggestions_generated = False
                
                # 게임 시작
                st.session_state.stage = 'game_play'
                st.session_state.master_message = f"모험이 시작되었습니다! {st.session_state.character['race']} {st.session_state.character['profession']}으로서의 여정이 펼쳐집니다."
                
                # 행동 단계 초기화
                st.session_state.action_phase = 'suggestions'
                st.rerun()
        
        with col2:
            if st.button("처음부터 다시 만들기", use_container_width=True):
                # 캐릭터 생성 단계 초기화
                st.session_state.character_creation_step = 'race'
                st.session_state.background_options_generated = False
                
                # 임시 데이터 삭제
                for key in ['selected_race', 'selected_profession', 'character_backgrounds', 'selected_background', 
                          'rolled_abilities', 'special_trait', 'race_bonus', 'race_ability', 'race_icon',
                          'profession_icon', 'profession_stats', 'profession_equipment', 'profession_skill',
                          'background_tags', 'dice_rolled', 'reroll_used']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # 캐릭터 정보 초기화
                st.session_state.character = {
                    'profession': '',
                    'stats': {'STR': 0, 'INT': 0, 'DEX': 0, 'CON': 0, 'WIS': 0, 'CHA': 0},
                    'backstory': '',
                    'inventory': ['기본 의류', '작은 주머니 (5 골드)']
                }
                
                st.session_state.master_message = "다시 시작해봅시다! 어떤 종족을 선택하시겠어요?"
                st.rerun()

# 게임 도구 영역 표시 함수
def display_game_tools():
    """게임 도구 및 옵션 UI 표시"""
    # 게임 정보 및 도구
    st.markdown("""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='margin-top: 0; color: #e0e0ff;'>게임 도구</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 세계관 요약 표시 - 수정 (st.popover 오류 해결)
    with st.expander("세계관 요약", expanded=False):
        # 세계관에서 주요 부분만 추출해서 요약 표시
        world_desc = st.session_state.world_description
        # 200자 내외로 잘라내기
        summary = world_desc[:200] + "..." if len(world_desc) > 200 else world_desc
        
        # 단락 구분 적용
        summary_paragraphs = summary.split("\n\n")
        formatted_summary = ""
        for para in summary_paragraphs:
            formatted_summary += f"<p>{para}</p>\n"
            
        st.markdown(f"<div class='story-text'>{formatted_summary}</div>", unsafe_allow_html=True)
        
        # 전체 보기 버튼 (popover 대신 확장 가능한 영역으로 변경)
        if st.button("세계관 전체 보기", key="view_full_world"):
            st.markdown("<div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-top: 10px;'>", unsafe_allow_html=True)
            
            # 단락 구분 적용
            world_paragraphs = world_desc.split("\n\n")
            formatted_world = ""
            for para in world_paragraphs:
                formatted_world += f"<p>{para}</p>\n"
            
            st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{formatted_world}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 마스터에게 질문 (개선됨)
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h4 style='margin-top: 0; color: #e0e0ff;'>마스터에게 질문</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 질문 제안 목록
    suggested_questions = [
        "이 지역의 위험 요소는 무엇인가요?",
        "주변에 어떤 중요한 인물이 있나요?",
        "이 장소에서 찾을 수 있는 가치 있는 것은?",
        "이 지역의 역사는 어떻게 되나요?",
        "현재 상황에서 가장 좋은 선택은?",
    ]
    
    # 질문 처리 상태 관리
    if 'master_question_processing' not in st.session_state:
        st.session_state.master_question_processing = False
    
    # 현재 선택된 질문 상태 관리
    if 'selected_master_question' not in st.session_state:
        st.session_state.selected_master_question = None
    
    # 제안된 질문 버튼 - 선택 시 시각적 피드백 개선
    with st.expander("제안된 질문", expanded=False):
        for i, q in enumerate(suggested_questions):
            # 선택된 질문인지 확인하고 스타일 변경
            is_selected = st.session_state.selected_master_question == q
            
            st.markdown(f"""
            <div style='background-color: {"#4CAF50" if is_selected else "#1e2636"}; 
                        padding: 10px; border-radius: 5px; margin-bottom: 10px;
                        border-left: 4px solid {"#FFFFFF" if is_selected else "#6b8afd"};'>
                <p style='margin: 0; color: {"#FFFFFF" if is_selected else "#e0e0ff"};'>
                    {q} {" ✓" if is_selected else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"{'이 질문 선택됨 ✓' if is_selected else '선택'}", 
                         key=f"master_q_{i}", 
                         use_container_width=True,
                         disabled=is_selected):
                st.session_state.selected_master_question = q
                st.session_state.master_question_input = q  # 입력 필드에 자동 입력
                st.rerun()
    
    # 질문 입력 폼 - 상태 유지를 위해 form 사용
    with st.form(key="master_question_form"):
        # 선택된 질문이 있으면 입력 필드에 표시
        default_question = st.session_state.get('selected_master_question', '')
        master_question = st.text_input("질문:", value=default_question, key="master_question_input")
        
        # 로딩 중이면 버튼 비활성화
        submit_question = st.form_submit_button(
            "질문하기", 
            disabled=st.session_state.master_question_processing
        )
    
    # 질문이 제출되었을 때
    if submit_question and master_question:
        st.session_state.master_question_processing = True
        
        # 플레이스홀더 생성 - 응답을 표시할 위치
        response_placeholder = st.empty()
        response_placeholder.info("마스터가 답변을 작성 중입니다... 잠시만 기다려주세요.")
        
        with st.spinner("마스터가 응답 중..."):
            try:
                # 질문에 대한 답변 생성
                answer = master_answer_game_question(
                    master_question,
                    st.session_state.theme,
                    st.session_state.current_location,
                    st.session_state.world_description
                )
                
                # 마스터 응답을 세계관에 반영하되, 별도의 상태로 저장
                if 'master_question_history' not in st.session_state:
                    st.session_state.master_question_history = []
                
                st.session_state.master_question_history.append({
                    "question": master_question,
                    "answer": answer
                })
                
                # 세계관에 반영 (나중에 참조 가능)
                st.session_state.world_description += f"\n\n질문-{master_question}: {answer}"
                
                # 단락 구분 적용
                answer_paragraphs = answer.split("\n\n")
                formatted_answer = ""
                for para in answer_paragraphs:
                    formatted_answer += f"<p>{para}</p>\n"
                
                # 응답 표시 - 페이지 새로고침 없이 표시
                response_placeholder.markdown(f"""
                <div style='background-color: #2d3748; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>질문: {master_question}</div>
                    <div>{formatted_answer}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 선택된 질문 초기화
                st.session_state.selected_master_question = None
            
            except Exception as e:
                st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
                response_placeholder.error("질문 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
            
            finally:
                # 처리 완료 상태로 변경
                st.session_state.master_question_processing = False
    
    # 질문 기록 표시
    if 'master_question_history' in st.session_state and st.session_state.master_question_history:
        with st.expander("이전 질문 기록"):
            for i, qa in enumerate(st.session_state.master_question_history):
                st.markdown(f"**Q{i+1}:** {qa['question']}")
                
                # 단락 구분 적용
                answer_paragraphs = qa['answer'].split("\n\n")
                formatted_answer = ""
                for para in answer_paragraphs:
                    formatted_answer += f"<p>{para}</p>\n"
                    
                st.markdown(f"**A:** <div>{formatted_answer}</div>", unsafe_allow_html=True)
                st.markdown("---")
    
    # 주사위 직접 굴리기 기능
    with st.expander("주사위 굴리기", expanded=False):
        dice_cols = st.columns(3)
        
        with dice_cols[0]:
            d6 = st.button("D6", use_container_width=True)
        with dice_cols[1]:
            d20 = st.button("D20", use_container_width=True)
        with dice_cols[2]:
            custom_dice = st.selectbox("커스텀", options=[4, 8, 10, 12, 100])
            roll_custom = st.button("굴리기", key="roll_custom")
        
        dice_result_placeholder = st.empty()
        
        if d6:
            result = random.randint(1, 6)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
        elif d20:
            result = random.randint(1, 20)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
        elif roll_custom:
            result = random.randint(1, custom_dice)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
    
    # 게임 관리 기능 - 수정 (첫 화면 돌아가기 문제 해결)
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-top: 20px;'>
        <h4 style='margin-top: 0; color: #e0e0ff;'>게임 관리</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 완전히 개선된 게임 초기화 및 첫 화면 돌아가기
    if st.button("세계관 설정화면으로 돌아가기", use_container_width=True):
        st.warning("⚠️ 주의: 모든 게임 진행 상황이 초기화됩니다!")
        restart_confirm = st.radio(
            "정말 세계관 설정화면으로 돌아가시겠습니까? 모든 진행사항과 세계관이 초기화됩니다.",
            ["아니오", "예"]
        )
        
        if restart_confirm == "예":
            # 확인 버튼
            if st.button("확인 - 처음부터 다시 시작", key="final_restart_confirm"):
                # 게임 세션 완전 초기화
                reset_game_session()
                st.success("첫 화면으로 돌아갑니다...")
                st.experimental_rerun()  # 강제 새로고침

# 스토리와 행동 표시 함수 수정
def display_story_and_actions():
    """스토리 로그와 플레이어 행동 관련 UI를 표시하는 함수"""
    st.header("모험의 이야기")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 스토리 로그가 있으면 표시
    if st.session_state.story_log:
        # 가장 최근 이야기는 강조하여 표시
        latest_story = st.session_state.story_log[-1]
        
        # 단락 구분 개선
        story_paragraphs = latest_story.split("\n\n")
        formatted_story = ""
        for para in story_paragraphs:
            # 아이템 이름 강조 처리 추가
            para = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
            para = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
            # 중요 키워드 강조 처리 추가
            para = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', r"<span style='color: #6b8afd; font-weight: bold;'>\1</span>", para)
            
            formatted_story += f"<p>{para}</p>\n"
        
        st.markdown(f"<div class='story-text'>{formatted_story}</div>", unsafe_allow_html=True)
            
        # 이전 이야기 표시 (접을 수 있는 형태)
        if len(st.session_state.story_log) > 1:
            with st.expander("이전 이야기", expanded=False):
                # 최신 것부터 역순으로 표시 (가장 최근 것 제외)
                for story in reversed(st.session_state.story_log[:-1]):
                    # 단락 구분 개선
                    prev_paragraphs = story.split("\n\n")
                    formatted_prev = ""
                    for para in prev_paragraphs:
                        # 아이템 이름 강조 처리 추가
                        para = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
                        para = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
                        # 중요 키워드 강조 처리 추가
                        para = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', r"<span style='color: #6b8afd; font-weight: bold;'>\1</span>", para)
                        
                        formatted_prev += f"<p>{para}</p>\n"
                    
                    st.markdown(f"<div class='previous-story'>{formatted_prev}</div>", unsafe_allow_html=True)
    
    # 아이템 알림 표시 (있을 경우)
    if st.session_state.get('show_item_notification', False) and st.session_state.get('item_notification', ''):
        # 아이템 이름 강조 처리 추가
        item_notification = st.session_state.item_notification
        item_notification = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", item_notification)
        item_notification = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", item_notification)
        
        st.markdown(f"""
        <div class='item-notification'>
            {item_notification}
        </div>
        """, unsafe_allow_html=True)
        # 알림을 표시한 후 초기화 (다음 번에 사라지게)
        st.session_state.show_item_notification = False
    
    # 행동 단계 처리
    st.subheader("당신의 행동")
    
    # 행동 처리 함수 호출
    handle_action_phase()
    
# 개선된 게임 플레이 페이지 (세계관 요약 및 게임 관리 문제 해결 + 반응형 UI)
def game_play_page():
    """개선된 게임 플레이 페이지"""
    # 모바일 모드 확인
    mobile_mode = is_mobile()
    
    # 모바일 패널 상태 초기화
    if mobile_mode and 'mobile_panel' not in st.session_state:
        st.session_state.mobile_panel = "스토리"
    
    # 레이아웃 설정 - 모바일/데스크톱 모드에 따라 다르게
    if mobile_mode:
        # 모바일: 선택된 패널만 표시
        current_panel = st.session_state.mobile_panel
        
        if current_panel == "캐릭터 정보":
            # 캐릭터 정보 패널
            display_character_panel(st.session_state.character, st.session_state.current_location)
            
            # 아이템 알림 표시 (있을 경우)
            if st.session_state.get('show_item_notification', False) and st.session_state.get('item_notification', ''):
                st.markdown(f"""
                <div class='item-notification'>
                    {st.session_state.item_notification}
                </div>
                """, unsafe_allow_html=True)
                # 알림을 표시한 후 초기화 (다음 번에 사라지게)
                st.session_state.show_item_notification = False
        
        elif current_panel == "게임 도구":
            # 게임 도구 패널
            display_game_tools()
        
        else:  # "스토리" (기본)
            # 스토리 영역
            display_story_and_actions()
    
    else:
        # 데스크톱: 3열 레이아웃
        game_col1, game_col2, game_col3 = st.columns([1, 2, 1])
        
        # 왼쪽 열 - 캐릭터 정보
        with game_col1:
            # 캐릭터 정보 패널
            display_character_panel(st.session_state.character, st.session_state.current_location)
            
            # 아이템 알림 표시 (있을 경우)
            if st.session_state.get('show_item_notification', False) and st.session_state.get('item_notification', ''):
                st.markdown(f"""
                <div class='item-notification'>
                    {st.session_state.item_notification}
                </div>
                """, unsafe_allow_html=True)
                # 알림을 표시한 후 초기화 (다음 번에 사라지게)
                st.session_state.show_item_notification = False
        
        # 중앙 열 - 스토리 및 행동
        with game_col2:
            display_story_and_actions()
        
        # 오른쪽 열 - 게임 도구
        with game_col3:
            display_game_tools()


# 메인 애플리케이션 타이틀과 컨셉 변경
def main():
    # 반응형 레이아웃 설정 (모바일/데스크톱 모드 설정)
    setup_responsive_layout()
    
    st.title("유니버스 원: 세상에서 하나뿐인 TRPG")
    
    # 컨셉 설명 추가
    if st.session_state.stage == 'theme_selection':
        st.markdown("""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
            <p>🌟 <strong>유니버스 원</strong>은 AI가 만들어내는 유일무이한 세계와 이야기를 경험하는 TRPG 플랫폼입니다.</p>
            <p>🎲 당신이 내리는 모든 선택과 행동이 세계를 형성하고, 이야기를 만들어갑니다.</p>
            <p>✨ 누구도 똑같은 이야기를 경험할 수 없습니다. 오직 당신만의 단 하나뿐인 모험이 시작됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 테마 선택 단계
    if st.session_state.stage == 'theme_selection':
        st.header("1️⃣ 세계관 선택")
        
        # 마스터 메시지 표시
        st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
        
        # 테마 설명 추가
        st.markdown("""
        <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
            <p>모험을 시작할 세계의 테마를 선택하세요. 각 테마는 독특한 분위기와 가능성을 제공합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
            # HTML로 색상 박스 생성
            st.markdown(create_theme_image("fantasy"), unsafe_allow_html=True)
            
            # 테마 설명 추가
            st.markdown(get_theme_description("fantasy"), unsafe_allow_html=True)
            
            if st.button("판타지", key="fantasy"):
                with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                    loading_placeholder = st.empty()
                    loading_placeholder.info("판타지 세계를 생성하는 중... 잠시만 기다려주세요.")
                    
                    st.session_state.theme = "fantasy"
                    st.session_state.world_description = generate_world_description("fantasy")
                    st.session_state.current_location = "왕국의 수도"
                    st.session_state.available_locations = generate_locations("fantasy")
                    st.session_state.master_message = "판타지 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                    st.session_state.world_generated = True
                    st.session_state.stage = 'world_description'
                    
                    loading_placeholder.empty()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
            st.markdown(create_theme_image("sci-fi"), unsafe_allow_html=True)
            
            # 테마 설명 추가
            st.markdown(get_theme_description("sci-fi"), unsafe_allow_html=True)
            
            if st.button("SF", key="scifi"):
                with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                    loading_placeholder = st.empty()
                    loading_placeholder.info("SF 세계를 생성하는 중... 잠시만 기다려주세요.")
                    
                    st.session_state.theme = "sci-fi"
                    st.session_state.world_description = generate_world_description("sci-fi")
                    st.session_state.current_location = "중앙 우주 정거장"
                    st.session_state.available_locations = generate_locations("sci-fi")
                    st.session_state.master_message = "SF 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                    st.session_state.world_generated = True
                    st.session_state.stage = 'world_description'
                    
                    loading_placeholder.empty()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
            st.markdown(create_theme_image("dystopia"), unsafe_allow_html=True)
            
            # 테마 설명 추가
            st.markdown(get_theme_description("dystopia"), unsafe_allow_html=True)
            
            if st.button("디스토피아", key="dystopia"):
                with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                    loading_placeholder = st.empty()
                    loading_placeholder.info("디스토피아 세계를 생성하는 중... 잠시만 기다려주세요.")
                    
                    st.session_state.theme = "dystopia"
                    st.session_state.world_description = generate_world_description("dystopia")
                    st.session_state.current_location = "지하 피난처"
                    st.session_state.available_locations = generate_locations("dystopia")
                    st.session_state.master_message = "디스토피아 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                    st.session_state.world_generated = True
                    st.session_state.stage = 'world_description'
                    
                    loading_placeholder.empty()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 세계관 설명 단계
    elif st.session_state.stage == 'world_description':
        world_description_page()
    
    # 캐릭터 생성 단계
    elif st.session_state.stage == 'character_creation':
        character_creation_page()
    
    # 게임 플레이 단계
    elif st.session_state.stage == 'game_play':
        game_play_page()

# 애플리케이션 실행
if __name__ == "__main__":
    main()