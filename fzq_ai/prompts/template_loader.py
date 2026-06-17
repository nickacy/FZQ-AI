# fzq_ai/prompts/template_loader.py

import os
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(
    loader=FileSystemLoader(BASE_DIR),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

def load_prompt_template(filename: str):
    """Load a Jinja2 template from the prompts directory."""
    return env.get_template(filename)
