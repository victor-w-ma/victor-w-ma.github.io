import shutil
import sys

TEMPORARY_PATH = 'temp.md'


def load_dictionaries(paths):
    replace_dict = {}
    for path in paths:
        with open(path) as dict_file:
            for line in dict_file:
                old_word, new_word = line[:-1].split(' ')
                replace_dict[old_word] = new_word
    return replace_dict


def read_file(path):
    print('Reading:')
    lines = []
    with open(path) as file_:
        for i, line in enumerate(file_):
            if i % 1000 == 0:
                print(f'l. {i}')
            lines.append(line[:-1])
    return lines


def dict_replace(lines, replace_dict):
    new_lines = []
    for i, line in enumerate(lines):
        for old_word, new_word in replace_dict.items():
            line = line.replace(old_word, new_word)
        new_lines.append(line)
    return new_lines


def write_out(lines, path):
    print('Writing:')
    with open(TEMPORARY_PATH, 'w') as file_:
        for i, line in enumerate(lines):
            if i % 1000 == 0:
                print(f'l. {i}')
            print(line, file=file_)
    shutil.move(TEMPORARY_PATH, path)


if __name__ == '__main__':
    path = sys.argv[1]
    replace_dict = load_dictionaries(['dict.txt', 'dict_radical_to_cjk.txt'])
    lines = read_file(path)
    new_lines = dict_replace(lines, replace_dict)
    write_out(new_lines, path)
