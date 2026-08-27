#!/usr/bin/env python3
"""
Nova Language Interpreter - V1.6.1
Features:
  - V1.0-V1.4: Classes, Enums, Lambdas, Native Comprehensions, Throw/Assert,
               Multi-Catch, String Interpolation, Control Flow, Block Scoping.
  - V1.5 Standard Library (8 Modules, 505+ Functions):
      1. math, 2. string, 3. list, 4. set, 5. file+os, 6. random, 7. time, 8. json
  - V1.6 Full-Stack Web Platform (http, server, db, auth, env)
  - V1.6.1 First UI Library (80 Functions for Web, Desktop, Apps):
      1. App/Window (13), 2. Basic Elements (16), 3. Inputs (11),
      4. Buttons (8), 5. Layout Containers (11), 6. Fluent Styles (30), 7. Events (9)
"""

import sys, os, math, random, time, json, datetime, re, shutil, tempfile, uuid, importlib
import urllib.request, urllib.parse, urllib.error, http.client, http.server, socketserver
import threading, sqlite3, hashlib, hmac, base64, secrets, webbrowser
from enum import Enum, auto
from typing import Any, List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor

from nova_libs import (
    loadLib, libsMap, StdModule, NovaFile,
    NovaRequest, NovaResponse, NovaRoute, NovaServerApp,
    NovaDB, NovaUIElement, NovaAppWindow, NovaHttpResponse, NovaAsyncTask,
    NumpyArray, NovaArray, NovaDF, NovaGroupedDF, ChartFigure, VizFigure,
    NovaAppUnified, UIElement, ResponsiveManager, MemPool, RawMemBlock,
    RenderEntity, Sprite, Camera, Light, Mesh, Texture, Material, Shader,
    GameApp, GameEntity, GameScene, PhysicsBody, PhysicsWorld, Asset
)


# ============================================================
# TOKEN TYPES
# ============================================================
class TT(Enum):
    INT=auto();FLOAT=auto();STRING=auto();BOOL=auto();NONE=auto()
    INTERP=auto()
    IDENT=auto();KEYWORD=auto()
    PLUS=auto();MINUS=auto();STAR=auto();SLASH=auto();DSLASH=auto()
    PERCENT=auto();DSTAR=auto();EQ=auto();PLUS_EQ=auto();MINUS_EQ=auto()
    STAR_EQ=auto();SLASH_EQ=auto();DSLASH_EQ=auto();PERCENT_EQ=auto()
    EQEQ=auto();NEQ=auto();LT=auto();GT=auto();LTE=auto();GTE=auto()
    ARROW=auto()        # <>  swap
    ARROW2=auto()       # ->  lambda
    PIPE=auto();AMP=auto();CARET=auto()
    LPAREN=auto();RPAREN=auto();LBRACKET=auto()
    RBRACKET=auto();LBRACE=auto();RBRACE=auto()
    COLON=auto();COMMA=auto();DOT=auto();NEWLINE=auto();EOF=auto()


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


# ============================================================
# TOKEN
# ============================================================
class Token:
    __slots__ = ("type","value","line")
    def __init__(self, t, v, l): self.type=t; self.value=v; self.line=l
    def __repr__(self): return f"Token({self.type.name},{self.value!r},L{self.line})"


# ============================================================
# LEXER
# ============================================================
class LexError(Exception):
    def __init__(self,m,l): super().__init__(f"[Line {l}] LexError: {m}")


class Lexer:
    def __init__(self, src: str):
        self.src=src; self.pos=0; self.line=1; self.tokens: List[Token]=[]

    def error(self,m): raise LexError(m,self.line)
    def peek(self,o=0):
        p=self.pos+o; return self.src[p] if p<len(self.src) else ""
    def advance(self):
        ch=self.src[self.pos]; self.pos+=1
        if ch=="\n": self.line+=1
        return ch
    def match(self,e):
        if self.pos<len(self.src) and self.src[self.pos]==e:
            self.pos+=1; return True
        return False
    def add(self,tt,v=None): self.tokens.append(Token(tt,v,self.line))

    _NUM_AFTER = frozenset([
        TT.EQ,TT.PLUS_EQ,TT.MINUS_EQ,TT.STAR_EQ,TT.SLASH_EQ,
        TT.DSLASH_EQ,TT.PERCENT_EQ,TT.LPAREN,TT.LBRACKET,
        TT.COMMA,TT.COLON,TT.NEWLINE,TT.EOF,TT.KEYWORD,
        TT.LT,TT.GT,TT.LTE,TT.GTE,TT.EQEQ,TT.NEQ,TT.ARROW2,
    ])

    def tokenize(self):
        while self.pos<len(self.src): self._scan()
        self.add(TT.EOF); return self.tokens

    def _scan(self):
        ch=self.peek()
        if ch in (" ","\t","\r"): self.advance(); return
        if ch=="\n":
            self.advance()
            if self.tokens and self.tokens[-1].type!=TT.NEWLINE: self.add(TT.NEWLINE)
            return
        if ch=="#":
            while self.pos<len(self.src) and self.peek()!="\n": self.advance()
            return
        if ch=='"':  self._dq_string(); return
        if ch=="'":  self._sq_string(); return
        if ch.isdigit(): self._number(); return
        if ch=="-" and self.peek(1).isdigit() and (
                not self.tokens or self.tokens[-1].type in self._NUM_AFTER):
            self._number(); return
        if ch.isalpha() or ch=="_": self._ident(); return
        self.advance()
        if ch=="=" and self.match("="): self.add(TT.EQEQ,"=="); return
        if ch=="!" and self.match("="): self.add(TT.NEQ,"!=");   return
        if ch=="<" and self.match(">"): self.add(TT.ARROW,"<>"); return
        if ch=="<" and self.match("="): self.add(TT.LTE,"<=");   return
        if ch==">" and self.match("="): self.add(TT.GTE,">=");   return
        if ch=="-" and self.match(">"): self.add(TT.ARROW2,"->"); return
        if ch=="+" and self.match("="): self.add(TT.PLUS_EQ,"+="); return
        if ch=="-" and self.match("="): self.add(TT.MINUS_EQ,"-="); return
        if ch=="*" and self.peek()=="*": self.advance(); self.add(TT.DSTAR,"**"); return
        if ch=="*" and self.match("="): self.add(TT.STAR_EQ,"*="); return
        if ch=="/" and self.peek()=="/" :
            self.advance()
            if self.match("="): self.add(TT.DSLASH_EQ,"//=")
            else: self.add(TT.DSLASH,"//")
            return
        if ch=="/" and self.match("="): self.add(TT.SLASH_EQ,"/="); return
        if ch=="%" and self.match("="): self.add(TT.PERCENT_EQ,"%="); return
        _ONE={"+":TT.PLUS,"-":TT.MINUS,"*":TT.STAR,"/":TT.SLASH,"%":TT.PERCENT,
              "=":TT.EQ,"<":TT.LT,">":TT.GT,"(":TT.LPAREN,")":TT.RPAREN,
              "[":TT.LBRACKET,"]":TT.RBRACKET,"{":TT.LBRACE,"}":TT.RBRACE,
              ":":TT.COLON,",":TT.COMMA,".":TT.DOT,
              "|":TT.PIPE,"&":TT.AMP,"^":TT.CARET}
        if ch in _ONE: self.add(_ONE[ch],ch); return
        self.error(f"Unexpected char: {ch!r}")

    def _sq_string(self):
        self.advance(); buf=[]
        _ESC={"n":"\n","t":"\t","r":"\r","\\":"\\","'":"'",'"':'"'}
        while self.pos<len(self.src):
            ch=self.peek()
            if ch=="\\": self.advance(); buf.append(_ESC.get(self.advance(),""))
            elif ch=="'": self.advance(); break
            elif ch=="\n": self.error("Unterminated string")
            else: buf.append(self.advance())
        self.add(TT.STRING,"".join(buf))

    def _dq_string(self):
        self.advance()
        parts=[]
        buf=[]
        while self.pos<len(self.src):
            ch=self.peek()
            if ch=="\\":
                self.advance()
                _ESC={"n":"\n","t":"\t","r":"\r","\\":"\\","'":"'",'"':'"'}
                buf.append(_ESC.get(self.advance(),""))
            elif ch=='"':
                self.advance(); break
            elif ch=="\n":
                self.error("Unterminated string")
            elif ch=="{":
                if buf: parts.append(("".join(buf), False)); buf=[]
                self.advance()
                depth=1; expr_chars=[]
                while self.pos<len(self.src) and depth>0:
                    c=self.advance()
                    if c=="{": depth+=1; expr_chars.append(c)
                    elif c=="}":
                        depth-=1
                        if depth>0: expr_chars.append(c)
                    else: expr_chars.append(c)
                parts.append(("".join(expr_chars), True))
            else:
                buf.append(self.advance())
        if buf: parts.append(("".join(buf), False))
        if all(not is_expr for _,is_expr in parts):
            self.add(TT.STRING,"".join(t for t,_ in parts))
        else:
            self.add(TT.INTERP, parts)

    def _number(self):
        s=self.pos
        if self.peek()=="-": self.advance()
        while self.peek().isdigit(): self.advance()
        f=False
        if self.peek()=="." and self.peek(1).isdigit():
            f=True; self.advance()
            while self.peek().isdigit(): self.advance()
        raw=self.src[s:self.pos]
        self.add(TT.FLOAT if f else TT.INT, float(raw) if f else int(raw))

    def _ident(self):
        s=self.pos
        while self.pos<len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos]=="_"):
            self.pos+=1
        w=self.src[s:self.pos]; w=ALIASES.get(w,w)
        if w in KEYWORDS:
            if   w=="true":  self.add(TT.BOOL,True)
            elif w=="false": self.add(TT.BOOL,False)
            elif w=="none":  self.add(TT.NONE,None)
            else:            self.add(TT.KEYWORD,w)
        else:
            self.add(TT.IDENT,w)


# ============================================================
# AST NODES
# ============================================================
class _N:
    __slots__=()

def _make_node(name,*field_names,**defaults):
    all_fields=list(field_names)+list(defaults.keys())
    slots=all_fields+["line"]
    def __init__(self,*args,line=0,**kwargs):
        for f,v in zip(all_fields,args): setattr(self,f,v)
        provided=all_fields[:len(args)]
        for f in all_fields:
            if f in provided: continue
            if f in kwargs: setattr(self,f,kwargs[f])
            elif f in defaults: setattr(self,f,defaults[f])
            else: setattr(self,f,None)
        self.line=line
    def __repr__(self):
        fv=", ".join(f"{f}={getattr(self,f,'?')!r}" for f in all_fields)
        return f"{name}({fv})"
    return type(name,(_N,),{"__slots__":slots,"__init__":__init__,"__repr__":__repr__})

Program    = _make_node("Program",    "body")
Assign     = _make_node("Assign",     "name","value", type_hint=None,is_const=False,op="=")
VarDecl    = _make_node("VarDecl",    "name","type_hint","value",is_const=False)
Var        = _make_node("Var",        "name")
Literal    = _make_node("Literal",    "value")
BinOp      = _make_node("BinOp",      "left","op","right")
UnaryOp    = _make_node("UnaryOp",    "op","operand")
ListLit    = _make_node("ListLit",    "elements")
SetLit     = _make_node("SetLit",     "elements")
MapLit     = _make_node("MapLit",     "pairs")
TupleLit   = _make_node("TupleLit",   "elements")
Index      = _make_node("Index",      "obj","index")
Slice      = _make_node("Slice",      "obj","start","stop","step",reverse=False)
MethodCall = _make_node("MethodCall", "obj","method","args")
Attr       = _make_node("Attr",       "obj","name")
AttrAssign = _make_node("AttrAssign", "obj","attr","value",op="=")
FuncDef    = _make_node("FuncDef",    "name","params","return_type","body")
Call       = _make_node("Call",       "callee","args")
Return     = _make_node("Return",     "value")
Show       = _make_node("Show",       "values")
InputExpr  = _make_node("InputExpr",  "prompt")
If         = _make_node("If",         "condition","then_body","elsif_clauses","else_body")
Choose     = _make_node("Choose",     "subject","when_clauses","otherwise_body")
ForRange   = _make_node("ForRange",   "var","start","stop","step","body")
ForEach    = _make_node("ForEach",    "var","iterable","body")
Keep       = _make_node("Keep",       "var","type_hint","init","condition","body")
TryCatch   = _make_node("TryCatch",   "try_body","catch_clauses","finally_body")
SwapStmt   = _make_node("SwapStmt",   "a","b")
BreckStmt  = _make_node("BreckStmt")
SkipStmt   = _make_node("SkipStmt")
ReverseStmt= _make_node("ReverseStmt","name")
ImportStmt = _make_node("ImportStmt", "module","names","alias")
ExprStmt   = _make_node("ExprStmt",   "expr")
Interpolated= _make_node("Interpolated","parts")
Lambda     = _make_node("Lambda",     "params","body")
ListComp   = _make_node("ListComp",   "expr","var","iterable","condition")
SetComp    = _make_node("SetComp",    "expr","var","iterable","condition")
ClassDef   = _make_node("ClassDef",   "name","superclass","body")
MethodDef  = _make_node("MethodDef",  "name","params","body","kind","is_static")
FieldDecl  = _make_node("FieldDecl",  "name","value","visibility")
EnumDef    = _make_node("EnumDef",    "name","members")
ThrowStmt  = _make_node("ThrowStmt",  "value")
AssertStmt = _make_node("AssertStmt", "condition","message")
SuperCall  = _make_node("SuperCall",  "method","args")
CdStmt     = _make_node("CdStmt",     "path")


