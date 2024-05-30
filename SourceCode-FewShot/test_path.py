import os
import glob

def find_js_files(directory):
    # 지정된 디렉토리에서 모든 .js 파일의 전체 경로를 찾아 리스트로 반환
    # glob.glob의 '**'는 모든 하위 디렉토리를 포함하며, recursive=True 옵션을 사용해야 함
    return glob.glob(os.path.join(directory, '**/*.js'), recursive=True)

# 사용 예시
directory_path = input()  # 검색을 시작할 디렉토리 경로
js_files = find_js_files(directory_path)
print(js_files)