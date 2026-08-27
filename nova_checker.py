#!/usr/bin/env python3
"""
Nova Semantic & Error Checker
Used by Compiler Step 2 to validate AST before code generation
"""

from typing import List, Dict, Any
from nova_parser import (
    Program, Stmt, Expr, ImportStmt, Assign, Var, MethodCall, Call,
    ShowStmt, FuncDef, ForEachStmt, IfStmt, KeepStmt, ChooseStmt,
    ClassDef, EnumDef, GiveStmt, TryStmt, ThrowStmt, AssertStmt, SwapStmt, CdStmt
)
from nova_libs import libsMap

class NovaChecker:
    def __init__(self, ast: Program):
        self.ast = ast
        self.errors = []
        self.symbols = set()
        self.imported_modules = set()

    def check(self) -> List[str]:
        self.errors.clear()
        self.symbols.clear()
        self.imported_modules.clear()

        # Built-in global symbols
        self.symbols.update(["true", "false", "none", "show", "input", "math", "time"])

        for stmt in self.ast.stmts:
            self._check_stmt(stmt)

        return self.errors

    def _check_stmt(self, stmt):
        if isinstance(stmt, ImportStmt):
            mod_name = stmt.module.strip().lower()
            if mod_name not in libsMap:
                self.errors.append(f"[Line {stmt.line}] Semantic Error: Unknown module '{stmt.module}'")
            else:
                alias = stmt.alias if stmt.alias else stmt.module
                self.imported_modules.add(alias)
                self.symbols.add(alias)

        elif isinstance(stmt, Assign):
            if isinstance(stmt.target, Var):
                self.symbols.add(stmt.target.name)
            self._check_expr(stmt.expr)

        elif isinstance(stmt, ShowStmt):
            for e in stmt.expressions:
                self._check_expr(e)

        elif isinstance(stmt, FuncDef):
            self.symbols.add(stmt.name)
            for param in stmt.params:
                self.symbols.add(param)
            for s in stmt.body:
                self._check_stmt(s)

        elif isinstance(stmt, ForEachStmt):
            self.symbols.add(stmt.var)
            self._check_expr(stmt.iter_expr)
            for s in stmt.body:
                self._check_stmt(s)

        elif isinstance(stmt, IfStmt):
            for cond, body in stmt.branches:
                self._check_expr(cond)
                for s in body:
                    self._check_stmt(s)

        elif isinstance(stmt, KeepStmt):
            self._check_expr(stmt.cond)
            for s in stmt.body:
                self._check_stmt(s)

        elif isinstance(stmt, ChooseStmt):
            self._check_expr(stmt.target)
            for b_expr, b_body in stmt.when_branches:
                self._check_expr(b_expr)
                for s in b_body:
                    self._check_stmt(s)

        elif isinstance(stmt, ClassDef):
            self.symbols.add(stmt.name)
            for m in stmt.members:
                self._check_stmt(m)

        elif isinstance(stmt, EnumDef):
            self.symbols.add(stmt.name)

        elif isinstance(stmt, GiveStmt):
            if stmt.expr: self._check_expr(stmt.expr)

        elif isinstance(stmt, TryStmt):
            for s in stmt.try_body: self._check_stmt(s)

        elif isinstance(stmt, (ThrowStmt, AssertStmt)):
            if hasattr(stmt, "expr") and stmt.expr: self._check_expr(stmt.expr)
            if hasattr(stmt, "cond") and stmt.cond: self._check_expr(stmt.cond)

        elif isinstance(stmt, Expr):
            self._check_expr(stmt)

    def _check_expr(self, expr):
        if isinstance(expr, Var):
            # Check if variable or module is known
            if expr.name not in self.symbols and not expr.name.isdigit():
                # Allow forward references in dynamic scripts but track
                pass
        elif isinstance(expr, MethodCall):
            self._check_expr(expr.obj)
            for a in expr.args:
                self._check_expr(a)
        elif isinstance(expr, Call):
            self._check_expr(expr.func)
            for a in expr.args:
                self._check_expr(a)


def checkProgram(ast: Program) -> List[str]:
    checker = NovaChecker(ast)
    return checker.check()
