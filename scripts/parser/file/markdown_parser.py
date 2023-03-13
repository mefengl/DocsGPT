"""Markdown parser.

Contains parser for md files.

"""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from parser.file.base_parser import BaseParser


class MarkdownParser(BaseParser):
    """Markdown parser.

    Extract text from markdown files.
    Returns dictionary with keys as headers and values as the text between headers.

    """

    def __init__(
        self,
        *args: Any,
        remove_hyperlinks: bool = True,
        remove_images: bool = True,
        # remove_tables: bool = True,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        # self._remove_tables = remove_tables

    def markdown_to_tups(self, markdown_text: str) -> List[Tuple[Optional[str], str]]:
        """Convert a markdown file to a dictionary.

        The keys are the headers and the values are the text under each header.

        """
        markdown_tups: List[Tuple[Optional[str], str]] = []
        lines = markdown_text.split("\n")

        current_header = None
        current_text = ""

        for line in lines:
            if header_match := re.match(r"^#+\s", line):
                if current_header is not None:
                    if current_text == "":
                        continue
                    markdown_tups.append((current_header, current_text))

                current_header = line
                current_text = ""
            else:
                current_text += line + "\n"
        markdown_tups.append((current_header, current_text))

        return (
            [
                (
                    re.sub(r"#", "", cast(str, key)).strip(),
                    re.sub(r"<.*?>", "", value),
                )
                for key, value in markdown_tups
            ]
            if current_header is not None
            else [(key, re.sub("\n", "", value)) for key, value in markdown_tups]
        )

    def remove_images(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"!{1}\[\[(.*)\]\]"
        return re.sub(pattern, "", content)

    # def remove_tables(self, content: str) -> List[List[str]]:
    #     """Convert markdown tables to nested lists."""
    #     table_rows_pattern = r"((\r?\n){2}|^)([^\r\n]*\|[^\r\n]*(\r?\n)?)+(?=(\r?\n){2}|$)"
    #     table_cells_pattern = r"([^\|\r\n]*)\|"
    #
    #     table_rows = re.findall(table_rows_pattern, content, re.MULTILINE)
    #     table_lists = []
    #     for row in table_rows:
    #         cells = re.findall(table_cells_pattern, row[2])
    #         cells = [cell.strip() for cell in cells if cell.strip()]
    #         table_lists.append(cells)
    #     return str(table_lists)

    def remove_hyperlinks(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"\[(.*?)\]\((.*?)\)"
        return re.sub(pattern, r"\1", content)

    def _init_parser(self) -> Dict:
        """Initialize the parser with the config."""
        return {}

    def parse_tups(
        self, filepath: Path, errors: str = "ignore"
    ) -> List[Tuple[Optional[str], str]]:
        """Parse file into tuples."""
        with open(filepath, "r") as f:
            content = f.read()
        if self._remove_hyperlinks:
            content = self.remove_hyperlinks(content)
        if self._remove_images:
            content = self.remove_images(content)
        return self.markdown_to_tups(content)

    def parse_file(
        self, filepath: Path, errors: str = "ignore"
    ) -> Union[str, List[str]]:
        """Parse file into string."""
        tups = self.parse_tups(filepath, errors=errors)
        results = []
        # TODO: don't include headers right now
        for header, value in tups:
            if header is None:
                results.append(value)
            else:
                results.append(f"\n\n{header}\n{value}")
        return results
