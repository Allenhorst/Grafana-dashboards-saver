from configparser import ConfigParser
import os
from datetime import datetime
from json import dump, load
from multiprocessing import Queue
from pathlib import Path

from git import Repo
from requests import get, exceptions


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
        except IOError as e:
            print('Oops. IOError has occurred!')
            print(f"Error: {e}")
        except Exception as e:
            print(f'Oops. Error is {e}!')

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
        except IOError as e:
            print('Oops. IOError has occurred!')
            print(f"Error: {e}")
        except Exception as e:
            print(f'Oops. Error is {e}!')

    def read(self) -> dict:
        """
        Чтение из файла json general'а/datasource'а
        :return: прочтённый json general'а/datasource'а
        :raise FileNotFoundError
        """
        try:
            with self.path.open(mode='r', encoding="utf-8") as file:
                return load(file)
        except FileNotFoundError as e:
            print('Oops. FileNotFoundError has occurred!')
            print("No such file or directory!")
            print(f"Error: {e}")
        except Exception as e:
            print(f'Oops. Error is {e}!')

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
        except KeyError as e:
            print('Oops. Key Error occured')
            print(f'Response is: {e}')
            if sub == "connect":
                print('Include default connection!')
                def_connect: str = '0.05'
                return def_connect
            if sub == "read":
                print('Include default reading!')
                def_read: str = '10.0'
                return def_read
        except Exception as e:
            print(f'Oops. Error is {e}!')


class Directory:
    __slots__ = 'path'

    def __init__(self) -> None:
        self.path: Path = Path(
            os.environ["cwd"]
        )

    def sections(self) -> list:
        try:
            folders = ConfigParser()
            folders.read(
                str(
                    Path(
                        self.path,
                        "ini",
                        "grafana.ini"
                    )
                )
            )
            return folders.sections()
        except KeyError as e:
            print('Oops. Key Error occured')
            print(f'Response is: {e}')
        except FileNotFoundError as e:
            print('Oops. FileNotFoundError has occurred!')
            print("No such file or directory!")
            print(f"Error: {e}")
        except Exception as e:
            print(f'Oops. Error is {e}!')

    def make(self) -> None:
        for section in self.sections():
            try:
                os.makedirs(
                    str(
                        Path(
                            self.path,
                            "docs",
                            section,
                            'dashboards'
                        )
                    )
                )
            except OSError:
                print(f'{section} already exists!')
                continue
            except Exception as e:
                print(f'Oops. Error is {e}!')


class Repository:
    """
    Модель получения git информации из удалённого репозитория
    """
    __slots__ = (
        'host',
        'remote',
        'branch',
        'origin',
        'message'
    )

    def __init__(self, remote: str) -> None:
        """
        Конструктор класса
        :param remote: адрес репозитория
        """
        self.remote: str = remote
        self.branch: str = 'master'
        self.origin: str = "origin"
        self.message: str = 'Auto commit'

    def push(self) -> None:
        """
        Обновление удалённого репозитория из локального
        :return: обновлённый удалённый репозиторий
        """
        try:
            local: Path = Path(os.environ["cwd"], ".git")
            repo: Repo = Repo(path=local)
            repo.git.add(update=True)
            repo.index.commit(self.message)
            origin = repo.remote(name=self.origin)
            origin.push()
        except Exception as e:
            print(f"Error: {e}")


