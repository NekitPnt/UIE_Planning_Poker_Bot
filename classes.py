from dataclasses import dataclass, field


@dataclass
class RoomTemp:
    chat_id: int
    onwer_id: int
    onwer_name: str
    tasks: field(default_factory=list)
    current_task: int = 0


@dataclass
class Param:
    key: str
    name: str = ""
    name2: str = ""
    weight: float = 0


@dataclass
class TaskTemp:
    name: str
    param: Param
    opened: bool = False
    score: dict = field(default_factory=dict)


@dataclass
class Score:
    label: str
    value: int


@dataclass
class ServiceButtons:
    label: str
    callback: str


class Ftr:
    all_instances = []

    def __init__(self, text: str = "", commands: list = field(default_factory=list), descr: str = ""):
        self.text = text
        self.commands = commands
        self.descr = descr
        self.__class__.all_instances.append(self)

    @classmethod
    def generate_help(cls):
        return '\n'.join(f"/{f.commands[0]} {f.descr}" for f in cls.all_instances)