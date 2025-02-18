from .models import DiffResult
from .diff_message_decorator import DiffMessageDecorator


def print_similarity_results(diff_result: DiffResult, message_decorator: DiffMessageDecorator):
    print('\n----- Similar -----')
    if len(diff_result.similar) > 0:
        print('The following files have a similar path but a different file size or checksum:')
        for similar in diff_result.similar:
            print(f'\t[{similar[0].path_to_node()}] -> [{similar[1].path_to_node()}]')
    else:
        print('No files with similar paths but different checksums or file sizes were found.')

    print('')

    print('----- Different -----')
    if len(diff_result.first_tree.missing) > 0:
        print(message_decorator.first_tree_has_diff_message())
        for missing in diff_result.first_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(message_decorator.first_tree_no_diff_message())

    print('')

    if len(diff_result.second_tree.missing) > 0:
        print(message_decorator.second_tree_has_diff_message())
        for missing in diff_result.second_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(message_decorator.second_tree_no_diff_message())

    print('')
