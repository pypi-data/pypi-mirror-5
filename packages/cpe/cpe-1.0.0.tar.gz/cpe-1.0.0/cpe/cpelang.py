#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
This file is part of cpe package.

This module contains the common characteristics of
any CPE language matching algorithm, associated with a version of
Common Platform Enumeration (CPE) specification.

Copyright (C) 2013  Alejandro Galindo Garc�a, Roberto Abdelkader Mart�nez P�rez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

For any problems using the cpe package, or general questions and
feedback about it, please contact:

- Alejandro Galindo Garc�a: galindo.garcia.alejandro@gmail.com
- Roberto Abdelkader Mart�nez P�rez: robertomartinezp@gmail.com
'''

from xml.dom import minidom


class CPELanguage(object):
    """
    Represents an expression in the CPE Language.

    This class allows match a CPE element against an expression
    in the CPE Language, that is, a XML document format for
    binding descriptive prose and diagnostic test to a CPE name
    (CPE Description Format).
    """

    ####################
    #  OBJECT METHODS  #
    ####################

    def __init__(self, expression, isFile=False):
        """
        Create an object that contains the input expression in
        the CPE Language (a set of CPE Names) and
        the DOM tree asociated with expression.

        INPUT:
            - expression: XML content in string or a path to XML file
            - isFile: indicates whether expression is a XML file or
                      XML content string
        OUPUT:
            - None
        """

        if isFile:
            self.expression = ""
            self.path = expression

            # Parse an XML file by name (filepath)
            self.document = minidom.parse(self.path)
        else:
            self.expression = expression
            self.path = ""

            # Parse an XML stored in a string
            self.document = minidom.parseString(self.expression)

    def __str__(self):
        """
        Returns a human-readable representation of CPE name.

        INPUT:
            - None
        OUTPUT:
            - Representation of CPE component as string
        """

        return "Expression of CPE language version {0}:\n{1}".format(
            self.VERSION, self.expression)

    def language_match(self, cpeset, cpel_dom=None):
        """
        Accepts a set of known CPE Names and an expression in the CPE language,
        and delivers the answer 'true' if the expression matches with the set.
        Otherwise, it returns 'false'.

        INPUT:
            - self: An expression in the CPE Language, represented as
                the XML infoset for the platform element.
            - cpeset: CPE set object to match with self expression.
            - cpel_dom: An expression in the CPE Language, represented as
                DOM tree.
        OUTPUT:
            - True if self expression can be satisfied by language matching
              against cpeset, False otherwise.
        """

        errmsg = "Class method not implemented. Use the method of some child class"
        raise NotImplementedError(errmsg)
