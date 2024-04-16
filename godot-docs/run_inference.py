import subprocess
import json

def get_similar_content(query):
    return subprocess.getoutput(f'llm similar blog-paragraphs -c "{query}" | jq')

def parse_similar_jsons(json_text):
    lines = json_text.split("\n")
    dicts = []
    current = []
    for line in lines:
        current.append(line)
        if "}" in line:
            dicts.append(current)
            current = []
    return [json.loads("\n".join(d)) for d in dicts]

def pick_highest_score_prompt(json_text):
    passages = parse_similar_jsons(json_text)
    m = 0
    p = None
    for passage in passages:
        score = passage["score"]
        if score > m:
            m = score
            p = passage["content"]
    return p

query = "How are Characters represented in Godot?" # "How do you represent a Character in Godot?"
json_text = get_similar_content(query)
passage = pick_highest_score_prompt(json_text)
output = subprocess.getoutput(
    f'llm -m mlc-chat-Llama-2-7b-chat-hf-q4f16_1 "{query} {passage}" -s "You answer questions"'
)
print(output)
