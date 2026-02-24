import textnode
import blocknode
import htmlnode
import os

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    
    content = open(from_path).read()
    template = open(template_path).read()

    converted_content = blocknode.markdown_to_html_node(content).to_html()

    title = blocknode.extract_title(content)

    final_html = template.replace("{{content}}", converted_content).replace("{{title}}", title)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(final_html)

    