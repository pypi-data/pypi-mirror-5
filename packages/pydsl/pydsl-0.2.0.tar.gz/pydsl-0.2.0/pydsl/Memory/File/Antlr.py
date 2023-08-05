#!/usr/bin/python
# -*- coding: utf-8 -*-
#This file is part of pydsl.
#
#pydsl is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pydsl is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pydsl.  If not, see <http://www.gnu.org/licenses/>.


"""ANLTr grammar format functions"""

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

import logging
LOG = logging.getLogger(__name__)
from pydsl.Alphabet.Lexer import Lexer
from pydsl.Alphabet.Token import Token
import re

#manual lexer

protectedwords = {"grammar": "GRAMMAR",
        "options": "OPTIONS",
        "language": "LANGUAGE",
        "output": "OUTPUT",
        "fragment": "FRAGMENT",
        "Java": "JAVA",
        "AST": "AST",
        "ASTLabelType": "ASTLABELTYPE"}

chardict = {",": "COMMA",
        ":": "COLON",
        ";": "SEMICOLON",
        "|": "VBAR",
        "{": "LCBRACKET",
        "}": "RCBRACKET",
        "(": "LPAR",
        ")": "RPAR",
        "=": "EQUAL",
        "!": "EMARK",
        "?": "QMARK",
        "^": "HAT",
        "*": "STAR",
        "-": "HYPHEN",
        "_": "UNDERSCORE",
        ">": "GT",
        #"'": "QUOTE",
        "&": "AMP",
        ".": "DOT",
        "\\": "ISLASH",
        "+": "PLUS",
        "$": "DOLLAR"}


class ANLTRGrammarLexer(Lexer):
    def matchchar(self, char):
        if not char in chardict:
            raise Exception
        current = self.current
        self.match(char)
        return Token(current, alias = chardict[char])

    def comment(self):
        self.match("/")
        self.match("*")
        while True:
            while self.current != "*":
                self.consume()
            self.consume()
            if self.current == "/":
                self.consume()
                break

    def name(self):
        import re
        string = ""
        while re.match("[a-zA-Z]", self.current):
            string += self.current
            self.consume()
        if string in protectedwords:
            return Token(string, alias = protectedwords[string])
        if string == string.lower():
            return Token(string, alias = "PARSERID")
        else:
            return Token(string, alias = "LEXERID")

    def rawstring(self):
        self.match("'")
        string = ""
        while self.current not in [None,"'"]:
            string += self.current
            self.consume()
            if string[-1] == "\\":
                string += self.current
                self.consume()
        self.match("'")
        return Token(string, alias="STRING")

    def number(self):
        import re
        string = ""
        while self.current and re.match("[0-9]", self.current):
            string += self.current
            self.consume()
        return Token(string, alias="NUMBER")

    def nextToken(self):
        while self.current:
            if self.current == "/":
                self.comment()
                continue
            elif self.current in [" ", '\n', '\t', '\i']:
                self.consume()
                continue
            elif self.current in chardict.keys():
                yield self.matchchar(self.current)
            elif re.match("[0-9]", self.current):
                yield self.number()
            elif self.current == "'":
                yield self.rawstring()
            elif re.match("[a-zA-Z]", self.current):
                yield self.name()
            else:
                raise Exception("Unknown char '%s'" % self.current)


def load_anltr_from_text(text):
    lexer = ANLTRGrammarLexer()
    return lexer(text)


#manual parser
def load_anltr_file(filepath):
    """Converts an anltr .g file into a BNFGrammar instance"""
    with open(filepath, 'r') as mlfile:
        content = mlfile.read()
        return load_anltr_from_text(content)
