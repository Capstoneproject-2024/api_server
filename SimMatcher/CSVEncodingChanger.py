import chardet

csv_path = f'data/keywords/test_csv_lack_keywords.csv'
new_csv_path = f'results/new_csv_saved.csv'

with open(csv_path, 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']
    print(f"The file encoding is: {encoding}")

with open(csv_path, "r", encoding=encoding) as f:
    content = f.read()
    print(f'File opened')

with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write(content)
    print('File saved')
    #print(f'Content: {content}')