from pathlib import Path

from git import Repo


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
            local: Path = Path(Path.cwd().parent, ".git")
            repo: Repo = Repo(path=local)
            repo.git.add(update=True)
            repo.index.commit(self.message)
            origin = repo.remote(name=self.origin)
            origin.push()
        except Exception as exception:
            print(f"Error: {exception}")
