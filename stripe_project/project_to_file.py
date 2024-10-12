import os

def write_project_to_file(project_dir, output_file):
    """
    Рекурсивно обходит директории проекта и записывает содержимое всех файлов в один выходной файл.
    Исключает файлы __init__.py, apps.py, tests.py, manage.py, а также директории с названием 'migrations'.
    Включает HTML-файлы из директорий 'templates'.

    Args:
        project_dir (str): Путь к корневой директории проекта.
        output_file (str): Путь к выходному файлу.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(project_dir):
            # Исключаем директорию 'migrations'
            if 'migrations' in dirs:
                dirs.remove('migrations')

            for file in files:
                file_path = os.path.join(root, file)

                # Исключаем файлы __init__.py, apps.py, tests.py, manage.py ...
                if file in ['__init__.py', 'apps.py', 'tests.py',
                            'manage.py', 'asgi.py', 'wsgi.py',
                            'project_to_file.py', 'admin.py']:
                    continue

                # Включаем HTML-файлы из директорий 'templates'
                if file.endswith('.html') and 'templates' in root:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        f.write(f'# {file_path}\n')
                        f.write(source_file.read() + '\n\n')

                # Включаем Python-файлы
                elif file.endswith('.py'):
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        f.write(f'# {file_path}\n')
                        f.write(source_file.read() + '\n\n')

if __name__ == '__main__':
    project_dir = 'D:/django/stripe_test/stripe_project'
    output_file = 'stripe_project_code.txt'
    write_project_to_file(project_dir, output_file)
    print(f'Код проекта записан в файл {output_file}')
