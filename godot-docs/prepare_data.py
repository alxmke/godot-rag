from bs4 import BeautifulSoup
import csv
import os
import re

def get_article_html(html_path):
    do_print = False
    open_divs = 0
    lines = []
    with open(html_path, 'r', encoding='utf-8') as f:
        for line in f:
            if str(line).startswith('<div itemprop="articleBody">'):
                do_print = True
                open_divs += 1
            if do_print:
                line = re.sub('[¶]', '', line)
                lines.append(line)
                
                if str(line).startswith("<div"):
                    open_divs += 1
                elif str(line).startswith("</div>"):
                    open_divs -= 1
                if open_divs < 1:
                    do_print = False
    return "".join(lines)

def get_html_as_plaintext(html):
    soup = BeautifulSoup(html)
    plaintext = soup.get_text()
    return plaintext

global_cleans = []
# for convenience and effiency, global_cleans is used instead of merging lists
def clean_article_plaintext(text):
    lines = text.split("\n")
    
    i = 0
    n = len(lines)
    
    # skip initial empty lines
    while i < n:
        line = str(lines[i])
        if line and not line.isspace():
            if line.startswith("Attention: Here be dragons"):
                i+=7 # warning spam message is 7 lines long
            else:
                break
        i+=1

    cleaning = []
    skip_empties = 0
    while i < n:
        if skip_empties < 1:
            cleaning.append(lines[i])
        else:
            skip_empties -= 1
        
        # skip next 3 empties if 3 in a row, store current block
        if i+3 < n:
            nxt1 = lines[i+1]
            nxt2 = lines[i+2]
            nxt3 = lines[i+3]
            if (not nxt1 or str(nxt1).isspace()) and (not nxt2 or str(nxt2).isspace()) and (not nxt3 or str(nxt3).isspace()):
                skip_empties = 3
                if cleaning:
                    clean = "\n".join(cleaning)
                    row = (len(global_cleans)+1, f"passage: {clean}")
                    global_cleans.append(row)
                    cleaning = []
        i+=1
    
    if cleaning:
        clean = "\n".join(cleaning)
        row = (len(global_cleans)+1, f"passage: {clean}")
        global_cleans.append(row)

def is_html(filename):
    return str(filename).endswith(".html")

def recurse_html(path):
    filenames = os.listdir(path)
    for filename in filenames:
        file = os.path.join(path, filename)
        if os.path.isdir(file):
            recurse_html(file)
        elif is_html(filename):
            article_html = get_article_html(file)
            plaintext = get_html_as_plaintext(article_html)
            clean_article_plaintext(plaintext)

html_path = "."
recurse_html(html_path)
output_csv_path = "godot_doc_sections.csv"
with open(output_csv_path, "w", encoding='utf-8', newline="") as f:
    csv_out = csv.writer(f)
    csv_out.writerow(["id", "section"])
    for row in global_cleans:
        try:
            csv_out.writerow(row)
        except Exception as e:
            print(str(e))
            print(row)