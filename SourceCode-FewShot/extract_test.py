import re

'''
LLM의 출력을 입력받아 소스코드를 추출하여 반환한다.
반환 형태: [(언어, 코드), ...]
'''
def extract_code(text): 
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)\n(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]
    


test_code='''
hello world in javascript
```javascript
alert("hello world");
alert("hello world again");
```

hello world in python
```python
print("hello world")
```
'''


print(extract_code(test_code))