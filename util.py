import json
from urllib import request
import random

def set_seeds(data, seed):
    # Load the JSON data from the file
    for node_id, node_data in data.items():
        # Check if the node is a KSampler
        if node_data.get('class_type') == 'KSampler':
            # Generate a random 15-digit integer
            data[node_id]['inputs']['seed'] = seed if seed else random.randint(100000000000000, 999999999999999)

def modify_workflow(flow, name, lora_id, prompt_p, prompt_n, bs=8, seed=None):
    set_seeds(flow, seed)
    flow["123"]["inputs"]["filename_prefix"] = name
    ckpt_node = flow['4']['inputs']
    lora_node = flow['49']['inputs']
    prompt_neg_node = flow['7']['inputs']
    prompt_pos_node = flow["6"]['inputs']
    ksampler_node = flow["107"]['inputs'] 
    latent_node = flow["5"]["inputs"]
    #save_image_node = flow["9"]['inputs']
    lora_node["lora_name"] = lora_id
    prompt_pos_node["text"] = prompt_p
    prompt_neg_node['text'] = prompt_n
    ksampler_node["steps"] = 15
    latent_node['batch_size'] = bs
    # verify this works

import traceback

def test_queue_prompt():
    try:
        req = request.Request("http://127.0.0.1:8188/prompt", method='GET') 
        response = request.urlopen(req)
        print(response.read().decode('utf-8'))
    except Exception as e:
        print(e)

def prompt_n(gender):
    return f"headshot of ohw a {gender}, beauty light headshot, continuous light, suit and tie clothing, close up"

def prompt_p(gender):
    neg = "woman, makeup" if gender == 'man' else "man, beard"
    return f'{neg}, gray background, black background, harsh shadows, bad eyes, serious, casual, selfie, female, painting, drawing, cartoon character, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured, asian,chinese,text,error,cropped,ugly,duplicate,morbid,mutilated,out of frame,extra fingers,mutated hands,poorly drawn hands,poorly drawn face,mutation,deformed,dehydrated,bad anatomy,bad proportions,extra limbs,cloned face,disfigured,gross proportions,malformed limbs,missing arms,missing legs,extra arms,extra legs,fused fingers,too many fingers,long neck,username,watermark,signature,'
