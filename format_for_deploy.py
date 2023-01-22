import os
import re
import shutil
import sys


# assume input filename is in downloads, unless provided as second arg, first arg is input filename
input_filename = sys.argv[1]
input_filename_prefix = '/Users/nate/Downloads'
if len(sys.argv) > 2:
    input_filename_prefix = sys.argv[2]
input_base_dir_filepath = f'{input_filename_prefix}/{input_filename}'

output_base_dir_filepath = '/Users/nate/Nate/nathanwilk7.github.io'
page_title_replacements = {
    'Blog.html': 'index.html',
}
files_to_skip = {
    '.DS_Store',
}
regex_to_remove = r'[0-9a-zA-Z]{32}'
filepath_regex_to_remove = ' ' + regex_to_remove
content_regex_to_remove = '%20' + regex_to_remove


# Relative filepaths
def all_filepaths(base_dir):
    import os
    filepaths = []
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # Remove the base dir from the filepath
            filepath = filepath.replace(base_dir, '')
            filepaths.append(filepath.strip('/'))
    return filepaths


filepaths = all_filepaths(input_base_dir_filepath)
for input_filepath in filepaths:
    # Skip files to skip
    if input_filepath in files_to_skip:
        continue

    output_filepath = re.sub(filepath_regex_to_remove, '', input_filepath)
    # If this is a page title replacement
    # import pdb; pdb.set_trace()
    if output_filepath in page_title_replacements:
        output_filepath = page_title_replacements[output_filepath]
    full_input_filepath = f'{input_base_dir_filepath}/{input_filepath}'

    # If this is a file
    if os.path.isfile(full_input_filepath):
        # Ensure intermediate output dirs exist
        full_output_filepath = f'{output_base_dir_filepath}/{output_filepath}'
        output_dir = os.path.dirname(full_output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # If this is an HTML file
        if full_input_filepath.endswith('.html'):
            # Read file and replace 
            with open(full_input_filepath, 'r') as r:
                content = r.read()
                content = re.sub(content_regex_to_remove, '', content)
                # replace page titles in content
                for page_title, replacement in page_title_replacements.items():
                    content = content.replace(page_title, replacement)
            # Write file to output_base_dir
            with open(full_output_filepath, 'w') as w:
                w.write(content)
        # If this is not an HTML file
        else:
            # Copy file to output_base_dir
            shutil.copyfile(full_input_filepath, full_output_filepath)
