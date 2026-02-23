from enum import Enum
from htmlnode import LeafNode, HtmlNode, ParentNode
import re


class TextType(Enum):
    TEXT = "plain text"
    BOLD = "**bold text**"
    ITALIC = "_italic_"
    CODE = "`code text`"
    LINKS = "[anchor text](url)"
    IMAGE = "![alt text](url)"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __repr__(self):
        return f"TextNode(text='{self.text}', text_type='{self.text_type}', url='{self.url}')"

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return NotImplemented
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )
    

# Standalone function for converting TextNode to HTML node
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINKS:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Unsupported text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        # Support for LeafNode (used in some tests)
        from htmlnode import LeafNode
        if isinstance(node, LeafNode):
            parts = node.value.split(delimiter)
            if len(parts) == 1:
                new_nodes.append(node)
                continue
            for i, part in enumerate(parts):
                if part:
                    new_nodes.append(LeafNode(text_type, part))
                if i < len(parts) - 1:
                    new_nodes.append(LeafNode(None, delimiter))
        # Support for TextNode (used in main code)
        elif isinstance(node, TextNode) and node.text_type == TextType.TEXT:
            parts = node.text.split(delimiter)
            if len(parts) == 1:
                new_nodes.append(node)
                continue
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        new_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    if part:
                        new_nodes.append(TextNode(part, text_type))
        else:
            new_nodes.append(node)
    return new_nodes

def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if isinstance(node, TextNode) and node.text_type == TextType.TEXT:
            images = extract_markdown_images(node.text)
            if images:
                last_index = 0
                for alt_text, url in images:
                    start_index = node.text.find(f"![{alt_text}]({url})", last_index)
                    if start_index != -1:
                        if start_index > last_index:
                            new_nodes.append(TextNode(node.text[last_index:start_index], TextType.TEXT))
                        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
                        last_index = start_index + len(f"![{alt_text}]({url})")
                if last_index < len(node.text):
                    new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
            else:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if isinstance(node, TextNode) and node.text_type == TextType.TEXT:
            links = extract_markdown_links(node.text)
            if links:
                last_index = 0
                for anchor_text, url in links:
                    start_index = node.text.find(f"[{anchor_text}]({url})", last_index)
                    if start_index != -1:
                        if start_index > last_index:
                            new_nodes.append(TextNode(node.text[last_index:start_index], TextType.TEXT))
                        new_nodes.append(TextNode(anchor_text, TextType.LINKS, url))
                        last_index = start_index + len(f"[{anchor_text}]({url})")
                if last_index < len(node.text):
                    new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
            else:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
