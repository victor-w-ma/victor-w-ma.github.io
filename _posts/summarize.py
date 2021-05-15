import sys


# replace_dict = {}
# with open('dict.txt') as dict_file:
#     for line in dict_file:
#         old_word, new_word = line[:-1].split(' ')
#         replace_dict[old_word] = new_word

path = sys.argv[1]

# new_lines = []
# with open(path) as file_:
#     for i, line in enumerate(file_):
#         if i % 1000 == 0:
#             print(f'{i}')
#         line = line[:-1]
#         for old_word, new_word in replace_dict.items():
#             line = line.replace(old_word, new_word)
#         new_lines.append(line)
# with open('new.md', 'w') as file_:
#     for i, new_line in enumerate(new_lines):
#         if i % 1000 == 0:
#             print(f'{i}')
#         print(new_line, file=file_)
# exit(0)
with open(path) as file_:
    for line in file_:
        if line.startswith('##'):
            head_level = 2
        elif line.startswith('#'):
            head_level = 1
        else:
            head_level = None
        if head_level:
            heading = line[head_level + 1:-1]
            link = heading.replace('-', '').replace(' ', '-').replace('、', '')
            toc_item = f'{" " * (head_level - 1) * 4}- [{heading}](#{link})'
            print(toc_item)
        
