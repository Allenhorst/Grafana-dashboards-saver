from configparser import ConfigParser
from json import dump, load
from pathlib import Path


class File:
    __slots__ = 'path'

    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def write_dict(self, data: dict) -> None:
        """
        Запись в файл json general'а/datasource'а
        :param data: json general'а/datasource'а
        :return: новый файл в локальном хранилище
        :raise IOError
        """
        try:
            with self.path.open(mode='w', encoding="utf-8") as file:
                dump(data, file, ensure_ascii=False)
        except IOError as exception:
            print('Oops. IOError has occurred!')
            print(f"Exception: {exception}")
        except Exception as exception:
            print(f'Oops. Exception is {exception}!')

    def write_str(self, data: str) -> None:
        """
        Запись в файл string
        :param data: string
        :return: новый файл в локальном хранилище
        :raise IOError
        """
        try:
            with self.path.open(mode='w', encoding="utf-8") as file:
                file.write(data)
        except IOError as exception:
            print('Oops. IOError has occurred!')
            print(f"Exception: {exception}")
        except Exception as exception:
            print(f'Oops. Exception is {exception}!')

    def read(self) -> dict:
        """
        Чтение из файла json general'а/datasource'а
        :return: прочтённый json general'а/datasource'а
        :raise FileNotFoundError
        """
        try:
            with self.path.open(mode='r', encoding="utf-8") as file:
                return load(file)
        except FileNotFoundError as exception:
            print('Oops. FileNotFoundError has occurred!')
            print("No such file or directory!")
            print(f"Exception: {exception}")
        except Exception as exception:
            print(f'Oops. Exception is {exception}!')

    def read_conf(self, section: str, sub: str) -> str:
        """
        Определение параметров для подключения и чтения
        :param section: раздел, который определяет все параметры подключения
        :param sub: раздел, определяющий способ взаимодействия
        :return: конфигурационные параметры
        :raise: KeyError
        """
        try:
            config = ConfigParser()
            config.read(str(self.path))
            return str(config[section][sub])
        except KeyError as exception:
            print('Oops. Key Error occured')
            print(f'Response is: {exception}')
            if sub == "connect":
                print('Include default connection!')
                def_connect: str = '0.05'
                return def_connect
            if sub == "read":
                print('Include default reading!')
                def_read: str = '10.0'
                return def_read
        except Exception as exception:
            print(f'Oops. Exception is {exception}!')
