import subprocess
import os
import sys
from nova_ide import TEMPLATES

for name, tmpl in TEMPLATES.items():
    code = tmpl["code"]
    print(f"=== TESTING SNIPPET: {name} ({tmpl['title']}) ===")
    fname = f"temp_test_{name}.no"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(code)
    
    # 1. Test interpreter
    print("--- Interpreter ---")
    p_interp = subprocess.run([sys.executable, "nova_interpreter.py", fname], capture_output=True, text=True)
    print(f"Interpreter Exit: {p_interp.returncode}")
    if p_interp.stdout:
        print("Interpreter STDOUT:\n" + p_interp.stdout[:300])
    if p_interp.stderr:
        print("Interpreter STDERR:\n" + p_interp.stderr)

    # 2. Test compiler
    print("--- Compiler ---")
    p_comp = subprocess.run([sys.executable, "nova_compiler.py", fname, "--run"], capture_output=True, text=True)
    print(f"Compiler Exit: {p_comp.returncode}")
    if p_comp.stdout:
        print("Compiler STDOUT:\n" + p_comp.stdout)
    if p_comp.stderr:
        print("Compiler STDERR:\n" + p_comp.stderr)

    try:
        os.remove(fname)
    except:
        pass
    print()
