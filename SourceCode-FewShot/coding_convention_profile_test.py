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
import sast_llm


def main():
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

    # profile_assistant를 사용하여 코딩 컨벤션 프로파일링 결과를 얻는다. (json 문자열 형태)
    coding_convention_profile_json = sast_llm.profile_coding_convention(project_path, zero_shot_cot=True)
    print(coding_convention_profile_json)




if __name__ == "__main__":
    main()