# ============================================================
# PARSER
# ============================================================
class ParseError(Exception):
    def __init__(self,m,l): super().__init__(f"[Line {l}] ParseError: {m}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens=tokens; self.pos=0

    def error(self,msg=None):
        t=self.current()
        raise ParseError(msg or f"Unexpected token {t.value!r}", t.line)
    def current(self): return self.tokens[self.pos]
    def peek(self,o=1):
        p=self.pos+o
        return self.tokens[p] if p<len(self.tokens) else self.tokens[-1]
    def check(self,*types): return self.current().type in types
    def check_kw(self,*words):
        t=self.current(); return t.type==TT.KEYWORD and t.value in words
    def advance(self):
        t=self.tokens[self.pos]
        if self.pos<len(self.tokens)-1: self.pos+=1
        return t
    def consume_newlines(self):
        while self.current().type==TT.NEWLINE: self.advance()
    def expect(self,tt,v=None):
        t=self.current()
        if t.type!=tt: self.error(f"Expected {tt.name}, got {t.type.name} ({t.value!r})")
        if v is not None and t.value!=v: self.error(f"Expected {v!r}, got {t.value!r}")
        return self.advance()
    def expect_kw(self,w):
        t=self.current()
        if t.type!=TT.KEYWORD or t.value!=w:
            self.error(f"Expected keyword '{w}', got {t.value!r}")
        return self.advance()

    def parse(self):
        self.consume_newlines()
        body=self._block_until()
        return Program(body,line=0)

    def _block_until(self,*terminators):
        stmts=[]
        while True:
            self.consume_newlines()
            t=self.current()
            if t.type==TT.EOF: break
            if t.type==TT.KEYWORD and t.value in terminators: break
            stmts.append(self._stmt())
        return stmts

    def _stmt(self):
        self.consume_newlines()
        t=self.current(); line=t.line
        if t.type==TT.KEYWORD:
            kw=t.value
            if kw=="show" and self.peek().type!=TT.EQ:    return self._show()
            if kw=="if":      return self._if()
            if kw=="choose":  return self._choose()
            if kw=="from":    return self._from_dispatch()
            if kw=="each":    return self._for_each()
            if kw=="keep":    return self._keep()
            if kw in ("func", "def", "fn"): return self._func(keyword=kw)
            if kw in ("give", "return"):    return self._give()
            if kw=="try":     return self._try()
            if kw=="import":  return self._import()
            if kw=="swap":    return self._swap()
            if kw in ("breck", "break"):   self.advance(); return BreckStmt(line=line)
            if kw in ("skip", "continu", "continue"):    self.advance(); return SkipStmt(line=line)
            if kw=="reverse": return self._reverse()
            if kw=="const":   return self._const()
            if kw=="class":   return self._class()
            if kw=="enum":    return self._enum()
            if kw=="throw":   return self._throw()
            if kw=="assert":  return self._assert()
            if kw=="cd":      return self._cd()
        return self._assign_or_expr()

    def _cd(self):
        line=self.current().line; self.advance()
        target=self._expr()
        return CdStmt(target, line=line)

    def _from_dispatch(self):
        saved=self.pos; self.advance()
        if self.current().type in (TT.IDENT, TT.KEYWORD):
            self.advance()
            while self.current().type==TT.DOT: self.advance(); self.advance()
            t=self.current()
            is_imp=(t.type==TT.KEYWORD and t.value=="import") or (t.type==TT.IDENT and t.value=="import")
            self.pos=saved
            if is_imp: return self._from_import()
        else:
            self.pos=saved
        return self._for_range()

    def _show(self):
        line=self.current().line; self.advance(); vals=[]
        while self.current().type not in (TT.NEWLINE,TT.EOF):
            vals.append(self._expr())
            if self.current().type==TT.COMMA: self.advance()
        return Show(vals,line=line)

    def _if(self):
        line=self.current().line
        self.expect_kw("if"); cond=self._expr(); self.expect(TT.COLON); self.consume_newlines()
        then=self._block_until("elsif","else","end")
        elsifs=[]
        while self.check_kw("elsif"):
            self.advance(); ec=self._expr(); self.expect(TT.COLON); self.consume_newlines()
            elsifs.append((ec,self._block_until("elsif","else","end")))
        else_body=None
        if self.check_kw("else"):
            self.advance(); self.expect(TT.COLON); self.consume_newlines()
            else_body=self._block_until("end")
        self.expect_kw("end")
        return If(cond,then,elsifs,else_body,line=line)

    def _choose(self):
        line=self.current().line
        self.expect_kw("choose"); subj=self._expr(); self.expect(TT.COLON); self.consume_newlines()
        whens=[]
        while self.check_kw("when"):
            self.advance(); val=self._expr(); self.expect(TT.COLON); self.consume_newlines()
            whens.append((val,self._block_until("when","otherwise","end")))
        otherwise=None
        if self.check_kw("otherwise"):
            self.advance(); self.expect(TT.COLON); self.consume_newlines()
            otherwise=self._block_until("end")
        self.expect_kw("end")
        return Choose(subj,whens,otherwise,line=line)

    def _for_range(self):
        line=self.current().line
        self.expect_kw("from"); start=self._expr()
        self.expect_kw("to");   stop=self._expr()
        step=None
        if self.check_kw("stp"): self.advance(); step=self._expr()
        self.expect_kw("in"); var=self.expect(TT.IDENT).value
        self.expect(TT.COLON); self.consume_newlines()
        body=self._block_until("end"); self.expect_kw("end")
        return ForRange(var,start,stop,step,body,line=line)

    def _for_each(self):
        line=self.current().line
        self.expect_kw("each"); var=self.expect(TT.IDENT).value
        self.expect_kw("in"); it=self._expr()
        self.expect(TT.COLON); self.consume_newlines()
        body=self._block_until("end"); self.expect_kw("end")
        return ForEach(var,it,body,line=line)

    def _keep(self):
        line=self.current().line; self.expect_kw("keep")
        var=self.expect(TT.IDENT).value; hint=None
        if self.current().type==TT.COLON:
            self.advance(); hint=self.current().value; self.advance()
        self.expect(TT.EQ)
        full=self._expr()
        if isinstance(full,BinOp) and full.op in ("<","<=",">",">=","==","!="):
            init=full.left
            cond=BinOp(Var(var,line=line),full.op,full.right,line=line)
        else:
            init=full; cond=full
        self.expect(TT.COLON); self.consume_newlines()
        body=self._block_until("end"); self.expect_kw("end")
        return Keep(var,hint,init,cond,body,line=line)

    def _func(self,keyword="func"):
        line=self.current().line; self.advance()
        name=self.expect(TT.IDENT).value; rtype=None
        if self.current().type==TT.COLON:
            self.advance(); rt=self.current()
            if rt.type in (TT.KEYWORD,TT.IDENT): rtype=rt.value; self.advance()
        params=[]
        if self.current().type==TT.LPAREN:
            self.advance()
            while self.current().type!=TT.RPAREN:
                pn=self.expect(TT.IDENT).value; pt=None
                if self.current().type==TT.COLON:
                    self.advance(); tp=self.current()
                    if tp.type in (TT.KEYWORD,TT.IDENT): pt=tp.value; self.advance()
                params.append((pn,pt))
                if self.current().type==TT.COMMA: self.advance()
            self.expect(TT.RPAREN)
        self.expect(TT.COLON); self.consume_newlines()
        body=self._block_until("end"); self.expect_kw("end")
        return FuncDef(name,params,rtype,body,line=line)

    def _give(self):
        line=self.current().line; self.advance()
        if self.current().type in (TT.NEWLINE,TT.EOF): return Return(None,line=line)
        return Return(self._expr(),line=line)

    def _try(self):
        line=self.current().line; self.expect_kw("try")
        self.expect(TT.COLON); self.consume_newlines()
        try_body=self._block_until("catch","finally","end")
        catch_clauses=[]
        while self.check_kw("catch"):
            self.advance()
            type_name=None; var=None
            if self.current().type==TT.IDENT:
                first=self.advance().value
                if self.check_kw("as"):
                    self.advance(); var=self.expect(TT.IDENT).value; type_name=first
                else:
                    var=first
            elif self.current().type==TT.KEYWORD and self.current().value not in ("as","finally","end"):
                type_name=self.advance().value
                if self.check_kw("as"): self.advance(); var=self.expect(TT.IDENT).value
            self.expect(TT.COLON); self.consume_newlines()
            cb=self._block_until("catch","finally","end")
            catch_clauses.append((type_name,var,cb))
        finally_body=None
        if self.check_kw("finally"):
            self.advance(); self.expect(TT.COLON); self.consume_newlines()
            finally_body=self._block_until("end")
        self.expect_kw("end")
        return TryCatch(try_body,catch_clauses,finally_body,line=line)

    def _import(self):
        line=self.current().line; self.advance()
        if self.current().type not in (TT.IDENT, TT.KEYWORD): self.error("Expected module name")
        mod=self.advance().value
        while self.current().type==TT.DOT:
            self.advance()
            if self.current().type not in (TT.IDENT, TT.KEYWORD): self.error("Expected module name")
            mod+="."+self.advance().value
        alias=None
        if (self.current().type in (TT.KEYWORD, TT.IDENT) and self.current().value == "as"):
            self.advance()
            if self.current().type not in (TT.IDENT, TT.KEYWORD): self.error("Expected alias name")
            alias=self.advance().value
        return ImportStmt(mod,None,alias,line=line)

    def _from_import(self):
        line=self.current().line; self.advance()
        if self.current().type not in (TT.IDENT, TT.KEYWORD): self.error("Expected module name")
        mod=self.advance().value
        while self.current().type==TT.DOT:
            self.advance()
            if self.current().type not in (TT.IDENT, TT.KEYWORD): self.error("Expected module name")
            mod+="."+self.advance().value
        t=self.current()
        if t.type==TT.KEYWORD and t.value=="import": self.advance()
        elif t.type==TT.IDENT and t.value=="import": self.advance()
        else: self.error("Expected 'import'")
        names=[]
        while self.current().type not in (TT.NEWLINE,TT.EOF):
            n=self.current()
            if n.type in (TT.IDENT,TT.KEYWORD): names.append(n.value); self.advance()
            if self.current().type==TT.COMMA: self.advance()
            else: break
        return ImportStmt(mod,names,None,line=line)

    def _swap(self):
        line=self.current().line; self.advance()
        self.expect(TT.LPAREN); a=self.expect(TT.IDENT).value
        self.expect(TT.ARROW); b=self.expect(TT.IDENT).value
        self.expect(TT.RPAREN); return SwapStmt(a,b,line=line)

    def _reverse(self):
        line=self.current().line; self.advance()
        return ReverseStmt(self.expect(TT.IDENT).value,line=line)

    def _const(self):
        line=self.current().line; self.advance()
        name=self.expect(TT.IDENT).value; self.expect(TT.EQ)
        return Assign(name,self._expr(),is_const=True,line=line)

    def _class(self):
        line=self.current().line; self.expect_kw("class")
        name=self.expect(TT.IDENT).value
        superclass=None
        if self.check_kw("extends"): self.advance(); superclass=self.expect(TT.IDENT).value
        self.expect(TT.COLON); self.consume_newlines()
        body=self._class_body()
        self.expect_kw("end")
        return ClassDef(name,superclass,body,line=line)

    def _class_body(self):
        members=[]
        while True:
            self.consume_newlines()
            t=self.current()
            if t.type==TT.EOF or (t.type==TT.KEYWORD and t.value=="end"): break
            members.append(self._class_member())
        return members

    def _class_member(self):
        t=self.current(); line=t.line
        if t.type==TT.KEYWORD:
            kw=t.value
            if kw in ("public","private","static"):
                vis=kw; self.advance()
                if (self.check_kw("def") or self.check_kw("func") or self.check_kw("fn")) and vis=="static":
                    self.advance(); return self._method_def("def",is_static=True)
                if self.check_kw("def") or self.check_kw("func") or self.check_kw("fn"):
                    self.advance(); return self._method_def("def",is_static=False)
                name=self.expect(TT.IDENT).value; val=None
                if self.current().type==TT.EQ: self.advance(); val=self._expr()
                return FieldDecl(name,val,vis,line=line)
            if kw=="init":
                self.advance(); return self._method_def("init",is_static=False,name="init")
            if kw in ("def", "func", "fn"):
                self.advance(); return self._method_def("def",is_static=False)
            if kw=="get":
                self.advance(); return self._method_def("get",is_static=False)
            if kw=="set":
                self.advance(); return self._method_def("set",is_static=False)
            if kw=="static":
                self.advance()
                if self.check_kw("def") or self.check_kw("func") or self.check_kw("fn"): self.advance(); return self._method_def("def",is_static=True)
                name=self.expect(TT.IDENT).value; val=None
                if self.current().type==TT.EQ: self.advance(); val=self._expr()
                return FieldDecl(name,val,"static",line=line)
        name=self.expect(TT.IDENT).value; val=None
        if self.current().type==TT.EQ: self.advance(); val=self._expr()
        return FieldDecl(name,val,"public",line=line)

    def _method_def(self,kind,is_static,name=None):
        line=self.current().line
        if name is None:
            name=self.expect(TT.IDENT).value
        params=[]
        if self.current().type==TT.LPAREN:
            self.advance()
            while self.current().type!=TT.RPAREN:
                pn=self.expect(TT.IDENT).value; pt=None
                if self.current().type==TT.COLON:
                    self.advance(); tp=self.current()
                    if tp.type in (TT.KEYWORD,TT.IDENT): pt=tp.value; self.advance()
                params.append((pn,pt))
                if self.current().type==TT.COMMA: self.advance()
            self.expect(TT.RPAREN)
        self.expect(TT.COLON); self.consume_newlines()
        body=self._block_until("end"); self.expect_kw("end")
        return MethodDef(name,params,body,kind,is_static,line=line)

    def _enum(self):
        line=self.current().line; self.expect_kw("enum")
        name=self.expect(TT.IDENT).value; self.expect(TT.COLON)
        self.consume_newlines()
        members=[]
        while not self.check_kw("end"):
            self.consume_newlines()
            if self.current().type==TT.EOF: break
            mname=self.expect(TT.IDENT).value; mval=None
            if self.current().type==TT.EQ: self.advance(); mval=self._expr()
            members.append((mname,mval))
            self.consume_newlines()
        self.expect_kw("end")
        return EnumDef(name,members,line=line)

    def _throw(self):
        line=self.current().line; self.advance()
        return ThrowStmt(self._expr(),line=line)

    def _assert(self):
        line=self.current().line; self.advance()
        cond=self._expr(); msg=None
        if self.current().type==TT.COMMA: self.advance(); msg=self._expr()
        return AssertStmt(cond,msg,line=line)

    def _assign_or_expr(self):
        line=self.current().line; expr=self._expr()
        _ASGN={TT.EQ:"=",TT.PLUS_EQ:"+=",TT.MINUS_EQ:"-=",
               TT.STAR_EQ:"*=",TT.SLASH_EQ:"/=",TT.DSLASH_EQ:"//=",TT.PERCENT_EQ:"%="}
        if self.current().type in _ASGN:
            op=_ASGN[self.current().type]; self.advance(); rhs=self._expr()
            if isinstance(expr,Var): return Assign(expr.name,rhs,op=op,line=line)
            if isinstance(expr,Attr): return AttrAssign(expr.obj,expr.name,rhs,op=op,line=line)
            if isinstance(expr,Index): return ExprStmt(BinOp(expr,op,rhs,line=line),line=line)
            self.error(f"Invalid assignment target")
        if isinstance(expr,Var) and self.current().type==TT.COLON:
            self.advance(); hint=None
            if self.current().type==TT.KEYWORD: hint=self.current().value; self.advance()
            if self.current().type==TT.EQ:
                self.advance(); return VarDecl(expr.name,hint,self._expr(),line=line)
            return VarDecl(expr.name,hint,None,line=line)
        return ExprStmt(expr,line=line)

    # ── Expressions ──────────────────────────────────────────
    def _expr(self):    return self._or()
    def _or(self):
        l=self._and()
        while self.check_kw("or"): self.advance(); l=BinOp(l,"or",self._and(),line=l.line)
        return l
    def _and(self):
        l=self._not()
        while self.check_kw("and"): self.advance(); l=BinOp(l,"and",self._not(),line=l.line)
        return l
    def _not(self):
        if self.check_kw("not"):
            line=self.current().line; self.advance()
            return UnaryOp("not",self._not(),line=line)
        return self._bitor()
    def _bitor(self):
        l=self._bitxor()
        while self.current().type==TT.PIPE:
            self.advance(); l=BinOp(l,"|",self._bitxor(),line=l.line)
        return l
    def _bitxor(self):
        l=self._bitand()
        while self.current().type==TT.CARET:
            self.advance(); l=BinOp(l,"^",self._bitand(),line=l.line)
        return l
    def _bitand(self):
        l=self._compare()
        while self.current().type==TT.AMP:
            self.advance(); l=BinOp(l,"&",self._compare(),line=l.line)
        return l
    def _compare(self):
        l=self._add()
        _CMP={TT.EQEQ:"==",TT.NEQ:"!=",TT.LT:"<",TT.GT:">",TT.LTE:"<=",TT.GTE:">="}
        while self.current().type in _CMP:
            op=_CMP[self.current().type]; self.advance()
            l=BinOp(l,op,self._add(),line=l.line)
        return l
    def _add(self):
        l=self._mul()
        while self.current().type in (TT.PLUS,TT.MINUS):
            op=self.advance().value; l=BinOp(l,op,self._mul(),line=l.line)
        return l
    def _mul(self):
        l=self._power()
        while self.current().type in (TT.STAR,TT.SLASH,TT.DSLASH,TT.PERCENT):
            op=self.advance().value; l=BinOp(l,op,self._power(),line=l.line)
        return l
    def _power(self):
        l=self._unary()
        if self.current().type==TT.DSTAR:
            self.advance(); return BinOp(l,"**",self._power(),line=l.line)
        return l
    def _unary(self):
        if self.current().type==TT.MINUS:
            line=self.current().line; self.advance()
            return UnaryOp("-",self._unary(),line=line)
        if self.current().type==TT.PLUS: self.advance()
        return self._postfix()

    def _postfix(self):
        node=self._primary()
        while True:
            if self.current().type==TT.DOT:
                self.advance()
                m=self.current()
                if m.type not in (TT.IDENT,TT.KEYWORD): self.error("Expected attr name")
                mn=m.value; self.advance()
                if self.current().type==TT.LPAREN:
                    self.advance(); args=[]
                    while True:
                        self.consume_newlines()
                        if self.current().type==TT.RPAREN: break
                        if self.current().type==TT.EOF: break
                        args.append(self._expr())
                        self.consume_newlines()
                        if self.current().type==TT.COMMA: self.advance()
                        self.consume_newlines()
                    self.expect(TT.RPAREN)
                    node=MethodCall(node,mn,args,line=node.line)
                else:
                    node=Attr(node,mn,line=node.line)
            elif self.current().type==TT.LBRACKET:
                save_bracket_pos = self.pos
                try:
                    self.advance(); line=node.line
                    sn=stop_n=step_n=None; rev=False
                    if self.check_kw("to"):
                        self.advance()
                        if self.check_kw("stp"):
                            self.advance(); step_n=self._expr()
                            if (isinstance(step_n,UnaryOp) and step_n.op=="-"
                                    and isinstance(step_n.operand,Literal)
                                    and step_n.operand.value==1): rev=True
                        elif self.current().type!=TT.RBRACKET:
                            stop_n=self._expr()
                            if self.check_kw("stp"): self.advance(); step_n=self._expr()
                    else:
                        e0=self._expr()
                        if self.check_kw("to"):
                            sn=e0; self.advance()
                            if not self.check_kw("stp") and self.current().type!=TT.RBRACKET:
                                stop_n=self._expr()
                            if self.check_kw("stp"): self.advance(); step_n=self._expr()
                        else:
                            if self.current().type == TT.COMMA:
                                self.pos = save_bracket_pos
                                break
                            self.expect(TT.RBRACKET); node=Index(node,e0,line=line); continue
                    self.expect(TT.RBRACKET)
                    node=Slice(node,sn,stop_n,step_n,rev,line=line)
                except ParseError:
                    self.pos = save_bracket_pos
                    break
            elif self.current().type==TT.LPAREN:
                if isinstance(node, (Literal, ListLit, SetLit, MapLit, TupleLit)):
                    break
                line=node.line; self.advance(); args=[]
                while True:
                    self.consume_newlines()
                    if self.current().type==TT.RPAREN: break
                    if self.current().type==TT.EOF: break
                    args.append(self._expr())
                    self.consume_newlines()
                    if self.current().type==TT.COMMA: self.advance()
                    self.consume_newlines()
                self.expect(TT.RPAREN); node=Call(node,args,line=line)
            else: break
        return node

    def _is_lambda(self):
        saved=self.pos
        try:
            if self.current().type==TT.IDENT and self.peek().type==TT.ARROW2: return True
            if self.current().type==TT.LPAREN:
                self.advance()
                while self.current().type in (TT.IDENT,TT.COMMA): self.advance()
                if self.current().type==TT.RPAREN and self.peek().type==TT.ARROW2: return True
        finally:
            self.pos=saved
        return False

    def _lambda(self):
        line=self.current().line; params=[]
        if self.current().type==TT.IDENT:
            params.append(self.advance().value)
        else:
            self.expect(TT.LPAREN)
            while self.current().type!=TT.RPAREN:
                params.append(self.expect(TT.IDENT).value)
                if self.current().type==TT.COMMA: self.advance()
            self.expect(TT.RPAREN)
        self.expect(TT.ARROW2)
        if self.current().type==TT.LBRACE:
            saved=self.pos
            self.advance()
            self.consume_newlines()
            if self.current().type in (TT.IDENT, TT.STRING, TT.INT) and self.peek(1).type==TT.COLON:
                self.pos=saved
                body=self._expr()
                return Lambda(params,body,line=line)
            stmts=[]
            while self.current().type!=TT.RBRACE and self.current().type!=TT.EOF:
                self.consume_newlines()
                if self.current().type==TT.RBRACE: break
                stmts.append(self._stmt())
                self.consume_newlines()
            self.expect(TT.RBRACE)
            return Lambda(params,stmts,line=line)
        body=self._expr()
        return Lambda(params,body,line=line)

    def _primary(self):
        t=self.current(); line=t.line
        if self._is_lambda(): return self._lambda()

        if t.type==TT.INT:    self.advance(); return Literal(t.value,line=line)
        if t.type==TT.FLOAT:  self.advance(); return Literal(t.value,line=line)
        if t.type==TT.STRING: self.advance(); return Literal(t.value,line=line)
        if t.type==TT.BOOL:   self.advance(); return Literal(t.value,line=line)
        if t.type==TT.NONE:   self.advance(); return Literal(None,line=line)
        if t.type==TT.INTERP:
            self.advance()
            parsed_parts=[]
            for txt,is_expr in t.value:
                if is_expr:
                    try:
                        sub_tokens=Lexer(txt).tokenize()
                        sub_parser=Parser(sub_tokens)
                        node=sub_parser._expr()
                    except Exception:
                        node=Literal(txt,line=line)
                    parsed_parts.append((node,True))
                else:
                    parsed_parts.append((txt,False))
            return Interpolated(parsed_parts,line=line)
        if t.type==TT.IDENT:  self.advance(); return Var(t.value,line=line)
        if t.type==TT.KEYWORD:
            kw=t.value
            if kw=="input": return self._input_expr()
            if kw=="super":
                self.advance()
                if self.current().type==TT.DOT:
                    self.advance()
                    m=self.current()
                    if m.type not in (TT.IDENT,TT.KEYWORD): self.error("Expected method name")
                    method=m.value; self.advance()
                    args=[]
                    if self.current().type==TT.LPAREN:
                        self.advance()
                        while self.current().type!=TT.RPAREN:
                            args.append(self._expr())
                            if self.current().type==TT.COMMA: self.advance()
                        self.expect(TT.RPAREN)
                    return SuperCall(method,args,line=line)
                return Var("super",line=line)
            if kw=="this": self.advance(); return Var("this",line=line)
            if kw in ("int","float","string","bool","list","set","map","tuple"):
                self.advance()
                if self.current().type==TT.LPAREN:
                    self.advance(); arg=self._expr(); self.expect(TT.RPAREN)
                    return MethodCall(arg,kw,[],line=line)
                return Var(kw,line=line)
            self.advance(); return Var(kw,line=line)
        if t.type==TT.LPAREN:
            self.advance()
            if self.current().type==TT.RPAREN: self.advance(); return TupleLit([],line=line)
            first=self._expr()
            if self.current().type==TT.COMMA:
                els=[first]
                while self.current().type==TT.COMMA:
                    self.advance()
                    if self.current().type==TT.RPAREN: break
                    els.append(self._expr())
                self.expect(TT.RPAREN); return TupleLit(els,line=line)
            self.expect(TT.RPAREN); return first
        if t.type==TT.LBRACKET: return self._list_or_comp()
        if t.type==TT.LBRACE:   return self._set_map_or_comp()
        self.error(f"Unexpected token {t.value!r}")

    def _input_expr(self):
        line=self.current().line; self.advance(); p=None
        if self.current().type==TT.LPAREN:
            self.advance()
            if self.current().type!=TT.RPAREN: p=self._expr()
            self.expect(TT.RPAREN)
            return InputExpr(p,line=line)
        return Var("input",line=line)

    def _list_or_comp(self):
        line=self.current().line; self.advance()
        if self.check_kw("take"):
            self.advance(); expr=self._expr()
            self.expect_kw("each"); var=self.expect(TT.IDENT).value
            self.expect_kw("in"); it=self._expr()
            cond=None
            if self.check_kw("if"): self.advance(); cond=self._expr()
            self.expect(TT.RBRACKET)
            return ListComp(expr,var,it,cond,line=line)
        els=[]
        while True:
            self.consume_newlines()
            if self.current().type==TT.RBRACKET: break
            if self.current().type==TT.EOF: break
            els.append(self._expr())
            self.consume_newlines()
            if self.current().type==TT.COMMA: self.advance()
            self.consume_newlines()
        self.expect(TT.RBRACKET); return ListLit(els,line=line)

    def _set_map_or_comp(self):
        line=self.current().line; self.advance()
        self.consume_newlines()
        if self.current().type==TT.RBRACE: self.advance(); return SetLit([],line=line)
        if self.check_kw("take"):
            self.advance(); expr=self._expr()
            self.expect_kw("each"); var=self.expect(TT.IDENT).value
            self.expect_kw("in"); it=self._expr()
            cond=None
            if self.check_kw("if"): self.advance(); cond=self._expr()
            self.consume_newlines()
            self.expect(TT.RBRACE)
            return SetComp(expr,var,it,cond,line=line)
        first=self._expr()
        if self.current().type==TT.COLON:
            if isinstance(first, Var): first = Literal(first.name, line=first.line)
            self.advance(); self.consume_newlines(); fv=self._expr(); pairs=[(first,fv)]
            while True:
                self.consume_newlines()
                if self.current().type==TT.COMMA:
                    self.advance()
                    self.consume_newlines()
                if self.current().type==TT.RBRACE: break
                if self.current().type==TT.EOF: break
                k=self._expr()
                if isinstance(k, Var): k = Literal(k.name, line=k.line)
                self.expect(TT.COLON); self.consume_newlines(); v=self._expr(); pairs.append((k,v))
                self.consume_newlines()
            self.consume_newlines()
            self.expect(TT.RBRACE); return MapLit(pairs,line=line)
        els=[first]
        while True:
            self.consume_newlines()
            if self.current().type==TT.COMMA:
                self.advance()
                self.consume_newlines()
            if self.current().type==TT.RBRACE: break
            if self.current().type==TT.EOF: break
            els.append(self._expr())
            self.consume_newlines()
        self.consume_newlines()
        self.expect(TT.RBRACE); return SetLit(els,line=line)


# ============================================================
# RUNTIME OBJECTS
# ============================================================
class NovaError(Exception): pass
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ReturnSignal(Exception):
    def __init__(self,v): self.value=v
class NovaThrown(Exception):
    def __init__(self,val): self.val=val; super().__init__(str(val))

class NovaFunction:
    def __init__(self,name,params,rtype,body,closure):
        self.name=name; self.params=params; self.rtype=rtype
        self.body=body; self.closure=closure
    def __repr__(self): return f"<func {self.name}>"

class NovaLambda:
    def __init__(self,params,body,closure):
        self.params=params; self.body=body; self.closure=closure
    def __repr__(self): return f"<lambda>"

class NovaClass:
    def __init__(self,name,superclass,methods,getters,setters,static_fields,instance_defaults):
        self.name=name; self.superclass=superclass
        self.methods=methods; self.getters=getters; self.setters=setters
        self.static_fields=static_fields; self.instance_defaults=instance_defaults
    def __repr__(self): return f"<class {self.name}>"

class NovaInstance:
    def __init__(self,klass):
        self.klass=klass
        self.fields=dict(klass.instance_defaults)
    def __repr__(self): return f"<{self.klass.name} instance>"

class NovaEnumMember:
    def __init__(self,name,value,enum_class):
        self.name=name; self.value=value; self.enum_class=enum_class
    def __eq__(self,other):
        if isinstance(other,NovaEnumMember): return self.value==other.value and self.name==other.name
        return self.value==other
    def __hash__(self): return hash((self.enum_class.name,self.name))
    def __repr__(self): return f"{self.enum_class.name}.{self.name}"

class NovaEnum:
    def __init__(self,name,members):
        self.name=name; self.members=members
    def __getattr__(self,key):
        if key in ("name","members"): raise AttributeError(key)
        if key in self.members: return self.members[key]
        raise AttributeError(f"Enum {self.name} has no member {key!r}")
    def __repr__(self): return f"<enum {self.name}>"

class NovaBuiltinError:
    def __init__(self,kind,msg,code=None):
        self.kind=kind; self.msg=msg; self.code=code
    def __str__(self): return f"{self.kind}: {self.msg}" + (f" (code {self.code})" if self.code else "")
    def __repr__(self): return str(self)

class _KProxy:
    def __init__(self,d): self.data=d
    def __iter__(self): return iter(self.data)
class _VProxy:
    def __init__(self,d): self.data=d
    def __iter__(self): return iter(self.data)


# ── Fluent File Handle ────────────────────────────────────────
class NovaFile:
    def __init__(self, path: str, mode: str = "read"):
        self.path = path
        self.mode = mode
        m_map = {
            "read": "r", "r": "r",
            "write": "w", "w": "w",
            "add": "a", "append": "a", "a": "a",
            "bytes": "rb", "rb": "rb",
            "wbytes": "wb", "wb": "wb",
        }
        self.py_mode = m_map.get(mode, "r")
        encoding = None if "b" in self.py_mode else "utf-8"
        self.f = open(path, self.py_mode, encoding=encoding)

    def read(self, n=-1):
        return self.f.read(n) if n > 0 else self.f.read()

    def readLine(self):
        return self.f.readline()

    def readLines(self):
        return self.f.readlines()

    def readBytes(self, n=-1):
        if "b" not in self.py_mode:
            with open(self.path, "rb") as bf: return bf.read(n) if n > 0 else bf.read()
        return self.f.read(n) if n > 0 else self.f.read()

    def write(self, data):
        self.f.write(str(data))
        self.f.flush()
        return self

    def writeLine(self, line):
        self.f.write(str(line) + "\n")
        self.f.flush()
        return self

    def writeBytes(self, b):
        if "b" not in self.py_mode:
            with open(self.path, "wb") as bf: bf.write(bytes(b))
        else:
            self.f.write(bytes(b))
        return self

    def close(self):
        if not self.f.closed: self.f.close()
        return None

    def seek(self, pos=0):
        self.f.seek(pos); return self

    def append(self, data):
        return self.write(data)

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    def __repr__(self): return f"<file '{self.path}' mode='{self.mode}'>"


# ============================================================
# ENVIRONMENT
# ============================================================
class Env:
    def __init__(self,parent=None):
        self.vars: Dict[str,Any]={}; self.consts: set=set(); self.parent=parent

    def get(self,name,line=0):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name,line)
        raise NovaError(f"[Line {line}] NameError: '{name}' is not defined")

    def set(self,name,value,line=0):
        if self._is_const(name): raise NovaError(f"[Line {line}] ConstError: cannot reassign const '{name}'")
        if name in self.vars: self.vars[name]=value
        elif self.parent and self.parent._has(name): self.parent.set(name,value,line)
        else: self.vars[name]=value

    def define(self,name,value,const=False):
        self.vars[name]=value
        if const: self.consts.add(name)

    def _has(self,n): return n in self.vars or (self.parent is not None and self.parent._has(n))
    def _is_const(self,n):
        if n in self.consts: return True
        return self.parent._is_const(n) if self.parent else False


# ============================================================
# BUILT-IN ERRORS
# ============================================================
_BUILTIN_ERRORS = {
    "Error","FileNotFoundError","PermissionError","ValueError",
    "TypeError","IndexError","KeyError","ZeroDivError","NetworkError",
    "AssertionError",
}


# ============================================================
# STANDARD MODULE STRUCT
# ============================================================
class StdModule:
    def __init__(self, name: str, exports: dict):
        self._name = name
        self._exports = exports
        for k, v in exports.items(): setattr(self, k, v)
    def __repr__(self): return f"<module '{self._name}'>"
    def __getitem__(self, item): return self._exports[item]


# ============================================================
# V1.5 STANDARD LIBRARIES (math, string, list, set, file, random, time, json)
# ============================================================

def _is_prime(n):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def _nth_prime(n):
    count = 0; candidate = 1
    while count < n:
        candidate += 1
        if _is_prime(candidate): count += 1
    return candidate


def build_math_module():
    m = {}
    m["pi"]   = math.pi
    m["e"]    = math.e
    m["tau"]  = math.tau
    m["inf"]  = float("inf")
    m["ninf"] = float("-inf")
    m["nan"]  = float("nan")
    m["phi"]  = (1.0 + math.sqrt(5)) / 2.0
    m["deg"]  = 180.0 / math.pi
    m["root"]  = lambda x, n=2: x ** (1.0 / n)
    m["sqrt"]  = math.sqrt
    m["power"] = lambda x, y: x ** y
    m["pow"]   = math.pow
    m["abs"]   = abs
    m["floor"] = math.floor
    m["ceil"]  = math.ceil
    m["round"] = round
    m["max"]   = lambda *a: max(a[0]) if len(a)==1 and isinstance(a[0], (list,tuple,set)) else max(a)
    m["min"]   = lambda *a: min(a[0]) if len(a)==1 and isinstance(a[0], (list,tuple,set)) else min(a)
    m["sum"]   = lambda it: sum(it)
    m["prod"]  = lambda it: math.prod(it)
    m["sin"]   = math.sin
    m["cos"]   = math.cos
    m["tan"]   = math.tan
    m["asin"]  = math.asin
    m["acos"]  = math.acos
    m["atan"]  = math.atan
    m["atan2"] = math.atan2
    m["sinh"]  = math.sinh
    m["cosh"]  = math.cosh
    m["tanh"]  = math.tanh
    m["toRad"] = math.radians
    m["toDeg"] = math.degrees
    m["exp"]     = math.exp
    m["log"]     = lambda x, b=math.e: math.log(x) if b==math.e else math.log(x, b)
    m["log10"]   = math.log10
    m["log2"]    = math.log2
    m["logBase"] = lambda x, b: math.log(x, b)
    m["exp2"]    = lambda x: 2.0 ** x
    m["expm1"]   = math.expm1
    m["log1p"]   = math.log1p
    m["mod"]     = lambda a, b: a % b
    m["gcd"]     = math.gcd
    m["lcm"]     = math.lcm
    m["fact"]    = math.factorial
    m["perm"]    = math.perm
    m["comb"]    = math.comb
    m["isEven"]  = lambda n: n % 2 == 0
    m["isOdd"]   = lambda n: n % 2 != 0
    m["isPrime"] = _is_prime
    m["prime"]   = _nth_prime
    m["clamp"]   = lambda v, lo, hi: max(lo, min(hi, v))
    m["lerp"]    = lambda a, b, t: a + (b - a) * t
    m["sign"]    = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
    m["dist"]    = lambda p1, p2: math.dist(p1, p2)
    m["hypot"]   = math.hypot
    m["cbrt"]    = math.cbrt
    m["nroot"]   = lambda x, n: x ** (1.0 / n)
    m["trunc"]   = math.trunc
    m["frac"]    = lambda x: x - math.floor(x)
    m["toInt"]   = int
    m["toFloat"] = float
    m["near"]    = lambda a, b, eps=1e-9: abs(a - b) <= eps
    m["range"]   = lambda s, e: list(range(int(s), int(e) + 1))
    m["range2"]  = lambda s, e, stp=1: list(range(int(s), int(e) + 1, int(stp)))
    m["rand"]    = random.random
    return StdModule("math", m)


