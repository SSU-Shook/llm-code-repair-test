import difflib

code1='''
Learning
Python
is
too
simple.
'''


code2='''
Learning
Python
is
too


simple.
'''


def diff_code(code1, code2):
    code1 = code1.splitlines()
    code2 = code2.splitlines()
    diff = difflib.unified_diff(code1, code2, lineterm='')
    return '\n'.join(diff)



print(diff_code(code1, code2))