##
##  Copyright (c) 2013 Michal Vyskocil
##
##  released under MIT License, see LICENSE
##

import ast
import _ast

from copy import copy
from io import StringIO
from itertools import chain
from collections import defaultdict
from pprint import pprint, isreadable

from .utils import _fix_imports, _make_globals

class PycklerBase():
    """Basic class implementing all verification, parsing and evaluation
    functionality. It does have empty __GLOBALS__, so even basic symbols like
    None, True or False are not supported. However it makes a perfect sense to
    use it as a subclass for your own pyckler """

    __GLOBALS__ = {}

    def __init__(self, source, filename, globals=dict(), fix_imports=True):
        """Initialize a PycklerBase instance, which analyzes and evaluates pyckle source
        
        :param source: The list or tuple of strings (each for one line)
        :param filename: The name of file used for error reporting
        :param globals: An aditional namespace mapping
        ``fix_imports`` - add all underlying modules into globals, defaults to True
        """

        assert source is not isinstance(source, str), "ERROR: source must be a list or tuple of strings"

        self._source = source
        self._filename = filename
        self._globals = copy(self.__GLOBALS__)
        self._globals.update(globals)
        if fix_imports:
            self._globals = _fix_imports(self._globals)

    @property
    def globals(self):
        """return copy of globals used for verification and evaluation"""
        return copy(self._globals)

    def visit(self, node):
        """verify if given node impose all pyckle restrictions
        
        raises SyntaxError or return given node
        """

        def visitor(node):
            method = 'visit_' + node.__class__.__name__
            visitor_f = getattr(self, method, self.generic_visit)
            return visitor_f(node)

        visitor(node)
        for n in ast.walk(node):
            visitor(n)
        return node

    def parse(self):
        """parse and verify the AST
        
        raises SyntaxError of return topmost AST node
        """
        
        node = ast.parse(''.join(self._source), self._filename, mode="eval")
        return self.visit(node)

    def eval(self):
        """evaluate the code, once is parsed and verifyied
        
        raises SyntaxError of return Python object
        """

        node = self.parse()
        code = compile(node, self._filename, mode="eval")
        return eval(code, self.globals)

    ### visit meths
    def visit_Expression(self, node):
        #self.visit(node.body)
        return

    def visit_Num(self, node):
        return

    def visit_Str(self, node):
        return

    def visit_Bytes(self, node):
        return

    def visit_BinOp(self, node):

        def isnumber(node):

            if isinstance(node, _ast.Num):
                return "complex" if isinstance(node.n, complex) else "number"
            elif hasattr(node, "op") and \
                isinstance(node.op, _ast.USub) and isinstance(node.operand, _ast.Num):
                return "complex" if isinstance(node.operand.n, complex) else "number"

            return None

        foo = isnumber(node.left), isnumber(node.right)

        if  None not in foo and \
            "complex" in foo and \
            isinstance(node.op, (_ast.Add, _ast.Sub)):
                return

        raise SyntaxError(
            "Illegal expression, only complex numbers are allowed",
            self._seargs(node)
            )

    def visit_Name(self, node):
        if node.id in self._globals:
            return
        raise SyntaxError(
            "'{}' is not allowed name".format(node.id),
            self._seargs(node)
            )

    def visit_Tuple(self, node):
        return

    def visit_List(self, node):
        return
    
    def visit_Set(self, node):
        return

    def visit_Dict(self, node):
        return

    def visit_Call(self, node):
        if  node.starargs is not None or \
            node.kwargs is not None:
            raise NotImplementedError("starargs or kwargs support is not implemented in visit_Call")

        return

    def visit_Attribute(self, node):
        n = node
        l = list()
        while isinstance(n, _ast.Attribute):

            if not isinstance(n.value, _ast.Name):
                raise SyntaxError(
                    "Only names are supported in attributes, found '{}'".format(n.value.__class__.__name__),
                    self._seargs(node)
                    )

            l.append(n.value.id)
            n = n.attr
        l.append(n)

        s = '.'.join(l)

        if s in self._globals:
            return

        raise SyntaxError(
            "'{}' is not allowed name".format(s),
            self._seargs(node)
            )

    #XXX: for ctx=Load() - no idea, what's this about
    def visit_Load(self, node):
        return

    # handled in visit_BinOp
    def visit_Add(self, node):
        return
    def visit_Sub(self, node):
        return

    # FIXME: this runs twice for complex numbers
    def visit_UnaryOp(self, node):
        if isinstance(node.op, _ast.USub) and isinstance(node.operand, _ast.Num):
            return
        raise SyntaxError(
            "Unsupported unary operator, only negative numbers are allowed",
            self._seargs(node)
            )

    def visit_USub(self, node):
        return
    
    # foo(bar=42)
    def visit_keyword(self, node):
        return


    def generic_visit(self, node):
        raise SyntaxError(
            "Unsupported type of node: '{}'".format(node.__class__.__name__),
            self._seargs(node)
            )

    ### private methods

    # prepare arguments for SyntaxError in a safe way
    def _seargs(self, node):

        offset = node.col_offset + 1 if hasattr(node, "col_offset") else 0
        lineno = node.lineno if hasattr(node, "lineno") else -1
        try:
            line = self._source[lineno-1]
        except IndexError:
            line = "<N/A>"

        return  self._filename, \
                lineno,         \
                offset,         \
                line


class Pyckler(PycklerBase):

    """The default pyckler - it supports most common datatypes available in python
    
    Usage:
    pyckler = Pyckler(["42", ], "<string>")
    obj = pyckler.eval()
    obj == 42
    """

    __GLOBALS__ = _make_globals()
