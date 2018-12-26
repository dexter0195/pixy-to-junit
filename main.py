#!/usr/bin/env python
from pprint import pprint

from codegen import CodeGen
import sys


codegen = CodeGen()

count = codegen.doAllTheStuff(sys.argv[1])
print("files generated:",count)
print("Bye")

