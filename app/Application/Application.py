from pathlib import Path

from app.Dashboard.Dashboard import Dashboard
from app.File.File import File


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
        self.section: str = section

        ini: File = File(
            path=Path(
                Path.cwd(),
                "data",
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
        except AttributeError as exception:
            print(f'Oops. AttributeError in {exception} with uid')
        except Exception as exception:
            print(f'Oops. Error is {exception}!')
        # endregion

        # region Set key
        key: str = ''
        try:
            key = ini.read_conf(
                section=self.section,
                sub="key",
            )
        except AttributeError as exception:
            print(f'Oops. AttributeError in {exception} with key')
        except Exception as exception:
            print(f'Oops. Error is {exception}!')
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
        except Exception as exception:
            print(f'Oops. Error is {exception}!')
        # endregion

        # region Set config
        config: dict = {}
        try:
            config: dict = {"uid": uid, "host": host, "key": key}
        except UnboundLocalError as config:
            print(f'Oops. UnboundLocalError in {config}')
        except Exception as exception:
            print(f'Oops. Error is {exception}!')
        # endregion

        try:
            self.dashboard: Dashboard = Dashboard(
                uid=config["uid"],
                host=config["host"],
                key=config["key"]
            )
        except KeyError as key:
            print(f'Oops. KeyError in {key}')
        except Exception as exception:
            print(f'Oops. Error is {exception}!')

    def write_datasource(self) -> dict:
        """
        Запись источников данных
        :return: файл с источником данных
        """
        datasource: File = File(
            path=Path(
                Path.cwd(),
                "data",
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
                    Path.cwd(),
                    "data",
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
                Path.cwd(),
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
