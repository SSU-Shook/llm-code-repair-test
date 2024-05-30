import os
import time
import json
import glob
import difflib
import re
from env import settings
from openai import OpenAI
import tempfile
import instructions
import csv

'''
Todo
# - .js filename list & path to .jsonl file
# - Upload the codebase
- Few-shot prompting with example codes
- query the model for the output
    - match code style
    - profiling the code style (e.g. tabWidth, semi, etc.)
- save the output to a file (e.g. security patch comments, etc.)
- refactoring the code
- testing the code (diffing, performance, etc.)
- translate english to korean or extract comment to korean
- 클래스화
'''



'''
A typical integration of the Assistants API has the following flow:

1. Create an Assistant by defining its custom instructions and picking a model. 
If helpful, add files and enable tools like Code Interpreter, File Search, and Function calling.

2. Create a Thread when a user starts a conversation.

3. Add Messages to the Thread as the user asks questions.

4. Run the Assistant on the Thread to generate a response by calling the model and the tools.
'''

try:
    client = OpenAI(
        api_key=settings.LLM_API_KEY['openai'],
    )
except:
    print("OpenAI() failed")
    
try:
    os.system("rm filelist.jsonl")
except:
    pass




def extract_code(text): 
    '''
    LLM의 출력을 입력받아 소스코드를 추출하여 반환한다.
    반환 형태: [(언어, 코드), ...]
    '''
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)\n(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]




def diff_code(code1, code2):
    '''
    두 코드를 비교하여 diff를 반환
    '''
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)



def check_status(run_id,thread_id):
    '''
    run의 상태를 반환한다.
    '''
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status



def upload_file(file_path):
    '''
    파일 하나를 클라이언트에 업로드하고, 업로드된 파일 객체를 반환한다.
    '''
    with open(file_path, "rb") as f:
        file = client.files.create(
            file=f,
            purpose = 'assistants'
        ) # 파일 업로드 하면 언제까지 유지가 되는지.... : 안 지우면 유지되는 듯
        print(file)
    return file



def preprocess_code(file_path):
    '''
    파일에서 쉬뱅을 삭제한다.
    '''
    with open(file_path, 'r', encoding='UTF8') as file:
        lines = file.readlines()
    
    if lines and lines[0].startswith('#!'):
        lines = lines[1:]

    temp_file = tempfile.NamedTemporaryFile(suffix='.js', delete=False, mode='w')
    temp_file.writelines(lines)
    temp_file.close()
    
    return temp_file.name



def get_assistant_id(assistant_type):
    '''
    어시스턴트를 아이디를 반환한다.

    profile_assistant: 코딩 컨벤션 프로파일링을 위한 assistant
    예제 코드 10개를 입력하여(10개인 이유는 API의 한계... 더 가능할 시 수정), 코딩 컨벤션을 분석한 결과를 반환한다.

    patch_assistant: 취약점 패치를 위한 assistant
    profile_assistant가 반환한 코딩 컨벤션 분석 결과와, 취약 소스코드를 입력하여 코드를 패치한다.

    explain_assistant: 취약점 패치 설명을 위한 assistant
    취약점이 존재하는 코드 파일과, 취약점 패치 후의 코드 파일을 diff 한 결과를 입력하여, 취약점과 패치 내용에 대한 설명을 반환받는다.
    '''

    if settings.ASSISTANT_ID[assistant_type] is None: # 만약 LLM_API_KEY 딕셔너리에 assistant id가 없다면 새로운 assistant를 만든다.
        raise Exception("Patch assistant is not defined.")
        
    return settings.ASSISTANT_ID[assistant_type]


def get_js_file_list(directory_path):
    '''
    특정 경로의 디렉터리에서 .js 파일 리스트를 재귀적으로 탐색하여 반환한다.
    '''
    file_list = []
    for path in glob.iglob(f'{directory_path}/**/*.js', recursive=True):
        file_list.append({"filename": os.path.basename(path), "path":path})
    return file_list



def save_js_file_list_to_jsonl(file_list, jsonl_file_path):
    '''
    file_list를 jsonl 파일로 저장한다.
    '''
    with open(jsonl_file_path, "w") as f:
        for file in file_list:
            f.write(json.dumps(file) + "\n")



def upload_files(file_list):
    '''
    파일 리스트를 입력받아 파일을 업로드하고, 업로드된 파일의 id 리스트를 반환한다.
    '''
    file_id_list = []
    for file in file_list:
        temp_file_path = preprocess_code(file['path'])
        print(f'[*] {temp_file_path}')
        assistant_file_object = upload_file(temp_file_path)
        file_id_list.append(assistant_file_object.id)
        os.remove(temp_file_path)
    return file_id_list



