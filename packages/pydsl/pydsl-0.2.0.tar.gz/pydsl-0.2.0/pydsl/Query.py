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

"""
Query and related classes
"""

#Current query class only works for indexable elements

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

class QueryElement(object):
    pass

class QueryTerm(QueryElement):
    """Any query Term"""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(self.left) ^ hash(self.right)


class QueryEquality(QueryTerm):
    """ a = b. It can use a string or a regexp"""
    def __str__(self):
        return "<" + str(self.left) + "=" + str(self.right) + ">"

class QueryPartial(QueryTerm):
    """ a = b. It can use a string or a regexp"""
    def __str__(self):
        return "<" + str(self.left) + "=~" + str(self.right) + ">"

class QueryInclusion(QueryTerm):
    """ looks for an element within a list """
    def __init__(self, left, right, dict_member = "values"):
        """dict_member could be keys or values"""
        QueryTerm.__init__(self, left, right)
        self.dict_member = dict_member

class BinaryOperator(QueryElement):
    def __init__(self, element1, element2):
        self.element1 = element1
        self.element2 = element2

class AndQueryOperator(BinaryOperator):
    def __str__(self):
        return "<" + str(self.element1) + "&&" + str(self.element2) + ">"

class OrQueryOperator(BinaryOperator):
    pass

class NotQueryOperator(QueryElement):
    def __init__(self, element):
        self.element = element

    def __str__(self):
        return "<!" + str(self.element) + ">"

class Query(object):
    """A generic query"""
    def __init__(self, content):
        self.content = content 

    def qand(self, element):
        self.content = AndQueryOperator(self.content, element)

    def qor(self, element):
        self.content = OrQueryOperator(self.content, element)

    def __str__(self):
        return"<Query:"+str(self.content)+">"

