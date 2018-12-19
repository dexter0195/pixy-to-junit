#!/usr/bin/env python
from codegen import CodeGen
from pagewalk import SourceTreeNavigator
import sys


codegen = CodeGen()
codegen.doAllTheStuff(sys.argv[1])
codegen.buildCode()
print("Bye")

pagewalk = SourceTreeNavigator()
pagewalk.walksite()
