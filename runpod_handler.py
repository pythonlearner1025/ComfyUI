import websocket
import os
import uuid
import json
import urllib.request
import urllib.parse
import runpod
import tempfile
from supabase import create_client, Client
from util import modify_workflow
from dotenv import load_dotenv

load_dotenv()

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    return filename

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            print("--history node output--")
            print(node_output)
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    print(f"--img is at: {image['filename']}--")
                    image_f = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_f)
            output_images[node_id] = images_output

    return output_images

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

ROOT = os.path.dirname(os.path.relpath(__file__))
config_loc = os.path.join(ROOT, 'configs', 'inference.json')
models_dir = os.path.join(ROOT, 'models')
loras_dir = os.path.join(ROOT, 'models/loras')
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def request_image(job):
    with open(config_loc, 'r') as f:
        flow = json.load(f)
    args = job["input"]
    user_id = args["user_id"]
    prompt_p = args['prompt_p']
    prompt_n = args['prompt_n']
    BS = int(args['BS'])
    seed = int(args['seed'])
    lora_id = args['lora_id']
    lora_loc = os.path.join(loras_dir, lora_id)

    # check if lora_id exists
    if not os.path.exists(lora_loc):
        if not os.path.exists(loras_dir): os.mkdir(loras_dir)
        with open(lora_loc, 'wb+') as f:
            res = supabase.storage.from_('Loras').download(f'loras/{lora_id}')
            f.write(res)
     
    with tempfile.TemporaryDirectory() as temp_d:
        modify_workflow(flow, temp_d, lora_id, prompt_p, prompt_n, bs=BS, seed=seed)
        print(flow)
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))

        imgs_data = get_images(ws, flow)
        # send these imgs
        paths = []
        for k,batch_imgs in imgs_data.items():
            batch_id = str(uuid.uuid4())
            for i,img in enumerate(batch_imgs):
                #img_id = str(uuid.uuid4())
                path = f'{user_id}/{lora_id}/{batch_id}/{i}.png'
                with open(img, 'rb') as f:
                    supabase.storage.from_("Photos").upload(
                        path=path,
                        file=f,
                        file_options={"content-type": "image/png"}
                    )
                paths.append(path)

    return paths

if __name__ == '__main__':
    runpod.serverless.start({
        'handler': request_image,
        "return_aggregate_stream": True
    })
