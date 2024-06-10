# -*- coding: utf-8 -*-
import os
import json 

table = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
all_data = []

def wash(data_path='data/'):
    """
    Wash the data.

    Method:

    If the file contains `iep.utm.edu`, for its content:
    - Remove prefix ending with "A-Z" in 26 rows.
    - Remove suffix starting with "An encyclopedia of philosophy articles written by professional philosophers."

    Args:
        data_path (str): The path to the data.
    """
    for file in os.listdir(data_path):
        if 'iep.utm.edu' in file:
            print(f'Washing file {file}...')
            with open(os.path.join(data_path, file), 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.split('\n')
            prefix_end = 0
            for i in range(25, len(content)):
                is_prefix_end = True
                for j in range(len(table)):
                    if not content[i-25+j].startswith(table[j]):
                        is_prefix_end = False
                        break
                if is_prefix_end:
                    prefix_end = i
                    break
            print(f'Prefix end: {prefix_end}')
            suffix_start = 0
            for i in range(len(content)-1, 0, -1):
                if content[i].startswith('An encyclopedia of philosophy articles written by professional philosophers.'):
                    suffix_start = i
                    break
            print(f'Suffix start: {suffix_start}')
            content = content[prefix_end+1:suffix_start]
            content = '\n'.join(content)
            content_dict = {
                'url': file,
                'content': content
            }
            all_data.append(content_dict)
        else:
            print(f'File {file} does not contain `iep.utm.edu`.')

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f)

if __name__ == '__main__':
    wash()