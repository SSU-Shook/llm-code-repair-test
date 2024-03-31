import csv
import os
from openai import OpenAI
from env import settings

openai_api_key = settings.LLM_API_KEY['openai']

client = OpenAI(api_key=openai_api_key)

script_directory = os.path.dirname(os.path.realpath(__file__))


csv_file_path = input("input csv file path: ")

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


prompt='''You are a tool that takes in source code, patches the vulnerability, and outputs it.
The input is always given as source code. The comments contain information about the vulnerability.
You should always output only the source code.
If you need an explanation of what was fixed, add a comment to the source code.
'''

prompt2='''You are a tool that takes in source code, patches the vulnerability, and outputs it.
The input is always given as source code. Information about the vulnerability is located after "vulnerability:" string in the comments area.
You should always output only the source code.
If you need an explanation of what was fixed, add a comment to the source code.
'''


for vulnerability_dict in vulnerabilities_dict_list:
    source_file_path = os.path.abspath(script_directory + vulnerability_dict['path'])

    lines = list()
    with open(source_file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    lines[vulnerability_dict['start_line']-1] += " //vulnerability: " + vulnerability_dict['description']

    print("\n"*5)
    print(source_file_path)
    code_commented = '\n'.join(lines)
    print(code_commented)
    print("\n"*3)



    llm_models = [
        'gpt-4',
        'gpt-3.5-turbo',
    ]


    for llm_model in llm_models:
        completion = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": prompt2},
            {"role": "user", "content": code_commented}
        ]
        )

        print("llm model: "+llm_model)
        print(completion.choices[0].message.content)
        print("\n"*3)