def build_string_module():
    m = {}
    import string as _py_str
    m["empty"]   = ""
    m["space"]   = " "
    m["digits"]  = _py_str.digits
    m["letters"] = _py_str.ascii_letters
    m["lower"]   = _py_str.ascii_lowercase
    m["upper"]   = _py_str.ascii_uppercase
    m["upper"]   = lambda s: str(s).upper()
    m["lower"]   = lambda s: str(s).lower()
    m["title"]   = lambda s: str(s).title()
    m["cap"]     = lambda s: str(s).capitalize()
    m["swap"]    = lambda s: str(s).swapcase()
    m["isUpper"] = lambda s: str(s).isupper()
    m["isLower"] = lambda s: str(s).islower()
    m["isTitle"] = lambda s: str(s).istitle()
    m["trim"]    = lambda s: str(s).strip()
    m["trimL"]   = lambda s: str(s).lstrip()
    m["trimR"]   = lambda s: str(s).rstrip()
    m["trimAll"] = lambda s: re.sub(r'\s+', '', str(s))
    m["trimC"]   = lambda s, c=" ": str(s).strip(c)
    m["len"]     = lambda s: len(str(s))
    m["has"]     = lambda s, sub: str(sub) in str(s)
    m["at"]      = lambda s, i: str(s)[int(i)]
    m["index"]   = lambda s, sub: str(s).find(str(sub))
    m["lastI"]   = lambda s, sub: str(s).rfind(str(sub))
    m["count"]   = lambda s, sub: str(s).count(str(sub))
    m["starts"]  = lambda s, pre: str(s).startswith(str(pre))
    m["ends"]    = lambda s, suf: str(s).endswith(str(suf))
    m["isEmpty"] = lambda s: len(str(s)) == 0
    m["isDigit"] = lambda s: str(s).isdigit()
    m["isLetter"]= lambda s: str(s).isalpha()
    m["isAlNum"] = lambda s: str(s).isalnum()
    m["isSpace"] = lambda s: str(s).isspace()
    m["split"]     = lambda s, sep=None: str(s).split(sep)
    m["join"]      = lambda sep, it: str(sep).join(str(x) for x in it)
    m["repeat"]    = lambda s, n=1: str(s) * int(n)
    m["replace"]   = lambda s, o, n: str(s).replace(str(o), str(n), 1)
    m["replaceA"]  = lambda s, o, n: str(s).replace(str(o), str(n))
    m["slice"]     = lambda s, st, en: str(s)[int(st):int(en)]
    m["sliceFrom"] = lambda s, st: str(s)[int(st):]
    m["sliceTo"]   = lambda s, en: str(s)[:int(en)]
    m["reverse"]   = lambda s: str(s)[::-1]
    m["padL"]      = lambda s, n, c=" ": str(s).rjust(int(n), c)
    m["padR"]      = lambda s, n, c=" ": str(s).ljust(int(n), c)
    m["pad"]       = lambda s, n, c=" ": str(s).center(int(n), c)
    m["first"]     = lambda s: str(s)[0] if s else ""
    m["last"]      = lambda s: str(s)[-1] if s else ""
    m["take"]      = lambda s, n: str(s)[:int(n)]
    m["drop"]      = lambda s, n: str(s)[int(n):]
    m["takeL"]     = lambda s, n: str(s)[-int(n):]
    m["dropL"]     = lambda s, n: str(s)[:-int(n)]
    m["words"]     = lambda s: str(s).split()
    m["wordC"]     = lambda s: len(str(s).split())
    m["codeAt"]    = lambda s, i=0: ord(str(s)[int(i)])
    m["fromCode"]  = lambda c: chr(int(c))
    m["toBytes"]   = lambda s: list(str(s).encode("utf-8"))
    m["fromBytes"] = lambda b: bytes(b).decode("utf-8", errors="replace")
    m["toList"]    = lambda s: list(str(s))
    m["equals"]    = lambda a, b: str(a) == str(b)
    m["equalsI"]   = lambda a, b: str(a).lower() == str(b).lower()
    m["same"]      = lambda a, b: str(a) == str(b)
    m["add"]       = lambda s, other: str(s) + str(other)
    m["addAt"]     = lambda s, i, other: str(s)[:int(i)] + str(other) + str(s)[int(i):]
    return StdModule("string", m)


def build_list_module():
    m = {}
    m["empty"]   = lambda: []
    m["range"]   = lambda s, e: list(range(int(s), int(e) + 1))
    m["range2"]  = lambda s, e, stp=1: list(range(int(s), int(e) + 1, int(stp)))
    m["repeat"]  = lambda v, n: [v] * int(n)
    m["repeatI"] = lambda v, n: [v] * int(n)
    m["fromSet"] = lambda s: sorted(list(s), key=str)
    m["size"]    = lambda l: len(l)
    m["len"]     = lambda l: len(l)
    m["isEmpty"] = lambda l: len(l) == 0
    m["has"]     = lambda l, x: x in l
    m["index"]   = lambda l, x: l.index(x) if x in l else -1
    m["lastI"]   = lambda l, x: (len(l) - 1 - l[::-1].index(x)) if x in l else -1
    m["count"]   = lambda l, x: l.count(x)
    m["first"]   = lambda l: l[0] if l else None
    m["last"]    = lambda l: l[-1] if l else None
    m["at"]      = lambda l, i: l[int(i)]
    m["atL"]     = lambda l, i: l[-int(i)]
    m["add"]       = lambda l, x: l.append(x) or l
    m["addAt"]     = lambda l, i, x: l.insert(int(i), x) or l
    m["addList"]   = lambda l, other: l.extend(other) or l
    m["remove"]    = lambda l, x: l.remove(x) or l if x in l else l
    m["removeAt"]  = lambda l, i: l.pop(int(i))
    m["removeF"]   = lambda l: l.pop(0) if l else None
    m["removeL"]   = lambda l: l.pop() if l else None
    m["removeAll"] = lambda l, x: [item for item in l if item != x]
    m["clear"]     = lambda l: l.clear() or l
    m["pop"]       = lambda l: l.pop() if l else None
    m["popAt"]     = lambda l, i: l.pop(int(i))
    m["set"]       = lambda l, i, v: l.__setitem__(int(i), v) or l
    m["sort"]      = lambda l: l.sort() or l
    m["dsort"]     = lambda l: l.sort(reverse=True) or l
    m["sorted"]    = lambda l: sorted(l)
    m["dsorted"]   = lambda l: sorted(l, reverse=True)
    m["reverse"]   = lambda l: l.reverse() or l
    m["reversed"]  = lambda l: l[::-1]
    m["shuffle"]   = lambda l: random.shuffle(l) or l
    m["shuffled"]  = lambda l: random.sample(list(l), len(l))
    m["filter"]    = lambda l, fn: [x for x in l if fn(x)]
    m["map"]       = lambda l, fn: [fn(x) for x in l]
    m["mapI"]      = lambda l, fn: [fn(x, i) for i, x in enumerate(l)]
    m["keep"]      = lambda l, fn: [x for x in l if fn(x)]
    m["change"]    = lambda l, fn: [fn(x) for x in l]
    m["flat"]      = lambda l: [item for sub in l for item in (sub if isinstance(sub, (list, tuple)) else [sub])]
    m["flatMap"]   = lambda l, fn: [item for x in l for item in (fn(x) if isinstance(fn(x), (list, tuple)) else [fn(x)])]
    m["slice"]     = lambda l, s, e: l[int(s):int(e)]
    m["sliceFrom"] = lambda l, s: l[int(s):]
    m["sliceTo"]   = lambda l, e: l[:int(e)]
    m["take"]      = lambda l, n: l[:int(n)]
    m["drop"]      = lambda l, n: l[int(n):]
    m["chunk"]     = lambda l, n=1: [list(l)[i:i+int(n)] for i in range(0, len(l), int(n))]
    m["window"]    = lambda l, n=2: [list(l)[i:i+int(n)] for i in range(len(l) - int(n) + 1)]
    m["zip"]       = lambda l, other: list(zip(l, other))
    m["countIf"]   = lambda l, fn: sum(1 for x in l if fn(x))
    m["find"]      = lambda l, fn: next((x for x in l if fn(x)), None)
    m["findLast"]  = lambda l, fn: next((x for x in reversed(l) if fn(x)), None)
    m["findIndex"] = lambda l, fn: next((i for i, x in enumerate(l) if fn(x)), -1)
    m["findAll"]   = lambda l, fn: [x for x in l if fn(x)]
    m["every"]     = lambda l, fn: all(fn(x) for x in l)
    m["some"]      = lambda l, fn: any(fn(x) for x in l)
    m["sum"]       = lambda l: sum(l)
    m["prod"]      = lambda l: math.prod(l)
    m["max"]       = lambda l: max(l) if l else None
    m["min"]       = lambda l: min(l) if l else None
    m["avg"]       = lambda l: sum(l) / len(l) if l else 0
    m["hasAll"]    = lambda l, sub: all(x in l for x in sub)
    m["hasAny"]    = lambda l, sub: any(x in l for x in sub)
    m["unique"]    = lambda l: list(dict.fromkeys(l))
    m["freq"]      = lambda l: {x: l.count(x) for x in set(l)}
    m["group"]     = lambda l, fn: {k: [x for x in l if fn(x) == k] for k in set(fn(x) for x in l)}
    m["join"]      = lambda l, sep=",": sep.join(str(x) for x in l)
    m["toSet"]     = lambda l: set(l)
    m["toMap"]     = lambda l: dict(l) if l and isinstance(l[0], (list, tuple)) else {i: x for i, x in enumerate(l)}
    m["toStr"]     = lambda l: str(l)
    m["copy"]      = lambda l: list(l)
    m["same"]      = lambda a, b: a == b
    return StdModule("list", m)


def build_set_module():
    m = {}
    m["U"]          = lambda a, b: a | b
    m["N"]          = lambda a, b: a & b
    m["diff"]       = lambda a, b: a ^ b
    m["size"]       = lambda s: len(s)
    m["len"]        = lambda s: len(s)
    m["isEmpty"]    = lambda s: len(s) == 0
    m["has"]        = lambda s, x: x in s
    m["hasAll"]     = lambda s, other: s.issuperset(other)
    m["hasAny"]     = lambda s, other: any(x in s for x in other)
    m["add"]        = lambda s, x: s.add(x) or s
    m["addAll"]     = lambda s, other: s.update(other) or s
    m["remove"]     = lambda s, x: s.discard(x) or s
    m["removeAll"]  = lambda s, other: s.difference_update(other) or s
    m["clear"]      = lambda s: s.clear() or s
    m["pop"]        = lambda s: s.pop() if s else None
    m["copy"]       = lambda s: set(s)
    m["toList"]     = lambda s: sorted(list(s), key=str)
    m["toListS"]    = lambda s: sorted(list(s), key=str)
    m["isSub"]      = lambda a, b: a.issubset(b)
    m["isSuper"]    = lambda a, b: a.issuperset(b)
    m["isEqual"]    = lambda a, b: a == b
    m["isDisjoint"] = lambda a, b: a.isdisjoint(b)
    m["sorted"]     = lambda s: sorted(list(s))
    m["dsorted"]    = lambda s: sorted(list(s), reverse=True)
    m["filter"]     = lambda s, fn: {x for x in s if fn(x)}
    m["map"]        = lambda s, fn: {fn(x) for x in s}
    m["take"]       = lambda s, n: set(list(s)[:int(n)])
    m["drop"]       = lambda s, n: set(list(s)[int(n):])
    m["slice"]      = lambda s, st, en: set(list(s)[int(st):int(en)])
    m["sum"]        = lambda s: sum(s)
    m["max"]        = lambda s: max(s) if s else None
    m["min"]        = lambda s: min(s) if s else None
    m["avg"]        = lambda s: sum(s) / len(s) if s else 0
    m["same"]       = lambda a, b: a == b
    m["count"]      = lambda s: len(s)
    m["unionAll"]   = lambda *sets: set().union(*sets)
    m["interAll"]   = lambda *sets: sets[0].intersection(*sets[1:]) if sets else set()
    m["diffAll"]    = lambda *sets: sets[0].difference(*sets[1:]) if sets else set()
    m["power"]      = lambda s: [set(comb) for r in range(len(s)+1) for comb in [list(s)[:r]]]
    m["cart"]       = lambda s1, s2: [(a, b) for a in s1 for b in s2]
    m["first"]      = lambda s: next(iter(s), None)
    m["last"]       = lambda s: list(s)[-1] if s else None
    m["toStr"]      = lambda s: str(s)
    m["join"]       = lambda s, sep=",": sep.join(str(x) for x in sorted(s, key=str))
    m["unique"]     = lambda s: set(s)
    m["range"]      = lambda st, en: set(range(int(st), int(en) + 1))
    m["range2"]     = lambda st, en, stp=1: set(range(int(st), int(en) + 1, int(stp)))
    m["fromList"]   = lambda l: set(l)
    m["empty"]      = lambda: set()
    m["keep"]       = lambda s, fn: {x for x in s if fn(x)}
    m["change"]     = lambda s, fn: {fn(x) for x in s}
    return StdModule("set", m)


def build_file_os_module():
    m = {}
    _dir_stack = []

    def _cd(path):
        nonlocal _dir_stack
        _dir_stack.append(os.getcwd())
        os.chdir(os.path.expanduser(path))
        return os.getcwd()

    def _go_back():
        if _dir_stack: os.chdir(_dir_stack.pop())
        return os.getcwd()

    m["cd"]       = _cd
    m["goBack"]   = _go_back
    m["pwd"]      = os.getcwd
    m["pathJoin"] = os.path.join
    m["pathBase"] = os.path.basename
    m["pathDir"]  = os.path.dirname
    m["open"]     = lambda path, mode="read": NovaFile(path, mode)
    m["readA"]    = lambda p: open(p, "r", encoding="utf-8").read()
    m["readL"]    = lambda p: open(p, "r", encoding="utf-8").readlines()
    m["writeA"]   = lambda p, d: open(p, "w", encoding="utf-8").write(str(d))
    m["add"]      = lambda p, d: open(p, "a", encoding="utf-8").write(str(d))
    m["copy"]     = shutil.copy2
    m["move"]     = shutil.move
    m["exists"]   = os.path.exists
    m["isFile"]   = os.path.isfile
    m["isDir"]    = os.path.isdir
    m["size"]     = os.path.getsize
    m["time"]     = os.path.getmtime
    m["create"]   = lambda p: open(p, "w", encoding="utf-8").close()
    m["remove"]   = os.remove
    m["rename"]   = os.rename
    m["list"]     = lambda p=".": os.listdir(p)
    m["listAll"]  = lambda p=".": [os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs]
    m["listDirs"] = lambda p=".": [d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d))]
    m["makeDir"]    = os.mkdir
    m["makeDirs"]   = lambda p: os.makedirs(p, exist_ok=True)
    m["removeDir"]  = os.rmdir
    m["removeDirs"] = shutil.rmtree
    m["isEmptyDir"] = lambda p: len(os.listdir(p)) == 0 if os.path.isdir(p) else False
    m["copyDir"]    = lambda s, d: shutil.copytree(s, d, dirs_exist_ok=True)
    m["moveDir"]    = shutil.move
    m["dirSize"]    = lambda p: sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)
    m["walk"]       = lambda p=".": list(os.walk(p))
    m["walkFiles"]  = lambda p=".": [f for _, _, fs in os.walk(p) for f in fs]
    m["hasText"]  = lambda p, s: str(s) in open(p, "r", encoding="utf-8", errors="ignore").read()
    m["lineC"]    = lambda p: len(open(p, "r", encoding="utf-8", errors="ignore").readlines())
    m["wordC"]    = lambda p: len(open(p, "r", encoding="utf-8", errors="ignore").read().split())
    m["isEmpty"]  = lambda p: os.path.getsize(p) == 0 if os.path.exists(p) else True
    m["clear"]    = lambda p: open(p, "w", encoding="utf-8").close()
    m["tempFile"] = tempfile.mktemp
    m["tempDir"]  = tempfile.mkdtemp
    m["homeDir"]  = os.path.expanduser
    m["absPath"]  = os.path.abspath
    m["relPath"]  = os.path.relpath
    m["sameFile"] = os.path.samefile
    m["canRead"]  = lambda p: os.access(p, os.R_OK)
    m["canWrite"] = lambda p: os.access(p, os.W_OK)
    m["hide"]     = lambda p: None
    m["unhide"]   = lambda p: None
    return StdModule("file", m)


def build_random_module():
    m = {}
    import string as _s
    m["int"]      = lambda a=0, b=100: random.randint(int(a), int(b))
    m["float"]    = random.random
    m["floatR"]   = lambda a=0.0, b=1.0: random.uniform(float(a), float(b))
    m["bool"]     = lambda: random.choice([True, False])
    m["pick"]     = lambda it: random.choice(list(it)) if it else None
    m["pickN"]    = lambda it, n=1: random.sample(list(it), min(int(n), len(list(it))))
    m["pickR"]    = lambda it, n=1: random.choices(list(it), k=int(n))
    m["shuffle"]  = lambda l: random.shuffle(l) or l
    m["shuffled"] = lambda l: random.sample(list(l), len(list(l)))
    m["sample"]   = lambda it, n=1: random.sample(list(it), min(int(n), len(list(it))))
    m["letter"]   = lambda: random.choice(_s.ascii_letters)
    m["upperL"]   = lambda: random.choice(_s.ascii_uppercase)
    m["digit"]    = lambda: random.choice(_s.digits)
    m["char"]     = lambda: random.choice(_s.ascii_letters + _s.digits)
    m["str"]      = lambda n=8: "".join(random.choices(_s.ascii_letters + _s.digits, k=int(n)))
    m["strUpper"] = lambda n=8: "".join(random.choices(_s.ascii_uppercase, k=int(n)))
    m["strNum"]   = lambda n=8: "".join(random.choices(_s.digits, k=int(n)))
    m["word"]     = lambda: random.choice(["nova", "alpha", "delta", "lumen", "apex", "swift", "hyper"])
    m["seed"]     = random.seed
    m["seedTime"] = lambda: random.seed(int(time.time()))
    m["range"]    = lambda s, e: random.randrange(int(s), int(e) + 1)
    m["range2"]   = lambda s, e, stp=1: random.randrange(int(s), int(e) + 1, int(stp))
    m["bin"]      = lambda: random.choice([0, 1])
    m["binA"]     = lambda n=5: [random.choice([0, 1]) for _ in range(int(n))]
    m["boolA"]    = lambda n=5: [random.choice([True, False]) for _ in range(int(n))]
    m["intA"]     = lambda n=5, a=0, b=100: [random.randint(int(a), int(b)) for _ in range(int(n))]
    m["floatA"]   = lambda n=5: [random.random() for _ in range(int(n))]
    m["color"]    = lambda: f"#{random.randint(0, 0xFFFFFF):06x}"
    m["colorRGB"] = lambda: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    m["uuid"]     = lambda: str(uuid.uuid4())
    m["normal"]   = lambda mu=0.0, sigma=1.0: random.normalvariate(mu, sigma)
    m["normalR"]  = lambda a=0, b=10: max(a, min(b, random.normalvariate((a+b)/2, (b-a)/6)))
    m["gauss"]    = lambda mu=0.0, sigma=1.0: random.gauss(mu, sigma)
    m["uniform"]  = random.uniform
    m["exp"]      = lambda l=1.0: random.expovariate(l)
    m["choice"]   = lambda it: random.choice(list(it))
    m["choices"]  = lambda it, k=1: random.choices(list(it), k=int(k))
    m["weight"]   = lambda items, weights, k=1: random.choices(list(items), weights=weights, k=int(k))
    m["shuffleS"] = lambda seq, s: (random.seed(s), random.sample(list(seq), len(list(seq))))[1]
    m["dice"]     = lambda: random.randint(1, 6)
    m["dice2"]    = lambda: (random.randint(1, 6), random.randint(1, 6))
    m["coin"]     = lambda: random.choice(["heads", "tails"])
    m["card"]     = lambda: f"{random.choice(['A','2','3','4','5','6','7','8','9','10','J','Q','K'])}{random.choice(['S','H','D','C'])}"
    m["cardN"]    = lambda n=5: [m["card"]() for _ in range(int(n))]
    m["suit"]     = lambda: random.choice(['S','H','D','C'])
    m["lottery"]  = lambda a=1, b=50, c=6: sorted(random.sample(range(int(a), int(b)+1), int(c)))
    m["otp"]      = lambda n=6: "".join(random.choices(_s.digits, k=int(n)))
    m["pass"]     = lambda n=8: "".join(random.choices(_s.ascii_letters + _s.digits + "!@#$%^&*", k=int(n)))
    m["time"]     = lambda: f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
    m["date"]     = lambda: f"{random.randint(2000,2026):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    m["day"]      = lambda: random.choice(["MON","TUE","WED","THU","FRI","SAT","SUN"])
    m["month"]    = lambda: random.choice(["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"])
    m["year"]     = lambda a=2000, b=2026: random.randint(int(a), int(b))
    m["name"]     = lambda: random.choice(["Ravi", "Aria", "Leo", "Maya", "Zane", "Nova", "Ethan"])
    m["firstN"]   = lambda: random.choice(["Ravi", "Aria", "Leo", "Maya", "Zane"])
    m["lastN"]    = lambda: random.choice(["Kumar", "Singh", "Patel", "Sharma", "Dev"])
    m["clamp"]    = lambda x, lo, hi: max(lo, min(x, hi))
    m["email"]    = lambda: f"user{random.randint(100,999)}@nova.lang"
    m["phone"]    = lambda: f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
    return StdModule("random", m)


