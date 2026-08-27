#!/usr/bin/env python3
"""
Nova Shared AST Parser & Lexer
Used by both nova_interpreter.py (DEV) and nova_compiler.py (PROD)
"""

from enum import Enum, auto
from typing import Any, List, Optional, Dict

# ============================================================
# TOKEN TYPES & KEYWORDS
# ============================================================
class TT(Enum):
    INT=auto(); FLOAT=auto(); STRING=auto(); BOOL=auto(); NONE=auto()
    INTERP=auto()
    IDENT=auto(); KEYWORD=auto()
    PLUS=auto(); MINUS=auto(); STAR=auto(); SLASH=auto(); DSLASH=auto()
    PERCENT=auto(); DSTAR=auto(); EQ=auto(); PLUS_EQ=auto(); MINUS_EQ=auto()
    STAR_EQ=auto(); SLASH_EQ=auto(); DSLASH_EQ=auto(); PERCENT_EQ=auto()
    EQEQ=auto(); NEQ=auto(); LT=auto(); GT=auto(); LTE=auto(); GTE=auto()
    ARROW=auto(); ARROW2=auto()
    PIPE=auto(); AMP=auto(); CARET=auto()
    LPAREN=auto(); RPAREN=auto(); LBRACKET=auto()
    RBRACKET=auto(); LBRACE=auto(); RBRACE=auto()
    COLON=auto(); COMMA=auto(); DOT=auto(); NEWLINE=auto(); EOF=auto()


KEYWORDS = {
    "if","elsif","else","end","func","def","fn","give","return","from","to","in","stp",
    "each","keep","choose","when","otherwise","try","catch","finally",
    "import","and","or","not","true","false","none","const","swap",
    "show","input","breck","break","skip","continu","continue","reverse","take","flat","as",
    "int","float","string","bool","list","set","map","tuple",
    "class","extends","init","public","private","static",
    "get","set","this","super","enum","throw","assert","cd",
}
ALIASES = {"continu": "skip", "continue": "skip", "break": "breck", "return": "give", "fn": "func", "def": "func"}


class Token:
    __slots__ = ("type", "value", "line")
    def __init__(self, t, v, l): self.type = t; self.value = v; self.line = l
    def __repr__(self): return f"Token({self.type.name},{self.value!r},L{self.line})"


class ParseError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[Line {line}] Parse Error: {msg}")
        self.line = line


# ============================================================
# AST NODE DEFINITIONS
# ============================================================
class ASTNode:
    def __init__(self, line=0): self.line = line

class Expr(ASTNode): pass
class Stmt(ASTNode): pass

class Literal(Expr):
    def __init__(self, value, line=0):
        super().__init__(line); self.value = value
    def __repr__(self): return f"Lit({self.value!r})"

class Var(Expr):
    def __init__(self, name, line=0):
        super().__init__(line); self.name = name
    def __repr__(self): return f"Var({self.name})"

class BinaryOp(Expr):
    def __init__(self, left, op, right, line=0):
        super().__init__(line); self.left = left; self.op = op; self.right = right
    def __repr__(self): return f"BinOp({self.left} {self.op} {self.right})"

class UnaryOp(Expr):
    def __init__(self, op, operand, line=0):
        super().__init__(line); self.op = op; self.operand = operand

class Call(Expr):
    def __init__(self, func, args, line=0):
        super().__init__(line); self.func = func; self.args = args
    def __repr__(self): return f"Call({self.func}, {self.args})"

class MethodCall(Expr):
    def __init__(self, obj, method, args, line=0):
        super().__init__(line); self.obj = obj; self.method = method; self.args = args
    def __repr__(self): return f"MethodCall({self.obj}.{self.method}({self.args}))"

class Attr(Expr):
    def __init__(self, obj, attr, line=0):
        super().__init__(line); self.obj = obj; self.attr = attr

class Index(Expr):
    def __init__(self, obj, index, line=0):
        super().__init__(line); self.obj = obj; self.index = index

