import csv
import os
import datetime
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from env import settings



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


prompt_by_claude_head='''You are a highly skilled security analyst tasked with fixing a vulnerability in the following source code:

'''



prompt_by_claude_tail='''Your task is to carefully review the code, identify the root cause of the vulnerability, and provide a detailed explanation of how to fix it. Please provide your analysis and proposed solution in the following format:

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



now = datetime.datetime.now()
log_filename = now.strftime(csv_name+"_"+"%Y-%m-%d-%H-%M.log")
log_file = open(log_filename, "w")



for vulnerability_dict in vulnerabilities_dict_list:
    source_file_path = os.path.abspath(script_directory + vulnerability_dict['path'])

    lines = list()
    with open(source_file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    lines[vulnerability_dict['start_line']-1] += " //vulnerability: " + vulnerability_dict['description'] #취약점이 발견된 줄 뒤에 한 줄 주석으로 codeql의 description 추가

    code_commented = '\n'.join(lines)
    print(code_commented)

    print("\n"*5)
    log_file.write("\n"*5+'\n')

    print(source_file_path)
    log_file.write(source_file_path+'\n')

    log_file.write(code_commented+'\n')

    print("\n"*3)
    log_file.write("\n"*3+'\n')


    llm_models_list = [
        ('openai', 'gpt-4'),
        ('openai', 'gpt-3.5-turbo'),
        ('anthropic', 'claude-3-opus-20240229'),
        ('gemini', 'gemini-pro')
    ]

    crafted_prompt=prompt_by_claude_head + code_commented + prompt_by_claude_tail

    for llm_model_tuple in llm_models_list:
        (llm_brand, llm_model) = llm_model_tuple
        result_code = str()

        if llm_brand == 'openai':
            completion = openai_client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "user", "content": crafted_prompt},
            ]
            )
            result_code = completion.choices[0].message.content


        elif llm_brand == 'anthropic':
            message = anthropic_client.messages.create(
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": crafted_prompt,
                    }
                ],
                model=llm_model
            )
            result_code = message.content[0].text

        
        elif llm_brand == 'gemini':
            model = genai.GenerativeModel(llm_model)
            response = model.generate_content(crafted_prompt)
            result_code = response.text            


        print("// llm model: "+llm_model)
        log_file.write("// llm model: "+llm_model+'\n')

        print(result_code)
        log_file.write(result_code+'\n')

        print("\n"*3)
        log_file.write("\n"*3+'\n')

        log_file.flush()

log_file.close()