def create_attachments_list(file_id_list):
    '''
    파일 id 리스트를 입력받아 attachments 리스트를 생성한다.
    '''
    attachments_list = []
    for file in file_id_list:
        attachments_list.append({"file_id": file, "tools": [{"type": "file_search"}]}) 
    return attachments_list


def parse_codeql_csv(csv_file_path):
    '''
    Parses the output CSV file from CodeQL and returns a dictionary.
    '''

    f = open(csv_file_path, 'r', encoding='utf-8')
    rdr = csv.reader(f)

    vulnerabilities_list = list()
    for line in rdr:
        vulnerabilities_list.append(line)
    f.close()

    vulnerabilities_dict_list = list()
    for vulnerability_list in vulnerabilities_list:
        vulnerability_dict = dict()
        vulnerability_dict['name'] = vulnerability_list[0]
        vulnerability_dict['description'] = vulnerability_list[1]
        vulnerability_dict['severity'] = vulnerability_list[2]
        vulnerability_dict['message'] = vulnerability_list[3]
        vulnerability_dict['path'] = vulnerability_list[4]
        vulnerability_dict['start_line'] = int(vulnerability_list[5])
        vulnerability_dict['start_column'] = int(vulnerability_list[6])
        vulnerability_dict['end_line'] = int(vulnerability_list[7])
        vulnerability_dict['end_column'] = int(vulnerability_list[8])

        #print(vulnerability_dict)
        vulnerabilities_dict_list.append(vulnerability_dict)

    return vulnerabilities_dict_list
    

def get_absolute_path(base_path, file_path):
    return os.path.abspath(os.path.join(base_path, file_path))




'''
변수 선언
'''
# codeql csv 파일의 경로
codeql_csv_path = input("Enter the path of the CodeQL CSV file: ")
codeql_csv_path = os.path.abspath(codeql_csv_path)


# 프로젝트의 경로 = codeql csv 상의 경로의 베이스 경로
project_path = input("Enter the path of the project: ")
project_path = os.path.abspath(project_path)


print('-'*50)
print(f'CodeQL CSV path: {codeql_csv_path}')
print(f'Project path: {project_path}')
print('-'*50)



'''
프로젝트 경로로부터 .js 파일 리스트 뽑기
'''
file_list = get_js_file_list(project_path)
print("File list:")
print(file_list)
print('-'*50)




'''
.js 파일들을 client에 업로드
'''
file_id_list = upload_files(file_list)
print("Uploaded file id list:")
print(file_id_list)
print('-'*50)



'''
코딩 스타일 프로파일을 위한 thread 생성
'''
profile_thread  = client.beta.threads.create() # 대화 세션 정도로 이해하면 될 듯



'''
코딩 스타일 추출 메시지에 첨부할 메시지 리스트 생성
'''
codebase_example_attachments_list = create_attachments_list(file_id_list)



'''
프로파일 생성 요청 메시지들을 스레드에 추가
'''
message = client.beta.threads.messages.create(
    thread_id=profile_thread.id,
    role="user",
    content=instructions.instruction_analysis_coding_convention,
    attachments=codebase_example_attachments_list,
)



'''
스레드 실행
'''
profile_run = client.beta.threads.runs.create(
    thread_id=profile_thread.id,
    assistant_id=get_assistant_id('profile_assistant')
)



start_time = time.time()


status = check_status(profile_run.id, profile_thread.id)
while status != 'completed':
    time.sleep(1)
    status = check_status(profile_run.id, profile_thread.id)



elapsed_time = time.time() - start_time
print("Elapsed time: {} minutes {} seconds".format(int((elapsed_time) // 60), int((elapsed_time) % 60)))
print(f'Status: {status}')
print('-'*50)


'''
thread의 메시지 목록 가져오기
'''
messages = client.beta.threads.messages.list(
    thread_id=profile_thread.id
)


'''
llm의 프로파일 결과 출력
'''
llm_profile_result = messages.data[0].content[0].text.value
print(llm_profile_result)
print('-'*50)


'''
llm의 출력 결과에서 코딩 컨벤션 프로파일(json 형태)만 추출
'''
print("Coding convention profile:")
extracted_codes_from_llm_profile_result = extract_code(llm_profile_result)
for code in extracted_codes_from_llm_profile_result:
    if code[0] == 'json':
        print(code[1])





'''
assistant 한 번 만들면 언제까지 유지되는가? (지우지 않으면 유지되는 듯)
이건 다른 프로젝트(다른 코드베이스) 사이에서 공유되어도 됨


thread의 개념...
한 프로젝트 내에서는 같은 thread 사용하면 될 듯 함



파일 upload 하면 같은 assistant 내에서 유지되는지
assistant나 thread가 아니라, client 내에서 계속해서 유지되는 듯 하다.
the size of all files uploaded by one organization can be up to 100 GB.
'''