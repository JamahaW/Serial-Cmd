from dataclasses import dataclass

from serialcmd.serializers import Primitive
from serialcmd.serializers import Serializable
from serialcmd.serializers import Serializer


@dataclass(frozen=True)
class ConnectPolicy[P: Serializable, S: Serializable]:
    """Политика подключения (Обмена) данными"""

    command_code: Primitive[P]
    """Примитивный тип распаковки индекса команды"""
    startup_serializer: Serializer[S]
    """Упаковщик пакета инициализации"""