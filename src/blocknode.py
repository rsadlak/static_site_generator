
from textnode import *
from htmlnode import *
from enum import Enum
import re

class BlockType(Enum):    
    PRAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered list"
    ORDERED_LIST = "ordered list"


def markdown_to_blocks(markdown):
    blocks = []

    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks if block.strip()]

    return blocks

def block_to_block_type(block):
    if block.startswith("# ") or block.startswith("## ") or block.startswith("### ") or block.startswith("#### ") or block.startswith("##### ") or block.startswith("###### "):
        return BlockType.HEADING
    elif block.startswith("- "):
        return BlockType.UNORDERED_LIST
    elif re.match(r"^\d+\. ", block):
        return BlockType.ORDERED_LIST
    elif block.startswith("> "):
        return BlockType.QUOTE
    elif block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    else:
        return BlockType.PRAGRAPH
    
def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            # Determine heading level
            level = len(block.split(' ')[0])
            tag = f"h{level}"
            content = block[level+1:].strip()
            children.append(LeafNode(tag, content))
        elif block_type == BlockType.UNORDERED_LIST:
            from textnode import text_to_textnodes, text_node_to_html_node
            items = [item[2:].strip() for item in block.split('\n') if item.startswith('- ')]
            li_nodes = []
            for item in items:
                text_nodes = text_to_textnodes(item)
                html_nodes = [text_node_to_html_node(node) for node in text_nodes]
                li_nodes.append(ParentNode('li', html_nodes))
            children.append(ParentNode('ul', li_nodes))
        elif block_type == BlockType.ORDERED_LIST:
            from textnode import text_to_textnodes, text_node_to_html_node
            items = [re.sub(r'^\d+\. ', '', item).strip() for item in block.split('\n') if re.match(r'^\d+\. ', item)]
            li_nodes = []
            for item in items:
                text_nodes = text_to_textnodes(item)
                html_nodes = [text_node_to_html_node(node) for node in text_nodes]
                li_nodes.append(ParentNode('li', html_nodes))
            children.append(ParentNode('ol', li_nodes))
        elif block_type == BlockType.QUOTE:
            content = '\n'.join([line[2:].strip() for line in block.split('\n') if line.startswith('> ')])
            children.append(LeafNode('blockquote', content))
        elif block_type == BlockType.CODE:
            content = block.strip('`')
            children.append(ParentNode('pre', [LeafNode('code', content)]))
        else:
            # Paragraph, with inline markdown parsing
            from textnode import text_to_textnodes, text_node_to_html_node
            text_nodes = text_to_textnodes(block)
            html_nodes = [text_node_to_html_node(node) for node in text_nodes]
            children.append(ParentNode('p', html_nodes))
    return ParentNode('div', children)

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block[2:].strip()
        else:
            raise Exception("No title found in markdown")