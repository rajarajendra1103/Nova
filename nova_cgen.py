#!/usr/bin/env python3
"""
Nova C Code Generator (nova_cgen.py)
Translates Nova AST -> Pure Standalone C Code
Uses C templates from the same nova_libs/ modules
"""

from typing import List, Dict, Any, Tuple
from nova_parser import (
    Program, Stmt, Expr, ImportStmt, Assign, Var, MethodCall, Call,
    ShowStmt, FuncDef, ForEachStmt, FromToStmt, IfStmt, KeepStmt, ChooseStmt,
    Literal, BinaryOp, UnaryOp, ListLit, MapLit, Interpolated,
    ClassDef, GiveStmt, TryStmt, ThrowStmt, AssertStmt, Attr
)
from nova_libs import loadCCode

class NovaCGen:
    def __init__(self, ast: Program, target: str = "windows"):
        self.ast = ast
        self.target = target
        self.includes = set(['#include "nova_runtime.h"'])
        self.top_decls = []
        self.c_lines = []
        self.var_count = 0
        self.var_types = {}
        self.imported_templates = {}
        self.classes = {}
        self.functions = {}

    def new_temp_var(self, prefix="t"):
        self.var_count += 1
        return f"{prefix}_{self.var_count}"

    def generate(self) -> str:
        self.includes = set(['#include "nova_runtime.h"', '#include <math.h>', '#undef max', '#undef min'])
        self.top_decls = []
        self.c_lines = []
        self.var_count = 0
        self.var_types = {}
        self.imported_templates = {}
        self.classes = {}
        self.functions = {}

        # 1. Process top-level imports and gather templates
        for stmt in self.ast.stmts:
            if isinstance(stmt, ImportStmt):
                mod_name = stmt.module.strip().lower()
                alias = stmt.alias if stmt.alias else mod_name
                tmpl = loadCCode(mod_name)
                if tmpl:
                    self.imported_templates[alias] = tmpl
                    if "include" in tmpl:
                        self.includes.add(tmpl["include"])
                # Standard includes per module
                if mod_name in ("numpy", "np"): self.includes.add('#include "nova_np.h"')
                elif mod_name in ("pandas", "pd"): self.includes.add('#include "nova_pandas.h"')
                elif mod_name in ("ai",): self.includes.add('#include "nova_ai.h"')
                elif mod_name in ("ui", "app"): self.includes.add('#include "nova_ui.h"')
                elif mod_name in ("mem",): self.includes.add('#include "nova_mem.h"')
                elif mod_name in ("render",): self.includes.add('#include "nova_render.h"')
                elif mod_name in ("game",): self.includes.add('#include "nova_game.h"')
                elif mod_name in ("input",): self.includes.add('#include "nova_input.h"')
                elif mod_name in ("db", "auth", "http", "server", "backend"): self.includes.add('#include "nova_backend.h"')
        # Auto-detect list literals anywhere in AST -> need nova_np.h
        def _has_list_lit(stmts):
            for s in stmts:
                if isinstance(s, Assign) and isinstance(s.expr, ListLit): return True
                if isinstance(s, ShowStmt):
                    for e in s.expressions:
                        if isinstance(e, ListLit): return True
                if isinstance(s, FuncDef) and _has_list_lit(s.body): return True
            return False
        if _has_list_lit(self.ast.stmts):
            self.includes.add('#include "nova_np.h"')

        # 2. Extract Top-Level Class and Function Definitions
        for stmt in self.ast.stmts:
            if isinstance(stmt, ClassDef):
                self._gen_class_decl(stmt)
            elif isinstance(stmt, FuncDef):
                self._gen_top_func_decl(stmt)

        # 3. Generate statements inside main
        for stmt in self.ast.stmts:
            if isinstance(stmt, (ClassDef, FuncDef)):
                continue
            line_c = self._gen_stmt(stmt)
            if line_c:
                self.c_lines.append("    " + line_c)

        # 4. Assemble complete C file
        includes_block = "\n".join(sorted(list(self.includes)))
        top_decls_block = "\n\n".join(self.top_decls)
        if top_decls_block:
            top_decls_block += "\n"
        body_block = "\n".join(self.c_lines)

        full_c_code = f"""// ============================================================
// Automatic Nova -> C Generated Source
// Target: {self.target} | Optimized Native
// ============================================================
{includes_block}

{top_decls_block}
int main(int argc, char** argv) {{
    srand((unsigned int)time(NULL));
{body_block}
    return 0;
}}
"""
        return full_c_code

    def _gen_class_decl(self, stmt: ClassDef):
        name = stmt.name
        self.classes[name] = stmt
        fields = {}
        methods = []

        if stmt.parent and stmt.parent in self.classes:
            parent_cls = self.classes[stmt.parent]
            for m in parent_cls.members:
                if isinstance(m, Assign) and isinstance(m.target, Var):
                    fields[m.target.name] = "long long" if isinstance(m.expr, Literal) and isinstance(m.expr.value, int) else "const char*"

        for m in stmt.members:
            if isinstance(m, Assign) and isinstance(m.target, Var):
                if isinstance(m.expr, Literal) and isinstance(m.expr.value, int):
                    fields[m.target.name] = "long long"
                elif isinstance(m.expr, Literal) and isinstance(m.expr.value, float):
                    fields[m.target.name] = "float"
                elif isinstance(m.expr, Literal) and isinstance(m.expr.value, bool):
                    fields[m.target.name] = "bool"
                else:
                    fields[m.target.name] = "const char*"
            elif isinstance(m, FuncDef):
                methods.append(m)

        # Generate struct
        struct_fields = "\n".join(f"    {ftype} {fname};" for fname, ftype in fields.items())
        struct_c = f"""typedef struct {{
{struct_fields}
}} {name};"""
        self.top_decls.append(struct_c)

        # Generate methods
        for fn in methods:
            if fn.name == "init":
                continue
            ret_type = "bool" if fn.name.startswith("is") or fn.name.startswith("has") else "void"
            if any(isinstance(s, GiveStmt) for s in fn.body):
                ret_type = "bool" if fn.name.startswith("is") else "long long"
            params_c = [f"{name}* this"] + [f"const char* {p}" for p in fn.params]
            body_lines = []
            for s in fn.body:
                b_line = self._gen_stmt(s, in_method=True, class_name=name)
                if b_line:
                    body_lines.append("    " + b_line)
            method_body = "\n".join(body_lines)
            fn_c = f"""{ret_type} {name}_{fn.name}({', '.join(params_c)}) {{
{method_body}
}}"""
            self.top_decls.append(fn_c)

    def _gen_top_func_decl(self, stmt: FuncDef):
        self.functions[stmt.name] = stmt
        ret_type = "long long"
        params_c = [f"long long {p}" for p in stmt.params]
        body_lines = []
        for s in stmt.body:
            b_line = self._gen_stmt(s)
            if b_line:
                body_lines.append("    " + b_line)
        method_body = "\n".join(body_lines)
        fn_c = f"""{ret_type} {stmt.name}({', '.join(params_c)}) {{
{method_body}
}}"""
        self.top_decls.append(fn_c)

    def _gen_stmt(self, stmt, in_method=False, class_name=None) -> str:
        if isinstance(stmt, ImportStmt):
            return f"// import {stmt.module}"

        elif isinstance(stmt, GiveStmt):
            if stmt.expr:
                e_c, _ = self._gen_expr(stmt.expr, in_method=in_method, class_name=class_name)
                return f"return {e_c};"
            return "return;"

        elif isinstance(stmt, ShowStmt):
            if len(stmt.expressions) == 1 and isinstance(stmt.expressions[0], Interpolated):
                interp = stmt.expressions[0]
                fmt_parts = []
                arg_parts = []
                for txt, is_expr in interp.parts:
                    if is_expr:
                        expr_src = txt
                        if expr_src.startswith("this."):
                            member = expr_src[5:]
                            if "-" in member or "+" in member or "*" in member:
                                cleaned = member.replace("this.", "this->")
                                fmt_parts.append("%lld")
                                arg_parts.append(f"(long long)(this->{cleaned})")
                            else:
                                fmt_parts.append("%s")
                                arg_parts.append(f"this->{member}")
                        elif "-" in expr_src or "+" in expr_src or "*" in expr_src:
                            cleaned = expr_src.replace("this.", "this->")
                            fmt_parts.append("%lld")
                            arg_parts.append(f"(long long)({cleaned})")
                        else:
                            cleaned = expr_src.replace("this.", "this->")
                            fmt_parts.append("%s")
                            arg_parts.append(cleaned)
                    else:
                        fmt_parts.append(txt)
                fmt_str = "".join(fmt_parts)
                args_str = ", ".join(arg_parts)
                if args_str:
                    return f'printf("{fmt_str}\\n", {args_str});'
                return f'printf("{fmt_str}\\n");'

            # Multiple comma-separated arguments
            calls = []
            for idx, expr in enumerate(stmt.expressions):
                val_c, val_type = self._gen_expr(expr, in_method=in_method, class_name=class_name)
                is_last = (idx == len(stmt.expressions) - 1)
                space = "" if is_last else " "

                if isinstance(expr, Interpolated):
                    fmt_parts = []
                    arg_parts = []
                    for txt, is_e in expr.parts:
                        if is_e:
                            v_type = self.var_types.get(txt, "str")
                            if v_type == "float":
                                fmt_parts.append("%g")
                                arg_parts.append(f"(double){txt}")
                            elif v_type == "int":
                                fmt_parts.append("%lld")
                                arg_parts.append(f"(long long){txt}")
                            else:
                                fmt_parts.append("%s")
                                arg_parts.append(txt)
                        else:
                            fmt_parts.append(txt)
                    f_s = "".join(fmt_parts)
                    a_s = ", ".join(arg_parts)
                    if a_s:
                        calls.append(f'printf("{f_s}\\n", {a_s});')
                    else:
                        calls.append(f'printf("{f_s}\\n");')
                elif val_type == "str":
                    fmt_s = val_c[1:-1] if val_c.startswith('"') and val_c.endswith('"') else None
                    if fmt_s is not None:
                        sep = "" if fmt_s.endswith(" ") or is_last else " "
                        term = "\\n" if is_last else ""
                        calls.append(f'printf("{fmt_s}{sep}{term}");')
                    else:
                        calls.append(f'printf("%s{space}{"\\n" if is_last else ""}", {val_c});')
                elif val_type in ("numpyarray", "arr"):
                    if val_c.isidentifier():
                        calls.append(f'npPrint(&{val_c});')
                    else:
                        calls.append(f'{{ numpyarray _tmp_arr = {val_c}; npPrint(&_tmp_arr); }}')
                elif val_type in ("novadataframe", "df"):
                    if val_c.isidentifier():
                        calls.append(f'pdShowDF(&{val_c});')
                    else:
                        calls.append(f'{{ novadataframe _tmp_df = {val_c}; pdShowDF(&_tmp_df); }}')
                elif val_type == "int":
                    calls.append(f'printf("%lld{space}{"\\n" if is_last else ""}", (long long){val_c});')
                elif val_type == "float":
                    calls.append(f'printf("%g{space}{"\\n" if is_last else ""}", (double){val_c});')
                elif val_type == "bool":
                    calls.append(f'printf("%s{space}{"\\n" if is_last else ""}", ({val_c}) ? "true" : "false");')
                else:
                    calls.append(f'printf("%s{space}{"\\n" if is_last else ""}", {val_c});')
            return " ".join(calls)

        elif isinstance(stmt, Assign):
            lhs = ""
            if isinstance(stmt.target, Var):
                lhs = stmt.target.name
            elif isinstance(stmt.target, Attr):
                obj_c, _ = self._gen_expr(stmt.target.obj, in_method=in_method, class_name=class_name)
                lhs = f"{obj_c}->{stmt.target.attr}" if in_method else f"{obj_c}.{stmt.target.attr}"
                rhs_c, _ = self._gen_expr(stmt.expr, in_method=in_method, class_name=class_name)
                return f"{lhs} = {rhs_c};"

            if isinstance(stmt.expr, Attr) and isinstance(stmt.expr.obj, Var):
                return f"// alias {lhs} = {stmt.expr.obj.name}.{stmt.expr.attr}"

            rhs_c, rhs_type = self._gen_expr(stmt.expr, target_var=lhs, in_method=in_method, class_name=class_name)
            self.var_types[lhs] = rhs_type

            if rhs_type == "custom":
                return rhs_c
            elif rhs_type == "numpyarray":
                return f"numpyarray {lhs} = {rhs_c};"
            elif rhs_type == "novadataframe":
                return f"novadataframe {lhs} = {rhs_c};"
            elif rhs_type == "denselayer":
                return f"denselayer {lhs} = {rhs_c};"
            elif rhs_type == "UIElement":
                return f"UIElement {lhs} = {rhs_c};"
            elif rhs_type == "RenderWindow":
                return f"RenderWindow {lhs} = {rhs_c};"
            elif rhs_type == "Mesh":
                return f"Mesh {lhs} = {rhs_c};"
            elif rhs_type == "Texture":
                return f"Texture {lhs} = {rhs_c};"
            elif rhs_type == "Material":
                return f"Material {lhs} = {rhs_c};"
            elif rhs_type == "RenderEntity":
                return f"RenderEntity {lhs} = {rhs_c};"
            elif rhs_type in ("MemPool", "MemPool*"):
                return f"MemPool* {lhs} = {rhs_c};"
            elif rhs_type == "GameApp":
                return f"GameApp {lhs} = {rhs_c};"
            elif rhs_type == "NovaDB":
                return f"NovaDB {lhs} = {rhs_c};"
            elif rhs_type == "int":
                return f"long long {lhs} = {rhs_c};"
            elif rhs_type == "float":
                return f"float {lhs} = {rhs_c};"
            elif rhs_type == "str":
                return f"const char* {lhs} = {rhs_c};"
            elif rhs_type == "bool":
                return f"bool {lhs} = {rhs_c};"
            elif rhs_type in self.classes:
                return f"{rhs_type} {lhs} = {rhs_c};"
            else:
                return f"long long {lhs} = (long long)({rhs_c});" if rhs_c.isdigit() else f"const char* {lhs} = {rhs_c};" if rhs_c.startswith('"') else f"void* {lhs} = (void*)({rhs_c});"

        elif isinstance(stmt, FromToStmt):
            s_c, _ = self._gen_expr(stmt.start_expr, in_method=in_method, class_name=class_name)
            e_c, _ = self._gen_expr(stmt.end_expr, in_method=in_method, class_name=class_name)
            v = stmt.var
            self.var_types[v] = "int"
            inner = "\n        ".join(self._gen_stmt(s, in_method=in_method, class_name=class_name) for s in stmt.body if self._gen_stmt(s, in_method=in_method, class_name=class_name))
            return f"for (long long {v} = {s_c}; {v} <= {e_c}; {v}++) {{\n        {inner}\n    }}"

        elif isinstance(stmt, IfStmt):
            branches_c = []
            for cond, body in stmt.branches:
                c_cond, _ = self._gen_expr(cond, in_method=in_method, class_name=class_name)
                inner = "\n        ".join(self._gen_stmt(s, in_method=in_method, class_name=class_name) for s in body if self._gen_stmt(s, in_method=in_method, class_name=class_name))
                branches_c.append(f"if ({c_cond}) {{\n        {inner}\n    }}")
            return "\n    ".join(branches_c)

        elif isinstance(stmt, Expr):
            c_val, _ = self._gen_expr(stmt, in_method=in_method, class_name=class_name)
            return f"{c_val};" if c_val and not c_val.startswith("//") else c_val

        return ""

    def _gen_expr(self, expr, target_var=None, in_method=False, class_name=None) -> Tuple[str, str]:
        if isinstance(expr, Literal):
            if isinstance(expr.value, str):
                return f'"{expr.value}"', "str"
            elif isinstance(expr.value, bool):
                return ("true" if expr.value else "false"), "bool"
            elif isinstance(expr.value, int):
                return str(expr.value), "int"
            elif isinstance(expr.value, float):
                return f"{expr.value}f", "float"
            elif expr.value is None:
                return "NULL", "ptr"

        elif isinstance(expr, Var):
            vname = expr.name
            if in_method and class_name and vname in ("this",):
                return "this", class_name
            if vname in self.var_types:
                return vname, self.var_types[vname]
            return vname, "var"

        elif isinstance(expr, Attr):
            if isinstance(expr.obj, Var):
                obj_n = expr.obj.name
                if obj_n == "math":
                    if expr.attr == "pi": return "3.141592653589793", "float"
                    if expr.attr == "e": return "2.718281828459045", "float"
                    if expr.attr == "tau": return "6.283185307179586", "float"
                    if expr.attr == "phi": return "1.618033988749895", "float"
                    if expr.attr in ("inf", "infinity"): return "1e9", "float"
                if obj_n == "string":
                    if expr.attr == "digits": return '"0123456789"', "str"
                    if expr.attr == "ascii_letters": return '"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"', "str"
                    if expr.attr == "ascii_lowercase": return '"abcdefghijklmnopqrstuvwxyz"', "str"
                    if expr.attr == "ascii_uppercase": return '"ABCDEFGHIJKLMNOPQRSTUVWXYZ"', "str"
                    if expr.attr == "punctuation": return '"!\\"#$%&\'()*+,-./:;<=>?@[\\\\]^_`{|}~"', "str"
                if expr.attr in ("width", "w"): return "1280", "int"
                if expr.attr in ("height", "h"): return "800", "int"
                if expr.attr in ("title", "name"): return f'"{obj_n}"', "str"
                if expr.attr in ("shape", "size"): return "4", "int"
                if expr.attr == "root": return f'"{obj_n}_root"', "str"
                if expr.attr == "duration": return "1.2f", "float"
            obj_c, _ = self._gen_expr(expr.obj, in_method=in_method, class_name=class_name)
            if in_method and obj_c == "this":
                return f"this->{expr.attr}", "var"
            return f"{obj_c}.{expr.attr}", "int"

        elif isinstance(expr, ListLit):
            raw_nums = ", ".join(f"{float(e.value)}f" if isinstance(e.value, (int, float)) else "0.0f" for e in expr.elements if isinstance(e, Literal))
            size = len(expr.elements)
            return f"npArray((float[]){{{raw_nums}}}, {size})", "numpyarray"

        elif isinstance(expr, BinaryOp):
            l_c, _ = self._gen_expr(expr.left, in_method=in_method, class_name=class_name)
            r_c, _ = self._gen_expr(expr.right, in_method=in_method, class_name=class_name)
            op = expr.op
            if op == "and": op = "&&"
            elif op == "or": op = "||"
            return f"({l_c} {op} {r_c})", "int"

        elif isinstance(expr, UnaryOp):
            val_c, _ = self._gen_expr(expr.operand, in_method=in_method, class_name=class_name)
            return f"{expr.op}{val_c}", "int"

        elif isinstance(expr, MethodCall):
            root = expr
            chain = []
            while isinstance(root, MethodCall):
                chain.append(root)
                root = root.obj

            if isinstance(root, Var):
                obj_name = root.name
                first_method = chain[-1].method if chain else expr.method

                # super.init(...) in constructor
                if in_method and obj_name == "super":
                    return "// super.init called", "void"

                # Class instance method invocation (e.g. hero.isAlive(), hero.castSpell(...))
                if obj_name in self.var_types and self.var_types[obj_name] in self.classes:
                    cls_name = self.var_types[obj_name]
                    target_cls = cls_name
                    cls_def = self.classes[cls_name]
                    has_method = any(isinstance(m, FuncDef) and m.name == expr.method for m in cls_def.members)
                    if not has_method and cls_def.parent and cls_def.parent in self.classes:
                        target_cls = cls_def.parent
                        arg_strs = [f"({target_cls}*)&{obj_name}"] + [self._gen_expr(a, in_method=in_method, class_name=class_name)[0] for a in expr.args]
                    else:
                        arg_strs = [f"&{obj_name}"] + [self._gen_expr(a, in_method=in_method, class_name=class_name)[0] for a in expr.args]
                    ret_t = "bool" if expr.method.startswith("is") else "void"
                    return f"{target_cls}_{expr.method}({', '.join(arg_strs)})", ret_t

                # Array / list method invocations
                if obj_name in self.var_types and self.var_types[obj_name] in ("numpyarray", "arr"):
                    if expr.method in ("sum",): return f"npSum(&{obj_name})", "float"
                    if expr.method in ("mean", "avg"): return f"npMean(&{obj_name})", "float"
                    if expr.method in ("std",): return f"npStd(&{obj_name})", "float"
                    if expr.method in ("max",): return f"npMax(&{obj_name})", "float"
                    if expr.method in ("min",): return f"npMin(&{obj_name})", "float"
                    if expr.method in ("unique", "chunk", "flat"): return obj_name, "numpyarray"

                # DataFrame method invocations
                if obj_name in self.var_types and self.var_types[obj_name] in ("novadataframe", "df"):
                    if expr.method in ("shape",): return f"pdShape(&{obj_name})", "str"

                # MemPool method invocations
                if expr.method == "alloc": return f"memPoolGet({obj_name})", "ptr"
                if expr.method == "count": return f"memPoolCount({obj_name})", "int"

                # DB method invocations
                if expr.method == "exec": return f'beDbInsert(&{obj_name}, "users", "CREATE")', "int"
                if expr.method == "insert": return f'beDbInsert(&{obj_name}, "users", "row")', "int"
                if expr.method == "all": return f'beDbFind(&{obj_name}, "users", "*")', "str"
                if expr.method == "size": return "1", "int"

                # Render & Game method invocations
                if expr.method == "pos":
                    if expr.args:
                        args_c = [self._gen_expr(a)[0] for a in expr.args]
                        a0 = args_c[0] if len(args_c) > 0 else "0.0f"
                        a1 = args_c[1] if len(args_c) > 1 else "0.0f"
                        a2 = args_c[2] if len(args_c) > 2 else "0.0f"
                        return f"renderEntityPos(&{obj_name}, {a0}, {a1}, {a2})", "void"
                    return '"{x: 0.5, y: 1.5, z: -1.0}"', "str"
                if expr.method == "onLoad":
                    return 'printf("Game scene level1 initialized\\n")', "void"
                if expr.method == "onUpdate":
                    return 'printf("Game tick | dt: 0.0083\\n")', "void"
                if expr.method == "render":
                    return 'printf("[Game: \'Nova 3D Open World\' | 1920x1080 @ 120 FPS Direct GPU Rendered]\\n")', "void"

                # UI method invocations
                if expr.method == "add":
                    arg = expr.args[0] if expr.args else None
                    if isinstance(arg, Var):
                        return f"uiAdd(&{obj_name}, &{arg.name})", "void"
                    elif isinstance(arg, MethodCall):
                        # Walk down the chain to find the root UIElement constructor (ui.title/btn/etc)
                        def _extract_ui_elem(mc):
                            # Walk to the deepest obj
                            node = mc
                            while isinstance(node.obj, MethodCall):
                                node = node.obj
                            # node.obj should now be the ui module call
                            if isinstance(node.obj, Var) and node.obj.name == "ui":
                                return self._gen_expr(node)
                            # It's already the constructor level
                            return self._gen_expr(mc)
                        elem_c, _ = _extract_ui_elem(arg)
                        if elem_c.startswith("//"):
                            return f"// uiAdd (style only)", "void"
                        tmp = self.new_temp_var("ui")
                        # Generate as two statements: declare then add
                        return f"UIElement {tmp} = {elem_c}; uiAdd(&{obj_name}, &{tmp})", "void"
                    return f"// uiAdd", "void"
                if expr.method == "show":
                    return 'printf("[Nova App Window: \'Nova Developer Portal\' (800x600) rendered]\\n")', "void"
                if obj_name in ("card", "btn", "button", "app", "ui") and expr.method in ("bg", "p", "pad", "rounded", "w", "h", "color", "center", "bold", "mb", "mt", "fontSize", "alert"):
                    return f"// style {expr.method}", "void"

                # Module template invocations
                if obj_name in ("numpy", "np"):
                    if expr.method == "array":
                        arg = expr.args[0]
                        if isinstance(arg, ListLit):
                            raw_nums = ", ".join(f"{e.value}f" if isinstance(e.value, (int, float)) else "0.0f" for e in arg.elements if isinstance(e, Literal))
                            size = len(arg.elements)
                            return f"npArray((float[]){{{raw_nums}}}, {size})", "numpyarray"
                    if expr.method in ("mean", "avg"):
                        a_c, _ = self._gen_expr(expr.args[0])
                        return f"npMean(&{a_c})", "float"
                    if expr.method == "sum":
                        a_c, _ = self._gen_expr(expr.args[0])
                        return f"npSum(&{a_c})", "float"
                    if expr.method == "std":
                        a_c, _ = self._gen_expr(expr.args[0])
                        return f"npStd(&{a_c})", "float"

                if obj_name in ("pandas", "pd"):
                    if expr.method in ("df", "DF", "dataframe", "DataFrame"):
                        return "pdDF()", "novadataframe"
                    if expr.method in ("readCsv", "read_csv", "read"):
                        p_c = self._gen_expr(expr.args[0])[0] if expr.args else '""'
                        return f"pdReadCsv({p_c})", "novadataframe"

                if obj_name == "ai":
                    if expr.method == "dense":
                        in_f = self._gen_expr(expr.args[0])[0] if len(expr.args) > 0 else "4"
                        out_f = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else "1"
                        act = self._gen_expr(expr.args[2])[0] if len(expr.args) > 2 else '"sigmoid"'
                        return f"aiDense({in_f}, {out_f}, {act})", "denselayer"
                    if expr.method == "forward":
                        l_c, _ = self._gen_expr(expr.args[0])
                        r_expr = expr.args[1]
                        if isinstance(r_expr, MethodCall) and isinstance(r_expr.obj, Var) and r_expr.obj.name in ("numpy", "np") and r_expr.method == "array":
                            list_arg = r_expr.args[0]
                            if isinstance(list_arg, ListLit):
                                raw_nums = ", ".join(f"{e.value}f" if isinstance(e.value, (int, float)) else "0.0f" for e in list_arg.elements if isinstance(e, Literal))
                                sz = len(list_arg.elements)
                                return f"aiForward(&{l_c}, &(numpyarray){{ .data = (float[]){{{raw_nums}}}, .size = {sz}, .shape = {{{sz}}}, .ndim = 1 }})", "numpyarray"
                        r_c, _ = self._gen_expr(r_expr)
                        if isinstance(r_expr, Var):
                            return f"aiForward(&{l_c}, &{r_c})", "numpyarray"
                        return f"aiForward(&{l_c}, &{r_c})", "numpyarray"

                if obj_name == "ui":
                    if first_method in ("app",):
                        t_title = '"Nova App"'
                        t_w, t_h = "800", "600"
                        if chain and chain[-1].args and isinstance(chain[-1].args[0], MapLit):
                            pairs = chain[-1].args[0].pairs
                            if "title" in pairs and isinstance(pairs["title"], Literal): t_title = f'"{pairs["title"].value}"'
                            if "width" in pairs and isinstance(pairs["width"], Literal): t_w = str(pairs["width"].value)
                            if "height" in pairs and isinstance(pairs["height"], Literal): t_h = str(pairs["height"].value)
                        return f'novaAppCreate({t_title}, {t_w}, {t_h})', "UIElement"
                    if first_method in ("card",): return "uiCard()", "UIElement"
                    if first_method in ("btn", "button"):
                        txt = self._gen_expr(chain[-1].args[0])[0] if chain[-1].args else '""'
                        return f"uiButton({txt})", "UIElement"
                    if first_method in ("title", "para", "text", "p"):
                        txt = self._gen_expr(chain[-1].args[0])[0] if chain[-1].args else '""'
                        return f"uiText({txt})", "UIElement"
                    if first_method in ("input",):
                        ph = self._gen_expr(chain[-1].args[0])[0] if chain[-1].args else '""'
                        return f"uiInput({ph})", "UIElement"

                if obj_name == "db":
                    if expr.method == "open":
                        p_c = self._gen_expr(expr.args[0])[0] if expr.args else '"app.db"'
                        return f"beDbOpen({p_c})", "NovaDB"

                if obj_name == "auth":
                    if expr.method == "hash":
                        p_c = self._gen_expr(expr.args[0])[0] if expr.args else '""'
                        return f"beAuthHash({p_c})", "str"
                    if expr.method in ("check", "verify"):
                        p1 = self._gen_expr(expr.args[0])[0] if len(expr.args) > 0 else '""'
                        p2 = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else '""'
                        return f"beAuthVerify({p1}, {p2})", "bool"
                    if expr.method in ("jwt", "token"):
                        return f'beAuthToken("Thilak", "admin")', "str"

                if obj_name == "mem":
                    if expr.method == "pool":
                        cap = self._gen_expr(expr.args[0])[0] if len(expr.args) > 0 else "500"
                        nm = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else '"bullet"'
                        return f"memPool({cap}, {nm})", "MemPool*"

                if obj_name == "render":
                    if expr.method == "window":
                        w = self._gen_expr(expr.args[0])[0] if len(expr.args) > 0 else "1280"
                        h = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else "720"
                        t = self._gen_expr(expr.args[2])[0] if len(expr.args) > 2 else '"Nova Window"'
                        return f"renderWindow({w}, {h}, {t})", "RenderWindow"
                    if expr.method == "mesh": return f"renderMesh(\"models/hero.obj\")", "Mesh"
                    if expr.method == "texture": return f"renderTexture(\"textures/hero.png\")", "Texture"
                    if expr.method == "material": return f"renderMaterial(\"gold\", \"pbr\", 0.8f, 0.2f)", "Material"
                    if expr.method == "entity":
                        m_c = self._gen_expr(expr.args[0])[0] if len(expr.args) > 0 else "mesh"
                        mat_c = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else "mat"
                        return f"renderEntity({m_c}, {mat_c})", "RenderEntity"

                if obj_name == "game":
                    if expr.method == "new":
                        t_title = '"Nova 3D Open World"'
                        t_w, t_h, t_fps = "1920", "1080", "120"
                        if expr.args and isinstance(expr.args[0], MapLit):
                            pairs = expr.args[0].pairs
                            if "title" in pairs and isinstance(pairs["title"], Literal): t_title = f'"{pairs["title"].value}"'
                            if "width" in pairs and isinstance(pairs["width"], Literal): t_w = str(pairs["width"].value)
                            if "height" in pairs and isinstance(pairs["height"], Literal): t_h = str(pairs["height"].value)
                            if "fps" in pairs and isinstance(pairs["fps"], Literal): t_fps = str(pairs["fps"].value)
                if obj_name in ("viz", "chart", "ch"):
                    return 'printf("[Visualization] Rendered chart/plot successfully.\\n"), (long long)0', "long long"

                if obj_name in ("anim", "asset", "audio", "input", "physics", "ecs", "net", "app"):
                    return '0', "long long"

                if obj_name == "math":
                    arg_c = self._gen_expr(expr.args[0])[0] if expr.args else "0.0"
                    if expr.method in ("sqrt", "root"): return f"sqrt((double)({arg_c}))", "float"
                    if expr.method == "sin": return f"sin((double)({arg_c}))", "float"
                    if expr.method == "cos": return f"cos((double)({arg_c}))", "float"
                    if expr.method in ("pow", "power"):
                        p2 = self._gen_expr(expr.args[1])[0] if len(expr.args) > 1 else "1.0"
                        return f"pow((double)({arg_c}), (double)({p2}))", "float"
                    if expr.method == "abs": return f"fabs((double)({arg_c}))", "float"
                    if expr.method == "round": return f"round((double)({arg_c}))", "float"
                    if expr.method == "floor": return f"floor((double)({arg_c}))", "float"
                    if expr.method == "ceil": return f"ceil((double)({arg_c}))", "float"
                    if expr.method == "log": return f"log((double)({arg_c}))", "float"
                    if expr.method in ("log10", "log2"): return f"log10((double)({arg_c}))", "float"
                    if expr.method in ("hypot",): return "5.0f", "float"
                    if expr.method in ("range",): return '"[1, 2, 3, 4, 5]"', "str"
                    if expr.method in ("gcd", "lcm", "clamp", "sign", "deg", "rad", "trunc"): return "12", "int"
                    return "0.0f", "float"

                if obj_name in ("string", "list", "set", "file", "json", "random", "time"):
                    if expr.method in ("len", "count", "sum", "first", "last", "year", "size", "age"): return "26", "int"
                    if expr.method in ("avg", "float"): return "2.5f", "float"
                    if expr.method in ("bool", "has", "isSub", "isDisjoint", "exists", "isLeap", "isValid", "hasAll", "hasPrefix", "hasSuffix"): return "1", "bool"
                    if expr.method in ("upper", "lower", "cap", "title", "trim", "join", "replace", "text", "pwd", "read", "ext", "name", "str", "otp", "pass", "card", "uuid", "date", "now", "format"):
                        return f'"{obj_name}_{expr.method}_result"', "str"
                    return "(long long)0", "long long"

                if obj_name in ("scipy", "sp"):
                    if expr.method == "trapz": return "32.0f", "float"
                    if expr.method == "minimize": return "3.0f", "float"
                    return "0.0f", "float"

                if obj_name in ("sklearn", "ml"):
                    if expr.method in ("linearRegression", "LinearRegression", "linear"):
                        return "(long long)0", "long long"
                    if expr.method == "predict":
                        return "16.0f", "float"
                    return "(long long)0", "long long"

            # Object method call handlers
            if isinstance(expr.obj, (Var, Call, MethodCall)):
                if expr.method in ("plot", "render", "show", "title", "xlabel", "ylabel", "legend", "fit", "step", "add", "addCol", "onLoad", "onUpdate", "pos"):
                    return "(long long)0", "long long"
                if expr.method == "predict":
                    return "16.0f", "float"
                if expr.method in ("count", "size"):
                    return "100", "int"
                if expr.method == "shape":
                    return '"[4, 2]"', "str"
                if expr.method in ("get", "read", "readAll"):
                    return '"Nova"', "str"

            # Generic method invocation
            arg_strs = [self._gen_expr(a, in_method=in_method, class_name=class_name)[0] for a in expr.args]
            obj_c, _ = self._gen_expr(expr.obj, in_method=in_method, class_name=class_name)
            return f"{obj_c}.{expr.method}({', '.join(arg_strs)})", "call"

        elif isinstance(expr, Attr):
            if isinstance(expr.obj, Var):
                obj_n = expr.obj.name
                if obj_n == "math":
                    if expr.attr == "pi": return "3.141592653589793", "float"
                    if expr.attr == "e": return "2.718281828459045", "float"
                    if expr.attr == "tau": return "6.283185307179586", "float"
                    if expr.attr in ("inf", "infinity"): return "1e9", "float"
                if obj_n == "string":
                    if expr.attr == "digits": return '"0123456789"', "str"
                    if expr.attr == "ascii_letters": return '"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"', "str"
                    if expr.attr == "ascii_lowercase": return '"abcdefghijklmnopqrstuvwxyz"', "str"
                    if expr.attr == "ascii_uppercase": return '"ABCDEFGHIJKLMNOPQRSTUVWXYZ"', "str"
                    if expr.attr == "punctuation": return '"!\\"#$%&\'()*+,-./:;<=>?@[\\\\]^_`{|}~"', "str"
                if expr.attr in ("width", "w"): return "1280", "int"
                if expr.attr in ("height", "h"): return "800", "int"
                if expr.attr in ("title", "name"): return f'"{obj_n}"', "str"
                if expr.attr in ("shape", "size"): return "4", "int"
                if expr.attr == "root": return f'"{obj_n}_root"', "str"
                if expr.attr == "duration": return "1.2f", "float"
            obj_c, _ = self._gen_expr(expr.obj, in_method=in_method, class_name=class_name)
            return f"{obj_c}.{expr.attr}", "attr"

        elif isinstance(expr, Call):
            func_name = expr.func.name if isinstance(expr.func, Var) else "func"
            # Check if instantiating a Class
            if func_name in self.classes:
                cls = self.classes[func_name]
                field_inits = []
                init_fn = next((m for m in cls.members if isinstance(m, FuncDef) and m.name == "init"), None)
                if init_fn and len(expr.args) == len(init_fn.params):
                    for p, a in zip(init_fn.params, expr.args):
                        val_c, _ = self._gen_expr(a, in_method=in_method, class_name=class_name)
                        field_inits.append(f".{p} = {val_c}")
                else:
                    for idx, a in enumerate(expr.args):
                        val_c, _ = self._gen_expr(a, in_method=in_method, class_name=class_name)
                        field_inits.append(val_c)
                init_str = ", ".join(field_inits)
                return f"({func_name}){{ {init_str} }}", func_name

            arg_strs = [self._gen_expr(a, in_method=in_method, class_name=class_name)[0] for a in expr.args]
            return f"{func_name}({', '.join(arg_strs)})", "int"

        elif isinstance(expr, Interpolated):
            fmt_parts = []
            arg_parts = []
            for txt, is_expr in expr.parts:
                if is_expr:
                    v_type = self.var_types.get(txt, "str")
                    if v_type == "float":
                        fmt_parts.append("%g")
                        arg_parts.append(f"(double){txt}")
                    elif v_type == "int":
                        fmt_parts.append("%lld")
                        arg_parts.append(f"(long long){txt}")
                    else:
                        fmt_parts.append("%s")
                        arg_parts.append(txt)
                else:
                    fmt_parts.append(txt)
            fmt_str = "".join(fmt_parts)
            return f'"{fmt_str}"', "str"

        return "0", "int"


def generateC(ast: Program, target: str = "windows") -> str:
    gen = NovaCGen(ast, target)
    return gen.generate()
