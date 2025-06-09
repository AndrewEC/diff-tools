from typing import Callable, Final

from .models import DiffResult
from .diff_message_decorator import DiffMessageDecorator


class SimilarityPrinter:

    def __init__(self, print_function: Callable[[str], None] = print):
        self._print_function = print_function

    def print_similarity_results(self, diff_result: DiffResult, message_decorator: DiffMessageDecorator):
        self._print_function('\n----- Similar -----')
        if len(diff_result.similar) > 0:
            self._print_function('The following files have a similar path but a different file size or checksum:')
            for similar in diff_result.similar:
                self._print_function(f'\t[{similar[0].path_to_node()}] -> [{similar[1].path_to_node()}]')
        else:
            self._print_function('No files with similar paths but different checksums or file sizes were found.')

        self._print_function('')

        self._print_function('----- Different -----')
        if len(diff_result.first_tree.missing) > 0:
            self._print_function(message_decorator.first_tree_has_diff_message())
            for missing in diff_result.first_tree.missing:
                self._print_function(f'\t[{missing.path_to_node()}]')
        else:
            self._print_function(message_decorator.first_tree_no_diff_message())

        self._print_function('')

        if len(diff_result.second_tree.missing) > 0:
            self._print_function(message_decorator.second_tree_has_diff_message())
            for missing in diff_result.second_tree.missing:
                self._print_function(f'\t[{missing.path_to_node()}]')
        else:
            self._print_function(message_decorator.second_tree_no_diff_message())

        self._print_function('')


SIMILARITY_PRINTER_SINGLETON: Final[SimilarityPrinter] = SimilarityPrinter()