class Slice(Expr):
    def __init__(self, obj, start, stop, step, rev=False, line=0):
        super().__init__(line); self.obj = obj; self.start = start; self.stop = stop; self.step = step; self.rev = rev

class Lambda(Expr):
    def __init__(self, params, body, line=0):
        super().__init__(line); self.params = params; self.body = body

class ListLit(Expr):
    def __init__(self, elements, line=0): super().__init__(line); self.elements = elements

class MapLit(Expr):
    def __init__(self, pairs, line=0): super().__init__(line); self.pairs = pairs

class SetLit(Expr):
    def __init__(self, elements, line=0): super().__init__(line); self.elements = elements

class TupleLit(Expr):
    def __init__(self, elements, line=0): super().__init__(line); self.elements = elements

class Interpolated(Expr):
    def __init__(self, parts, line=0): super().__init__(line); self.parts = parts

class CompExpr(Expr):
    def __init__(self, expr, var, iter_expr, cond_expr=None, is_set=False, line=0):
        super().__init__(line); self.expr = expr; self.var = var; self.iter_expr = iter_expr; self.cond_expr = cond_expr; self.is_set = is_set

class InputExpr(Expr):
    def __init__(self, prompt=None, line=0): super().__init__(line); self.prompt = prompt

class SuperCall(Expr):
    def __init__(self, method, args, line=0): super().__init__(line); self.method = method; self.args = args

class Assign(Stmt):
    def __init__(self, target, expr, is_const=False, line=0):
        super().__init__(line); self.target = target; self.expr = expr; self.is_const = is_const

class MultiAssign(Stmt):
    def __init__(self, targets, expr, line=0): super().__init__(line); self.targets = targets; self.expr = expr

class ShowStmt(Stmt):
    def __init__(self, expressions, line=0): super().__init__(line); self.expressions = expressions

class IfStmt(Stmt):
    def __init__(self, branches, else_branch=None, line=0):
        super().__init__(line); self.branches = branches; self.else_branch = else_branch

class ForEachStmt(Stmt):
    def __init__(self, var, iter_expr, body, line=0):
        super().__init__(line); self.var = var; self.iter_expr = iter_expr; self.body = body

class FromToStmt(Stmt):
    def __init__(self, var, start_expr, end_expr, step_expr=None, body=None, line=0):
        super().__init__(line); self.var = var; self.start_expr = start_expr; self.end_expr = end_expr; self.step_expr = step_expr; self.body = body or []

class KeepStmt(Stmt):
    def __init__(self, cond, body, line=0): super().__init__(line); self.cond = cond; self.body = body

class ChooseStmt(Stmt):
    def __init__(self, target, when_branches, otherwise=None, line=0):
        super().__init__(line); self.target = target; self.when_branches = when_branches; self.otherwise = otherwise

class FuncDef(Stmt):
    def __init__(self, name, params, body, is_static=False, is_async=False, is_def=False, line=0):
        super().__init__(line); self.name = name; self.params = params; self.body = body
        self.is_static = is_static; self.is_async = is_async; self.is_def = is_def

class GiveStmt(Stmt):
    def __init__(self, expr=None, line=0): super().__init__(line); self.expr = expr

class BreckStmt(Stmt): pass
class SkipStmt(Stmt): pass

class ImportStmt(Stmt):
    def __init__(self, module, alias=None, line=0):
        super().__init__(line); self.module = module; self.alias = alias

class ClassDef(Stmt):
    def __init__(self, name, parent, members, line=0):
        super().__init__(line); self.name = name; self.parent = parent; self.members = members

class EnumDef(Stmt):
    def __init__(self, name, members, line=0): super().__init__(line); self.name = name; self.members = members

class TryStmt(Stmt):
    def __init__(self, try_body, catches, finally_body, line=0):
        super().__init__(line); self.try_body = try_body; self.catches = catches; self.finally_body = finally_body

class ThrowStmt(Stmt):
    def __init__(self, expr, line=0): super().__init__(line); self.expr = expr

class AssertStmt(Stmt):
    def __init__(self, cond, msg=None, line=0): super().__init__(line); self.cond = cond; self.msg = msg

