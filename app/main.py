from datetime import datetime
from multiprocessing import Queue
from pathlib import Path

from app.Application.Application import Application
from app.Directory.Directory import Directory
from app.File.File import File
from app.Repository.Repository import Repository


def push() -> None:
    """
    Отправка general в удалённый репозиторий
    :return: обновлённый удалённый репозиторий
    """
    sect: str = "bitbucket"
    ini: File = File(
        path=Path(
            Path.cwd(),
            "data",
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
            Path.cwd(),
            "data"
            "time.txt"
        )
    )
    time.write_str(str(datetime.now()))
    return datetime.now()


if __name__ == '__main__':
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
