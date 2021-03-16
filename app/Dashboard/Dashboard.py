from pathlib import Path

from requests import get, exceptions
from requests.models import Response

from app.File.File import File


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
                Path.cwd(),
                "data",
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
            response: Response = get(
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
            response: Response = get(
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
            response: Response = get(
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
            response: Response = get(
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
            response: Response = get(
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
