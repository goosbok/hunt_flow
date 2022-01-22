from logic import run
from const import LOG_FILE

if __name__ == '__main__':
    if run():
        print(f'Something went wrong. Check the log: logs/{LOG_FILE}')
    else:
        print('OK')
