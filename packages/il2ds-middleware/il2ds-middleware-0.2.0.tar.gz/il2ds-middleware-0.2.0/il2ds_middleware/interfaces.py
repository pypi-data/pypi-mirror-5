# -*- coding: utf-8 -*-

from zope.interface import Interface


class ILineParser(Interface):

    def parse_line(self, line):
        """Parse line.

        :param line: line to parse.
        :type line: str.

        :returns: bool -- True if line was successfully parsed, otherwise False.
        """
