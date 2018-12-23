#!/usr/bin/env python
from pprint import pprint

from codegen import CodeGen
from pagewalk import SourceTreeNavigator
import sys


codegen = CodeGen()
for i in codegen.doAllTheStuff(sys.argv[1]):
    if i["username"] != "":
        codegen.buildCode(i)
# codegen.doAllTheStuff(sys.argv[1])
#codegen.buildCode()
print("Bye")

