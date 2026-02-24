from textnode import *
from blocknode import *
from htmlnode import *
from generation import *
import os
import shutil

def static_to_public():
    if os.path.exists('public'):
        shutil.rmtree('public')
    shutil.copytree('static', 'public')

    for root, dirs, files in os.walk('content'):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                rel_path = os.path.relpath(md_path, 'content')
                html_path = os.path.splitext(rel_path)[0] + '.html'
                dest_path = os.path.join('public', html_path)
                generate_page(md_path, 'template.html', dest_path)
    

if __name__ == "__main__":
    text_node = TextNode('This is some anchor text', 'link', 'https://www.boot.dev')
    print(text_node)

    static_to_public()