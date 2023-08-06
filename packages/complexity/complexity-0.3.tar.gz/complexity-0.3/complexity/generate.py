#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from complexity.utils import make_sure_path_exists, unicode_open

def generate_html(input_dir, output_dir, context=None):

    # List the stem of each input HTML file
    input_file_list = os.listdir(input_dir)

    pages = []
    for f in input_file_list:
        if f.endswith('html'):
            file_stem = f.split('.')[0]
            pages.append(file_stem)
            
    context = context or {}
    env = Environment()
    env.loader = FileSystemLoader(input_dir)

    for page in pages:
        tmpl = env.get_template('{0}.html'.format(page))
        rendered_html = tmpl.render(**context)

        # Put index in the root. It's a special case.
        if page == 'index':
            output_filename = os.path.join(output_dir, 'index.html')
            with unicode_open(output_filename, 'w') as fh:
                fh.write(rendered_html)

        # Put other pages in page/index.html, for better URL formatting.
        elif page != 'base':
            output_filename = os.path.join(output_dir, '{0}/index.html'.format(page))
            make_sure_path_exists(os.path.dirname(output_filename))
            with unicode_open(output_filename, 'w') as fh:
                fh.write(rendered_html)


def generate_context(input_dir):
    """
    Generates the context for all complexity pages.

    Description:

        Iterates through the contents of the input_dir and finds all JSON files.
        Loads the JSON file as a Python object with the key being the JSON file name.

    Example:

        Assume the following files exist:

            input/names.json
            input/numbers.json

        Depending on their content, might generate a context as follows:

        contexts = {"names":
                        ['Audrey', 'Danny']
                    "numbers":
                        [1, 2, 3, 4]
                    }
    """
    context = {}
    
    all_input_files = os.listdir(input_dir)

    for file_name in all_input_files:
        
        if file_name.endswith('json'):

            # Open the JSON file and convert to Python object
            json_file = "{0}/{1}".format(input_dir, file_name)
            with unicode_open(json_file) as f:
                obj = json.load(f)

            # Add the Python object to the context dictionary
            context[file_name[:-5]] = obj

    return context
