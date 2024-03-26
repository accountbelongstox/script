import re
import os

class contentHandle:
    def __int__(self):
        pass

    @staticmethod
    def replace_by_map(content, mapping):
        """
        Replace values in the content based on curses.pyc mapping table.

        Parameters:
        - content (str): The input content.
        - mapping (dict): A dictionary where keys are the original values to replace,
          and values are the corresponding replacement values.

        Returns:
        - str: The content with replacements applied.
        """
        for origin, target in mapping.items():
            content = content.replace(origin, target)
        return content

    @staticmethod
    def replace(content, origin_text, target_text):
        """
        Replace all occurrences of origin text with target text in the content.

        Parameters:
        - content (str): The input content.
        - origin_text (str): The text to be replaced.
        - target_text (str): The text to replace origin_text.

        Returns:
        - str: The content with replacements applied.
        """
        return content.replace(origin_text, target_text)
