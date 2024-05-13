import math
import time
import csv
import os
import datetime
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import sys

from env import settings
import difflib
import re


gemini_safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]



def extract_code(text):
    try:
        if '```' in text:
            matches = re.findall(r'`{3}(.*?)`{3}', text, re.DOTALL)
            return matches

        else:
            return [text,]
        
    except Exception as exception:
        return [text,]



def diff_code(code1, code2):
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)



openai_api_key = settings.LLM_API_KEY['openai'] #OpenAI API Key
anthropic_api_key = settings.LLM_API_KEY['anthropic'] #Anthropic(Claude) API Key
gemini_api_key = settings.LLM_API_KEY['gemini'] #Gemini API Key


openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = Anthropic(
    # This is the default and can be omitted
    api_key=anthropic_api_key
)
genai.configure(api_key=gemini_api_key)


script_directory = os.path.dirname(os.path.realpath(__file__)) #파이썬 스크립트가 존재하는 디렉터리


csv_file_path = input("input csv file path: ") #csv 파일은 절대경로로 입력받음
csv_name = os.path.basename(csv_file_path)


f=open(csv_file_path, 'r', encoding='utf-8')
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
    print('\n'*3)


prompt_with_comment='''You are a tool that takes in source code, patches the vulnerability, and outputs it.
The input is always given as source code. The comments contain information about the vulnerability.
You should always output only the source code.
If you need an explanation of what was fixed, add a comment to the source code.
''' # 기본 프롬프트. LLM의 역할 명시, 입력 형태와 출력 형태를 명시.

prompt_with_comment_prefix='''You are a tool that takes in source code, patches the vulnerability, and outputs it.
The input is always given as source code. Information about the vulnerability is located after "vulnerability:" string in the comments area.
You should always output only the source code.
If you need an explanation of what was fixed, add a comment to the source code.
''' # 주석의 어느 부분(vulnerability: 문자열 뒤)에 취약점 정보가 존재하는지 구체적으로 명시

prompt_psuedo_cot='''You are a program development tool that takes in source code and fixes vulnerabilities.
The input is given as source code. The comments in the source code contain information about the vulnerability. Comments for vulnerability information start with the string "vulnerability:".
Analyze the input source code and explain what each line does. And be specific about why the vulnerability occurs. Describe information about the vulnerability. Explain specifically what needs to be done to fix the vulnerability.

Afterward, print out the source code with the vulnerability patched.
''' #패치된 코드를 출력하기 전에 각 줄에 대한 설명, 취약점에 대한 설명 등을 요구함. 그 이후 패치가 완료된 코드 출력을 요구함. Chain Of Thought 효과 기대
# Large Language Models are Zero-Shot Reasoners: https://arxiv.org/pdf/2205.11916.pdf


prompt_by_claude='''You are a highly skilled security analyst tasked with fixing a vulnerability in the following source code:

[Paste the source code here, including any annotations or comments about the vulnerability]

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
- Claude가 작성한 프롬프트
'''



log_file = open(script_directory+"/logs/"+csv_name+'.log', "a")



for vulnerability_dict in vulnerabilities_dict_list:
    system_prompt=prompt_with_comment_prefix

    source_file_path = os.path.abspath(script_directory + vulnerability_dict['path'])

    original_code=str()
    patched_code=str()

    with open(source_file_path, 'r') as file:
        #diff code - 위에 함수 적용 가능하도록        #코드 추출 -- langchain coder 참고
        original_code = file.read()
        lines = original_code.splitlines()
            

    _, extension = os.path.splitext(source_file_path)
    



    if extension in ['py',]:
        lines[vulnerability_dict['start_line']-1] += " #vulnerability: " + vulnerability_dict['description'] #취약점이 발견된 줄 뒤에 한 줄 주석으로 codeql의 description 추가
    else:
        lines[vulnerability_dict['start_line']-1] += " //vulnerability: " + vulnerability_dict['description'] #취약점이 발견된 줄 뒤에 한 줄 주석으로 codeql의 description 추가


    code_commented = '\n'.join(lines)
    print(code_commented)
    

    print("\n"*5)
    log_file.write("\n"*5+'\n')

    print(source_file_path)
    log_file.write(source_file_path+'\n')

    log_file.write(code_commented+'\n')

    print('\n'*2+"system prompt")
    print(system_prompt+'\n'*3)
    log_file.write('\n'*2+"system prompt")
    log_file.write('\n'*2+system_prompt+'\n')

    print("\n"*3)
    log_file.write("\n"*3+'\n')


    llm_models_list = [
        ('openai', 'gpt-4'),
        ('openai', 'gpt-3.5-turbo'),
        ('anthropic', 'claude-3-opus-20240229'),
        ('gemini', 'gemini-1.5-pro-latest')
    ]


    for llm_model_tuple in llm_models_list:
        start = time.time()
        (llm_brand, llm_model) = llm_model_tuple

        if llm_brand == 'openai':
            completion = openai_client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code_commented}
            ]
            )
            llm_output = completion.choices[0].message.content


        elif llm_brand == 'anthropic':
            continue #Claude은 현재 사용하지 않음
            message = anthropic_client.messages.create(
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": code_commented,
                    }
                ],
                model=llm_model, system=system_prompt
            )
            llm_output = message.content[0].text

        
        elif llm_brand == 'gemini':
            model = genai.GenerativeModel(model_name=llm_model, 
                                          system_instruction=system_prompt, 
                                          safety_settings=gemini_safety_settings)
            response = model.generate_content(code_commented)
            llm_output = response.text            


        patched_code=extract_code(llm_output)[-1]
        diff_code_output = diff_code(original_code, patched_code)


        #print diffing results to console and log file
        for output_file in [sys.stdout, log_file]:
            print('\n\nDiff Code', file=output_file)
            print(diff_code_output, file=output_file)

            print("\n\n// llm model: "+llm_model, file=output_file)

            print(patched_code, file=output_file)

            print("\n"*3, file=output_file)

            
            end = time.time()
            print(f"{end - start:.5f} sec", file=output_file)

log_file.close()