import sys
import chinese_converter


def simplify_file(file_path):
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Convert to simplified Chinese
    simplified_content = chinese_converter.to_simplified(content)
    
    # Write the simplified content back to the same file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(simplified_content)


if __name__ == '__main__':
    file_path = sys.argv[1]
    simplify_file(file_path)
