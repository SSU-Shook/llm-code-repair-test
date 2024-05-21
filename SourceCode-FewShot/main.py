import os
import time
import json
import glob
import difflib
import re
from env import settings
from openai import OpenAI
import tempfile


'''
Todo
# - .js filename list & path to .jsonl file
# - Upload the codebase
- Few-shot prompting with .jsonl lists
- query the model for the output
    - match code style with few-shot prompt
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

def extract_code(text):
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)`{3}', text, re.DOTALL)
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

def upload_file(assistant_id, uploaded_file):
    global client
    with open(uploaded_file, "rb") as f:
        file = client.files.create(
            file=f,
            purpose = 'assistants'
        )
        print(file)
    return file

def preprocess_code(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    if lines and lines[0].startswith('#!'):
        lines = lines[1:]

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
    temp_file.writelines(lines)
    temp_file.close()
    
    return temp_file.name

instruction = '''
You are a program development tool that takes in source code and fixes vulnerabilities.
'''.strip()

# create assistant
# assistant = client.beta.assistants.create(
#     name="Code Refactorer",
#     instructions=instruction,
#     tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
#     model="gpt-4o",
# )
# id : asst_V3qdl7fwrsz1CI6iC3a1ZCuZ

# .js filename list & write to .jsonl file
# get ./example dir .js list glob
for path in glob.iglob('example/**/*.js', recursive=True):
    with open("filelist.jsonl", "a+") as f:
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
    # file_id = client.files.create(
    #     file = file['path'],
    #     # file=open(file['path'], "rb"),
    #     # purpose="user_data",
    #     purpose="assistants"
    # )
    temp_file_path = preprocess_code(file['path'])
    assistant_file_id = upload_file(settings.LLM_API_KEY['assistant'], temp_file_path)
    file_id_list.append(assistant_file_id)
    os.remove(temp_file_path)

    # client.beta.assistants.files.create(assistant_id=assistant_id, file_id=uploaded_file.id)

print(file_id_list)

prompt_instruction = '''
You are a highly skilled security analyst tasked with fixing a vulnerability in the following source code:

Your task is to carefully review the code, identify the root cause of the vulnerability, and provide a detailed explanation of how to fix it. Please provide your analysis and proposed solution in the following format:

1. Vulnerability Summary:
   - Briefly describe the type of vulnerability and its potential impact.

2. Root Cause Analysis:
   - Explain the specific code patterns, design flaws, or coding practices that led to this vulnerability.
   - Provide line numbers or code snippets to illustrate the problematic areas.

3. Proposed Solution:
   - Outline the steps or code changes required to remediate the vulnerability.
   - If applicable, provide sample code snippets or pseudocode to demonstrate the secure implementation.

4. Additional Considerations:
   - Mention any potential side effects, trade-offs, or best practices to consider when implementing the proposed solution.
   - Suggest any additional security measures or coding practices that could further strengthen the codebase.

Please provide a thorough and actionable response, ensuring that your proposed solution effectively mitigates the identified vulnerability while adhering to secure coding principles and best practices.'''
'''
I'm working on a project to fix a vulnerability by entering the source code into LLM.
The source code is annotated with information about the vulnerability.
Please create a prompt for me to enter the LLM.
'''

thread  = client.beta.threads.create()

# thread = client.beta.threads.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "summarize this code",
#             "attachments": [
#                 {
#                     "file_id": file_id_list[0],
#                     "tools": [{"type": "code_interpreter"}]
#                 }
#             ]
#         }
#     ]
# )

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="summarize this attachments code",
    attachments=[
        {
            "file_id": file_id_list[0].id,
            "tools": [{"type": "code_interpreter"}]
        }
    ]
)


my_run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=settings.LLM_API_KEY['assistant'],
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
