import os
from configparser import ConfigParser
from pathlib import Path


class Directory:
    __slots__: str = 'path'

    def __init__(self) -> None:
        self.path: Path = Path.cwd()

    def sections(self) -> list:
        try:
            folders = ConfigParser()
            folders.read(
                str(
                    Path(
                        self.path,
                        "data",
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
                            "data",
                            "docs",
                            section,
                            'dashboards'
                        )
                    )
                )
            except OSError:
                print(f'{section} already exists!')
                continue
            except Exception as exception:
                print(f'Oops. Error is {exception}!')