class Dashboard:
    """
    Модель доски для мониторинга в Grafana
    """
    __slots__ = (
        'uid',
        'host',
        'port',
        'headers',
        'connect',
        'read'
    )

    def __init__(self, uid: str, host: str, key: str) -> None:
        """
        Конструктор класса
        :param uid: внутренний идентификатор, создаваемый Grafana
        :param host: url адрес сервера, на котором располагается Grafana
        :param key: ключ для взаимодействия с api системы
        """
        self.uid: str = uid
        self.host: str = host
        self.port: int = 3000
        self.headers: dict = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {key}"
        }

        ini: File = File(
            path=Path(
                os.environ["cwd"],
                "ini",
                "base.ini"
            )
        )
        self.connect: float = float(
            ini.read_conf(
                section="requests",
                sub="connect"
            )
        )
        self.read: float = float(
            ini.read_conf(
                section="requests",
                sub="read"
            )
        )

    def query(self, query: str) -> str:
        """
        Создание адреса для произвольного запроса к api системы
        :param query: url необходимого запроса
        :return: конечный адрес для запроса
        """
        return f"http://{self.host}:{self.port}/api/{query}"

    def folder(self) -> dict:
        """
        Получение json folder'а из Grafana
        :return: сохранённый json folder'а
        :raise exceptions.ReadTimeout
        :raise exceptions.ConnectTimeout
        :raise exceptions.ConnectionError
        :raise exceptions.HTTPError
        """
        try:
            response = get(
                self.query(f"folders/{self.uid}"),
                headers=self.headers,
                timeout=(self.connect, self.read)
            )
            response.raise_for_status()
            return response.json()
        except exceptions.ReadTimeout:
            print('Oops. Read  timeout occured!')
        except exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except exceptions.ConnectionError:
            print('Seems like dns lookup failed.')
        except exceptions.HTTPError as e:
            print('Oops. HTTP Error occured')
            print(f'Response is: {e.response.content}')

    def general(self, version) -> dict:
        """
        Получение json general'а из Grafana
        :return: сохранённый json general'а
        :raise exceptions.ReadTimeout
        :raise exceptions.ConnectTimeout
        :raise exceptions.ConnectionError
        :raise exceptions.HTTPError
        """
        try:
            response = get(
                self.query(f"search?folderIds={int(version)}"),
                headers=self.headers,
                timeout=(self.connect, self.read)
            )
            response.raise_for_status()
            return response.json()
        except exceptions.ReadTimeout:
            print('Oops. Read  timeout occured!')
        except exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except exceptions.ConnectionError:
            print('Seems like dns lookup failed.')
        except exceptions.HTTPError as e:
            print('Oops. HTTP Error occured')
            print(f'Response is: {e.response.content}')

    def dashboard(self, uid: str) -> dict:
        """
        Получение json general'а из Grafana
        :return: сохранённый json general'а
        :raise exceptions.ReadTimeout
        :raise exceptions.ConnectTimeout
        :raise exceptions.ConnectionError
        :raise exceptions.HTTPError
        """
        try:
            response = get(
                self.query(f"dashboards/uid/{uid}"),
                headers=self.headers,
                timeout=(self.connect, self.read)
            )
            response.raise_for_status()
            return response.json()
        except exceptions.ReadTimeout:
            print('Oops. Read  timeout occured!')
        except exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except exceptions.ConnectionError:
            print('Seems like dns lookup failed.')
        except exceptions.HTTPError as e:
            print('Oops. HTTP Error occured')
            print(f'Response is: {e.response.content}')

    def datasource(self) -> dict:
        """
        Получение json всех data source из Grafana
        :return: сохранённый json data source
        :raise exceptions.ReadTimeout
        :raise exceptions.ConnectTimeout
        :raise exceptions.ConnectionError
        :raise exceptions.HTTPError
        """
        try:
            response = get(
                self.query("datasources"),
                headers=self.headers,
                timeout=(self.connect, self.read)
            )
            response.raise_for_status()
            return response.json()
        except exceptions.ReadTimeout:
            print('Oops. Read  timeout occured!')
        except exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except exceptions.ConnectionError:
            print('Seems like dns lookup failed.')
        except exceptions.HTTPError as e:
            print('Oops. HTTP Error occured')
            print(f'Response is: {e.response.content}')

    def alerts(self) -> dict:
        try:
            response = get(
                self.query("alerts"),
                headers=self.headers,
                timeout=(self.connect, self.read)
            )
            response.raise_for_status()
            return response.json()
        except exceptions.ReadTimeout:
            print('Oops. Read  timeout occured!')
        except exceptions.ConnectTimeout:
            print('Oops. Connection timeout occured!')
        except exceptions.ConnectionError:
            print('Seems like dns lookup failed.')
        except exceptions.HTTPError as e:
            print('Oops. HTTP Error occured')
            print(f'Response is: {e.response.content}')


