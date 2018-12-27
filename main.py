#!/usr/bin/env python
from pprint import pprint

from codegen import CodeGen
import sys


codegen = CodeGen()

choice = input("you are about to overwrite everything, are you sure? (y/N)")
if choice != "y":
    exit()

count = codegen.doAllTheStuff(sys.argv[1])
print("files generated:", count)
print("Bye")