def build_time_module():
    m = {}
    m["now"]      = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m["date"]     = lambda: datetime.date.today().strftime("%Y-%m-%d")
    m["time"]     = lambda: datetime.datetime.now().strftime("%H:%M:%S")
    m["dateTime"] = lambda: datetime.datetime.now().isoformat()
    m["year"]     = lambda: datetime.datetime.now().year
    m["month"]    = lambda: datetime.datetime.now().month
    m["day"]      = lambda: datetime.datetime.now().day
    m["hour"]     = lambda: datetime.datetime.now().hour
    m["min"]      = lambda: datetime.datetime.now().minute
    m["sec"]      = lambda: datetime.datetime.now().second
    m["milli"]    = lambda: int(time.time() * 1000)
    m["make"]      = lambda y, m, d: f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    m["makeT"]     = lambda h, m, s: f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    m["makeDT"]    = lambda y, m, d, h=0, mn=0, s=0: f"{int(y):04d}-{int(m):02d}-{int(d):02d} {int(h):02d}:{int(mn):02d}:{int(s):02d}"
    m["fromStr"]   = lambda s: datetime.datetime.fromisoformat(str(s).replace(" ", "T"))
    m["fromStamp"] = lambda ts: datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    m["stamp"]     = lambda: int(time.time())
    m["stampM"]    = lambda: int(time.time() * 1000)
    m["today"]     = lambda: datetime.date.today().strftime("%Y-%m-%d")
    m["tomorrow"]  = lambda: (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    m["yesterday"] = lambda: (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    def _parse_dt(t):
        if isinstance(t, (datetime.datetime, datetime.date)): return t
        try: return datetime.datetime.fromisoformat(str(t).replace(" ", "T"))
        except Exception: return datetime.datetime.now()

    m["addDay"]   = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(days=int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["addMonth"] = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(days=30*int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["addYear"]  = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(days=365*int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["addHour"]  = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(hours=int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["addMin"]   = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(minutes=int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["addSec"]   = lambda t, n=1: (_parse_dt(t) + datetime.timedelta(seconds=int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["subDay"]   = lambda t, n=1: (_parse_dt(t) - datetime.timedelta(days=int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["subMonth"] = lambda t, n=1: (_parse_dt(t) - datetime.timedelta(days=30*int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["subYear"]  = lambda t, n=1: (_parse_dt(t) - datetime.timedelta(days=365*int(n))).strftime("%Y-%m-%d %H:%M:%S")
    m["diffDay"]  = lambda a, b: abs((_parse_dt(a) - _parse_dt(b)).days)
    m["diffHour"] = lambda a, b: abs((_parse_dt(a) - _parse_dt(b)).total_seconds()) / 3600.0
    m["diffMin"]  = lambda a, b: abs((_parse_dt(a) - _parse_dt(b)).total_seconds()) / 60.0
    m["diffSec"]  = lambda a, b: abs((_parse_dt(a) - _parse_dt(b)).total_seconds())
    m["isBefore"] = lambda a, b: _parse_dt(a) < _parse_dt(b)
    m["isAfter"]  = lambda a, b: _parse_dt(a) > _parse_dt(b)
    m["isSame"]   = lambda a, b: _parse_dt(a) == _parse_dt(b)
    m["isLeap"]   = lambda y: (int(y) % 4 == 0 and int(y) % 100 != 0) or (int(y) % 400 == 0)
    m["daysInMonth"] = lambda y, mn: 29 if int(mn)==2 and m["isLeap"](y) else [0,31,28,31,30,31,30,31,31,30,31,30,31][int(mn)]
    m["format"]   = lambda t, fmt="YYYY-MM-DD": _parse_dt(t).strftime(fmt.replace("YYYY","%Y").replace("MM","%m").replace("DD","%d").replace("HH","%H").replace("mm","%M").replace("ss","%S"))
    m["formatT"]  = lambda t, fmt="HH:mm:ss": m["format"](t, fmt)
    m["formatD"]  = lambda t, fmt="DD/MM/YYYY": m["format"](t, fmt)
    m["format12"] = lambda t: _parse_dt(t).strftime("%I:%M:%S %p")
    m["format24"] = lambda t: _parse_dt(t).strftime("%H:%M:%S")
    m["weekDay"]  = lambda t: _parse_dt(t).strftime("%A")
    m["weekNum"]  = lambda t: _parse_dt(t).isocalendar()[1]
    m["monthName"]= lambda t: _parse_dt(t).strftime("%B")
    m["sleep"]    = lambda s=1: time.sleep(float(s))
    m["sleepM"]   = lambda ms=100: time.sleep(float(ms) / 1000.0)
    m["sleepU"]   = lambda us=1000: time.sleep(float(us) / 1000000.0)
    m["wait"]     = lambda s=1: time.sleep(float(s))
    m["waitUntil"]= lambda ts: None
    m["timer"]    = lambda: time.perf_counter()
    m["timerEnd"] = lambda t: time.perf_counter() - t
    m["elapsed"]  = lambda t: time.perf_counter() - t
    m["zone"]     = lambda: time.tzname[0]
    m["zoneName"] = lambda: time.tzname[0]
    m["utc"]      = lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    m["utcNow"]   = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    m["toUTC"]    = lambda t: _parse_dt(t).astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    m["toLocal"]  = lambda t: _parse_dt(t).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    m["age"]      = lambda ds: (datetime.date.today() - _parse_dt(ds).date()).days // 365
    m["isWeekend"]= lambda t: _parse_dt(t).weekday() in (5, 6)
    return StdModule("time", m)


def build_json_module():
    m = {}
    m["text"]     = lambda d: json.dumps(d)
    m["map"]      = lambda s: json.loads(s)
    m["read"]     = lambda p: json.load(open(p, "r", encoding="utf-8"))
    m["write"]    = lambda p, d: json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
    m["pretty"]   = lambda d: json.dumps(d, indent=2)
    m["prettyW"]  = lambda p, d: json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
    m["minify"]   = lambda s: json.dumps(json.loads(s), separators=(",", ":"))
    m["isValid"]  = lambda s: (lambda: (json.loads(s), True)[1])() if _is_valid_json(s) else False
    m["isEmpty"]  = lambda d: len(d) == 0
    m["size"]     = lambda d: len(d)

    def _is_valid_json(s):
        try: json.loads(s); return True
        except Exception: return False

    m["has"]      = lambda d, k: k in d if isinstance(d, dict) else False
    m["keys"]     = lambda d: list(d.keys()) if isinstance(d, dict) else []
    m["values"]   = lambda d: list(d.values()) if isinstance(d, dict) else []
    m["hasValue"] = lambda d, v: v in d.values() if isinstance(d, dict) else False
    m["get"]      = lambda d, k: d.get(k) if isinstance(d, dict) else None
    m["getOr"]    = lambda d, k, default=None: d.get(k, default) if isinstance(d, dict) else default

    def _get_path(d, path):
        parts = str(path).split(".")
        cur = d
        for p in parts:
            if isinstance(cur, dict): cur = cur.get(p)
            elif isinstance(cur, list) and p.isdigit(): cur = cur[int(p)]
            else: return None
        return cur

    def _set_path(d, path, val):
        parts = str(path).split(".")
        cur = d
        for p in parts[:-1]:
            if p not in cur or not isinstance(cur[p], dict): cur[p] = {}
            cur = cur[p]
        cur[parts[-1]] = val
        return d

    m["getPath"]  = _get_path
    m["set"]      = lambda d, k, v: d.__setitem__(k, v) or d
    m["setPath"]  = _set_path
    m["remove"]   = lambda d, k: d.pop(k, None) or d
    m["add"]      = lambda d, k, v: d.__setitem__(k, v) or d
    m["addIfNot"] = lambda d, k, v: d.__setitem__(k, v) or d if k not in d else d
    m["merge"]    = lambda d1, d2: {**d1, **d2}
    m["mergeAll"] = lambda l: {k: v for d in l for k, v in d.items()}
    m["copy"]     = lambda d: dict(d)
    m["copyD"]    = lambda d: json.loads(json.dumps(d))
    m["clear"]    = lambda d: d.clear() or d
    m["equals"]   = lambda d1, d2: d1 == d2
    m["same"]     = lambda d1, d2: d1 == d2
    m["clone"]    = lambda d: json.loads(json.dumps(d))
    m["listText"] = lambda l: json.dumps(l)
    m["listMap"]  = lambda s: json.loads(s)
    m["listRead"] = lambda p: json.load(open(p, "r", encoding="utf-8"))
    m["listWrite"]= lambda p, l: json.dump(l, open(p, "w", encoding="utf-8"), indent=2)
    m["listHas"]  = lambda l, item: item in l
    m["listGet"]  = lambda l, idx: l[int(idx)] if 0 <= int(idx) < len(l) else None
    m["listFilter"] = lambda l, fn: [x for x in l if fn(x)]
    m["listMapE"]   = lambda l, fn: [fn(x) for x in l]
    m["listKeys"]   = lambda l: [list(d.keys()) for d in l if isinstance(d, dict)]
    m["listVals"]   = lambda l: [list(d.values()) for d in l if isinstance(d, dict)]
    m["toList"]   = lambda d: list(d.items()) if isinstance(d, dict) else list(d)
    m["fromList"] = lambda l: dict(l)
    def _flat(d, prefix=""):
        res = {}
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict): res.update(_flat(v, key))
            else: res[key] = v
        return res
    m["flat"]     = _flat
    def _unflat(d):
        res = {}
        for k, v in d.items(): _set_path(res, k, v)
        return res
    m["unflat"]   = _unflat
    m["paths"]    = lambda d: list(_flat(d).keys()) if isinstance(d, dict) else []
    m["type"]     = lambda d, k: type(d.get(k)).__name__ if isinstance(d, dict) else None
    m["isMap"]    = lambda d: isinstance(d, dict)
    m["isList"]   = lambda d: isinstance(d, list)
    m["isStr"]    = lambda d: isinstance(d, str)
    m["toStr"]    = lambda d: json.dumps(d)
    m["addF"]       = lambda p, item: json.dump(json.load(open(p, "r", encoding="utf-8")) + [item], open(p, "w", encoding="utf-8"), indent=2)
    m["readLines"]  = lambda p: [json.loads(line) for line in open(p, "r", encoding="utf-8") if line.strip()]
    m["writeLines"] = lambda p, lines: open(p, "w", encoding="utf-8").write("\n".join(json.dumps(x) for x in lines) + "\n")
    m["lineC"]      = lambda p: len(open(p, "r", encoding="utf-8").readlines())
    m["hasFile"]    = os.path.exists
    m["fileSize"]   = lambda p: os.path.getsize(p) if os.path.exists(p) else 0
    m["backup"]     = lambda p: shutil.copy(p, p + ".bak")
    m["restore"]    = lambda p: shutil.copy(p + ".bak", p)
    m["diff"]       = lambda d1, d2: {k: (d1.get(k), d2.get(k)) for k in set(d1) | set(d2) if d1.get(k) != d2.get(k)}
    m["patch"]      = lambda d, diff: {**d, **{k: v[1] for k, v in diff.items() if v[1] is not None}}
    return StdModule("json", m)


# ============================================================
# V1.6 FULL-STACK WEB PLATFORM LIBRARIES
# ============================================================

# ── 1. HTTP LIBRARY ──────────────────────────────────────────

class NovaHttpResponse:
    def __init__(self, status: int, text: str, headers: dict, time_ms: float, url: str, raw_bytes: bytes):
        self.status = status
        self.text = text
        self.headers = headers
        self.time = time_ms
        self.url = url
        self._bytes = raw_bytes

    @property
    def ok(self): return 200 <= self.status < 300
    def isOk(self): return 200 <= self.status < 300
    def is404(self): return self.status == 404
    def is500(self): return self.status == 500
    def bytes(self): return self._bytes
    def json(self):
        try: return json.loads(self.text)
        except Exception: return None
    def header(self, name: str):
        lname = name.lower()
        for k, v in self.headers.items():
            if k.lower() == lname: return v
        return ""
    def __repr__(self): return f"<HttpResponse {self.status} {self.url}>"


class NovaAsyncTask:
    def __init__(self, future):
        self.future = future
    def wait(self): return self.future.result()
    def isDone(self): return self.future.done()
    def __repr__(self): return "<AsyncTask>"


_http_pool = ThreadPoolExecutor(max_workers=16)

def _http_request(method: str, url: str, params=None, data=None, headers=None, options=None):
    params = params or {}
    headers = headers or {}
    options = options or {}
    timeout = options.get("timeout", 10000) / 1000.0 if isinstance(options.get("timeout"), (int, float)) else 10.0
    retries = options.get("retry", 1)

    if params and isinstance(params, dict):
        qs = urllib.parse.urlencode(params)
        url = url + ("&" if "?" in url else "?") + qs

    body_bytes = None
    hdrs = dict(headers)
    if data is not None:
        if isinstance(data, (dict, list)):
            body_bytes = json.dumps(data).encode("utf-8")
            if "Content-Type" not in hdrs and "content-type" not in hdrs and "content" not in hdrs:
                hdrs["Content-Type"] = "application/json"
        elif isinstance(data, str):
            body_bytes = data.encode("utf-8")
        elif isinstance(data, bytes):
            body_bytes = data

    if "auth" in hdrs:
        hdrs["Authorization"] = hdrs.pop("auth")
    if "content" in hdrs:
        hdrs["Content-Type"] = "application/json" if hdrs.pop("content") == "json" else "text/plain"

    last_err = None
    for attempt in range(retries):
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, data=body_bytes, headers=hdrs, method=method.upper())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                raw = resp.read()
                resp_hdrs = dict(resp.getheaders())
                elapsed = (time.perf_counter() - t0) * 1000.0
                text = raw.decode("utf-8", errors="replace")
                return NovaHttpResponse(status, text, resp_hdrs, elapsed, resp.geturl(), raw)
        except urllib.error.HTTPError as e:
            raw = e.read() if hasattr(e, "read") else b""
            text = raw.decode("utf-8", errors="replace")
            resp_hdrs = dict(e.headers.items()) if hasattr(e, "headers") else {}
            elapsed = (time.perf_counter() - t0) * 1000.0
            return NovaHttpResponse(e.code, text, resp_hdrs, elapsed, url, raw)
        except Exception as e:
            last_err = e
            time.sleep(0.05 * (attempt + 1))
    return NovaHttpResponse(0, f"Error: {last_err}", {}, 0, url, b"")


def build_http_module():
    m = {}
    m["get"]    = lambda u, p=None, h=None, o=None: _http_request("GET", u, p, None, h, o)
    m["post"]   = lambda u, d=None, h=None, o=None: _http_request("POST", u, None, d, h, o)
    m["postJ"]  = lambda u, d=None, h=None, o=None: _http_request("POST", u, None, d, {**(h or {}), "Content-Type": "application/json"}, o)
    m["put"]    = lambda u, d=None, h=None, o=None: _http_request("PUT", u, None, d, h, o)
    m["delete"] = lambda u, h=None, o=None: _http_request("DELETE", u, None, None, h, o)
    m["patch"]  = lambda u, d=None, h=None, o=None: _http_request("PATCH", u, None, d, h, o)

    # Aliases
    m["g"]  = m["get"]
    m["p"]  = m["post"]
    m["pu"] = m["put"]
    m["d"]  = m["delete"]

    def _download(url, local_path):
        res = _http_request("GET", url)
        with open(local_path, "wb") as f: f.write(res.bytes())
        return res.ok

    def _upload(url, local_path):
        with open(local_path, "rb") as f: data = f.read()
        return _http_request("POST", url, None, data, {"Content-Type": "application/octet-stream"})

    def _upload_data(url, data_map):
        return _http_request("POST", url, None, data_map)

    m["download"]   = _download
    m["upload"]     = _upload
    m["uploadData"] = _upload_data

    # Async
    m["getAsync"] = lambda u, p=None, h=None, o=None: NovaAsyncTask(_http_pool.submit(_http_request, "GET", u, p, None, h, o))
    m["postAsync"]= lambda u, d=None, h=None, o=None: NovaAsyncTask(_http_pool.submit(_http_request, "POST", u, None, d, h, o))
    m["getAll"]   = lambda urls: [m["get"](u) for u in urls]

    return StdModule("http", m)


# ── 2. SERVER LIBRARY ────────────────────────────────────────

class NovaRequest:
    def __init__(self, method: str, path: str, url: str, query: dict, params: dict, headers: dict, body: Any, raw_text: str, client_ip: str):
        self.method = method
        self.path = path
        self.url = url
        self.query = query
        self.params = params
        self.headers = headers
        self.body = body
        self.text = raw_text
        self.ip = client_ip
        self.form = body if isinstance(body, dict) else {}
        self.cookies = self._parse_cookies(headers.get("cookie", ""))

    def header(self, name: str):
        lname = name.lower()
        for k, v in self.headers.items():
            if k.lower() == lname: return v
        return ""

    def _parse_cookies(self, cookie_str: str):
        res = {}
        if not cookie_str: return res
        for part in cookie_str.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                res[k.strip()] = v.strip()
        return res

    def __repr__(self): return f"<Request {self.method} {self.path}>"


class NovaResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = {"Content-Type": "text/html; charset=utf-8"}
        self.body = b""
        self.finished = False

    def status(self, code: int):
        self.status_code = int(code)
        return self

    def header(self, k: str, v: str):
        self.headers[k] = str(v)
        return self

    def cookie(self, k: str, v: str):
        self.headers["Set-Cookie"] = f"{k}={v}; Path=/"
        return self

    def type(self, mime: str):
        t_map = {"json": "application/json", "html": "text/html", "text": "text/plain", "xml": "application/xml"}
        self.headers["Content-Type"] = t_map.get(mime, mime)
        return self

    def send(self, data: Any):
        if not self.headers.get("Content-Type"):
            self.headers["Content-Type"] = "text/plain; charset=utf-8"
        self.body = str(data).encode("utf-8")
        self.finished = True
        return self

    def json(self, data: Any):
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(data).encode("utf-8")
        self.finished = True
        return self

    def html(self, data: Any):
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        self.body = str(data).encode("utf-8")
        self.finished = True
        return self

    def redirect(self, url: str):
        self.status_code = 302
        self.headers["Location"] = url
        self.body = b""
        self.finished = True
        return self

    def file(self, path: str):
        if os.path.exists(path):
            with open(path, "rb") as f: self.body = f.read()
            if path.endswith(".json"): self.headers["Content-Type"] = "application/json"
            elif path.endswith(".html"): self.headers["Content-Type"] = "text/html"
            elif path.endswith(".js"): self.headers["Content-Type"] = "application/javascript"
            elif path.endswith(".css"): self.headers["Content-Type"] = "text/css"
            elif path.endswith(".png"): self.headers["Content-Type"] = "image/png"
            elif path.endswith(".jpg"): self.headers["Content-Type"] = "image/jpeg"
            else: self.headers["Content-Type"] = "application/octet-stream"
        else:
            self.status_code = 404
            self.body = b"File Not Found"
        self.finished = True
        return self

    def download(self, path: str):
        self.file(path)
        fname = os.path.basename(path)
        self.headers["Content-Disposition"] = f'attachment; filename="{fname}"'
        return self

    def __repr__(self): return f"<Response {self.status_code}>"


class NovaServerApp:
    def __init__(self, interp):
        self.interp = interp
        self.routes = []
        self.middlewares = []
        self.auto_json = False
        self.cors_opts = None
        self.static_dirs = []
        self.httpd = None
        self.server_thread = None

    def _add_route(self, method: str, pattern: str, handler):
        param_names = re.findall(r':([a-zA-Z_0-9]+)', pattern)
        regex_pat = "^" + re.sub(r':([a-zA-Z_0-9]+)', r'(?P<\1>[^/]+)', pattern) + "$"
        self.routes.append((method.upper(), pattern, re.compile(regex_pat), param_names, handler))

    def get(self, path: str, handler): self._add_route("GET", path, handler); return self
    def post(self, path: str, handler): self._add_route("POST", path, handler); return self
    def put(self, path: str, handler): self._add_route("PUT", path, handler); return self
    def delete(self, path: str, handler): self._add_route("DELETE", path, handler); return self
    def patch(self, path: str, handler): self._add_route("PATCH", path, handler); return self
    def all(self, path: str, handler): self._add_route("ALL", path, handler); return self

    def group(self, prefix: str):
        class RouteGroup:
            def __init__(rg, app, pfx): rg.app = app; rg.pfx = pfx.rstrip("/")
            def get(rg, p, h): rg.app.get(rg.pfx + p, h); return rg
            def post(rg, p, h): rg.app.post(rg.pfx + p, h); return rg
            def put(rg, p, h): rg.app.put(rg.pfx + p, h); return rg
            def delete(rg, p, h): rg.app.delete(rg.pfx + p, h); return rg
            def patch(rg, p, h): rg.app.patch(rg.pfx + p, h); return rg
        return RouteGroup(self, prefix)

    def use(self, *args):
        if len(args) == 1: self.middlewares.append(("", args[0]))
        elif len(args) >= 2: self.middlewares.append((args[0], args[1]))
        return self

    def json(self): self.auto_json = True; return self
    def cors(self, opts=None): self.cors_opts = opts or {"origin": "*"}; return self
    def static(self, folder: str, prefix: str = "/"):
        self.static_dirs.append((prefix, folder))
        return self

    def _call_handler(self, handler, req, res, next_fn=None):
        if isinstance(handler, (NovaFunction, NovaLambda)):
            args = [req, res] + ([next_fn] if next_fn else [])
            return self.interp._call_method(handler, None, args, 0, None)
        elif callable(handler):
            if next_fn: return handler(req, res, next_fn)
            return handler(req, res)

    def handle_request(self, method: str, full_url: str, headers: dict, body_bytes: bytes, client_ip: str):
        parsed = urllib.parse.urlparse(full_url)
        path = parsed.path
        query = {k: v[0] if len(v)==1 else v for k, v in urllib.parse.parse_qs(parsed.query).items()}
        raw_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""
        body = None
        if raw_text:
            try: body = json.loads(raw_text)
            except Exception:
                if "=" in raw_text:
                    body = {k: v[0] if len(v)==1 else v for k, v in urllib.parse.parse_qs(raw_text).items()}
                else: body = raw_text

        req = NovaRequest(method, path, full_url, query, {}, headers, body, raw_text, client_ip)
        res = NovaResponse()

        if self.cors_opts:
            res.header("Access-Control-Allow-Origin", self.cors_opts.get("origin", "*"))
            res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
            res.header("Access-Control-Allow-Headers", "Content-Type, Authorization, *")
            if method == "OPTIONS":
                res.status(204).send("")
                return res

        for pfx, m_fn in self.middlewares:
            if not pfx or path.startswith(pfx):
                passed = False
                def next_step(): nonlocal passed; passed = True
                self._call_handler(m_fn, req, res, next_step)
                if res.finished: return res
                if not passed: break

        for pfx, folder in self.static_dirs:
            if path.startswith(pfx):
                rel = path[len(pfx):].lstrip("/")
                fpath = os.path.join(folder, rel if rel else "index.html")
                if os.path.exists(fpath) and os.path.isfile(fpath):
                    res.file(fpath)
                    return res

        for r_method, r_pat, r_regex, pnames, handler in self.routes:
            if r_method == "ALL" or r_method == method:
                m = r_regex.match(path)
                if m:
                    req.params = m.groupdict()
                    self._call_handler(handler, req, res)
                    return res

        res.status(404).send(f"Cannot {method} {path}")
        return res

    def listen(self, port: int = 3000, background: bool = True):
        app = self
        class CustomHTTPHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self): self._dispatch("GET")
            def do_POST(self): self._dispatch("POST")
            def do_PUT(self): self._dispatch("PUT")
            def do_DELETE(self): self._dispatch("DELETE")
            def do_PATCH(self): self._dispatch("PATCH")
            def do_OPTIONS(self): self._dispatch("OPTIONS")

            def _dispatch(self, method):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length > 0 else b""
                hdrs = {k: v for k, v in self.headers.items()}
                res = app.handle_request(method, self.path, hdrs, body, self.client_address[0])
                self.send_response(res.status_code)
                for hk, hv in res.headers.items(): self.send_header(hk, hv)
                self.end_headers()
                self.wfile.write(res.body)

            def log_message(self, format, *args): pass

        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", int(port)), CustomHTTPHandler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.server_thread.start()
        return self

    def l(self, port: int): return self.listen(port)
    def close(self):
        if self.httpd: self.httpd.shutdown()


def build_server_module(interp):
    m = {}
    m["new"] = lambda: NovaServerApp(interp)
    return StdModule("server", m)


# ── 3. BACKEND: DB, AUTH, ENV ────────────────────────────────

class NovaDB:
    def __init__(self):
        self.conn = None
        self.curr_db = None

    def connect(self, uri: str = "app.db"):
        self.curr_db = uri
        self.conn = sqlite3.connect(uri, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self

    def _ensure_conn(self):
        if not self.conn: self.connect("app.db")

    def create(self, table: str, schema: Any):
        self._ensure_conn()
        if isinstance(schema, (list, tuple)):
            schema = {str(c): "TEXT" for c in schema}
        cols = []
        for k, v in schema.items():
            t = str(v).lower()
            if "primary" in t: cols.append(f"{k} INTEGER PRIMARY KEY AUTOINCREMENT" if "int" in t else f"{k} TEXT PRIMARY KEY")
            elif "int" in t: cols.append(f"{k} INTEGER")
            elif "float" in t or "num" in t: cols.append(f"{k} REAL")
            else: cols.append(f"{k} TEXT")
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(cols)});"
        self.conn.execute(sql); self.conn.commit()
        return True

    def table(self, table: str, schema: dict): return self.create(table, schema)

    def insert(self, table: str, data: dict):
        self._ensure_conn()
        keys = list(data.keys()); vals = list(data.values())
        placeholders = ", ".join(["?"] * len(keys))
        sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders});"
        cur = self.conn.cursor()
        cur.execute(sql, vals); self.conn.commit()
        return cur.lastrowid

    def find(self, table: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table};")
        return [dict(row) for row in cur.fetchall()]

    def findOne(self, table: str, where: dict):
        self._ensure_conn()
        keys = list(where.keys()); vals = list(where.values())
        where_clause = " AND ".join([f"{k} = ?" for k in keys])
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1;", vals)
        row = cur.fetchone()
        return dict(row) if row else None

    def findWhere(self, table: str, cond_str: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE {cond_str};")
        return [dict(row) for row in cur.fetchall()]

    def sort(self, table: str, field: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY {field} ASC;")
        return [dict(row) for row in cur.fetchall()]

    def dsort(self, table: str, field: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY {field} DESC;")
        return [dict(row) for row in cur.fetchall()]

    def update(self, table: str, where: dict, data: dict):
        self._ensure_conn()
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        vals = list(data.values()) + list(where.values())
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause};", vals)
        self.conn.commit()
        return cur.rowcount

    def updateWhere(self, table: str, cond_str: str, data: dict):
        self._ensure_conn()
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        vals = list(data.values())
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {table} SET {set_clause} WHERE {cond_str};", vals)
        self.conn.commit()
        return cur.rowcount

    def delete(self, table: str, where: dict):
        self._ensure_conn()
        keys = list(where.keys()); vals = list(where.values())
        where_clause = " AND ".join([f"{k} = ?" for k in keys])
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {where_clause};", vals)
        self.conn.commit()
        return cur.rowcount

    def deleteWhere(self, table: str, cond_str: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {cond_str};")
        self.conn.commit()
        return cur.rowcount

    def count(self, table: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        return cur.fetchone()[0]

    def has(self, table: str, where: dict):
        return self.findOne(table, where) is not None

    def clear(self, table: str):
        self._ensure_conn()
        self.conn.execute(f"DELETE FROM {table};")
        try: self.conn.execute("DELETE FROM sqlite_sequence WHERE name = ?;", (table,))
        except Exception: pass
        self.conn.commit()
        return True

    def drop(self, table: str):
        self._ensure_conn()
        self.conn.execute(f"DROP TABLE IF EXISTS {table};"); self.conn.commit()
        return True

    def query(self, sql: str, params=()):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(sql, params)
        if sql.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cur.fetchall()]
        self.conn.commit()
        return cur.rowcount


def build_auth_module():
    m = {}
    def _hash(password: str):
        salt = secrets.token_hex(8)
        h = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${h}"

    def _check(password: str, hash_str: str):
        if not hash_str or "$" not in hash_str: return False
        salt, h = hash_str.split("$", 1)
        expected = hashlib.sha256((salt + password).encode()).hexdigest()
        return hmac.compare_digest(h, expected)

    def _token(payload: dict, secret: str):
        hdr = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).decode().rstrip("=")
        body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        sig = hmac.new(secret.encode(), f"{hdr}.{body}".encode(), hashlib.sha256).hexdigest()
        return f"{hdr}.{body}.{sig}"

    def _verify(token: str, secret: str):
        try:
            parts = token.split(".")
            if len(parts) != 3: return None
            hdr, body, sig = parts
            expected = hmac.new(secret.encode(), f"{hdr}.{body}".encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected): return None
            padded = body + "=" * ((4 - len(body) % 4) % 4)
            return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        except Exception: return None

    m["hash"]   = _hash
    m["check"]  = _check
    m["token"]  = _token
    m["verify"] = _verify
    return StdModule("auth", m)


def build_env_module():
    m = {}
    m["get"] = lambda k, d="": os.environ.get(k, d)
    m["set"] = lambda k, v: os.environ.__setitem__(k, str(v))
    m["has"] = lambda k: k in os.environ
    m["all"] = lambda: dict(os.environ)
    return StdModule("env", m)


# ── 4. FRONTEND UI LIBRARY (V1.6.1 FIRST UI — 80 FUNCTIONS) ──

class NovaUIElement:
    def __init__(self, tag: str = "div", text: str = "", attrs=None):
        self.tag = tag
        self.text_content = str(text) if text is not None and text != "" else ""
        self.children = []
        self.styles = {}
        self.attrs = attrs or {}
        self.events = {}
        self._val = ""

    # Tree Structure & Container Methods
    def add(self, *args):
        if len(args) == 1:
            child = args[0]
            if isinstance(child, list): self.children.extend(child)
            elif child is not None: self.children.append(child)
        elif len(args) == 3:
            child, r, c = args
            if hasattr(child, "styles"):
                child.styles["grid-row"] = str(r)
                child.styles["grid-column"] = str(c)
            self.children.append(child)
        return self

    def addTo(self, parent):
        if parent is not None and hasattr(parent, "add"):
            parent.add(self)
        return self

    def clear(self):
        self.children.clear()
        return self

    # Identification & Properties
    def id(self, name: str):
        self.attrs["id"] = str(name)
        return self

    def type(self, t: str):
        self.attrs["type"] = str(t)
        return self

    def placeholder(self, ph: str):
        self.attrs["placeholder"] = str(ph)
        return self

    @property
    def value(self): return self._val
    @value.setter
    def value(self, v): self._val = str(v)

    # 30 Fluent Style Methods (All return self)
    def bg(self, color: str): self.styles["background-color"] = str(color); return self
    def color(self, c: str): self.styles["color"] = str(c); return self
    def colorR(self, c: str): self.styles["color"] = str(c); return self

    def w(self, px: Any):
        self.styles["width"] = f"{px}px" if isinstance(px, (int, float)) else str(px)
        return self

    def h(self, px: Any):
        self.styles["height"] = f"{px}px" if isinstance(px, (int, float)) else str(px)
        return self

    def size(self, *args):
        if len(args) == 1:
            return self.fontSize(args[0])
        elif len(args) >= 2:
            self.w(args[0]); self.h(args[1])
        return self

    def wFull(self): self.styles["width"] = "100%"; return self
    def hFull(self): self.styles["height"] = "100vh"; return self
    def wHalf(self): self.styles["width"] = "50%"; return self
    def sizeFull(self): self.styles["width"] = "100%"; self.styles["height"] = "100%"; return self

    def pad(self, *args):
        if len(args) == 1: self.styles["padding"] = f"{args[0]}px" if isinstance(args[0], (int, float)) else str(args[0])
        elif len(args) >= 2: self.styles["padding"] = f"{args[0]}px {args[1]}px"
        return self

    def padL(self, px: int): self.styles["padding-left"] = f"{px}px"; return self
    def padR(self, px: int): self.styles["padding-right"] = f"{px}px"; return self
    def padT(self, px: int): self.styles["padding-top"] = f"{px}px"; return self
    def padB(self, px: int): self.styles["padding-bottom"] = f"{px}px"; return self

    def margin(self, px: Any):
        self.styles["margin"] = f"{px}px" if isinstance(px, (int, float)) else str(px)
        return self

    def marginL(self, px: int): self.styles["margin-left"] = f"{px}px"; return self
    def marginR(self, px: int): self.styles["margin-right"] = f"{px}px"; return self
    def marginT(self, px: int): self.styles["margin-top"] = f"{px}px"; return self
    def marginB(self, px: int): self.styles["margin-bottom"] = f"{px}px"; return self
    def marginC(self): self.styles["margin"] = "0 auto"; return self

    def border(self, *args):
        if len(args) == 1: self.styles["border"] = f"{args[0]}px solid black"
        elif len(args) >= 2: self.styles["border"] = f"{args[0]}px solid {args[1]}"
        return self

    def borderC(self, color: str): self.styles["border-color"] = str(color); return self
    def borderW(self, width: int): self.styles["border-width"] = f"{width}px"; return self

    def round(self, px: int): self.styles["border-radius"] = f"{px}px"; return self
    def roundFull(self): self.styles["border-radius"] = "9999px"; return self
    def roundT(self, px: int):
        self.styles["border-top-left-radius"] = f"{px}px"
        self.styles["border-top-right-radius"] = f"{px}px"
        return self

    def show(self): self.styles["display"] = "block"; return self
    def hide(self): self.styles["display"] = "none"; return self
    def flex(self): self.styles["display"] = "flex"; return self

    def center(self):
        self.styles["text-align"] = "center"
        self.styles["margin"] = self.styles.get("margin", "0 auto")
        if self.styles.get("display") == "flex":
            self.styles["justify-content"] = "center"
            self.styles["align-items"] = "center"
        return self

    def left(self): self.styles["text-align"] = "left"; return self
    def right(self): self.styles["text-align"] = "right"; return self
    def top(self): self.styles["vertical-align"] = "top"; return self
    def bottom(self): self.styles["vertical-align"] = "bottom"; return self

    def pos(self, x: int, y: int):
        self.styles["position"] = "absolute"
        self.styles["left"] = f"{x}px"; self.styles["top"] = f"{y}px"
        return self

    def posA(self, x: int = 0, y: int = 0):
        self.styles["position"] = "absolute"
        if x != 0: self.styles["left"] = f"{x}px"
        if y != 0: self.styles["top"] = f"{y}px"
        return self

    def posR(self): self.styles["position"] = "relative"; return self

    def bold(self): self.styles["font-weight"] = "bold"; return self
    def fontSize(self, px: int): self.styles["font-size"] = f"{px}px"; return self
    def font(self, name: str): self.styles["font-family"] = str(name); return self
    def align(self, val: str): self.styles["text-align"] = str(val); return self

    # Events (9 functions)
    def onClick(self, fn): self.events["click"] = fn; return self
    def onChange(self, fn): self.events["change"] = fn; return self
    def onEnter(self, fn): self.events["enter"] = fn; return self
    def onFocus(self, fn): self.events["focus"] = fn; return self
    def onBlur(self, fn): self.events["blur"] = fn; return self
    def onSubmit(self, fn): self.events["submit"] = fn; return self
    def onHover(self, fn): self.events["hover"] = fn; return self
    def onLeave(self, fn): self.events["leave"] = fn; return self

    # HTML Generator
    def toHTML(self):
        style_str = " ".join([f"{k}:{v};" for k, v in self.styles.items()])
        attr_str = " ".join([f'{k}="{v}"' for k, v in self.attrs.items()])
        full_attrs = (f' style="{style_str}"' if style_str else "") + (f" {attr_str}" if attr_str else "")

        if self.tag in ("input", "img", "hr", "br"):
            return f"<{self.tag}{full_attrs} />"
        inner = self.text_content + "".join(c.toHTML() if hasattr(c, "toHTML") else str(c) for c in self.children)
        return f"<{self.tag}{full_attrs}>{inner}</{self.tag}>"

    def render(self): return self.toHTML()
    def __repr__(self): return f"<{self.tag} UIElement>"


class NovaAppWindow(NovaUIElement):
    def __init__(self, title: str = "Nova App", w: int = 800, h: int = 600):
        super().__init__("div")
        self.app_title = title
        self.app_w = w
        self.app_h = h
        self.w(w).h(h)
        self.styles["box-sizing"] = "border-box"
        self.styles["margin"] = "0 auto"
        self.styles["padding"] = "20px"
        self.resize_handler = None
        self.close_handler = None
        self.routes = {}

    def title(self, t: str): self.app_title = str(t); return self
    def full(self): self.wFull().hFull(); return self
    def onResize(self, fn): self.resize_handler = fn; return self
    def onClose(self, fn): self.close_handler = fn; return self
    def close(self): return None

    def theme(self, t: str = "dark"):
        if str(t).lower() == "light":
            self.styles["background-color"] = "#f8fafc"
            self.styles["color"] = "#0f172a"
        else:
            self.styles["background-color"] = "#0f172a"
            self.styles["color"] = "#f8fafc"
        return self

    def icon(self, url: str):
        self.attrs["data-icon"] = str(url)
        return self

    def route(self, path: str, view_fn):
        self.routes[str(path)] = view_fn
        return self

    def saveHtml(self, path: str = "app_preview.html"):
        html = self.toHTML()
        doc = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.app_title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: #0f172a;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: flex-start;
    }}
    button, input, select, textarea {{
      font-family: inherit;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
  </style>
</head>
<body>
  {html}
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[Nova UI] Saved to: {os.path.abspath(path)}")
        return self

    def show(self, open_browser: bool = True):
        html = self.toHTML()
        doc = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.app_title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: #0f172a;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: flex-start;
    }}
    button, input, select, textarea {{
      font-family: inherit;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
  </style>
</head>
<body>
  {html}
</body>
</html>"""
        fname = re.sub(r'[^a-zA-Z0-9_]', '_', self.app_title.lower()).strip('_') + ".html"
        if not fname or fname == ".html": fname = "app_preview.html"
        out_path = os.path.abspath(fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[Nova UI] Preview saved to: {out_path}")
        if open_browser:
            try: webbrowser.open("file://" + out_path)
            except Exception: pass
        return out_path

    def render(self): return self.show()
    def __repr__(self): return f"<AppWindow '{self.app_title}' ({self.app_w}x{self.app_h})>"


class NovaTableElement(NovaUIElement):
    def __init__(self):
        super().__init__("table")
        self.styles["width"] = "100%"
        self.styles["border-collapse"] = "collapse"
        self.thead = NovaUIElement("thead")
        self.tbody = NovaUIElement("tbody")
        self.children = [self.thead, self.tbody]

    def head(self, cols: list):
        tr = NovaUIElement("tr")
        tr.styles["background-color"] = "#334155"
        for c in cols:
            th = NovaUIElement("th", str(c))
            th.styles["padding"] = "10px"; th.styles["text-align"] = "left"
            th.styles["border-bottom"] = "2px solid #475569"
            tr.add(th)
        self.thead.children = [tr]
        return self

    def row(self, vals: list):
        tr = NovaUIElement("tr")
        tr.styles["border-bottom"] = "1px solid #334155"
        for v in vals:
            td = NovaUIElement("td", str(v))
            td.styles["padding"] = "10px"
            tr.add(td)
        self.tbody.add(tr)
        return self


def build_ui_module():
    m = {}

    def _elem(tag, text="", attrs=None, **styles):
        el = NovaUIElement(tag, text, attrs)
        for k, v in styles.items():
            el.styles[k.replace("_", "-")] = v
        return el

    # 1. App / Window (13 functions)
    def _app(title="Nova App", w=800, h=600): return NovaAppWindow(title, int(w), int(h))
    m["app"]     = _app
    m["new"]     = _app
    m["window"]  = _app
    m["page"]    = _app

    # 2. Basic Elements (16 functions + aliases)
    m["text"]     = lambda t="": _elem("span", t)
    m["label"]    = lambda t="": _elem("span", t)
    m["title"]    = lambda t="": _elem("h1", t, margin="0 0 10px 0")
    m["subTitle"] = lambda t="": _elem("h2", t, margin="0 0 8px 0")
    m["sub"]      = m["subTitle"]
    m["para"]     = lambda t="": _elem("p", t)
    m["bold"]     = lambda t="": _elem("b", t)
    m["italic"]   = lambda t="": _elem("i", t)
    m["link"]     = lambda text="", url="#": _elem("a", text, {"href": url}, color="#38bdf8")

    def _img(src="", w=None, h=None):
        el = _elem("img", "", {"src": src})
        if w is not None: el.w(w)
        if h is not None: el.h(h)
        return el
    m["img"]      = _img
    m["line"]     = lambda: _elem("hr", border="none", border_top="1px solid #334155")
    m["hr"]       = m["line"]
    m["space"]    = lambda h=20: _elem("div").h(h)
    m["br"]       = m["space"]
    m["box"]      = lambda: _elem("div")
    def _card():
        return _elem("div", background_color="#1e293b", box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.3)", border_radius="8px", padding="16px")
    m["card"]     = _card
    m["badge"]    = lambda t="": _elem("span", t, background_color="#3b82f6", color="#fff", padding="2px 8px", border_radius="12px", font_size="12px")
    m["icon"]     = lambda name="": NovaUIElement("span", f"[{name}]", {"data-icon": name})
    def _code(c=""):
        pre = _elem("pre", background_color="#0f172a", padding="12px", border_radius="6px")
        pre.add(_elem("code", c))
        return pre
    m["code"]     = _code
    m["alert"]    = lambda msg="": _elem("div", msg, background_color="#ef4444", color="#fff", padding="10px 16px", border_radius="6px")

    # Feedback & Rich Display
    m["spinner"]  = lambda s=24, c="#6366f1": _elem("div", "", border="3px solid rgba(255,255,255,0.2)", border_top=f"3px solid {c}", border_radius="50%", width=f"{s}px", height=f"{s}px", animation="spin 1s linear infinite", display="inline-block")
    def _progress(val=0, max_v=100):
        pct = max(0, min(100, int((val / max_v) * 100 if max_v else 0)))
        bar = _elem("div", "", background_color="#3b82f6", height="100%", width=f"{pct}%", border_radius="4px")
        cont = _elem("div", "", background_color="#334155", height="8px", width="100%", border_radius="4px", overflow="hidden")
        cont.add(bar)
        return cont
    m["progress"] = _progress
    m["avatar"]   = lambda src="", s=40: _elem("div", src if not str(src).startswith("http") and len(str(src)) <= 3 else "", {"data-src": str(src)}, width=f"{s}px", height=f"{s}px", border_radius="50%", background_color="#475569", display="inline-flex", justify_content="center", align_items="center", font_weight="bold", color="#ffffff")
    m["quote"]    = lambda t="": _elem("blockquote", t, border_left="4px solid #3b82f6", margin="10px 0", padding="8px 16px", background_color="#1e293b", color="#cbd5e1", font_style="italic")

    # 3. Input Elements (11 functions + aliases)
    m["input"]    = lambda ph="": _elem("input", "", {"placeholder": ph, "type": "text"}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["inputP"]   = lambda ph="Password": _elem("input", "", {"placeholder": ph, "type": "password"}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["pass"]     = m["inputP"]
    m["inputN"]   = lambda ph="0": _elem("input", "", {"placeholder": ph, "type": "number"}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["numInput"] = m["inputN"]
    m["inputE"]   = lambda ph="Email": _elem("input", "", {"placeholder": ph, "type": "email"}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["textArea"] = lambda ph="": _elem("textarea", "", {"placeholder": ph}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["area"]     = m["textArea"]
    m["check"]    = lambda lbl="": _elem("label").add(_elem("input", "", {"type": "checkbox"})).add(_elem("span", f" {lbl}"))
    m["radio"]    = lambda lbl="": _elem("label").add(_elem("input", "", {"type": "radio"})).add(_elem("span", f" {lbl}"))
    m["toggle"]   = lambda lbl="": _elem("label", display="inline-flex", align_items="center", cursor="pointer", gap="8px").add(_elem("input", "", {"type": "checkbox", "role": "switch"})).add(_elem("span", lbl))
    m["file"]     = lambda ph="Choose file": _elem("input", "", {"type": "file"}).pad(6).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
    m["date"]     = lambda d="": _elem("input", "", {"type": "date", "value": str(d)}).pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")

    def _select(opts, def_val=None):
        sel = _elem("select").pad(8).round(6).bg("#1e293b").color("#f8fafc").border(1, "#475569")
        for o in opts:
            opt = _elem("option", str(o), {"value": str(o)})
            if def_val is not None and str(o) == str(def_val): opt.attrs["selected"] = "selected"
            sel.add(opt)
        return sel
    m["select"]   = _select
    def _slider(min_v=0, max_v=100, def_v=50):
        return _elem("input", "", {"type": "range", "min": str(min_v), "max": str(max_v), "value": str(def_v)})
    m["slider"]   = _slider

    # 4. Buttons (8 functions + extended variants)
    m["btn"]      = lambda l="": _elem("button", l).pad(8, 16).round(6).border(1, "#475569").bg("#334155").color("#f8fafc")
    m["btnP"]     = lambda l="": _elem("button", l).pad(8, 16).round(6).bg("#2563eb").color("#ffffff").border(0)
    m["btnS"]     = lambda l="": _elem("button", l).pad(4, 8).round(4).fontSize(12).bg("#334155").color("#ffffff")
    m["btnL"]     = lambda l="": _elem("button", l).pad(12, 24).round(8).fontSize(18).bg("#2563eb").color("#ffffff")
    m["btnD"]     = lambda l="": _elem("button", l, {"disabled": "disabled"}).pad(8, 16).round(6).bg("#475569").color("#94a3b8")
    m["btnO"]     = lambda l="": _elem("button", l).pad(8, 16).round(6).border(2, "#3b82f6").bg("transparent").color("#3b82f6")
    m["btnI"]     = lambda text="", icon="": _elem("button").add(_elem("span", f"[{icon}] " if icon else "")).add(_elem("span", text)).pad(8, 16).round(6).bg("#334155").color("#ffffff")
    m["btnIcon"]  = lambda icon="", text="": _elem("button").add(_elem("span", f"[{icon}] " if icon else "")).add(_elem("span", text)).pad(8, 12).round(6).bg("#334155").color("#ffffff").border(0)
    m["fab"]      = lambda icon="": _elem("button", f"[{icon}]").pad(16).roundFull().bg("#3b82f6").color("#ffffff").border(0)
    m["btnLink"]  = lambda text="", url="#": _elem("a", text, {"href": url}, text_decoration="none", display="inline-block").pad(8, 16).round(6).bg("#2563eb").color("#ffffff")
    m["btnClose"] = lambda: _elem("button", "&times;").pad(4, 8).roundFull().bg("#ef4444").color("#ffffff").border(0)
    def _btnGroup(btns=None):
        grp = _elem("div", display="inline-flex", border_radius="6px", overflow="hidden")
        if btns:
            for b in btns: grp.add(b)
        return grp
    m["btnGroup"] = _btnGroup

    # 5. Layout Containers & Semantic Shells (11 functions + extended)
    def _row():
        return _elem("div", display="flex", flex_direction="row", gap="10px", align_items="center")
    def _col():
        return _elem("div", display="flex", flex_direction="column", gap="10px")
    def _grid(r=2, c=2):
        return _elem("div", display="grid", grid_template_columns=f"repeat({c}, 1fr)", gap="10px")
    def _stack():
        return _elem("div", display="grid", grid_template_areas="'stack'")
    def _center():
        return _elem("div", display="flex", justify_content="center", align_items="center")
    def _scroll():
        return _elem("div", overflow_y="auto")

    m["row"]      = _row
    m["col"]      = _col
    m["flex"]     = _row
    m["grid"]     = _grid
    m["stack"]    = _stack
    m["center"]   = _center
    m["scroll"]   = _scroll
    m["form"]     = lambda: _elem("form")
    m["list"]     = lambda items=None: _elem("div", display="flex", flex_direction="column", gap="6px").add(items or [])
    m["table"]    = lambda: NovaTableElement()
    m["sidebar"]  = lambda: _elem("aside", display="flex", flex_direction="column", width="240px", background_color="#1e293b", padding="16px", gap="10px")
    m["nav"]      = lambda: _elem("nav", display="flex", flex_direction="row", align_items="center", justify_content="space-between", padding="12px 20px", background_color="#1e293b", width="100%")
    m["footer"]   = lambda: _elem("footer", display="flex", justify_content="center", padding="16px", color="#94a3b8", border_top="1px solid #334155", width="100%")

    def _modal(title="", children=None):
        backdrop = _elem("div", position="fixed", top="0", left="0", width="100vw", height="100vh", background_color="rgba(0,0,0,0.6)", display="flex", justify_content="center", align_items="center", z_index="1000")
        dialog = _elem("div", background_color="#1e293b", padding="24px", border_radius="10px", width="480px", max_width="90%").add(_elem("h3", title, margin="0 0 16px 0"))
        if children:
            for c in children: dialog.add(c)
        backdrop.add(dialog)
        return backdrop
    m["modal"]    = _modal

    # 6. Advanced Interactive Display & Charts
    def _tabs(tab_dict=None):
        container = _elem("div", display="flex", flex_direction="column", width="100%")
        bar = _elem("div", display="flex", gap="8px", border_bottom="1px solid #334155", margin_bottom="12px")
        content_box = _elem("div")
        if isinstance(tab_dict, dict):
            first = True
            for k, v in tab_dict.items():
                btn = _elem("button", str(k)).pad(8, 16).bg("#3b82f6" if first else "#334155").color("#ffffff").roundT(6).border(0)
                bar.add(btn)
                if first:
                    content_box.add(v if isinstance(v, NovaUIElement) else _elem("div", str(v)))
                    first = False
        container.add(bar).add(content_box)
        return container
    m["tabs"]     = _tabs

    def _accordion(items=None):
        acc = _elem("div", display="flex", flex_direction="column", gap="8px", width="100%")
        if isinstance(items, dict):
            for k, v in items.items():
                head = _elem("div", str(k), background_color="#334155", padding="10px 14px", font_weight="bold", border_radius="6px", cursor="pointer")
                body = _elem("div", str(v) if not isinstance(v, NovaUIElement) else "", padding="10px 14px", background_color="#1e293b", border_radius="0 0 6px 6px")
                if isinstance(v, NovaUIElement): body.add(v)
                acc.add(_elem("div").add(head).add(body))
        return acc
    m["accordion"] = _accordion

    m["toast"]    = lambda msg="", t="info": _elem("div", msg, position="fixed", bottom="20px", right="20px", background_color="#3b82f6" if t=="info" else "#22c55e" if t=="success" else "#ef4444", color="#ffffff", padding="12px 20px", border_radius="8px", box_shadow="0 4px 12px rgba(0,0,0,0.3)")

    def _chart(chart_type="bar", data=None):
        svg = _elem("div", "", {"data-chart-type": chart_type}, padding="16px", background_color="#1e293b", border_radius="8px")
        svg.add(_elem("div", f"Chart [{str(chart_type).upper()}]", font_weight="bold", margin_bottom="8px"))
        if isinstance(data, (list, tuple)):
            chart_bar_cont = _elem("div", display="flex", align_items="flex-end", gap="8px", height="120px", border_bottom="2px solid #475569", padding_top="10px")
            max_val = max(data) if data and max(data) > 0 else 1
            for val in data:
                h_pct = int((val / max_val) * 100)
                col = _elem("div", "", title=str(val), background_color="#3b82f6", width="24px", height=f"{h_pct}%", border_radius="4px 4px 0 0")
                chart_bar_cont.add(col)
            svg.add(chart_bar_cont)
        return svg
    m["chart"]    = _chart

    # Key helper
    class KeyHelper:
        def __init__(self, key_name): self.key_name = key_name
        def onPress(self, fn): return self
    m["key"] = lambda k: KeyHelper(k)

    return StdModule("ui", m)


# ============================================================
# V2.0 BACKEND UNIFIED PLATFORM MODULES (be / backend)
# ============================================================
def build_cache_module():
    m = {}
    _cache_data = {}  # key -> (value, expire_timestamp_or_None)
    _lock = threading.Lock()

    def _clean():
        now = time.time()
        expired = [k for k, (v, exp) in _cache_data.items() if exp is not None and now > exp]
        for k in expired: del _cache_data[k]

    def _get(k, default=None):
        with _lock:
            _clean()
            if k in _cache_data: return _cache_data[k][0]
            return default

    def _set(k, v, ttl=None):
        with _lock:
            exp = (time.time() + float(ttl)) if ttl is not None else None
            _cache_data[str(k)] = (v, exp)
            return v

    def _has(k):
        with _lock:
            _clean()
            return str(k) in _cache_data

    def _del(k):
        with _lock:
            if str(k) in _cache_data:
                del _cache_data[str(k)]
                return True
            return False

    def _clear():
        with _lock:
            _cache_data.clear()
            return True

    def _ttl(k):
        with _lock:
            _clean()
            if str(k) in _cache_data:
                exp = _cache_data[str(k)][1]
                if exp is None: return -1
                return max(0.0, exp - time.time())
            return -2

    def _size():
        with _lock:
            _clean()
            return len(_cache_data)

    m["get"]    = _get
    m["set"]    = _set
    m["has"]    = _has
    m["del"]    = _del
    m["delete"] = _del
    m["clear"]  = _clear
    m["ttl"]    = _ttl
    m["size"]   = _size
    m["keys"]   = lambda: list(_cache_data.keys())
    m["values"] = lambda: [v[0] for v in _cache_data.values()]
    return StdModule("cache", m)


def build_store_module():
    m = {}
    _store_file = "nova_store.json"
    _store_data = {}
    _lock = threading.Lock()

    def _load():
        nonlocal _store_data
        if os.path.exists(_store_file):
            try:
                with open(_store_file, "r", encoding="utf-8") as f:
                    _store_data = json.load(f)
            except Exception: _store_data = {}
        else: _store_data = {}

    def _persist():
        try:
            with open(_store_file, "w", encoding="utf-8") as f:
                json.dump(_store_data, f, indent=2)
        except Exception: pass

    _load()

    def _save(k_or_dict, v=None):
        with _lock:
            if v is None and isinstance(k_or_dict, dict):
                _store_data.update(k_or_dict)
            else:
                _store_data[str(k_or_dict)] = v
            _persist()
            return True

    def _get(k, default=None):
        with _lock:
            return _store_data.get(str(k), default)

    def _has(k):
        with _lock:
            return str(k) in _store_data

    def _del(k):
        with _lock:
            if str(k) in _store_data:
                del _store_data[str(k)]
                _persist()
                return True
            return False

    def _list(prefix=""):
        with _lock:
            if prefix:
                return {k: v for k, v in _store_data.items() if k.startswith(str(prefix))}
            return dict(_store_data)

    def _clear():
        with _lock:
            _store_data.clear()
            _persist()
            return True

    m["save"]   = _save
    m["set"]    = _save
    m["get"]    = _get
    m["has"]    = _has
    m["del"]    = _del
    m["delete"] = _del
    m["list"]   = _list
    m["all"]    = _list
    m["clear"]  = _clear
    return StdModule("store", m)


def build_queue_module(interp):
    m = {}
    _queues = {}
    _lock = threading.Lock()

    def _add(topic_or_val, val=None):
        with _lock:
            if val is None:
                topic = "default"; data = topic_or_val
            else:
                topic = str(topic_or_val); data = val
            if topic not in _queues: _queues[topic] = []
            _queues[topic].append(data)
            return len(_queues[topic])

    def _pop(topic="default"):
        with _lock:
            topic = str(topic)
            if topic in _queues and _queues[topic]:
                return _queues[topic].pop(0)
            return None

    def _peek(topic="default"):
        with _lock:
            topic = str(topic)
            if topic in _queues and _queues[topic]:
                return _queues[topic][0]
            return None

    def _size(topic="default"):
        with _lock:
            topic = str(topic)
            return len(_queues.get(topic, []))

    def _clear(topic=None):
        with _lock:
            if topic is None: _queues.clear()
            elif str(topic) in _queues: _queues[str(topic)].clear()
            return True

    def _process(topic_or_fn, fn=None):
        if fn is None:
            topic = "default"; handler = topic_or_fn
        else:
            topic = str(topic_or_fn); handler = fn
        processed = 0
        while True:
            item = _pop(topic)
            if item is None: break
            interp._invoke(handler, [item])
            processed += 1
        return processed

    m["add"]     = _add
    m["push"]    = _add
    m["pop"]     = _pop
    m["peek"]    = _peek
    m["size"]    = _size
    m["clear"]   = _clear
    m["process"] = _process
    return StdModule("queue", m)


def build_cron_module(interp):
    m = {}
    _tasks = {}
    _task_counter = 0
    _lock = threading.Lock()

    def _every(interval_sec, fn):
        nonlocal _task_counter
        with _lock:
            _task_counter += 1
            tid = f"job_{_task_counter}"
            stop_evt = threading.Event()

            def _worker():
                while not stop_evt.wait(float(interval_sec)):
                    try:
                        interp._invoke(fn, [])
                    except Exception as e:
                        print(f"[Cron Error]: {e}", file=sys.stderr)

            t = threading.Thread(target=_worker, daemon=True)
            t.start()
            _tasks[tid] = (t, stop_evt, f"every {interval_sec}s")
            return tid

    def _cancel(tid):
        with _lock:
            if tid in _tasks:
                t, evt, desc = _tasks[tid]
                evt.set()
                del _tasks[tid]
                return True
            return False

    def _list():
        with _lock:
            return {tid: desc for tid, (t, evt, desc) in _tasks.items()}

    def _clear():
        with _lock:
            for tid, (t, evt, desc) in list(_tasks.items()):
                evt.set()
            _tasks.clear()
            return True

    m["every"]    = _every
    m["schedule"] = _every
    m["cancel"]   = _cancel
    m["list"]     = _list
    m["clear"]    = _clear
    return StdModule("cron", m)


def build_ws_module(interp):
    m = {}
    _clients = {}
    _handlers = {"message": [], "connect": [], "close": []}
    _lock = threading.Lock()

    def _send_all(msg):
        with _lock:
            for fn in _handlers["message"]:
                try: interp._invoke(fn, [msg])
                except Exception: pass
            return len(_clients)

    def _send(cid, msg):
        with _lock:
            return True

    def _on_message(fn): _handlers["message"].append(fn); return fn
    def _on_connect(fn): _handlers["connect"].append(fn); return fn
    def _on_close(fn): _handlers["close"].append(fn); return fn

    m["sendAll"]   = _send_all
    m["broadcast"] = _send_all
    m["send"]      = _send
    m["onMessage"] = _on_message
    m["onConnect"] = _on_connect
    m["onClose"]   = _on_close
    m["clients"]   = lambda: list(_clients.keys())
    m["count"]     = lambda: len(_clients)
    return StdModule("ws", m)


def build_mail_module():
    m = {}
    _templates = {}

    def _send(to, subject, body, opts=None):
        opts = opts or {}
        print(f"[Mail Sent] To: {to} | Subject: {subject}")
        return {"ok": True, "to": to, "subject": subject, "id": str(uuid.uuid4())}

    def _template(name, tmpl_str=None):
        if tmpl_str is not None:
            _templates[str(name)] = str(tmpl_str)
            return True
        return _templates.get(str(name), "")

    def _verify(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, str(email).strip()))

    m["send"]     = _send
    m["template"] = _template
    m["verify"]   = _verify
    return StdModule("mail", m)


def build_valid_module():
    m = {}

    def _email(val):
        return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', str(val).strip()))

    def _url(val):
        return bool(re.match(r'^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(\/.*)?$', str(val).strip()))

    def _phone(val):
        return bool(re.match(r'^\+?[0-9\s\-()]{7,20}$', str(val).strip()))

    def _ip(val):
        return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(val).strip()))

    def _num(val):
        try: float(val); return True
        except Exception: return False

    def _alpha(val):
        return str(val).isalpha()

    def _len(val, min_l, max_l=None):
        l = len(str(val))
        if max_l is None: return l >= int(min_l)
        return int(min_l) <= l <= int(max_l)

    def _req(val):
        if val is None: return False
        if isinstance(val, (str, list, dict, set, tuple)): return len(val) > 0
        return True

    def _match(val, pattern):
        return bool(re.search(str(pattern), str(val)))

    m["email"] = _email
    m["url"]   = _url
    m["phone"] = _phone
    m["ip"]    = _ip
    m["num"]   = _num
    m["alpha"] = _alpha
    m["len"]   = _len
    m["req"]   = _req
    m["match"] = _match
    return StdModule("valid", m)


def build_log_module():
    m = {}
    _log_file = [None]

    def _fmt(level, *args):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = " ".join(str(a) for a in args)
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        if _log_file[0]:
            try:
                with open(_log_file[0], "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception: pass
        return line

    def _set_file(path):
        _log_file[0] = str(path)
        return str(path)

    m["info"]  = lambda *args: _fmt("INFO", *args)
    m["warn"]  = lambda *args: _fmt("WARN", *args)
    m["error"] = lambda *args: _fmt("ERROR", *args)
    m["debug"] = lambda *args: _fmt("DEBUG", *args)
    m["file"]  = _set_file
    return StdModule("log", m)


def build_session_module():
    m = {}
    _sessions = {}
    _lock = threading.Lock()

    def _clean():
        now = time.time()
        expired = [sid for sid, (d, exp) in _sessions.items() if now > exp]
        for sid in expired: del _sessions[sid]

    def _create(data=None, ttl=86400):
        with _lock:
            _clean()
            sid = secrets.token_hex(16)
            d = dict(data) if isinstance(data, dict) else {}
            exp = time.time() + float(ttl)
            _sessions[sid] = (d, exp)
            return sid

    def _get(sid, k=None, default=None):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, exp = _sessions[str(sid)]
                if k is None: return dict(d)
                return d.get(str(k), default)
            return default

    def _set(sid, k, v):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, exp = _sessions[str(sid)]
                d[str(k)] = v
                return True
            return False

    def _has(sid):
        with _lock:
            _clean()
            return str(sid) in _sessions

    def _destroy(sid):
        with _lock:
            if str(sid) in _sessions:
                del _sessions[str(sid)]
                return True
            return False

    def _touch(sid, ttl=86400):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, _ = _sessions[str(sid)]
                _sessions[str(sid)] = (d, time.time() + float(ttl))
                return True
            return False

    m["create"]  = _create
    m["get"]     = _get
    m["set"]     = _set
    m["has"]     = _has
    m["destroy"] = _destroy
    m["del"]     = _destroy
    m["touch"]   = _touch
    m["count"]   = lambda: len(_sessions)
    return StdModule("session", m)


def build_backend_module(interp, server_mod, db_inst, auth_mod, env_mod,
                         cache_mod, store_mod, queue_mod, cron_mod,
                         ws_mod, mail_mod, valid_mod, log_mod, session_mod):
    m = {
        "server": server_mod,
        "db": db_inst,
        "cache": cache_mod,
        "store": store_mod,
        "queue": queue_mod,
        "cron": cron_mod,
        "ws": ws_mod,
        "mail": mail_mod,
        "valid": valid_mod,
        "log": log_mod,
        "session": session_mod,
        "auth": auth_mod,
        "env": env_mod,
    }
    return StdModule("backend", m)


# ============================================================
# NUMPY / NP - ARRAY COMPUTING ENGINE
# ============================================================
class NovaArray:
    def __init__(self, data):
        if isinstance(data, NovaArray):
            self.data = [x for x in data.data]
            self.shape = list(data.shape)
        elif isinstance(data, (list, tuple)):
            self.data, self.shape = self._parse_nested(data)
        else:
            self.data = [data]
            self.shape = [1]
        self.size = len(self.flat_list())
        self.len = self.shape[0] if self.shape else 0

    def _parse_nested(self, d):
        if not isinstance(d, (list, tuple)):
            return d, []
        if len(d) == 0:
            return [], [0]
        first = d[0]
        if isinstance(first, (list, tuple)):
            sub_shape = None
            parsed = []
            for item in d:
                p, s = self._parse_nested(item)
                parsed.append(p)
                if sub_shape is None: sub_shape = s
            return parsed, [len(d)] + sub_shape
        else:
            return list(d), [len(d)]

    def flat_list(self):
        def _f(x):
            if isinstance(x, (list, tuple)):
                res = []
                for item in x: res.extend(_f(item))
                return res
            return [x]
        return _f(self.data)

    def flat(self):
        return NovaArray(self.flat_list())

    def toList(self):
        return self.data

    @property
    def T(self):
        return self.transpose()

    def transpose(self):
        if len(self.shape) <= 1:
            return NovaArray(self.data)
        if len(self.shape) == 2:
            r, c = self.shape
            t_data = [[self.data[i][j] for i in range(r)] for j in range(c)]
            return NovaArray(t_data)
        raise ValueError("Transpose supported up to 2D")

    def trans(self): return self.transpose()

    def reshape(self, new_shape):
        if isinstance(new_shape, (int, float)): new_shape = [int(new_shape)]
        elif isinstance(new_shape, (list, tuple)): new_shape = [int(s) for s in new_shape]
        flat = self.flat_list()
        total = 1
        for s in new_shape: total *= s
        if total != len(flat):
            raise ValueError(f"Cannot reshape array of size {len(flat)} into shape {new_shape}")
        
        def _build(shape, idx):
            if len(shape) == 1:
                return flat[idx:idx+shape[0]], idx + shape[0]
            res = []
            cur_idx = idx
            for _ in range(shape[0]):
                sub, cur_idx = _build(shape[1:], cur_idx)
                res.append(sub)
            return res, cur_idx

        new_data, _ = _build(new_shape, 0)
        return NovaArray(new_data)

    def get(self, *indices):
        cur = self.data
        for idx in indices:
            cur = cur[int(idx)]
        return NovaArray(cur) if isinstance(cur, list) else cur

    def set(self, *args):
        if len(args) < 2: return self
        val = args[-1]
        val = val.data if isinstance(val, NovaArray) else val
        indices = [int(x) for x in args[:-1]]
        cur = self.data
        for idx in indices[:-1]:
            cur = cur[idx]
        cur[indices[-1]] = val
        return self

    def slice(self, start=0, end=None):
        st = int(start) if start is not None else 0
        en = int(end) if end is not None else len(self.data)
        return NovaArray(self.data[st:en])

    # Element-wise and Math operations
    def _apply_op(self, other, op_fn):
        if isinstance(other, NovaArray):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            def _rec(a, b):
                if isinstance(a, list):
                    return [_rec(x, y) for x, y in zip(a, b)]
                return op_fn(a, b)
            return NovaArray(_rec(self.data, other.data))
        else:
            def _rec(a):
                if isinstance(a, list):
                    return [_rec(x) for x in a]
                return op_fn(a, other)
            return NovaArray(_rec(self.data))

    def __add__(self, o): return self._apply_op(o, lambda a, b: a + b)
    def __radd__(self, o): return self._apply_op(o, lambda a, b: b + a)
    def __sub__(self, o): return self._apply_op(o, lambda a, b: a - b)
    def __rsub__(self, o): return self._apply_op(o, lambda a, b: b - a)
    def __mul__(self, o): return self._apply_op(o, lambda a, b: a * b)
    def __rmul__(self, o): return self._apply_op(o, lambda a, b: b * a)
    def __truediv__(self, o): return self._apply_op(o, lambda a, b: a / b)
    def __rtruediv__(self, o): return self._apply_op(o, lambda a, b: b / a)
    def __floordiv__(self, o): return self._apply_op(o, lambda a, b: a // b)
    def __mod__(self, o): return self._apply_op(o, lambda a, b: a % b)
    def __pow__(self, o): return self._apply_op(o, lambda a, b: a ** b)
    def __neg__(self): return self._apply_op(0, lambda a, b: -a)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return NovaArray(self.data[idx])
        res = self.data[int(idx)]
        if isinstance(res, list):
            return NovaArray(res)
        return res

    def __setitem__(self, idx, val):
        self.data[int(idx)] = val.data if isinstance(val, NovaArray) else val

    def __len__(self): return self.len

    def sum(self): return sum(self.flat_list())
    def mean(self): return sum(self.flat_list()) / len(self.flat_list()) if self.flat_list() else 0
    def avg(self): return self.mean()
    def max(self): return max(self.flat_list()) if self.flat_list() else None
    def min(self): return min(self.flat_list()) if self.flat_list() else None

    def var(self):
        m = self.mean()
        fl = self.flat_list()
        return sum((x - m) ** 2 for x in fl) / len(fl) if fl else 0

    def std(self):
        return math.sqrt(self.var())

    def norm(self):
        return math.sqrt(sum(x ** 2 for x in self.flat_list()))

    def dot(self, other):
        o_flat = other.flat_list() if isinstance(other, NovaArray) else NovaArray(other).flat_list()
        s_flat = self.flat_list()
        if len(s_flat) != len(o_flat):
            raise ValueError(f"Dot product dimension mismatch: {len(s_flat)} vs {len(o_flat)}")
        return sum(a * b for a, b in zip(s_flat, o_flat))

    def matMul(self, other):
        b = other if isinstance(other, NovaArray) else NovaArray(other)
        if len(self.shape) != 2 or len(b.shape) != 2:
            raise ValueError("Matrix multiplication requires 2D arrays")
        r1, c1 = self.shape; r2, c2 = b.shape
        if c1 != r2:
            raise ValueError(f"Matrix dimension mismatch: ({r1}x{c1}) and ({r2}x{c2})")
        res = [[sum(self.data[i][k] * b.data[k][j] for k in range(c1)) for j in range(c2)] for i in range(r1)]
        return NovaArray(res)

    def softmax(self):
        fl = self.flat_list()
        max_v = max(fl) if fl else 0
        exp_vals = [math.exp(x - max_v) for x in fl]
        sum_exp = sum(exp_vals) or 1
        res = [v / sum_exp for v in exp_vals]
        return NovaArray(res).reshape(self.shape)

    def relu(self):
        def _r(x):
            if isinstance(x, list): return [_r(v) for v in x]
            return max(0, x)
        return NovaArray(_r(self.data))

    def sigmoid(self):
        def _s(x):
            if isinstance(x, list): return [_s(v) for v in x]
            return 1.0 / (1.0 + math.exp(-x))
        return NovaArray(_s(self.data))

    def __repr__(self):
        return f"array({self.data})"


def build_numpy_module():
    m = {}

    def _array(data):
        return NovaArray(data)

    def _zeros(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [0] * s[0]
            return [_b(s[1:]) for _ in range(s[0])]
        return NovaArray(_b(shape))

    def _ones(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [1] * s[0]
            return [_b(s[1:]) for _ in range(s[0])]
        return NovaArray(_b(shape))

    def _rand(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [random.random() for _ in range(s[0])]
            return [_b(s[1:]) for _ in range(s[0])]
        return NovaArray(_b(shape))

    def _range(start, end=None, step=1):
        if end is None:
            st, en = 0, int(start)
        else:
            st, en = int(start), int(end)
        stp = int(step)
        return NovaArray(list(range(st, en, stp)))

    def _oneHot(idx, classes):
        c = int(classes)
        i = int(idx)
        res = [1 if k == i else 0 for k in range(c)]
        return NovaArray(res)

    def _to_arr(a):
        return a if isinstance(a, NovaArray) else NovaArray(a)

    m["array"]   = _array
    m["zeros"]   = _zeros
    m["ones"]    = _ones
    m["rand"]    = _rand
    m["random"]  = _rand
    m["range"]   = _range
    m["reshape"] = lambda a, s: _to_arr(a).reshape(s)
    m["shape"]   = lambda a: _to_arr(a).shape
    m["size"]    = lambda a: _to_arr(a).size
    m["flat"]    = lambda a: _to_arr(a).flat()
    m["T"]       = lambda a: _to_arr(a).T
    m["trans"]   = lambda a: _to_arr(a).T
    m["dot"]     = lambda a, b: _to_arr(a).dot(_to_arr(b))
    m["matMul"]  = lambda a, b: _to_arr(a).matMul(_to_arr(b))
    m["sum"]     = lambda a: _to_arr(a).sum()
    m["mean"]    = lambda a: _to_arr(a).mean()
    m["avg"]     = lambda a: _to_arr(a).mean()
    m["max"]     = lambda a: _to_arr(a).max()
    m["min"]     = lambda a: _to_arr(a).min()
    m["std"]     = lambda a: _to_arr(a).std()
    m["var"]     = lambda a: _to_arr(a).var()
    m["norm"]    = lambda a: _to_arr(a).norm()
    m["softmax"] = lambda a: _to_arr(a).softmax()
    m["relu"]    = lambda a: _to_arr(a).relu()
    m["sigmoid"] = lambda a: _to_arr(a).sigmoid()
    m["oneHot"]  = _oneHot

    return StdModule("numpy", m)


# ============================================================
# PANDAS / PD - DATAFRAME ENGINE
# ============================================================
class NovaGroupedDF:
    def __init__(self, df, group_col):
        self.df = df
        self.group_col = str(group_col)
        self.groups = {}
        for r in df._rows:
            key = r.get(self.group_col, "Unknown")
            if key not in self.groups: self.groups[key] = []
            self.groups[key].append(r)

    def mean(self):
        numeric_cols = [c for c in self.df._columns if c != self.group_col and any(isinstance(r.get(c), (int, float)) for r in self.df._rows)]
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in numeric_cols:
                vals = [r[c] for r in rows if isinstance(r.get(c), (int, float))]
                row_res[c] = sum(vals) / len(vals) if vals else 0
            res.append(row_res)
        return NovaDF(res)

    def sum(self):
        numeric_cols = [c for c in self.df._columns if c != self.group_col and any(isinstance(r.get(c), (int, float)) for r in self.df._rows)]
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in numeric_cols:
                vals = [r[c] for r in rows if isinstance(r.get(c), (int, float))]
                row_res[c] = sum(vals) if vals else 0
            res.append(row_res)
        return NovaDF(res)

    def count(self):
        res = [{self.group_col: g_val, "count": len(rows)} for g_val, rows in self.groups.items()]
        return NovaDF(res)

    def max(self):
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in self.df._columns:
                if c == self.group_col: continue
                vals = [r[c] for r in rows if r.get(c) is not None]
                row_res[c] = max(vals) if vals else None
            res.append(row_res)
        return NovaDF(res)

    def min(self):
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in self.df._columns:
                if c == self.group_col: continue
                vals = [r[c] for r in rows if r.get(c) is not None]
                row_res[c] = min(vals) if vals else None
            res.append(row_res)
        return NovaDF(res)

    def __repr__(self):
        return f"<GroupedDF by '{self.group_col}' ({len(self.groups)} groups)>"


class NovaDF:
    def __init__(self, data, columns=None, interp=None):
        self._rows = []
        self._columns = []
        self._interp = interp

        if isinstance(data, dict):
            self._columns = list(data.keys())
            max_len = max(len(v) if isinstance(v, (list, tuple, NovaArray)) else 1 for v in data.values()) if data else 0
            for i in range(max_len):
                row = {}
                for k in self._columns:
                    v = data[k]
                    if isinstance(v, (list, tuple, NovaArray)):
                        val = v[i] if i < len(v) else None
                        row[k] = val.data if isinstance(val, NovaArray) else val
                    else:
                        row[k] = v
                self._rows.append(row)
        elif isinstance(data, (list, tuple)):
            if columns is None:
                if data and isinstance(data[0], dict):
                    self._columns = list(data[0].keys())
                    self._rows = [dict(r) for r in data]
                else:
                    self._columns = [f"col_{i}" for i in range(len(data[0]))] if data and isinstance(data[0], (list, tuple)) else []
                    for r in data:
                        self._rows.append({c: v for c, v in zip(self._columns, r)})
            else:
                self._columns = list(columns)
                for r in data:
                    if isinstance(r, dict):
                        self._rows.append({c: r.get(c, None) for c in self._columns})
                    else:
                        self._rows.append({c: v for c, v in zip(self._columns, r)})

        self.colNames = list(self._columns)
        self.rows = len(self._rows)
        self.cols = len(self._columns)
        self.shape = [self.rows, self.cols]

    def col(self, name):
        name = str(name)
        return [r.get(name, None) for r in self._rows]

    def getCol(self, name): return self.col(name)

    def row(self, idx):
        return dict(self._rows[int(idx)])

    def getRow(self, idx): return self.row(idx)

    def __getitem__(self, item):
        if isinstance(item, str): return self.col(item)
        if isinstance(item, (int, float)): return self.row(int(item))
        if isinstance(item, slice): return NovaDF(self._rows[item], self._columns, self._interp)
        raise KeyError(item)

    def __setitem__(self, col_name, values):
        self.addCol(col_name, values)

    def __len__(self): return self.rows

    def head(self, n=5):
        return NovaDF(self._rows[:int(n)], self._columns, self._interp)

    def tail(self, n=5):
        return NovaDF(self._rows[-int(n):], self._columns, self._interp)

    def info(self):
        lines = [f"<NovaDF {self.rows} rows x {self.cols} cols>"]
        for c in self._columns:
            non_null = sum(1 for r in self._rows if r.get(c) is not None)
            lines.append(f"  {c}: {non_null} non-null")
        info_str = "\n".join(lines)
        print(info_str)
        return info_str

    def where(self, condition):
        cond_str = str(condition)
        matched = []
        for r in self._rows:
            try:
                if eval(cond_str, {"__builtins__": {}}, dict(r)):
                    matched.append(r)
            except Exception:
                pass
        return NovaDF(matched, self._columns, self._interp)

    def filter(self, fn):
        matched = []
        for r in self._rows:
            try:
                if self._interp is not None:
                    res = self._interp._invoke(fn, [r])
                elif callable(fn):
                    res = fn(r)
                else:
                    res = False
                if res: matched.append(r)
            except Exception:
                pass
        return NovaDF(matched, self._columns, self._interp)

    def sort(self, col):
        col = str(col)
        sorted_rows = sorted(self._rows, key=lambda r: (r.get(col) is None, r.get(col)))
        return NovaDF(sorted_rows, self._columns, self._interp)

    def sortBy(self, col): return self.sort(col)

    def dsort(self, col):
        col = str(col)
        sorted_rows = sorted(self._rows, key=lambda r: (r.get(col) is None, r.get(col)), reverse=True)
        return NovaDF(sorted_rows, self._columns, self._interp)

    def group(self, col): return NovaGroupedDF(self, col)
    def groupBy(self, col): return NovaGroupedDF(self, col)

    def mean(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if isinstance(r.get(str(col)), (int, float))]
            return sum(vals) / len(vals) if vals else 0
        return {c: self.mean(c) for c in self._columns if any(isinstance(r.get(c), (int, float)) for r in self._rows)}

    def avg(self, col=None): return self.mean(col)

    def sum(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if isinstance(r.get(str(col)), (int, float))]
            return sum(vals) if vals else 0
        return {c: self.sum(c) for c in self._columns if any(isinstance(r.get(c), (int, float)) for r in self._rows)}

    def max(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if r.get(str(col)) is not None]
            return max(vals) if vals else None
        return {c: self.max(c) for c in self._columns}

    def min(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if r.get(str(col)) is not None]
            return min(vals) if vals else None
        return {c: self.min(c) for c in self._columns}

    def count(self, col=None):
        if col is not None:
            return sum(1 for r in self._rows if r.get(str(col)) is not None)
        return self.rows

    def fill(self, value):
        new_rows = []
        for r in self._rows:
            new_r = {k: (value if v is None else v) for k, v in r.items()}
            new_rows.append(new_r)
        return NovaDF(new_rows, self._columns, self._interp)

    def fillNA(self, value): return self.fill(value)

    def dropNA(self):
        new_rows = [r for r in self._rows if all(v is not None for v in r.values())]
        return NovaDF(new_rows, self._columns, self._interp)

    def drop(self, col):
        col = str(col)
        new_cols = [c for c in self._columns if c != col]
        new_rows = [{k: v for k, v in r.items() if k != col} for r in self._rows]
        return NovaDF(new_rows, new_cols, self._interp)

    def dropRow(self, idx):
        i = int(idx)
        new_rows = [r for k, r in enumerate(self._rows) if k != i]
        return NovaDF(new_rows, self._columns, self._interp)

    def addCol(self, name, values):
        name = str(name)
        if name not in self._columns: self._columns.append(name)
        vals = values.flat_list() if isinstance(values, NovaArray) else list(values)
        for i, r in enumerate(self._rows):
            r[name] = vals[i] if i < len(vals) else None
        self.colNames = list(self._columns)
        self.cols = len(self._columns)
        self.shape = [self.rows, self.cols]
        return self

    def addRow(self, row):
        if isinstance(row, dict):
            new_r = {c: row.get(c, None) for c in self._columns}
        elif isinstance(row, (list, tuple)):
            new_r = {c: v for c, v in zip(self._columns, row)}
        else:
            new_r = {c: None for c in self._columns}
        self._rows.append(new_r)
        self.rows = len(self._rows)
        self.shape = [self.rows, self.cols]
        return self

    def set(self, rowIndex, colName, value):
        r = int(rowIndex); c = str(colName)
        if 0 <= r < len(self._rows):
            self._rows[r][c] = value
        return self

    def update(self, rowIndex, row_map):
        r = int(rowIndex)
        if 0 <= r < len(self._rows) and isinstance(row_map, dict):
            self._rows[r].update(row_map)
        return self

    def toArray(self):
        return [[r.get(c, None) for c in self._columns] for r in self._rows]

    def toNum(self):
        return NovaArray(self.toArray())

    def toNumpy(self): return self.toNum()

    def toCsv(self, path):
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._columns)
            writer.writeheader()
            writer.writerows(self._rows)
        return True

    def toJson(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._rows, f, indent=2)
        return True

    def toExcel(self, path):
        return self.toCsv(path)

    def save(self, path):
        p = str(path).lower()
        if p.endswith(".json"): return self.toJson(path)
        return self.toCsv(path)

    def __repr__(self):
        if not self._rows: return "Empty DataFrame"
        hdr = " | ".join(f"{str(c):<12}" for c in self._columns)
        sep = "-+-".join("-" * 12 for _ in self._columns)
        rows_str = []
        for r in self._rows[:10]:
            rows_str.append(" | ".join(f"{str(r.get(c, '')):<12}" for c in self._columns))
        if len(self._rows) > 10:
            rows_str.append(f"... ({len(self._rows) - 10} more rows)")
        return f"{hdr}\n{sep}\n" + "\n".join(rows_str)


def build_pandas_module(interp):
    m = {}

    def _df(data=None, columns=None):
        return NovaDF(data if data is not None else {}, columns, interp)

    def _readCsv(path):
        import csv
        rows = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                parsed_r = {}
                for k, v in r.items():
                    try:
                        parsed_r[k] = int(v) if v.isdigit() else float(v)
                    except Exception:
                        parsed_r[k] = v
                rows.append(parsed_r)
        return NovaDF(rows, interp=interp)

    def _readJson(path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return NovaDF(d, interp=interp)

    def _readExcel(path):
        return _readCsv(path)

    def _read(path):
        p = str(path).lower()
        if p.endswith(".json"): return _readJson(path)
        return _readCsv(path)

    m["df"]         = _df
    m["DF"]         = _df
    m["DataFrame"]  = _df
    m["dataframe"]  = _df
    m["readCsv"]    = _readCsv
    m["read_csv"]   = _readCsv
    m["readJson"]   = _readJson
    m["read_json"]  = _readJson
    m["readExcel"]  = _readExcel
    m["read_excel"] = _readExcel
    m["read"]       = _read

    return StdModule("pandas", m)


# ============================================================
# INTERPRETER
# ============================================================
class Interpreter:
    def __init__(self):
        self.global_env = Env()
        self.modules = {}
        self._setup_modules()
        self._setup_builtins()

    def _invoke(self, fn, args, line=1):
        if isinstance(fn, BoundMethod): return fn(*args)
        if isinstance(fn, NovaFunction):
            child = Env(fn.closure)
            for (pn, pt), val in zip(fn.params, args):
                if pt: val = self._coerce(val, pt, line)
                child.define(pn, val)
            try: self._exec_block(fn.body, child)
            except ReturnSignal as r: return r.value
            return None
        if isinstance(fn, NovaLambda):
            child = Env(fn.closure)
            for p, val in zip(fn.params, args): child.define(p, val)
            if isinstance(fn.body, list):
                try: self._exec_block(fn.body, child)
                except ReturnSignal as r: return r.value
                return None
            else:
                return self._eval(fn.body, child)
        if callable(fn):
            return fn(*args)
        return None

    def _setup_modules(self):
        for name in libsMap:
            mod = loadLib(name, self)
            if mod is not None:
                self.modules[name] = mod

    def _setup_builtins(self):
        e = self.global_env
        for mod_name, mod_obj in self.modules.items():
            e.define(mod_name, mod_obj)

        e.define("open", lambda path, mode="read": NovaFile(path, mode))
        e.define("pwd", os.getcwd)
        e.define("cd", lambda p: os.chdir(os.path.expanduser(p)) or os.getcwd())

        for name in _BUILTIN_ERRORS:
            def make_ctor(n):
                return lambda *args: NovaBuiltinError(n, str(args[0]) if args else "", args[1] if len(args)>1 else None)
            e.define(name, make_ctor(name))

    def run(self, prog):
        self._exec_block(prog.body, self.global_env)

    def _exec_block(self, stmts, env):
        for s in stmts: self._exec(s, env)

    def _exec(self, node, env):
        t = type(node)
        if t == Assign:       self._exec_assign(node, env)
        elif t == VarDecl:    self._exec_vdecl(node, env)
        elif t == AttrAssign: self._exec_attr_assign(node, env)
        elif t == Show:       self._exec_show(node, env)
        elif t == If:         self._exec_if(node, env)
        elif t == Choose:     self._exec_choose(node, env)
        elif t == ForRange:   self._exec_for_range(node, env)
        elif t == ForEach:    self._exec_for_each(node, env)
        elif t == Keep:       self._exec_keep(node, env)
        elif t == FuncDef:    env.define(node.name, NovaFunction(node.name, node.params, node.return_type, node.body, env))
        elif t == ClassDef:   self._exec_classdef(node, env)
        elif t == EnumDef:    self._exec_enumdef(node, env)
        elif t == Return:
            v = self._eval(node.value, env) if node.value else None; raise ReturnSignal(v)
        elif t == TryCatch:   self._exec_try(node, env)
        elif t == ThrowStmt:  raise NovaThrown(self._eval(node.value, env))
        elif t == AssertStmt: self._exec_assert(node, env)
        elif t == CdStmt:     self._exec_cd(node, env)
        elif t == SwapStmt:   self._exec_swap(node, env)
        elif t == ReverseStmt:self._exec_reverse(node, env)
        elif t == BreckStmt:  raise BreakSignal()
        elif t == SkipStmt:   raise ContinueSignal()
        elif t == ImportStmt: self._exec_import(node, env)
        elif t == ExprStmt:
            e2 = node.expr
            if isinstance(e2, BinOp) and isinstance(e2.left, Index):
                obj = self._eval(e2.left.obj, env); idx = self._eval(e2.left.index, env)
                val = self._eval(e2.right, env)
                if isinstance(obj, list): obj[int(idx)] = val
                elif isinstance(obj, dict): obj[idx] = val
                else: raise NovaError(f"[Line {node.line}] Cannot index-assign")
            else: self._eval(node.expr, env)
        else: raise NovaError(f"Unknown stmt: {t.__name__}")

    def _exec_cd(self, n, env):
        target = str(self._eval(n.path, env))
        try: os.chdir(os.path.expanduser(target))
        except Exception as e: raise NovaError(f"[Line {n.line}] cd error: {e}")

    def _exec_assign(self, n, env):
        val = self._eval(n.value, env)
        if n.op != "=":
            old = env.get(n.name, n.line); val = self._augment(old, n.op, val, n.line)
        if n.is_const: env.define(n.name, val, const=True)
        else: env.set(n.name, val, n.line)

    def _exec_attr_assign(self, n, env):
        obj = self._eval(n.obj, env); val = self._eval(n.value, env)
        attr = n.attr
        if isinstance(obj, NovaInstance):
            klass = obj.klass
            meth = self._resolve_method(klass, "set_" + attr)
            if meth is None: meth = klass.setters.get(attr)
            if meth is not None:
                self._call_method(meth, obj, [val], n.line, env); return
            if n.op != "=":
                old = obj.fields.get(attr, klass.static_fields.get(attr, 0))
                val = self._augment(old, n.op, val, n.line)
            obj.fields[attr] = val
        elif isinstance(obj, NovaClass):
            if n.op != "=":
                old = obj.static_fields.get(attr, 0); val = self._augment(old, n.op, val, n.line)
            obj.static_fields[attr] = val
        elif isinstance(obj, NovaUIElement):
            if attr == "value": obj.value = str(val)
            else: obj.attrs[attr] = val
        else:
            setattr(obj, attr, val)

    def _augment(self, old, op, val, line):
        try:
            if op == "+=": return old + val
            if op == "-=": return old - val
            if op == "*=": return old * val
            if op == "/=": return old / val
            if op == "//=": return old // val
            if op == "%=": return old % val
        except Exception as e:
            raise NovaError(f"[Line {line}] TypeError: {e}")

    def _exec_vdecl(self, n, env):
        val = self._eval(n.value, env) if n.value else None
        if val is not None and n.type_hint: val = self._coerce(val, n.type_hint, n.line)
        env.define(n.name, val, const=n.is_const)

    def _coerce(self, val, hint, line):
        try:
            if hint == "int":    return int(val)
            if hint == "float":  return float(val)
            if hint == "string": return str(val)
            if hint == "bool":   return bool(val)
            if hint == "list":   return list(val)
            if hint == "set":    return set(val)
            if hint == "tuple":  return tuple(val)
        except Exception as e:
            raise NovaError(f"[Line {line}] Cannot coerce to {hint}: {e}")
        return val

    def _exec_show(self, n, env):
        print(" ".join(self._display(self._eval(v, env)) for v in n.values))

    def _display(self, val):
        if val is True:  return "true"
        if val is False: return "false"
        if val is None:  return "none"
        if isinstance(val, NovaInstance): return self._instance_str(val)
        if isinstance(val, NovaEnumMember): return repr(val)
        if isinstance(val, NovaEnum): return repr(val)
        if isinstance(val, NovaClass): return repr(val)
        if isinstance(val, StdModule): return repr(val)
        if isinstance(val, NovaFile): return repr(val)
        if isinstance(val, NovaHttpResponse): return repr(val)
        if isinstance(val, NovaUIElement): return repr(val)
        if isinstance(val, set):
            return "{" + ", ".join(self._display(x) for x in sorted(val, key=str)) + "}"
        if isinstance(val, dict):
            return "{" + ", ".join(f"{self._display(k)}: {self._display(v)}" for k, v in val.items()) + "}"
        if isinstance(val, list):  return "[" + ", ".join(self._display(x) for x in val) + "]"
        if isinstance(val, tuple): return "(" + ", ".join(self._display(x) for x in val) + ")"
        return str(val)

    def _instance_str(self, inst):
        klass = inst.klass
        meth = self._resolve_method(klass, "__str__") or self._resolve_method(klass, "toString")
        if meth:
            r = self._call_method(meth, inst, [], 0, None); return str(r)
        return f"<{klass.name}>"

    def _exec_if(self, n, env):
        if self._truthy(self._eval(n.condition, env)):
            self._exec_block(n.then_body, Env(env)); return
        for cond, body in n.elsif_clauses:
            if self._truthy(self._eval(cond, env)):
                self._exec_block(body, Env(env)); return
        if n.else_body: self._exec_block(n.else_body, Env(env))

    def _exec_choose(self, n, env):
        subj = self._eval(n.subject, env)
        for vn, body in n.when_clauses:
            if subj == self._eval(vn, env):
                self._exec_block(body, Env(env)); return
        if n.otherwise_body: self._exec_block(n.otherwise_body, Env(env))

    def _exec_for_range(self, n, env):
        start = int(self._eval(n.start, env)); stop = int(self._eval(n.stop, env))
        step = int(self._eval(n.step, env)) if n.step else 1
        try:
            for i in range(start, stop + 1, step):
                child = Env(env); child.define(n.var, i)
                try: self._exec_block(n.body, child)
                except ContinueSignal: pass
        except BreakSignal: pass

    def _exec_for_each(self, n, env):
        it = self._eval(n.iterable, env)
        if isinstance(it, NovaEnum): it = list(it.members.values())
        try:
            for item in it:
                child = Env(env); child.define(n.var, item)
                try: self._exec_block(n.body, child)
                except ContinueSignal: pass
        except BreakSignal: pass
        except TypeError: raise NovaError(f"[Line {n.line}] TypeError: not iterable")

    def _exec_keep(self, n, env):
        child = Env(env); child.define(n.var, self._eval(n.init, env))
        try:
            while self._truthy(self._eval(n.condition, child)):
                try: self._exec_block(n.body, child)
                except ContinueSignal: pass
        except BreakSignal: pass

    def _exec_classdef(self, n, env):
        superclass = None
        if n.superclass:
            superclass = env.get(n.superclass, n.line)
            if not isinstance(superclass, NovaClass):
                raise NovaError(f"[Line {n.line}] '{n.superclass}' is not a class")
        methods = {}; getters = {}; setters = {}
        static_fields = {}; instance_defaults = {}
        if superclass:
            instance_defaults.update(superclass.instance_defaults)
            static_fields.update(superclass.static_fields)
        for member in n.body:
            t = type(member)
            if t == MethodDef:
                if member.is_static:
                    fn = NovaFunction(member.name, member.params, None, member.body, env)
                    static_fields[member.name] = fn
                elif member.kind == "get":
                    getters[member.name] = NovaFunction(member.name, member.params, None, member.body, env)
                elif member.kind == "set":
                    setters[member.name] = NovaFunction(member.name, member.params, None, member.body, env)
                else:
                    methods[member.name] = NovaFunction(member.name, member.params, None, member.body, env)
            elif t == FieldDecl:
                val = self._eval(member.value, env) if member.value else None
                if member.visibility == "static": static_fields[member.name] = val
                else: instance_defaults[member.name] = val
        klass = NovaClass(n.name, superclass, methods, getters, setters, static_fields, instance_defaults)
        env.define(n.name, klass)

    def _exec_enumdef(self, n, env):
        members = {}; auto_val = 0
        for mname, mval_node in n.members:
            val = self._eval(mval_node, env) if mval_node else auto_val
            auto_val = (val if isinstance(val, int) else auto_val) + 1
            members[mname] = NovaEnumMember(mname, val, None)
        enum = NovaEnum(n.name, members)
        for m in members.values(): m.enum_class = enum
        enum.values = lambda: list(members.values())
        enum.count = lambda: len(members)
        enum.has = lambda name: name in members
        enum.fromName = lambda name: members.get(name)
        enum.fromValue = lambda val: next((m for m in members.values() if m.value == val), None)
        env.define(n.name, enum)

    def _exec_try(self, n, env):
        try:
            self._exec_block(n.try_body, Env(env))
        except NovaThrown as thrown:
            self._handle_catch(thrown.val, str(thrown.val), n.catch_clauses, env, n.line)
        except NovaError as e:
            self._handle_catch(str(e), str(e), n.catch_clauses, env, n.line)
        except Exception as e:
            self._handle_catch(str(e), str(e), n.catch_clauses, env, n.line)
        finally:
            if n.finally_body: self._exec_block(n.finally_body, Env(env))

    def _handle_catch(self, val, msg, clauses, env, line):
        if not clauses: return
        for type_name, var, body in clauses:
            matched = False
            if type_name is None:
                matched = True
            elif isinstance(val, NovaBuiltinError) and val.kind == type_name:
                matched = True
            elif type_name and str(type_name) in str(type(val).__name__):
                matched = True
            elif type_name is None:
                matched = True
            if matched:
                child = Env(env)
                if var: child.define(var, val)
                self._exec_block(body, child); return
        raise NovaError(msg)

    def _exec_assert(self, n, env):
        cond = self._eval(n.condition, env)
        if not self._truthy(cond):
            msg = self._eval(n.message, env) if n.message else "Assertion failed"
            raise NovaThrown(NovaBuiltinError("AssertionError", str(msg)))

    def _exec_swap(self, n, env):
        a = env.get(n.a, n.line); b = env.get(n.b, n.line)
        env.set(n.a, b, n.line); env.set(n.b, a, n.line)

    def _exec_reverse(self, n, env):
        val = env.get(n.name, n.line)
        if isinstance(val, list): val.reverse()
        elif isinstance(val, (str, tuple)): env.set(n.name, val[::-1], n.line)
        else: raise NovaError(f"[Line {n.line}] Cannot reverse {type(val).__name__}")

    def _exec_import(self, n, env):
        mod_name = n.module
        alias_name = getattr(n, "alias", None)
        target_name = alias_name if alias_name else mod_name.split(".")[-1]
        mod = self.modules.get(mod_name) or loadLib(mod_name, self)
        if mod is not None:
            self.modules[mod_name] = mod
            if n.names:
                for nm in n.names:
                    if hasattr(mod, nm): env.define(nm, getattr(mod, nm))
                    else: raise NovaError(f"[Line {n.line}] Cannot import '{nm}' from built-in module '{mod_name}'")
            else:
                env.define(target_name, mod)
            return

        try:
            mod = importlib.import_module(mod_name)
            if n.names:
                for nm in n.names:
                    obj = getattr(mod, nm, None)
                    if obj is None: raise NovaError(f"Cannot import '{nm}' from '{mod_name}'")
                    env.define(nm, obj)
            else: env.define(target_name, mod)
        except ImportError as e:
            raise NovaError(f"[Line {n.line}] ImportError: {e}")

    # ── Evaluation ──────────────────────────────────────────
    def _eval(self, node, env):
        t = type(node)
        if t == Literal:    return node.value
        if t == Var:        return self._eval_var(node, env)
        if t == BinOp:      return self._eval_binop(node, env)
        if t == UnaryOp:
            v = self._eval(node.operand, env)
            if node.op == "-": return -v
            if node.op == "not": return not self._truthy(v)
        if t == ListLit:    return [self._eval(e, env) for e in node.elements]
        if t == SetLit:     return set(self._eval(e, env) for e in node.elements)
        if t == TupleLit:   return tuple(self._eval(e, env) for e in node.elements)
        if t == MapLit:
            result = {}
            for kn, vn in node.pairs:
                try: k = self._eval(kn, env)
                except NovaError:
                    if isinstance(kn, Var): k = kn.name
                    else: raise
                v = self._eval(vn, env)
                if isinstance(k, _KProxy) and isinstance(v, _VProxy):
                    for ki, vi in zip(k.data, v.data): result[ki] = vi
                else: result[k] = v
            return result
        if t == Index:
            obj = self._eval(node.obj, env); idx = self._eval(node.index, env)
            try:
                if isinstance(obj, dict):
                    return obj[idx]
                if isinstance(obj, (list, str, tuple)):
                    return obj[int(idx)]
                if hasattr(obj, "__getitem__"):
                    return obj[idx]
                return obj[int(idx)]
            except (KeyError, IndexError) as e:
                raise NovaError(f"[Line {node.line}] IndexError: {e}")
        if t == Slice:
            obj = self._eval(node.obj, env)
            if node.reverse: return obj[::-1]
            s = int(self._eval(node.start, env)) if node.start else None
            e = int(self._eval(node.stop, env))  if node.stop  else None
            p = int(self._eval(node.step, env))  if node.step  else None
            return obj[slice(s, e, p)]
        if t == Attr:       return self._eval_attr(node, env)
        if t == MethodCall: return self._eval_method(node, env)
        if t == Call:       return self._eval_call(node, env)
        if t == InputExpr:
            prompt = self._eval(node.prompt, env) if node.prompt else ""
            return input(str(prompt))
        if t == Interpolated: return self._eval_interp(node, env)
        if t == Lambda:       return NovaLambda(node.params, node.body, env)
        if t == ListComp:     return self._eval_listcomp(node, env)
        if t == SetComp:      return self._eval_setcomp(node, env)
        if t == SuperCall:    return self._eval_super(node, env)
        raise NovaError(f"[Line {node.line}] Unknown expr type: {t.__name__}")

    def _eval_var(self, node, env):
        return env.get(node.name, node.line)

    def _eval_binop(self, n, env):
        op = n.op; line = n.line
        if op == "and":
            l = self._eval(n.left, env); return l if not self._truthy(l) else self._eval(n.right, env)
        if op == "or":
            l = self._eval(n.left, env); return l if self._truthy(l) else self._eval(n.right, env)
        l = self._eval(n.left, env); r = self._eval(n.right, env)
        if isinstance(l, set) and isinstance(r, set):
            if op == "|": return l | r
            if op == "&": return l & r
            if op == "-": return l - r
            if op == "^": return l ^ r
        try:
            if op == "+":  return l + r
            if op == "-":  return l - r
            if op == "*":  return l * r
            if op == "/":  return l / r
            if op == "//": return l // r
            if op == "%":  return l % r
            if op == "**": return l ** r
            if op == "==": return l == r
            if op == "!=": return l != r
            if op == "<":  return l < r
            if op == ">":  return l > r
            if op == "<=": return l <= r
            if op == ">=": return l >= r
            if op == "|":  return l | r
            if op == "&":  return l & r
            if op == "^":  return l ^ r
        except ZeroDivisionError:
            raise NovaError(f"[Line {line}] ZeroDivisionError")
        except TypeError as e:
            raise NovaError(f"[Line {line}] TypeError: {e}")
        raise NovaError(f"[Line {line}] Unknown op: {op}")

    def _eval_attr(self, node, env):
        obj = self._eval(node.obj, env); nm = node.name; line = node.line
        _PROPS = {
            "size", "upper", "lower", "title", "cap", "swap", "trim", "trimL", "trimR", "trimAll",
            "int", "float", "string", "bool", "list", "set", "tuple", "map",
            "first", "last", "keys", "values", "items", "len", "length",
            "sum", "avg", "max", "min", "prod", "unique", "flat", "reverse", "reversed",
            "isEmpty", "isUpper", "isLower", "isTitle", "isDigit", "isLetter", "isAlNum", "isSpace",
            "wordC", "toList", "toSet", "toMap", "toStr", "copy", "now", "date", "time",
            "year", "month", "day", "hour", "min", "sec", "milli", "stamp", "stampM", "today", "tomorrow", "yesterday",
            "status", "text", "ok", "url", "headers"
        }
        if isinstance(obj, NovaInstance):
            klass = obj.klass
            getter = self._resolve_getter(klass, nm)
            if getter: return self._call_method(getter, obj, [], line, env)
            if nm in obj.fields: return obj.fields[nm]
            meth = self._resolve_method(klass, nm)
            if meth: return BoundMethod(meth, obj, self)
            raise NovaError(f"[Line {line}] '{klass.name}' has no attr '{nm}'")
        if isinstance(obj, NovaClass):
            if nm in obj.static_fields: return obj.static_fields[nm]
            raise NovaError(f"[Line {line}] Class '{obj.name}' has no static attr '{nm}'")
        if isinstance(obj, NovaEnum):
            if nm in obj.members: return obj.members[nm]
            if hasattr(obj, nm): return getattr(obj, nm)
            raise NovaError(f"[Line {line}] Enum '{obj.name}' has no member '{nm}'")
        if isinstance(obj, NovaEnumMember):
            if nm == "name":  return obj.name
            if nm == "value": return obj.value
        if isinstance(obj, StdModule) or hasattr(obj, "_exports"):
            if hasattr(obj, nm): return getattr(obj, nm)
            raise NovaError(f"[Line {line}] Module '{getattr(obj, '_name', 'unknown')}' has no attribute '{nm}'")
        if isinstance(obj, (NovaHttpResponse, NovaRequest, NovaResponse, NovaUIElement, NovaArray, NumpyArray, NovaDF, NovaGroupedDF, ChartFigure, VizFigure)) or hasattr(obj, nm):
            if hasattr(obj, nm):
                val = getattr(obj, nm)
                if not callable(val):
                    return val
        if isinstance(obj, NovaDB):
            if hasattr(obj, nm): return getattr(obj, nm)
        if isinstance(obj, dict) and nm in obj:
            return obj[nm]
        if nm in _PROPS:
            mc = MethodCall(node.obj, nm, [], line=line); return self._eval_method(mc, env)
        try: return getattr(obj, nm)
        except AttributeError:
            if isinstance(obj, dict): return None
            raise NovaError(f"[Line {line}] AttributeError: no attr '{nm}'")

    def _eval_interp(self, node, env):
        parts = []
        for part, is_expr in node.parts:
            if is_expr: parts.append(self._display(self._eval(part, env)))
            else: parts.append(part)
        return "".join(parts)

    def _eval_listcomp(self, node, env):
        it = self._eval(node.iterable, env); result = []
        if isinstance(it, NovaEnum): it = list(it.members.values())
        for item in it:
            child = Env(env); child.define(node.var, item)
            if node.condition and not self._truthy(self._eval(node.condition, child)): continue
            result.append(self._eval(node.expr, child))
        return result

    def _eval_setcomp(self, node, env):
        it = self._eval(node.iterable, env); result = set()
        if isinstance(it, NovaEnum): it = list(it.members.values())
        for item in it:
            child = Env(env); child.define(node.var, item)
            if node.condition and not self._truthy(self._eval(node.condition, child)): continue
            result.add(self._eval(node.expr, child))
        return result

    def _eval_super(self, node, env):
        line = node.line
        this = env.get("this", line)
        if not isinstance(this, NovaInstance):
            raise NovaError(f"[Line {line}] 'super' used outside class method")
        klass = this.klass.superclass
        if not klass: raise NovaError(f"[Line {line}] Class has no superclass")
        meth = self._resolve_method(klass, node.method)
        if not meth: raise NovaError(f"[Line {line}] Superclass has no method '{node.method}'")
        args = [self._eval(a, env) for a in node.args]
        return self._call_method(meth, this, args, line, env)

    def _resolve_method(self, klass, name):
        if klass is None: return None
        if name in klass.methods: return klass.methods[name]
        return self._resolve_method(klass.superclass, name)

    def _resolve_getter(self, klass, name):
        if klass is None: return None
        if name in klass.getters: return klass.getters[name]
        return self._resolve_getter(klass.superclass, name)

    def _resolve_setter(self, klass, name):
        if klass is None: return None
        if name in klass.setters: return klass.setters[name]
        return self._resolve_setter(klass.superclass, name)

    def _call_method(self, fn, this, args, line, env):
        if isinstance(fn, BoundMethod): return fn(*args)
        if isinstance(fn, NovaLambda):
            child = Env(fn.closure)
            for p, val in zip(fn.params, args): child.define(p, val)
            if isinstance(fn.body, list):
                try: self._exec_block(fn.body, child)
                except ReturnSignal as r: return r.value
                return None
            else:
                return self._eval(fn.body, child)
        child = Env(fn.closure)
        child.define("this", this)
        if this is not None and isinstance(this, NovaInstance):
            child.define(this.klass.name, this.klass)
        for (pn, pt), val in zip(fn.params, args):
            if pt: val = self._coerce(val, pt, line)
            child.define(pn, val)
        try: self._exec_block(fn.body, child)
        except ReturnSignal as r: return r.value
        return None

    def _eval_call(self, node, env):
        line = node.line; callee = self._eval(node.callee, env)
        args = [self._eval(a, env) for a in node.args]
        if isinstance(callee, NovaClass):
            return self._instantiate(callee, args, line, env)
        if isinstance(callee, NovaFunction):
            if len(args) != len(callee.params):
                raise NovaError(f"[Line {line}] {callee.name}() expects {len(callee.params)} args, got {len(args)}")
            child = Env(callee.closure)
            for (pn, pt), val in zip(callee.params, args):
                if pt: val = self._coerce(val, pt, line)
                child.define(pn, val)
            try: self._exec_block(callee.body, child)
            except ReturnSignal as r: return r.value
            return None
        if isinstance(callee, NovaLambda):
            child = Env(callee.closure)
            for p, val in zip(callee.params, args): child.define(p, val)
            if isinstance(callee.body, list):
                try: self._exec_block(callee.body, child)
                except ReturnSignal as r: return r.value
                return None
            else:
                return self._eval(callee.body, child)
        if isinstance(callee, BoundMethod): return callee(*args)
        if callable(callee):
            try: return callee(*args)
            except Exception as e: raise NovaError(f"[Line {line}] Error: {e}")
        raise NovaError(f"[Line {line}] '{callee!r}' is not callable")

    def _instantiate(self, klass, args, line, env):
        inst = NovaInstance(klass)
        init_meth = self._resolve_method(klass, "init")
        if init_meth:
            self._call_method(init_meth, inst, args, line, env)
        elif args:
            raise NovaError(f"[Line {line}] {klass.name} has no init but got {len(args)} args")
        return inst

    # ── Collection & Method eval (Comprehensive V1.6.1) ──────
    def _eval_method(self, node, env):
        line = node.line; obj = self._eval(node.obj, env)
        m = node.method; args = [self._eval(a, env) for a in node.args]

        # Instance method dispatch
        if isinstance(obj, NovaInstance):
            meth = self._resolve_method(obj.klass, m)
            if meth: return self._call_method(meth, obj, args, line, env)

        # Class static method dispatch
        if isinstance(obj, NovaClass):
            if m in obj.static_fields:
                fn = obj.static_fields[m]
                if isinstance(fn, NovaFunction):
                    return self._call_method(fn, None, args, line, env)
                elif callable(fn):
                    return fn(*args)
            raise NovaError(f"[Line {line}] Class '{obj.name}' has no static method '{m}'")

        # Enum methods
        if isinstance(obj, NovaEnum):
            if m == "values": return list(obj.members.values())
            if m == "count": return len(obj.members)
            if m == "has": return args[0] in obj.members if args else False
            if m == "fromName": return obj.members.get(str(args[0])) if args else None
            if m == "fromValue":
                v = args[0] if args else None
                return next((mem for mem in obj.members.values() if mem.value == v), None)

        # Module method call
        if isinstance(obj, StdModule) or hasattr(obj, "_exports"):
            if hasattr(obj, m):
                fn = getattr(obj, m)
                return fn(*args) if callable(fn) else fn
            raise NovaError(f"[Line {line}] Module '{getattr(obj, '_name', 'unknown')}' has no function '{m}'")

        # Fluent NovaFile / Response / Server / UI / DB / NovaArray / NovaDF / Chart / Viz / App / Mem / Game / Render / Physics methods
        if isinstance(obj, (NovaFile, NovaHttpResponse, NovaRequest, NovaResponse, NovaServerApp, NovaDB, NovaUIElement, NovaAsyncTask, NovaArray, NumpyArray, NovaDF, NovaGroupedDF, ChartFigure, VizFigure, NovaAppUnified, UIElement, ResponsiveManager, MemPool, RawMemBlock, RenderEntity, Sprite, Camera, Light, Mesh, Texture, Material, Shader, GameApp, GameEntity, GameScene, PhysicsBody, PhysicsWorld, Asset)):
            if hasattr(obj, m):
                fn = getattr(obj, m)
                return fn(*args) if callable(fn) else fn

        # Type conversions
        if m == "int":    return int(obj)
        if m == "float":  return float(obj)
        if m == "string": return str(obj)
        if m == "bool":   return bool(obj)
        if m == "list":
            if isinstance(obj, str): return [self._parse_val(x) for x in obj.split()]
            return list(obj)
        if m == "set":
            if isinstance(obj, str): return set(self._parse_val(x) for x in obj.split())
            return set(obj)
        if m == "tuple":
            if isinstance(obj, str): return tuple(self._parse_val(x) for x in obj.split())
            return tuple(obj)

        # ── STRING methods ────────────────────────────────────
        if isinstance(obj, str):
            sm = self.modules["string"]
            if hasattr(sm, m):
                fn = getattr(sm, m)
                if callable(fn): return fn(obj, *args)
            if m == "size" or m == "len": return len(obj)
            if m == "trim": return obj.strip()
            if m == "upper": return obj.upper()
            if m == "lower": return obj.lower()

        # ── LIST & TUPLE methods ──────────────────────────────
        if isinstance(obj, (list, tuple)):
            lm = self.modules["list"]
            lam = args[0] if args and isinstance(args[0], NovaLambda) else None
            def call_lam(fn, item):
                child = Env(fn.closure); child.define(fn.params[0], item)
                if isinstance(fn.body, list):
                    try: self._exec_block(fn.body, child)
                    except ReturnSignal as r: return r.value
                    return None
                return self._eval(fn.body, child)
            def call_lam2(fn, *items):
                child = Env(fn.closure)
                for p, v in zip(fn.params, items): child.define(p, v)
                if isinstance(fn.body, list):
                    try: self._exec_block(fn.body, child)
                    except ReturnSignal as r: return r.value
                    return None
                return self._eval(fn.body, child)

            if m == "size" or m == "len": return len(obj)
            if m == "unique": seen = []; [seen.append(x) for x in obj if x not in seen]; return seen
            if m == "freq":
                d = {}
                for x in obj: d[x] = d.get(x, 0) + 1
                return d
            if m == "sum": return sum(obj)
            if m == "avg": return sum(obj) / len(obj) if obj else 0
            if m == "max": return max(obj) if obj else None
            if m == "min": return min(obj) if obj else None
            if m == "prod": return math.prod(obj)
            if m == "flat":
                res = []
                for x in obj:
                    if isinstance(x, (list, tuple)): res.extend(x)
                    else: res.append(x)
                return res
            if m == "flatMap" and lam:
                res = []
                for x in obj:
                    r2 = call_lam(lam, x)
                    if isinstance(r2, (list, tuple)): res.extend(r2)
                    else: res.append(r2)
                return res
            if m == "chunk":
                n2 = int(args[0]) if args else 1
                return [list(obj)[i:i+n2] for i in range(0, len(obj), n2)]
            if m == "window":
                n2 = int(args[0]) if args else 2
                return [list(obj)[i:i+n2] for i in range(len(obj) - n2 + 1)]
            if m == "zip":
                other = args[0] if args else []
                return list(zip(obj, other))
            if m == "hasAll":  return all(x in obj for x in (args[0] if args else []))
            if m == "hasAny":  return any(x in obj for x in (args[0] if args else []))
            if m == "countIf" and lam: return sum(1 for x in obj if self._truthy(call_lam(lam, x)))
            if m == "find"    and lam: return next((x for x in obj if self._truthy(call_lam(lam, x))), None)
            if m == "findLast" and lam:
                r2 = None
                for x in obj:
                    if self._truthy(call_lam(lam, x)): r2 = x
                return r2
            if m == "findIndex" and lam:
                for i, x in enumerate(obj):
                    if self._truthy(call_lam(lam, x)): return i
                return -1
            if m == "findAll" and lam: return [x for x in obj if self._truthy(call_lam(lam, x))]
            if m == "every"   and lam: return all(self._truthy(call_lam(lam, x)) for x in obj)
            if m == "some"    and lam: return any(self._truthy(call_lam(lam, x)) for x in obj)
            if m == "filter"  and lam: return [x for x in obj if self._truthy(call_lam(lam, x))]
            if m == "map"     and lam: return [call_lam(lam, x) for x in obj]
            if m == "mapI"    and lam: return [call_lam2(lam, x, i) for i, x in enumerate(obj)]
            if m == "group"   and lam:
                d = {}
                for x in obj:
                    k = call_lam(lam, x)
                    if k not in d: d[k] = []
                    d[k].append(x)
                return d
            if m == "sort":
                if isinstance(obj, list): obj.sort(); return obj
                return sorted(obj)
            if m == "dsort":
                if isinstance(obj, list): obj.sort(reverse=True); return obj
                return sorted(obj, reverse=True)
            if m == "sorted":  return sorted(obj)
            if m == "dsorted": return sorted(obj, reverse=True)
            if m == "take":    return list(obj)[:int(args[0])] if args else list(obj)
            if m == "drop":    return list(obj)[int(args[0]):] if args else []
            if m == "first":   return obj[0] if obj else None
            if m == "last":    return obj[-1] if obj else None
            if m == "at":      return obj[int(args[0])] if args else None
            if m == "get":     return obj[int(args[0])] if args else None
            if m == "has":     return args[0] in obj if args else False
            if m == "index":   return list(obj).index(args[0]) if args and args[0] in obj else -1
            if m == "toList":  return list(obj)
            if m == "toSet":   return set(obj)
            if m == "add":
                if isinstance(obj, list): obj.append(args[0]); return obj
            if m == "remove":
                if isinstance(obj, list) and args and args[0] in obj: obj.remove(args[0]); return obj
            if hasattr(lm, m):
                fn = getattr(lm, m)
                if callable(fn): return fn(obj, *args)

        # ── SET methods ──────────────────────────────────────
        if isinstance(obj, set):
            sm = self.modules["set"]
            lam = args[0] if args and isinstance(args[0], NovaLambda) else None
            def call_lam(fn, item):
                child = Env(fn.closure); child.define(fn.params[0], item)
                return self._eval(fn.body, child)

            other = args[0] if args else set()
            if m == "U" or m == "union":      return obj | other
            if m == "N" or m == "intersect":  return obj & other
            if m == "diff" or m == "symDiff": return obj ^ other
            if m == "size" or m == "len":     return len(obj)
            if m == "has":                    return args[0] in obj if args else False
            if m == "isSub":                  return obj <= other
            if m == "isSuper":                return obj >= other
            if m == "isDisjoint":             return obj.isdisjoint(other)
            if m == "toList" or m == "toListS": return sorted(list(obj), key=str)
            if m == "sum":                    return sum(obj)
            if m == "filter" and lam:         return {x for x in obj if self._truthy(call_lam(lam, x))}
            if m == "map" and lam:            return {call_lam(lam, x) for x in obj}
            if m == "cart":                   return [(a, b) for a in obj for b in other]
            if hasattr(sm, m):
                fn = getattr(sm, m)
                if callable(fn): return fn(obj, *args)

        # ── MAP methods ──────────────────────────────────────
        if isinstance(obj, dict):
            jm = self.modules["json"]
            lam = args[0] if args and isinstance(args[0], NovaLambda) else None
            def call_lam2(fn, *items):
                child = Env(fn.closure)
                for p, v in zip(fn.params, items): child.define(p, v)
                return self._eval(fn.body, child)

            if m == "size" or m == "len": return len(obj)
            if m == "has": return args[0] in obj if args else False
            if m == "get":
                if len(args) >= 2: return obj.get(args[0], args[1])
                return obj.get(args[0])
            if m == "getPath": return jm.getPath(obj, args[0])
            if m == "setPath": return jm.setPath(obj, args[0], args[1])
            if m == "keys": return list(obj.keys())
            if m == "values": return list(obj.values())
            if m == "items": return list(obj.items())
            if m == "hasValue": return args[0] in obj.values() if args else False
            if m == "merge": return {**obj, **(args[0] if args else {})}
            if m == "invert": return {v: k for k, v in obj.items()}
            if m == "pick": return {k: obj[k] for k in (args[0] if args else []) if k in obj}
            if m == "omit": return {k: v for k, v in obj.items() if k not in (args[0] if args else [])}
            if m == "filter" and lam:
                return {k: v for k, v in obj.items() if self._truthy(call_lam2(lam, k, v))}
            if m == "mapValues" and lam:
                child = Env(lam.closure)
                return {k: (child.define(lam.params[0], v), self._eval(lam.body, child))[1] for k, v in obj.items()}
            if m == "mapKeys" and lam:
                child = Env(lam.closure)
                return {(child.define(lam.params[0], k), self._eval(lam.body, child))[1]: v for k, v in obj.items()}
            if m == "copy": return dict(obj)
            if m == "toList": return list(obj.items())

        try:
            fn = getattr(obj, m)
            if callable(fn):
                return fn(*args)
            elif not args:
                return fn
            raise NovaError(f"[Line {line}] '{type(obj).__name__}.{m}' is not callable")
        except AttributeError:
            raise NovaError(f"[Line {line}] '{type(obj).__name__}' has no method '{m}'")
        except Exception as e:
            if isinstance(e, (NovaError, NovaThrown)): raise
            raise NovaError(f"[Line {line}] Error in .{m}(): {e}")

    def _parse_val(self, s):
        s = s.strip()
        if s == "true": return True
        if s == "false": return False
        if s == "none": return None
        try: return int(s)
        except ValueError: pass
        try: return float(s)
        except ValueError: pass
        return s

    def _truthy(self, val):
        if val is None or val is False: return False
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, (str, list, dict, set, tuple)): return len(val) > 0
        return True


# ── Bound method helper ───────────────────────────────────────
class BoundMethod:
    def __init__(self, fn, instance, interp):
        self.fn = fn; self.instance = instance; self.interp = interp
    def __call__(self, *args):
        return self.interp._call_method(self.fn, self.instance, list(args), 0, None)
    def __repr__(self): return f"<bound method {self.fn.name}>"


# ============================================================
# ENTRY POINT
# ============================================================
BANNER = """  Nova V1.6.1 Full-Stack Platform & First UI  |  Type 'exit' to quit REPL"""


def run_file(path: str):
    if not os.path.exists(path):
        if os.path.exists(path + ".no"):
            path = path + ".no"
        elif os.path.exists(path + ".nova"):
            path = path + ".nova"
    try:
        with open(path, "r", encoding="utf-8") as f: source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr); sys.exit(1)
    try:
        tokens = Lexer(source).tokenize()
        tree = Parser(tokens).parse()
        Interpreter().run(tree)
    except (LexError, ParseError, NovaError) as e:
        print(f"\n{e}", file=sys.stderr); sys.exit(1)
    except NovaThrown as e:
        print(f"\nUncaught throw: {e.val}", file=sys.stderr); sys.exit(1)
    except ReturnSignal: pass


def run_repl():
    print(BANNER)
    interp = Interpreter(); env = interp.global_env; buf: List[str] = []
    while True:
        try: line_in = input("... " if buf else ">>> ")
        except (EOFError, KeyboardInterrupt): print("\nBye!"); break
        if line_in.strip() == "exit": print("Bye!"); break
        buf.append(line_in); source = "\n".join(buf)
        try: toks = Lexer(source + "\n").tokenize()
        except LexError: continue
        opens = sum(1 for t in toks if t.type == TT.KEYWORD
                  and t.value in ("if", "func", "def", "from", "each", "keep", "try", "choose", "class", "enum"))
        ends = sum(1 for t in toks if t.type == TT.KEYWORD and t.value == "end")
        if opens > ends: continue
        buf = []
        try:
            toks = Lexer(source).tokenize(); tree = Parser(toks).parse()
            for s in tree.body:
                if isinstance(s, ExprStmt):
                    r = interp._eval(s.expr, env)
                    if r is not None: print(interp._display(r))
                else: interp._exec(s, env)
        except ReturnSignal as r:
            if r.value is not None: print(interp._display(r.value))
        except NovaThrown as e: print(f"  Uncaught throw: {e.val}")
        except (LexError, ParseError, NovaError) as e: print(f"  {e}")


if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    if len(sys.argv) == 1: run_repl()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage: python nova_interpreter.py [file.no]")
        else: run_file(sys.argv[1])
    else:
        print("Usage: python nova_interpreter.py [file.no]", file=sys.stderr); sys.exit(1)
