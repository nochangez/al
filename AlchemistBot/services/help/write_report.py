# coding=utf-8


from datetime import datetime
from os import listdir, remove

from data.config import path_to_config_files


def delete_file(filename: str):
    remove(f"{path_to_config_files}{filename}") if filename in listdir(path_to_config_files) else None


def create_file(filename: str):
    file = open(f"{path_to_config_files}{filename}", 'w+', encoding='utf-8')
    file.close()


def write_in_file(filename: str, text: str):
    delete_file(filename)
    create_file(filename)

    with open(f"{path_to_config_files}filename", 'a+', encoding='utf-8') as file:
        file.write(text)
