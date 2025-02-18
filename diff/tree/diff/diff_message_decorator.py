from abc import ABC, abstractmethod


class DiffMessageDecorator(ABC):

    @abstractmethod
    def first_tree_has_diff_message(self) -> str:
        pass

    @abstractmethod
    def first_tree_no_diff_message(self) -> str:
        pass

    @abstractmethod
    def second_tree_has_diff_message(self) -> str:
        pass

    @abstractmethod
    def second_tree_no_diff_message(self) -> str:
        pass
