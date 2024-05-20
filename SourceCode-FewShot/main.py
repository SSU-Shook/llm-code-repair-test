import os
from openai import OpenAI
import time
import json
import glob

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

# Setting the API key
OpenAI.api_key = os.environ['OPENAI_API_KEY']

try:
    client = OpenAI()
except:
    print("OpenAI() failed")
    
# Get model list
# print(client.models.list())
# Our Target Model
# Model(id='gpt-4o-2024-05-13', created=1715368132, object='model', owned_by='system')

try:
    os.system("rm mydata.jsonl")
except:
    pass

# .js filename list & write to .jsonl file
# get ./example dir .js list glob
for path in glob.iglob('example/**/*.js', recursive=True):
    with open("mydata.jsonl", "a+") as f:
        f.write(json.dumps({"filename": os.path.basename(path), "path":path}) + "\n")

with open("mydata.jsonl", "r") as f:
    print(f.read())

# Upload the codebase
client.files.create(
    file=open("mydata.jsonl", "rb"),
    purpose="assistant"
)


# assistant = client.beta.assistants.create(
#     name="Data visualizer",
#     description="You are great at creating beautiful data visualizations. You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed.",
#     model="gpt-4o",
#     tools=[{"type": "code_interpreter"}],
#     tool_resources={
#         "code_interpreter": {
#             "file_ids": [file.id]
#         }
#     }
# )