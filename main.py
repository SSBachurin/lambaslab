import argparse
import yaml
import os
import subprocess
import shutil
from dataclasses import dataclass


@dataclass
class Lambas:
    yaml_file_path = ''
    home_dir = ''  # домашняя директория
    cur_dir = ''  # Текущая рабочая папка
    geometry_folder = os.path.join(home_dir, 'geometries')
    # protocols_folder = ''
    results_folder = os.path.join(home_dir, 'results')
    geometries = [f for f in os.listdir(geometry_folder)
                  if f.endswith('.pdb')]

    commands_list = []
    lambaslab_commands = dict()
    bufer = dict()
    work_dict = dict()

    def load_inner_methods(self):
        self.lambaslab_commands = {'llab_charge': self.charge,
                                   }

    def process(self):
        '''Запускает конвеер обработки геометрий. Сначала происходит
        подготовка директории, затем выполняются команды в секции'''
        for geometry in self.geometries:
            self.build(geometry).execute()
            os.chdir(self.home_dir)

    def load_command(self, section: str):
        # Загружаем конфигурацию из YAML-файла
        with open(self.yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)
        # Извлекаем последовательность команд из конфигурации
        self.commands_list = config.get(section)
        return self

    def execute(self):
        for command in self.commands_list:
            if command[0] in self.lambaslab_commands.keys():
                self.lambaslab_commands[command[0]](*command[1:])
            else:
                # Формируем команду, добавляя имя файла .pdb
                for key, value in self.work_dict:
                    command = command.replace(key, value)
                # Выполняем команду в консоли
                process = subprocess.Popen(command, shell=True)
                process.wait()
        # Возвращаемся обратно в исходную папку
        os.chdir(self.home_dir)
        return self

    def build(self, geometry):
        print(f"BUILDING. {geometry} in process")
        geometry_name = geometry[:-4]
        self.work_dict['{file}'] = geometry_name
        # Создаем папку с именем файла .pdb
        self.cur_dir = os.path.join(self.home_dir,
                                    os.path.splitext(geometry)[0])
        os.makedirs(self.cur_dir, exist_ok=False)
        # Копируем файл .pdb в созданную папку
        shutil.copy2(os.path.join(self.geometry_folder, geometry),
                     self.cur_dir)
        # Переходим в созданную папку
        os.chdir(self.cur_dir)
        return self

    def charge(self, substring, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith(substring):
                    charge = int(line.strip().split()[-1])
        with open('topol.top', 'r') as top:
            for line in top:
                if line.startswith('WT4'):
                    wt_amount = int(line.strip().split()[-1])
        ion_amout = wt_amount / 34
        self.work_dict['p_amount'] = charge + ion_amout
        self.work_dict['n_amount'] = ion_amout
        # Если строка с подстрокой не найдена, возвращаем None
        return self
    
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
    work.home_dir = os.getcwd()
    #work.protocols_folder = os.path.abspath(args.protocols_folder)
    work.work_dict['{protocols_folder}'] = os.path.abspath(args.protocols_folder)
    work.yaml_file_path = os.path.abspath(args.conf)

    print("У Вас есть необходимые папки geometries и protocols "
          "в рабочей директории. Удостоверьтесь, что они содержат "
          "необходимые для расчётов файлы и запустите команду build.")

    exec_commands = {'build': [work.load_inner_methods,
                               work.load_command('build'),
                               work.process,],
                     'analyse': [work.analyse,],
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
            for i in exec_commands[inp]:
                exec_commands[inp][i]()
            inp = input("Введите команду: ")
        else:
            print("Неизвестная команда")
            inp = input("Введите команду: ")