class SwapStmt(Stmt):
    def __init__(self, a, b, line=0): super().__init__(line); self.a = a; self.b = b

class CdStmt(Stmt):
    def __init__(self, target, line=0): super().__init__(line); self.target = target

class Program(ASTNode):
    def __init__(self, stmts): super().__init__(1); self.stmts = stmts


# ============================================================
# LEXER & TOKENIZER
# ============================================================
class Lexer:
    def __init__(self, src: str):
        self.src = src; self.pos = 0; self.line = 1; self.tokens = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c in " \t\r": self.pos += 1; continue
            if c == "#":
                while self.pos < len(self.src) and self.src[self.pos] != "\n": self.pos += 1
                continue
            if c == "\n":
                self.tokens.append(Token(TT.NEWLINE, "\n", self.line))
                self.line += 1; self.pos += 1; continue
            if c == '"':
                self.tokens.append(self._string()); continue
            if c == "'":
                self.tokens.append(self._raw_string()); continue
            if c.isdigit() or (c == "." and self.pos + 1 < len(self.src) and self.src[self.pos+1].isdigit()):
                self.tokens.append(self._number()); continue
            if c.isalpha() or c == "_":
                self.tokens.append(self._ident()); continue
            tok = self._op(); self.tokens.append(tok)
        self.tokens.append(Token(TT.EOF, "", self.line))
        return self.tokens

    def _string(self):
        l = self.line; self.pos += 1; parts = []; cur = ""
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c == '"': self.pos += 1; break
            if c == "\n": self.line += 1
            if c == "{" and self.pos + 1 < len(self.src):
                if cur: parts.append((cur, False)); cur = ""
                self.pos += 1; expr_s = ""
                while self.pos < len(self.src) and self.src[self.pos] != "}":
                    expr_s += self.src[self.pos]; self.pos += 1
                self.pos += 1; parts.append((expr_s, True)); continue
            cur += c; self.pos += 1
        if cur or not parts: parts.append((cur, False))
        if any(is_expr for _, is_expr in parts):
            return Token(TT.INTERP, parts, l)
        return Token(TT.STRING, "".join(txt for txt, _ in parts), l)

    def _raw_string(self):
        l = self.line; self.pos += 1; res = ""
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c == "'": self.pos += 1; break
            if c == "\n": self.line += 1
            res += c; self.pos += 1
        return Token(TT.STRING, res, l)

    def _number(self):
        l = self.line; start = self.pos; is_flt = False
        while self.pos < len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos] == "."):
            if self.src[self.pos] == ".":
                if is_flt or (self.pos + 1 < len(self.src) and self.src[self.pos+1] == "."): break
                is_flt = True
            self.pos += 1
        val = self.src[start:self.pos]
        return Token(TT.FLOAT if is_flt else TT.INT, float(val) if is_flt else int(val), l)

    def _ident(self):
        l = self.line; start = self.pos
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == "_"): self.pos += 1
        val = self.src[start:self.pos]
        if val in KEYWORDS:
            val = ALIASES.get(val, val)
            return Token(TT.KEYWORD, val, l)
        return Token(TT.IDENT, val, l)

    def _op(self):
        l = self.line; c = self.src[self.pos]; p2 = self.src[self.pos:self.pos+2]
        if p2 == "->": self.pos += 2; return Token(TT.ARROW2, "->", l)
        if p2 == "<>": self.pos += 2; return Token(TT.ARROW, "<>", l)
        if p2 == "==": self.pos += 2; return Token(TT.EQEQ, "==", l)
        if p2 == "!=": self.pos += 2; return Token(TT.NEQ, "!=", l)
        if p2 == "<=": self.pos += 2; return Token(TT.LTE, "<=", l)
        if p2 == ">=": self.pos += 2; return Token(TT.GTE, ">=", l)
        if p2 == "+=": self.pos += 2; return Token(TT.PLUS_EQ, "+=", l)
        if p2 == "-=": self.pos += 2; return Token(TT.MINUS_EQ, "-=", l)
        if p2 == "*=": self.pos += 2; return Token(TT.STAR_EQ, "*=", l)
        if p2 == "/=": self.pos += 2; return Token(TT.SLASH_EQ, "/=", l)
        if p2 == "//": self.pos += 2; return Token(TT.DSLASH, "//", l)
        if p2 == "**": self.pos += 2; return Token(TT.DSTAR, "**", l)
        self.pos += 1
        ops = {
            "+": TT.PLUS, "-": TT.MINUS, "*": TT.STAR, "/": TT.SLASH, "%": TT.PERCENT,
            "=": TT.EQ, "<": TT.LT, ">": TT.GT, "|": TT.PIPE, "&": TT.AMP, "^": TT.CARET,
            "(": TT.LPAREN, ")": TT.RPAREN, "[": TT.LBRACKET, "]": TT.RBRACKET,
            "{": TT.LBRACE, "}": TT.RBRACE, ":": TT.COLON, ",": TT.COMMA, ".": TT.DOT
        }
        return Token(ops.get(c, TT.EOF), c, l)


