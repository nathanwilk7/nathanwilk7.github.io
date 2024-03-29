import os
import re
import shutil
import sys
import time


# assume input filename is in downloads, unless provided as second arg, first arg is input filename
# input_filename = sys.argv[1]
# input_filename_prefix = '/Users/nate/Downloads'
# if len(sys.argv) > 2:
#     input_filename_prefix = sys.argv[2]
input_base_dir_filepath = os.path.expanduser(sys.argv[1])

output_base_dir_filepath = os.getcwd() #'/Users/nate/Nate/nathanwilk7.github.io'
page_title_replacements = {
    'Home.html': 'index.html',
}
files_to_skip = {
    '.DS_Store',
    '.nojekyll',
    'CNAME',
    'README.md',
    'format_for_deploy.py',
    'robots.txt',
    'sitemap.txt',
    'prism.js',
    'prism.css',
}
dirs_to_skip = {
    '.git',
}
regex_to_remove = r'( |%20)[0-9a-zA-Z]{32}'

content_replacements = {
    r'%20': '-',
    r'TEXTAREA': '<textarea style="width: 100%; font-family: monospace;" rows="5" placeholder="Enter text here (scratch space)"></textarea>',
    r'<details open="">' : '<details>',
    r'<summary>' : '<summary style="cursor: pointer">',
    r'(?P<myprefix><pre id="([a-z0-9]| |-)+" class="([a-z0-9]| |-)+")>': lambda matchobject: matchobject.group('myprefix') + 'style="overflow-x:auto;"' + '>',
    r'(?P<pretag><pre[^<>]*>)<code>(?P<prismalias>[a-z]+)':  lambda matchobject: matchobject.group('pretag') + '<code class="language-' + matchobject.group('prismalias') + '">',
}
content_replacements_dot_all = {
    r'(?P<prefix>\.code > code {.*font-size: )\d+%': lambda matchobject: matchobject.group('prefix') + '90%',
}
filepath_replacements = {
    r' ': '-',
}

head_override_start = '<html><head><meta'
# https://stackoverflow.com/questions/9386429/simple-bootstrap-page-is-not-responsive-on-the-iphone
head_override = '''
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LEEFT9748K"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-LEEFT9748K');
</script>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans&display=swap" rel="stylesheet">
'''

code_head_override = '''
<link href="REPLACE_WITH_RELATIVE_PATH_TO_ROOT/prism.css" rel="stylesheet" />
'''

style_override_end = '</style></head>'
# https://getbootstrap.com/docs/5.0/layout/breakpoints/
# https://torquemag.io/2021/08/media-queries-guide/
max_width_to_vals = {
    '575.98': {
        'font-size': '1.6',
        'img_min_width': '36',
    },
    '767.98': {
        'font-size': '1.5',
        'img_min_width': '36',
    },
    '991.98': {
        'font-size': '1.4',
        'img_min_width': '36',
    },
    '1199.98': {
        'font-size': '1.3',
        'img_min_width': '36',
    },
    '1399.98': {
        'font-size': '1.2',
        'img_min_width': '36',
    },
}
max_width_placeholder = 'MAXW'
font_size_placeholder = 'FS'
img_min_width_placeholder = 'IMINW'
# https://css-tricks.com/snippets/css/media-queries-for-standard-devices/
# https://www.webmobilefirst.com/en/devices/apple-iphone-se-2020/
initial_style_override = '''
@media (max-width: MAXWpx) {
	body {
		padding-left: 1rem;
		padding-right: 1rem;
		font-size: FSrem;
	}
	a {
		font-size: FSrem;
	}
	h1 {
		font-size: Fsrem;
	}
	h2 {
		font-size: FSrem;
	}
	h3 {
		font-size: FSrem;
	}
    p {
        font-size: FSrem;
    }
	img {
   		max-width: 90%;
  	  	min-width: IMINWpx;
 	   	height: auto;
	}
}
'''
temp_style_overrides = []
for max_width, vals in max_width_to_vals.items():
    temp_style_override = initial_style_override.replace(max_width_placeholder, max_width)
    temp_style_override = temp_style_override.replace(font_size_placeholder, vals['font-size'])
    temp_style_override = temp_style_override.replace(img_min_width_placeholder, vals['img_min_width'])
    temp_style_overrides.append(temp_style_override)
