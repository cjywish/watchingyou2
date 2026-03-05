import re

def extract_status(text):
    """
    Gemini 답변 텍스트에서 <defect_status> 태그 안의 값을 추출합니다.
    형식: <defect_status>: [정상/주의/불량]
    """
    # 대괄호([]) 안의 내용이나 태그 뒤의 텍스트를 찾음
    match = re.search(r'<defect_status>:\s*\[?(정상|주의|불량)\]?', text)
    if match:
        return match.group(1)
    
    # 태그가 없을 경우 텍스트 내 키워드 검색 (Fallback)
    if "불량" in text:
        return "불량"
    elif "주의" in text:
        return "주의"
    else:
        return "정상"
