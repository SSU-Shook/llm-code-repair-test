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
    # codeql csv 파일의 경로
    vulnerable_code_path = input("Enter the path of the vulnerable code: ")
    vulnerable_code_path = os.path.abspath(vulnerable_code_path)

    # 프로젝트의 경로 = codeql csv 상의 경로의 베이스 경로
    patched_code_path = input("Enter the path of the patched code: ")
    patched_code_path = os.path.abspath(patched_code_path)

    print('-'*50)
    print(f'CodeQL CSV path: {vulnerable_code_path}')
    print(f'Project path: {patched_code_path}')
    print('-'*50)

    # profile_assistant를 사용하여 코딩 컨벤션 프로파일링 결과를 얻는다. (json 문자열 형태)
    code_patch_explanation = sast_llm.explain_patch(vulnerable_code_path, patched_code_path, zero_shot_cot=False)
    print(code_patch_explanation)



if __name__ == "__main__":
    main()