# ============================================================
# PARSER
# ============================================================
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens; self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current(); self.pos += 1; return tok

    def consume_newlines(self):
        while self.current().type == TT.NEWLINE: self.advance()

    def expect(self, tt: TT) -> Token:
        self.consume_newlines()
        t = self.current()
        if t.type != tt: raise ParseError(f"Expected {tt.name}, got {t.type.name} ({t.value!r})", t.line)
        return self.advance()

    def parse(self) -> Program:
        stmts = []
        while self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.EOF: break
            stmts.append(self._stmt())
        return Program(stmts)

    def _stmt(self) -> Stmt:
        self.consume_newlines()
        t = self.current(); line = t.line
        if t.type == TT.KEYWORD:
            kw = t.value
            if kw in ("public", "private", "static"):
                self.advance()
                return self._stmt()
            if kw == "show" and self.peek().type != TT.EQ: return self._show()
            if kw == "import": return self._import()
            if kw == "if": return self._if()
            if kw in ("give", "return"): return self._give()
            if kw in ("func", "def", "fn"): return self._func()
            if kw in ("get", "set"): return self._func()
            if kw == "init": return self._func()
            if kw == "from": return self._from()
            if kw == "each": return self._each()
            if kw == "keep": return self._keep()
            if kw == "choose": return self._choose()
            if kw == "try": return self._try()
            if kw == "throw": return self._throw()
            if kw == "assert": return self._assert()
            if kw == "class": return self._class()
            if kw == "enum": return self._enum()
            if kw in ("breck", "break"): self.advance(); return BreckStmt(line=t.line)
            if kw in ("skip", "continu", "continue"): self.advance(); return SkipStmt(line=t.line)
        if t.type == TT.IDENT and t.value == "init" and self.peek().type == TT.LPAREN:
            return self._func()
        return self._assign_or_expr()

    def _show(self):
        l = self.current().line; self.advance(); exprs = []
        while True:
            self.consume_newlines()
            if self.current().type in (TT.NEWLINE, TT.EOF): break
            exprs.append(self._expr())
            if self.current().type == TT.COMMA: self.advance()
            elif self.current().type in (TT.NEWLINE, TT.EOF): break
        return ShowStmt(exprs, line=l)

    def _import(self):
        l = self.current().line; self.advance(); mod = self.current().value; self.advance(); alias = None
        if self.current().type == TT.KEYWORD and self.current().value == "as":
            self.advance(); alias = self.current().value; self.advance()
        return ImportStmt(mod, alias, line=l)

    def _give(self):
        l = self.current().line; self.advance()
        e = self._expr() if self.current().type not in (TT.NEWLINE, TT.EOF) else None
        return GiveStmt(e, line=l)

    def _assign_or_expr(self):
        e = self._expr(); l = e.line
        if self.current().type == TT.EQ:
            self.advance(); rhs = self._expr()
            return Assign(e, rhs, line=l)
        if self.current().type == TT.PLUS_EQ:
            self.advance(); rhs = self._expr()
            return Assign(e, BinaryOp(e, "+", rhs, line=l), line=l)
        if self.current().type == TT.MINUS_EQ:
            self.advance(); rhs = self._expr()
            return Assign(e, BinaryOp(e, "-", rhs, line=l), line=l)
        if self.current().type == TT.STAR_EQ:
            self.advance(); rhs = self._expr()
            return Assign(e, BinaryOp(e, "*", rhs, line=l), line=l)
        if self.current().type == TT.SLASH_EQ:
            self.advance(); rhs = self._expr()
            return Assign(e, BinaryOp(e, "/", rhs, line=l), line=l)
        return e

    def _expr(self):
        return self._pipe()

    def _pipe(self):
        left = self._or()
        while self.current().type in (TT.PIPE, TT.AMP, TT.CARET):
            op = "|" if self.current().type == TT.PIPE else ("&" if self.current().type == TT.AMP else "^")
            self.advance(); right = self._or()
            left = BinaryOp(left, op, right, line=left.line)
        return left

    def _or(self):
        left = self._and()
        while self.current().type == TT.KEYWORD and self.current().value == "or":
            self.advance(); right = self._and()
            left = BinaryOp(left, "or", right, line=left.line)
        return left

    def _and(self):
        left = self._comp()
        while self.current().type == TT.KEYWORD and self.current().value == "and":
            self.advance(); right = self._comp()
            left = BinaryOp(left, "and", right, line=left.line)
        return left

    def _comp(self):
        left = self._add()
        ops = {TT.EQEQ: "==", TT.NEQ: "!=", TT.LT: "<", TT.GT: ">", TT.LTE: "<=", TT.GTE: ">="}
        while self.current().type in ops:
            op_sym = ops[self.current().type]; self.advance(); right = self._add()
            left = BinaryOp(left, op_sym, right, line=left.line)
        return left

    def _add(self):
        left = self._mul()
        while self.current().type in (TT.PLUS, TT.MINUS):
            op = "+" if self.current().type == TT.PLUS else "-"; self.advance(); right = self._mul()
            left = BinaryOp(left, op, right, line=left.line)
        return left

    def _mul(self):
        left = self._unary()
        while self.current().type in (TT.STAR, TT.SLASH, TT.DSLASH, TT.PERCENT):
            op = self.current().value; self.advance(); right = self._unary()
            left = BinaryOp(left, str(op), right, line=left.line)
        return left

    def _unary(self):
        self.consume_newlines()
        t = self.current(); l = t.line
        if t.type in (TT.PLUS, TT.MINUS) or (t.type == TT.KEYWORD and t.value == "not"):
            op = "-" if t.type == TT.MINUS else ("+" if t.type == TT.PLUS else "not")
            self.advance()
            operand = self._unary()
            if isinstance(operand, Literal) and isinstance(operand.value, (int, float)) and op in ("+", "-"):
                return Literal(-operand.value if op == "-" else operand.value, line=l)
            return UnaryOp(op, operand, line=l)
        return self._primary()

    def _is_lambda(self):
        saved = self.pos
        try:
            if self.current().type in (TT.IDENT, TT.KEYWORD) and self.peek().type == TT.ARROW2:
                return True
            if self.current().type == TT.LPAREN:
                self.advance()
                while self.current().type in (TT.IDENT, TT.KEYWORD, TT.COMMA):
                    self.advance()
                if self.current().type == TT.RPAREN and self.peek().type == TT.ARROW2:
                    return True
        finally:
            self.pos = saved
        return False

    def _lambda(self):
        l = self.current().line; params = []
        if self.current().type in (TT.IDENT, TT.KEYWORD):
            params.append(self.advance().value)
        else:
            self.expect(TT.LPAREN)
            while self.current().type != TT.RPAREN and self.current().type != TT.EOF:
                params.append(self.advance().value)
                if self.current().type == TT.COMMA: self.advance()
            self.expect(TT.RPAREN)
        self.expect(TT.ARROW2)
        if self.current().type == TT.LBRACE:
            self.advance(); body = []
            while self.current().type != TT.RBRACE and self.current().type != TT.EOF:
                self.consume_newlines()
                if self.current().type == TT.RBRACE: break
                body.append(self._stmt())
                self.consume_newlines()
            self.expect(TT.RBRACE)
            return Lambda(params, body, line=l)
        body = self._expr()
        return Lambda(params, body, line=l)

    def _primary(self):
        self.consume_newlines()
        t = self.current(); l = t.line
        if self._is_lambda(): return self._lambda()
        if t.type == TT.INT or t.type == TT.FLOAT or t.type == TT.STRING:
            self.advance(); return Literal(t.value, line=l)
        if t.type == TT.KEYWORD and t.value in ("true", "false"):
            self.advance(); return Literal(t.value == "true", line=l)
        if t.type == TT.KEYWORD and t.value == "none":
            self.advance(); return Literal(None, line=l)
        if t.type == TT.INTERP:
            self.advance(); return Interpolated(t.value, line=l)
        if t.type == TT.LBRACKET:
            self.advance()
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "take":
                self.advance()
                out_expr = self._expr()
                if self.current().type == TT.KEYWORD and self.current().value == "each": self.advance()
                var_name = self.advance().value
                if self.current().type == TT.KEYWORD and self.current().value == "in": self.advance()
                iter_expr = self._expr()
                cond_expr = None
                if self.current().type == TT.KEYWORD and self.current().value == "if":
                    self.advance()
                    cond_expr = self._expr()
                self.expect(TT.RBRACKET)
                return self._postfix(CompExpr(out_expr, var_name, iter_expr, cond_expr, is_set=False, line=l))
            els = []
            while self.current().type != TT.RBRACKET and self.current().type != TT.EOF:
                self.consume_newlines()
                if self.current().type == TT.RBRACKET: break
                els.append(self._expr())
                if self.current().type == TT.COMMA: self.advance()
            self.expect(TT.RBRACKET)
            return self._postfix(ListLit(els, line=l))

        if t.type == TT.LBRACE:
            self.advance(); els = []; pairs = {}
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "take":
                self.advance()
                out_expr = self._expr()
                if self.current().type == TT.KEYWORD and self.current().value == "each": self.advance()
                var_name = self.advance().value
                if self.current().type == TT.KEYWORD and self.current().value == "in": self.advance()
                iter_expr = self._expr()
                cond_expr = None
                if self.current().type == TT.KEYWORD and self.current().value == "if":
                    self.advance()
                    cond_expr = self._expr()
                self.expect(TT.RBRACE)
                return self._postfix(CompExpr(out_expr, var_name, iter_expr, cond_expr, is_set=True, line=l))
            if self.current().type == TT.RBRACE:
                self.advance()
                node = MapLit({}, line=l)
            else:
                first_expr = self._expr()
                if self.current().type == TT.COLON:
                    self.advance()
                    first_val = self._expr()
                    k = first_expr.name if isinstance(first_expr, Var) else (first_expr.value if isinstance(first_expr, Literal) else str(first_expr))
                    pairs[k] = first_val
                    while self.current().type != TT.RBRACE and self.current().type != TT.EOF:
                        if self.current().type == TT.COMMA: self.advance()
                        self.consume_newlines()
                        if self.current().type == TT.RBRACE: break
                        k_expr = self._expr()
                        self.expect(TT.COLON)
                        v_expr = self._expr()
                        k = k_expr.name if isinstance(k_expr, Var) else (k_expr.value if isinstance(k_expr, Literal) else str(k_expr))
                        pairs[k] = v_expr
                    self.expect(TT.RBRACE)
                    node = MapLit(pairs, line=l)
                else:
                    els.append(first_expr)
                    while self.current().type != TT.RBRACE and self.current().type != TT.EOF:
                        if self.current().type == TT.COMMA: self.advance()
                        self.consume_newlines()
                        if self.current().type == TT.RBRACE: break
                        els.append(self._expr())
                    self.expect(TT.RBRACE)
                    node = ListLit(els, line=l)
            return self._postfix(node)

        if t.type in (TT.IDENT, TT.KEYWORD):
            name = t.value; self.advance()
            node = Var(name, line=l)
            return self._postfix(node)

        if t.type == TT.LPAREN:
            self.advance()
            self.consume_newlines()
            if self.current().type == TT.RPAREN:
                self.advance()
                return self._postfix(ListLit([], line=l))
            first = self._expr()
            if self.current().type == TT.COMMA:
                items = [first]
                while self.current().type == TT.COMMA:
                    self.advance()
                    self.consume_newlines()
                    if self.current().type == TT.RPAREN: break
                    items.append(self._expr())
                self.expect(TT.RPAREN)
                return self._postfix(ListLit(items, line=l))
            self.expect(TT.RPAREN)
            return self._postfix(first)
        raise ParseError(f"Unexpected token {t.value!r}", l)

    def _postfix(self, node):
        l = node.line
        while True:
            if self.current().type == TT.DOT:
                self.advance()
                attr_name = self.advance().value
                if self.current().type == TT.LPAREN:
                    self.advance(); args = []
                    while self.current().type != TT.RPAREN and self.current().type != TT.EOF:
                        self.consume_newlines()
                        if self.current().type == TT.RPAREN: break
                        args.append(self._expr())
                        if self.current().type == TT.COMMA: self.advance()
                    self.expect(TT.RPAREN)
                    node = MethodCall(node, attr_name, args, line=l)
                else:
                    node = Attr(node, attr_name, line=l)
            elif self.current().type == TT.LBRACKET:
                self.advance()
                idx_expr = self._expr()
                self.expect(TT.RBRACKET)
                node = MethodCall(node, "get", [idx_expr], line=l)
            elif self.current().type == TT.LPAREN:
                self.advance(); args = []
                while self.current().type != TT.RPAREN and self.current().type != TT.EOF:
                    self.consume_newlines()
                    if self.current().type == TT.RPAREN: break
                    args.append(self._expr())
                    if self.current().type == TT.COMMA: self.advance()
                self.expect(TT.RPAREN)
                node = Call(node, args, line=l)
            else:
                break
        return node

    def _if(self):
        l = self.current().line; self.advance(); cond = self._expr()
        if self.current().type == TT.COLON: self.advance()
        body = []
        while self.current().type not in (TT.KEYWORD, TT.EOF) or (self.current().type == TT.KEYWORD and self.current().value not in ("end", "else", "elsif")):
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value in ("end", "else", "elsif"): break
            body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return IfStmt([(cond, body)], line=l)

    def _func(self):
        l = self.current().line
        first_tok = self.current()
        if first_tok.value == "init":
            name = "init"
            self.advance()
        else:
            self.advance()
            name = self.advance().value
        self.expect(TT.LPAREN); params = []
        while self.current().type != TT.RPAREN and self.current().type != TT.EOF:
            params.append(self.advance().value)
            if self.current().type == TT.COMMA: self.advance()
        self.expect(TT.RPAREN)
        if self.current().type == TT.COLON: self.advance()
        body = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return FuncDef(name, params, body, line=l)

    def _from(self):
        l = self.current().line; self.advance()
        start_expr = self._expr()
        self.expect(TT.KEYWORD) # to
        end_expr = self._expr()
        step_expr = None
        if self.current().type == TT.KEYWORD and self.current().value == "stp":
            self.advance()
            step_expr = self._expr()
        self.expect(TT.KEYWORD) # in
        var = self.advance().value
        if self.current().type == TT.COLON: self.advance()
        body = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return FromToStmt(var, start_expr, end_expr, step_expr, body, line=l)

    def _each(self):
        l = self.current().line; self.advance(); var = self.advance().value; self.expect(TT.KEYWORD) # in
        iter_expr = self._expr()
        if self.current().type == TT.COLON: self.advance()
        body = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return ForEachStmt(var, iter_expr, body, line=l)

    def _keep(self):
        l = self.current().line; self.advance(); cond = self._expr()
        if self.current().type == TT.COLON: self.advance()
        body = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return KeepStmt(cond, body, line=l)

    def _choose(self):
        l = self.current().line; self.advance(); target = self._expr()
        if self.current().type == TT.COLON: self.advance()
        branches = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            kw = self.advance().value # when / otherwise
            if kw == "otherwise":
                b_expr = None
            else:
                b_expr = self._expr()
            if self.current().type == TT.COLON: self.advance()
            b_body = []
            while not (self.current().type == TT.KEYWORD and self.current().value in ("when", "otherwise", "end")) and self.current().type != TT.EOF:
                self.consume_newlines()
                if self.current().type == TT.KEYWORD and self.current().value in ("when", "otherwise", "end"): break
                if self.current().type == TT.EOF: break
                b_body.append(self._stmt())
            branches.append((b_expr, b_body))
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return ChooseStmt(target, branches, line=l)

    def _try(self):
        l = self.current().line; self.advance()
        if self.current().type == TT.COLON: self.advance()
        body = []
        while not (self.current().type == TT.KEYWORD and self.current().value in ("catch", "finally", "end")) and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value in ("catch", "finally", "end"): break
            if self.current().type == TT.EOF: break
            body.append(self._stmt())
        catches = []
        finally_body = []
        while self.current().type == TT.KEYWORD and self.current().value == "catch":
            self.advance()
            catch_var = None
            if self.current().type in (TT.IDENT, TT.KEYWORD) and self.current().type != TT.COLON and self.current().value != "end":
                catch_var = self.advance().value
                if self.current().type == TT.KEYWORD and self.current().value == "as":
                    self.advance()
                    catch_var = self.advance().value
            if self.current().type == TT.COLON: self.advance()
            catch_stmts = []
            while not (self.current().type == TT.KEYWORD and self.current().value in ("catch", "finally", "end")) and self.current().type != TT.EOF:
                self.consume_newlines()
                if self.current().type == TT.KEYWORD and self.current().value in ("catch", "finally", "end"): break
                if self.current().type == TT.EOF: break
                catch_stmts.append(self._stmt())
            catches.append((catch_var, catch_stmts))
        if self.current().type == TT.KEYWORD and self.current().value == "finally":
            self.advance()
            if self.current().type == TT.COLON: self.advance()
            while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
                self.consume_newlines()
                if self.current().type == TT.KEYWORD and self.current().value == "end": break
                if self.current().type == TT.EOF: break
                finally_body.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return TryStmt(body, catches, finally_body, line=l)

    def _throw(self):
        l = self.current().line; self.advance(); e = self._expr()
        return ThrowStmt(e, line=l)

    def _assert(self):
        l = self.current().line; self.advance(); cond = self._expr()
        msg = None
        if self.current().type == TT.COMMA:
            self.advance()
            msg = self._expr()
        return AssertStmt(cond, msg, line=l)

    def _class(self):
        l = self.current().line; self.advance(); name = self.advance().value
        parent = None
        if self.current().type == TT.KEYWORD and self.current().value == "extends":
            self.advance()
            parent = self.advance().value
        if self.current().type == TT.COLON: self.advance()
        members = []
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            members.append(self._stmt())
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return ClassDef(name, parent, members, line=l)

    def _enum(self):
        l = self.current().line; self.advance(); name = self.advance().value
        if self.current().type == TT.COLON: self.advance()
        members = {}
        while not (self.current().type == TT.KEYWORD and self.current().value == "end") and self.current().type != TT.EOF:
            self.consume_newlines()
            if self.current().type == TT.KEYWORD and self.current().value == "end": break
            if self.current().type == TT.EOF: break
            k = self.advance().value
            members[k] = len(members)
        if self.current().type == TT.KEYWORD and self.current().value == "end":
            self.advance()
        return EnumDef(name, members, line=l)


def parseSource(src: str) -> Program:
    tokens = Lexer(src).tokenize()
    return Parser(tokens).parse()
