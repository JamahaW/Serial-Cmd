from __future__ import annotations

from abc import ABC
from abc import abstractmethod

type ItemID = int | str
type Color3i = tuple[int, int, int]


class Item(ABC):
    """Элемент UI"""

    @abstractmethod
    def getItemID(self) -> ItemID:
        """Получить ID этого элемента"""

    @abstractmethod
    def enable(self) -> None:
        """Enable"""

    @abstractmethod
    def disable(self) -> None:
        """Disable"""

    @abstractmethod
    def delete(self) -> None:
        """Удалить элемент"""

    @abstractmethod
    def show(self) -> None:
        """Показать элемент"""

    @abstractmethod
    def hide(self) -> None:
        """Скрыть элемент"""

    def setVisible(self, is_visible: bool) -> None:
        """Установить видимость элемента"""
        if is_visible:
            self.show()
        else:
            self.hide()


class Placeable(Item):
    """Размещаемый элемент"""

    def place(self, parent: Item = None) -> Placeable:
        """Установить элемент внутри родительского"""
        self.placeRaw(0 if parent is None else parent.getItemID())
        return self

    @abstractmethod
    def placeRaw(self, parent_id: ItemID) -> None:
        """Реализация размещения"""


class Container(Item, ABC):
    """Контейнер"""

    def add(self, item: Placeable) -> Container:
        """Добавить элемент внутрь"""
        item.place(self)
        return self


class VariableItem[T](ABC):
    """Элемент с значением"""

    @abstractmethod
    def setValue(self, value: T) -> None:
        """Установить значение"""

    @abstractmethod
    def getValue(self) -> T:
        """Получить значение"""


class RangedItem[T: (int, float)](VariableItem, ABC):
    """Item with defined value range"""

    @abstractmethod
    def setMinValue(self, value: T) -> None:
        """Установить минимальное значение элемента"""

    @abstractmethod
    def setMaxValue(self, value: T) -> None:
        """Установить максимальное значение элемента"""

    @abstractmethod
    def getMinValue(self) -> T:
        """Получить минимальное ограничение"""

    @abstractmethod
    def getMaxValue(self) -> T:
        """Получить максимальное ограничение"""

    def setRange(self, value_range: tuple[T, T]) -> None:
        """Установить диапазон значений"""
        min_value, max_value = value_range
        self.setMaxValue(max_value)
        self.setMinValue(min_value)