style_override = '\n'.join(temp_style_overrides)

font_override_start = '</title><style>'
# https://www.typewolf.com/recommendations https://www.typewolf.com/google-fonts
font_override = '''
body, h1, h2, h3, a, p {
	font-family: 'DM Sans', sans-serif;
	letter-spacing: .02em;
	font-size: 1.2rem;
}
'''

code_end_of_body_script_additions = '''
<script src="REPLACE_WITH_RELATIVE_PATH_TO_ROOT/prism.js"></script>
'''


# Relative filepaths
def all_filepaths(base_dir):
    import os
    filepaths_and_paths_to_root = []
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # Remove the base dir from the filepath
            filepath = filepath.replace(base_dir, '')
            # get the path to the root
            path_from_root = filepath.lstrip(base_dir)
            num_slashes_to_root = path_from_root.count('/')
            filepaths_and_paths_to_root.append((
                filepath.strip('/'),
                '/'.join(['..'] * num_slashes_to_root)))
    return filepaths_and_paths_to_root

# current timestamp (w/ 10 seconds of buffer)
script_start_time = int(time.time()) - 10

filepaths_and_paths_to_root = all_filepaths(input_base_dir_filepath)
for input_filepath, path_to_root in filepaths_and_paths_to_root:
    # Skip files to skip
    if input_filepath in files_to_skip:
        continue

    output_filepath = re.sub(regex_to_remove, '', input_filepath)
    for original, replacement in filepath_replacements.items():
        output_filepath = re.sub(original, replacement, output_filepath)
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
                content = re.sub(regex_to_remove, '', content)
                # replace page titles in content
                for page_title, replacement in page_title_replacements.items():
                    content = content.replace(page_title, replacement)
                for original, replacement in content_replacements.items():
                    content = re.sub(original, replacement, content)
                for original, replacement in content_replacements_dot_all.items():
                    content = re.sub(original, replacement, content, 1, re.DOTALL)
            # Write file to output_base_dir
            with open(full_output_filepath, 'w') as w:
                # Add head override to end of head if found
                head_override_index = content.find(head_override_start)
                if head_override_index != -1:
                    if '<code' in content:
                        temp = head_override + code_head_override
                    else:
                        temp = head_override
                    content = content[:head_override_index + 12] + temp + content[head_override_index + 12:]
                # Add style override to end of style/head if found
                style_override_index = content.find(style_override_end)
                if style_override_index != -1:
                    content = content[:style_override_index] + style_override + content[style_override_index:]

                # Add font override to end of style/head if found
                font_override_index = content.find(font_override_start)
                if font_override_index != -1:
                    content = (
                        content[:font_override_index + len(font_override_start)]
                        + f'\n{font_override}'
                        + content[font_override_index + len(font_override_start):])
                if '<code' in content:
                    content = content.replace('</body>', code_end_of_body_script_additions + '</body>')
                content = content.replace('REPLACE_WITH_RELATIVE_PATH_TO_ROOT', path_to_root)
                w.write(content)
        # If this is not an HTML file
        else:
            # Copy file to output_base_dir
            shutil.copyfile(full_input_filepath, full_output_filepath)


print(f'Would you like to delete or skip?')
print('d + enter) Delete')
print('enter) Skip')
print()
for filepath, _ in all_filepaths(output_base_dir_filepath):
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
    if os.path.getmtime(full_filepath) < script_start_time:
        print(filepath)
        response = input()
        if response == 'd':
            os.remove(full_filepath)

# remove empty directories
for dirpath, dirnames, filenames in os.walk(output_base_dir_filepath):
    if not dirnames and not filenames:
        os.rmdir(dirpath)
