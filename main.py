import argparse
import yaml
import os
import subprocess
import shutil
from dataclasses import dataclass
from lib import build_methods as bm
import gmxapi

@dataclass
class Lambas:
    yaml_file_path = ''
    cur_dir = ''
    geometry_folder = os.path.join(cur_dir, 'geometries')
    protocols_folder = ''
    results_folder = os.path.join(cur_dir, 'results')
    geometries = [f for f in os.listdir(geometry_folder)
                  if f.endswith('.pdb')]
    commands_list = []
    # Перечень комманд, которые должна парсить программа из файла .yaml
    lambaslab_commands = dict()

    def build(self):
        self.lambaslab_commands = bm.build_methods_list

        # Загружаем конфигурацию из YAML-файла
        with open(self.yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)
        # Извлекаем последовательность команд из конфигурации
        self.commands_list = config.get('build')

        for geometry in self.geometries:
            print(f"BUILDING. {geometry} in process")
            geometry_name = geometry[:-4]
            # Создаем папку с именем файла .pdb
            output_folder = os.path.join(self.cur_dir,
                                         os.path.splitext(geometry)[0])
            os.makedirs(output_folder, exist_ok=False)
            # Копируем файл .pdb в созданную папку
            shutil.copy2(os.path.join(self.geometry_folder, geometry),
                         output_folder)
            # Переходим в созданную папку
            os.chdir(output_folder)
            # Выполняем команды для каждого файла .pdb
            for command in self.commands_list:
                if command[0] in self.lambaslab_commands.keys():
                    self.lambaslab_commands[command]() #тут разобраться как передать команду с параметрами корректно, видимо написать функцию parse_command(command)
                else:
                    # Формируем команду, добавляя имя файла .pdb
                    command = command.replace('{file}', geometry_name).replace('{protocols_folder}', work.protocols_folder)
                    # Выполняем команду в консоли
                    process = subprocess.Popen(command, shell=True)
                    process.wait()
            # Возвращаемся обратно в исходную папку
            os.chdir(self.cur_dir)

    def analyse(self):
        ...


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Пример обработки команд для lambdaslab")

    parser.add_argument('-c', '--conf', type=str,
                        default="protocol.yaml",
                        help="Yaml протокол работы")
    parser.add_argument('-pf', '--protocols_folder', type=str,
                        default="./protocols",
                        help="Папка с протоколами")
    args = parser.parse_args()

    os.makedirs(os.path.join(os.getcwd(), 'geometries'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'protocols'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'results'), exist_ok=True)

    work = Lambas()
    work.cur_dir = os.getcwd()
    work.protocols_folder = os.path.abspath(args.protocols_folder)
    work.yaml_file_path = os.path.abspath(args.conf)

    print("У Вас есть необходимые папки geometries и protocols "
          "в рабочей директории. Удостоверьтесь, что они содержат "
          "необходимые для расчётов файлы и запустите команду build.")

    exec_commands = {'build': work.build,
                     'analyse': work.analyse,
                     }

    inp = input('''
                Введите команду.
                build - подготовка расчётов,
                run - запуск симуляции,
                analyse - выполнение анализа,
                quit - для выхода
                Введите команду: ''')

    while inp != 'quit':
        if inp in exec_commands:
            exec_commands[inp]()
            inp = input("Введите команду: ")
        else:
            print("Неизвестная команда")
            inp = input("Введите команду: ")