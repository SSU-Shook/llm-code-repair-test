import re

def find_strings_within_brackets(text):
    # 정규 표현식을 사용하여 괄호 안의 문자열 찾기
    matches = re.findall(r'`{3}(.*?)`{3}', text, re.DOTALL)
    return matches

# 테스트 문자열
test_text = "```여기는 첫 번째 문자열입니다.``` 그리고 여기는 두 번째 문자열 ```두 번째 문자열입니다.```"

# 함수 호출 및 결과 출력
found_strings = find_strings_within_brackets(test_text)
print("괄호 안에 있는 문자열들:", found_strings)