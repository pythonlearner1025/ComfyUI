import subprocess

def execute_command(command):
    print(f'executing cmd: {command}')
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    code = process.returncode
    return stdout.decode('utf-8'), stderr.decode('utf-8'), code

import json

i = {
    "user_id": "minjunes",
    "lora_id": "3c37d.safetensors",
    "prompt_p": "happy man",
    "prompt_n": "sad",
    "BS": "4",
    "seed": 0,
}

d = {
    "input": i
}

cmd = f'conda run python runpod_handler.py --test_input \'{json.dumps(d)}\''
#cmd = f'conda run python scripts/train.py'
o, e, c = execute_command(cmd)
print(o, e)