class Application:
    __slots__ = (
        "section",
        "dashboard"
    )

    def __init__(self, section: str) -> None:
        """
        Конструктор класса
        :param section: имя папки и раздела для сохранения
        """
        self.section = section

        ini: File = File(
            path=Path(
                os.environ["cwd"],
                "ini",
                "grafana.ini"
            )
        )
        # region Set uid
        uid: str = ''
        try:
            uid = ini.read_conf(
                section=self.section,
                sub="uid",
            )
        except AttributeError as e:
            print(f'Oops. AttributeError in {e} with uid')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        # endregion

        # region Set key
        key: str = ''
        try:
            key = ini.read_conf(
                section=self.section,
                sub="key",
            )
        except AttributeError as e:
            print(f'Oops. AttributeError in {e} with key')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        # endregion

        # region Set host
        host: str = ''
        try:
            host = ini.read_conf(
                section=self.section,
                sub="host",
            )
        except AttributeError as host:
            print(f'Oops. AttributeError in {host} with host')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        # endregion

        # region Set config
        config: dict = {}
        try:
            config: dict = {"uid": uid, "host": host, "key": key}
        except UnboundLocalError as config:
            print(f'Oops. UnboundLocalError in {config}')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        # endregion

        try:
            self.dashboard: Dashboard = Dashboard(
                uid=config["uid"],
                host=config["host"],
                key=config["key"]
            )
        except KeyError as key:
            print(f'Oops. KeyError in {key}')
        except Exception as e:
            print(f'Oops. Error is {e}!')

    def write_datasource(self) -> dict:
        """
        Запись источников данных
        :return: файл с источником данных
        """
        datasource: File = File(
            path=Path(
                os.environ["cwd"],
                "datasource",
                "datasource.json"
            )
        )
        try:
            datasource.write_dict(
                data=self.dashboard.datasource()
            )
        except AttributeError as e:
            print(f'Oops. AttributeError in {e}')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        return self.dashboard.datasource()

    def write_dashboard(self) -> dict:
        """
        Запись каждой отдельной
        :return: файл с каждой отдельной
        """
        dashboards: dict = self.dashboard.general(
            version=self.dashboard.folder()['id']
        )
        for board in dashboards:
            name: File = File(
                path=Path(
                    os.environ["cwd"],
                    "docs",
                    self.section,
                    "dashboards",
                    f"{board['title']}.json"
                )
            )
            name.write_dict(
                data=self.dashboard.dashboard(
                    uid=board['uid']
                )
            )
        return dashboards

    def write_alerts(self) -> dict:
        alerts: File = File(
            path=Path(
                os.environ["cwd"],
                "alerts",
                "alerts.json"
            )
        )
        try:
            alerts.write_dict(
                data=self.dashboard.alerts()
            )
        except AttributeError as e:
            print(f'Oops. AttributeError in {e}')
        except Exception as e:
            print(f'Oops. Error is {e}!')
        return self.dashboard.alerts()


def push() -> None:
    """
    Отправка general в удалённый репозиторий
    :return: обновлённый удалённый репозиторий
    """
    sect: str = "bitbucket"
    ini: File = File(
        path=Path(
            os.environ["cwd"],
            "ini",
            "base.ini"
        )
    )
    remote: str = ini.read_conf(
        section=sect,
        sub="host"
    )
    git_repo: Repository = Repository(remote=remote)
    git_repo.push()


def current_time() -> datetime:
    """
    Запись текущего времени для детектирования изменений
    :return: файл time.txt с временем
    """
    time: File = File(
        path=Path(
            os.environ["cwd"],
            "time.txt"
        )
    )
    time.write_str(str(datetime.now()))
    return datetime.now()


if __name__ == '__main__':
    # region Environment
    os.environ["cwd"]: str = str(Path.cwd())
    # endregion

    directory: Directory = Directory()
    directory.make()

    queue: Queue = Queue()
    for folder in directory.sections():
        app: Application = Application(
            section=folder
        )
        print(f"Current dashboards for folder {folder}")
        try:
            queue.put(app.write_datasource())
            queue.put(app.write_dashboard())
            queue.put(app.write_alerts())
        except AttributeError as err:
            print(f'Oops. AttributeError in {err} with queue')
        except Exception as err:
            print(f'Oops. Error is {err}!')
        while not queue.empty():
            print(f"Datasource: {queue.get()}")
            print(f"Dashboard: {queue.get()}")
            print(f"Alerts: {queue.get()}")

    # region Write current time
    print(f"Current time: {current_time()}")
    # endregion

    # region Push changes
    push()
    # endregion
