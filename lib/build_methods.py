import subprocess


def test():
    print('test of printing')
    subprocess.run('touch test_console_protocol.txt', shell=True)


def charge(string):
    substring, filename = string.split(' ')[1,2]
    # Открываем файл для чтения
    with open(filename, 'r') as file:
        # Используем цикл для поиска строки, начинающейся с подстроки
        for line in file:
            if line.startswith(substring):
                # Разделяем строку и возвращаем последнее значение
                values = line.strip().split()
                return int(values[-1])
    
    # Если строка с подстрокой не найдена, возвращаем None
    return None

build_methods_list = {'test': test,
                      'llab_charge': chagre,
                      }
