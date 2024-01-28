import subprocess


def test():
    print('test of printing')
    subprocess.run('touch test_console_protocol.txt', shell=True)


build_methods_list = {'test': test,
                      
                      }
