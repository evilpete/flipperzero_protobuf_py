"""
command Completion callback class for FlipperCMD interface.
"""

import sys
import readline
import os

__all__ = ['Cmd_Complete']


class Cmd_Complete():  # Custom completer
    """Command Completion callback class for FlipperCMD interface."""

    def __init__(self, **kwargs):

        self.volcab = kwargs.get('volcab', [])
        self.volcab.sort()

        self.flip = kwargs.get('flip', None)
        # self.cmd_comp_key = []
        self.cmd_comp_cache = {}
        self.cmd_hook_cache = {}
        self.prompt = ">"

    def setup(self, volcab=None):
        """Command Completion setup callback."""

        if volcab:
            self.volcab = sorted(volcab)
        elif self.flip is not None:
            self.volcab = self.flip.get_cmd_keys()

        self.prompt = "Flipper>>"
        readline.parse_and_bind("tab: complete")
        # readline.set_completer(self.cmd_complete)
        readline.set_completer(self.complete_callback)

        completer_delims = readline.get_completer_delims()
        completer_delims = completer_delims.replace("-", "")
        completer_delims = completer_delims.replace("/", "")
        readline.set_completer_delims(completer_delims)

        # readline.set_completion_display_matches_hook(self.display_matches)

    look_table = {
        'GET-TREE': ['FD', 'LD'],
        'GET': ['FF', 'LD'],
        'CAT': ['FF'],
        'MD5': ['FF'],
        'RENAME': ['FF', 'FF'],
        'MV': ['FF', 'FF'],
        'LS': ['FD'],
        'MKDIR': ['FD'],
    }


    # GET-TREE_D  GET_F cat_F  MD5_F  RENAME_F ls_D  mkdir_D
    def complete_callback(self, text, state) -> list:
        """Completion callback hook."""


        print(f"complete_callback: '{text}' {state}")
        buf = readline.get_line_buffer()
        buf_list = buf.strip().split()
        buf_len = len(buf_list)

        if buf_len == 1:
            return self.cmd_complete(text, state)

        print('\n')
        print("BUF: ", len(buf_list), '|'.join(buf_list), '\n\n')


        try:
            if buf_list[0].upper() == 'LS':

                print(f'buf_list[0] = {buf_list[0]}')

                if buf in self.cmd_hook_cache:
                    print(f"return cmd_hook_cache '{buf}'")
                    return self.cmd_hook_cache[buf][state]

                print(f"text = {text}")
                path, targ = os.path.split(text)

                print(f"path={path} targ={targ}")

                file_list = self.flip._get_list(path, ftype='DIR')
                file_list.sort()
                print(f"file_list={file_list}")
                results = [x for x in file_list if x.startswith(targ)] + [None]
                print(f"results={results}")

                if results[1] is None:
                    results[0] = f"{path}/{results[0]}"
                    print(f"RESULTS={results}")

                self.cmd_hook_cache[buf] = results

                sys.stdout.flush()
                return results[state]

        except Exception as e:
            print(f"Exception: {e}")


        # print('\n\n')

        # cmd_line = test.strip().split()

        return [None]

    def cmd_complete(self, text, state) -> list:
        """Command Completion callback hook."""

        print(f"cmd_complete: '{text}' {state}")
        # print(f"Call '{text}' {state}")
        buf = readline.get_line_buffer()
        # print(f"buf= >{buf}<")
        # print()
        # ct = readline.get_completion_type()
        # print(f"ct={ct}\n\n")

        # if buf.endswith('?'):
        #     print help syntax

        # only do completion for first word
        if buf and buf[-1] == ' ' and buf.strip().upper() in self.volcab:
            return [None]

        text = text.upper()
        if text in self.cmd_comp_cache:
            # print(f"Cache {text} {state}", self.cmd_comp_cache[text])
            return self.cmd_comp_cache[text][state]

        results = [x for x in self.volcab if x.startswith(text)] + [None]
        self.cmd_comp_cache[text] = results
        return results[state]

        # https://stackoverflow.com/questions/20625642/autocomplete-with-readline-in-python3

    def display_matches(self, _substitution, matches, _longest_match_length):
        """Command Completion display callback hook."""
        # line_buffer = readline.get_line_buffer()
        columns = os.environ.get("COLUMNS", 80)

        tpl = "{:<" + str(int(_longest_match_length * 1.2)) + "}"

        # print(f"substitution={substitution}")
        # print(f"matches={matches}")
        # print(f"_longest_match_length={_longest_match_length}")
        # print(f"tpl={tpl}")

        buffer = ""
        for match in matches:
            match = tpl.format(match)
            if len(buffer + match) > columns:
                print(buffer)
                buffer = ""
            buffer += match

        print(self.prompt.rstrip(), readline.get_line_buffer(), sep='', end='')

        sys.stdout.flush()
