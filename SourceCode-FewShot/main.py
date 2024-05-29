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

def extract_code(text): # LLM의 출력에서 코드만 추출하여 배열로 반환
    try:
        if '```' in text:
            matches = re.findall(r'`{3}.*?\n(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]
    
    '''
    function = None
    match = re.search('```(.*?)```', code, re.DOTALL)
    if match:
        function = match.group(1)
        function = function.replace("python","")

    if function != None:
        if len(Check_Syntax(function)) != 0:
            return None
        
    return function
    '''


def diff_code(code1, code2):
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)


def check_status(run_id,thread_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

def upload_file(uploaded_file):
    global client
    with open(uploaded_file, "rb") as f:
        file = client.files.create(
            file=f,
            purpose = 'assistants'
        )
        print(file)
    return file

# def preprocess_code(file_path):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
    
#     if lines and lines[0].startswith('#!'):
#         lines = lines[1:]
    
#     temp_dir = tempfile.mkdtemp()

#     temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
#     with open(temp_file_path, 'w') as temp_file:
#         temp_file.writelines(lines)

#     # temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
#     # temp_file.writelines(lines)
#     # temp_file.close()
    
#     return temp_file_path

def preprocess_code(file_path):
    with open(file_path, 'r', encoding='UTF8') as file:
        lines = file.readlines()
    
    if lines and lines[0].startswith('#!'):
        lines = lines[1:]

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
    temp_file.writelines(lines)
    temp_file.close()
    
    return temp_file.name


# instruction_assistance = 
'''
You are a program development tool that takes in source code and fixes vulnerabilities.
'''
assistant_id = ''
if settings.LLM_API_KEY['assistant'] is None:
    # create assistant
    assistant = client.beta.assistants.create(
        name="Code Refactorer",
        instructions=instructions.instruction_assistance,
        tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
        model="gpt-4o",
    )
    assistant_id = assistant.id
    print(f'Created new assistant : {assistant.id}')
    

else :
    assistant_id = settings.LLM_API_KEY['assistant']
    print(f'Loaded existing assistant : {assistant_id}')
    
    

# .js filename list & write to .jsonl file
# get ./example dir .js list glob
with open("filelist.jsonl", "w") as f:
    for path in glob.iglob('example/**/*.js', recursive=True):
        f.write(json.dumps({"filename": os.path.basename(path), "path":path}) + "\n")

with open("filelist.jsonl", "r") as f:
    print(f.read())

# Upload the codebase
file_list = []
file_id_list = []

with open("filelist.jsonl", "r") as f:
    for line in f:
        file_list.append(json.loads(line))

for file in file_list:
    temp_file_path = preprocess_code(file['path'])
    print(f'[*] {temp_file_path}')
    assistant_file_id = upload_file(temp_file_path)
    file_id_list.append(assistant_file_id)
    os.remove(temp_file_path)

thread  = client.beta.threads.create()

attachments_list = []
for file in file_id_list:
    attachments_list.append({"file_id": file.id, "tools": [{"type": "code_interpreter"}]})
'''
code_interpreter
'''


#instruction_learning_code = 
'''
Maintain Consistency:
- Use a consistent coding style throughout the codebase.
- Follow the existing conventions for naming variables, functions, and classes.
- Follow the same rules for variable naming, indentation, spacing, and commenting

Don't spit out output, just learn the source code. **Don't say anything!**
'''
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=instructions.instruction_learning_code,
    attachments=attachments_list[:10], #documentation에서는 20개로 나와있는데, 여기서는 10개 넘었다고 오류 발생, 일단 10개로 바꾸어 봄
)
'''
openai.BadRequestError: Error code: 400 - {'error': {'message': "Invalid 'attachments': array too long. 
Expected an array with maximum length 10, but got an array with length 12 instead.", 
'type': 'invalid_request_error', 'param': 'attachments', 'code': 'array_above_max_length'}}        
'''
#https://platform.openai.com/docs/assistants/how-it-works/agents


my_run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id
)

start_time = time.time()
status = check_status(my_run.id,thread.id)

while status != 'completed':
    time.sleep(1)
    status = check_status(my_run.id,thread.id)

print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
print(f'Status: {status}')

messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

print(messages)



script_directory = os.path.dirname(os.path.realpath(__file__)) #파이썬 스크립트가 존재하는 디렉터리

csv_file_path = input("input csv file path: ")
csv_name = os.path.basename(csv_file_path)

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

print(vulnerability_dict)
vulnerabilities_dict_list.append(vulnerability_dict)



response = client.beta.threads.delete(thread.id)
# response = client.beta.assistants.delete(assistant.id)
for my_file in file_id_list:
    response = client.files.delete(my_file.id)




'''
assistant 한 번 만들면 언제까지 유지되는가?
thread의 개념...
'''