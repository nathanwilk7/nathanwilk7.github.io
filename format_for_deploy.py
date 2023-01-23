import os
import re
import shutil
import sys
import time


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
    'format_for_deploy.py',
    'README.md',
}
dirs_to_skip = {
    '.git',
}
regex_to_remove = r'[0-9a-zA-Z]{32}'
filepath_regex_to_remove = ' ' + regex_to_remove
content_regex_to_remove = '%20' + regex_to_remove
style_override_end = '</style></head>'
# https://css-tricks.com/snippets/css/media-queries-for-standard-devices/

style_override = '''
@media only screen and (max-device-width: 1025px) {
	body {
		padding-left: 1rem;
		padding-right: 1rem;
		font-size: 2rem;
	}
	a {
		font-size: 2rem;
	}
	h1 {
		font-size: 2rem;
	}
	h2 {
		font-size: 2rem;
	}
	h3 {
		font-size: 2rem;
	}
	img {
   		max-width: 100%;
  	  	min-width: 500px;
 	   	height: auto;
	}
}
	
@media only screen
and (min-device-width: 100px)
and (max-device-width: 670px)
and (
    (-webkit-min-device-pixel-ratio: 2)
    or (-webkit-device-pixel-ratio: 2)
    or (-webkit-device-pixel-ratio: 3)
    or (-webkit-device-pixel-ratio: 4)
    )
)
{
	body {
		padding-left: 1rem;
		padding-right: 1rem;
		font-size: 3rem;
	}
	a {
		font-size: 3rem;
	}
	h1 {
		font-size: 3rem;
	}
	h2 {
		font-size: 3rem;
	}
	h3 {
		font-size: 3rem;
	}
	img {
   		max-width: 100%;
  	  	min-width: 200px;
 	   	height: auto;
	}
}
'''
archived_str = '[ARCHIVED]'

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

# current timestamp (w/ 10 seconds of buffer)
script_start_time = int(time.time()) - 10

filepaths = all_filepaths(input_base_dir_filepath)
for input_filepath in filepaths:
    # Skip files to skip
    if input_filepath in files_to_skip:
        continue

    output_filepath = re.sub(filepath_regex_to_remove, '', input_filepath)
    # If this is a page title replacement
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
                # Add style override to end of style/head if found
                style_override_index = content.find(style_override_end)
                if style_override_index != -1:
                    content = content[:style_override_index] + style_override + content[style_override_index:]
                w.write(content)
        # If this is not an HTML file
        else:
            # Copy file to output_base_dir
            shutil.copyfile(full_input_filepath, full_output_filepath)


# for any files the output directory with a timestamp less than the current one, ask whether to archive or delete them?
print(f'Would you like to delete or skip?')
print('d + enter) Delete')
print('enter) Skip')
print()
for filepath in all_filepaths(output_base_dir_filepath):
    if filepath in files_to_skip:
        continue
    
    skip_dir = False
    for d in dirs_to_skip:
        if d in filepath:
            skip_dir = True
    if skip_dir:
        continue

    full_filepath = f'{output_base_dir_filepath}/{filepath}'
    # if the timestamp is less than the script start time 
    if archived_str not in full_filepath and os.path.getmtime(full_filepath) < script_start_time:
        print(filepath)
        response = input()
        if response == 'd':
            os.remove(full_filepath)

# remove empty directories
for dirpath, dirnames, filenames in os.walk(output_base_dir_filepath):
    if not dirnames and not filenames:
        os.rmdir(dirpath)