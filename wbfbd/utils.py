import os

template_directory = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]) + '/templates/'

def read_template(file_, encoding='utf-8'):
    with open(template_directory + file_, 'r', encoding=encoding) as f:
        return f.read()
