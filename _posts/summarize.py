import sys

path = sys.argv[1]

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
            link = heading.lower().replace(' ', '-')
            link = ''.join(c for c in link if c.isalnum() or c == '-')
            toc_item = f'{" " * (head_level - 1) * 4}- [{heading}](#{link})'
            print(toc_item)
