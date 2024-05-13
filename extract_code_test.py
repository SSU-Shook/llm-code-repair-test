import re

def extract_code(text):
    # reference (MIT License): github.com/haseeb-heaven/langchain-coder/
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]

# 테스트 문자열
test_text = '''
헬로월드
```
printf("hello");
``` 

코드
```
#include <stdio.h>
int main(){printf("hello");}
```
'''

# 함수 호출 및 결과 출력
found_strings = extract_code(test_text)
print("괄호 안에 있는 문자열들:", found_strings[-1])