#!/usr/bin/env python


import re


nvim = None


class PythonNvimUtils():
    comment_pattern = re.compile(r"(^(?:(?<![\.\w\)\}\]])'[^']*'|[^%]*?)*)(%.*|$)")
    cell_header_pattern = re.compile( r'(?:^%%(?:[^%]|$)|^[ \t]*?(?<!%)[ \t]*?(?:function|classdef)\s+)')
    ellipsis_pattern = re.compile(r'^(.*[^\s])\s*\.\.\.\s*$')
    variable_pattern = re.compile(r"\b((?:[a-zA-Z_]\w*)*\.?[a-zA-Z_]*\w*)")
    function_block_pattern = re.compile( r'(?:^|\n[ \t]*)(?<!%)[ \t]*(?:function|classdef)(?:.*?)[^\w]([a-zA-Z]\w*) *(?:\(|(?:%|\n|\.\.\.|$))[\s\S]*?(?=(?:\n)(?<!%)[ \t]*(?:function[^a-zA-Z]|classdef[^a-zA-Z])|$)')
    option_line_pattern = re.compile(r'%%! *vim-matlab: *(\w+) *\(([^\(]+)\)')

    @staticmethod
    def get_current_file_path() -> str:
        return nvim.current.buffer.name

    @staticmethod
    def is_current_buffer_modified() -> bool:
        return nvim.eval('&modified') == 1

    @staticmethod
    def save_current_buffer() -> None:
        if PythonNvimUtils.is_current_buffer_modified():
            nvim.command('w')

    @staticmethod
    def edit_file(file_path: str) -> None:
        nvim.command(f"silent e! {file_path}")

    @staticmethod
    def get_lines_selected() -> list[str]:
        # buf = nvim.current.buffer
        # row_start, _ = buf.mark('<')
        # row_end, _ = buf.mark('>')
        # lines = buf[row_start-1:row_end]

        lines = [line for line in nvim.current.range]
        return PythonNvimUtils.trim_matlab_code(lines)

    @staticmethod
    def trim_matlab_code(lines: list[str]) -> list[str]:
        trim_lines = []

        is_continuation = False

        for line in lines:
            line = PythonNvimUtils.comment_pattern.sub(r"\1", line).strip()

            if line in ('', '...'):
                continue

            has_ellipsis_suffix = PythonNvimUtils.ellipsis_pattern.match(line)
            if has_ellipsis_suffix:
                line = PythonNvimUtils.ellipsis_pattern.sub(r"\1", line)

            if is_continuation and trim_lines:
                trim_lines[-1] += line
            else:
                trim_lines.append(line)

            is_continuation = has_ellipsis_suffix

        return trim_lines

    @staticmethod
    def get_current_line() -> list[str] | None:
        row, col = nvim.current.window.cursor
        full_text = nvim.current.buffer
        num_lines = len(full_text)
        if row > num_lines:
            return None

        cur_pos = row - 1

        cont = PythonNvimUtils.ellipsis_pattern

        offset = 0
        while cur_pos + 1 < num_lines and cont.match(full_text[cur_pos + offset]):
            offset += 1
        end = cur_pos + offset + 1

        while cur_pos + offset > 0 and cont.match(full_text[cur_pos + offset - 1]):
            offset -= 1
        start = cur_pos + offset
        
        return PythonNvimUtils.trim_matlab_code(full_text[start:end])
