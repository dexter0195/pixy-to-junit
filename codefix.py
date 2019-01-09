#!/usr/bin/env python
import os
import sys
import re


class CodeFix:


    inDir = "/home/alessio/schoolmate-dir"
    outDir = "/home/alessio/schoolmate-fixed-dir"

    pixy_dir = "/home/alessio/Desktop/pixy-report"

    def getFiles(self, dir):


        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(dir):
            path = root.split(os.sep)
            for file in files:
                if ".php" in file:
                    f = os.path.join(root,file)
                    yield f

    def __init__(self):
        pass

    def print_problem(self, file, row):
        with open(file, "r") as f:
            return f.readlines()[row -1]

    def appendvars(self, file, vars):
        old_lines = []
        new_file = os.path.join("/home/alessio/schoolmate-new", file)

        with open(file, "r") as f:
            old_lines = f.readlines()

        #replace $_POST with varname
        for i in range(len(old_lines)):
            if "$_POST" in old_lines[i]:
                old_lines[i] = re.sub(r'\$_POST\[[\W]*(\w*)[\W]*\]',r'$_post_\1',old_lines[i])

        for i in vars:
            line = "$_post_"+i+" = htmlspecialchars($_POST['"+i+"']);\n"
            old_lines.insert(1, line)

        with open(new_file, "w+") as f:
            f.writelines(old_lines)



    def find_post_vars(self, filename):
        post_lines = []
        with open(filename,"r") as f:
            for i in f.readlines():
                if "$_POST" in i:
                    for t in i.split("$"):
                        # print("i: ",i)
                        if "_POST" in t:
                            var = re.sub(r'.*_POST\[[\W]*(\w*)[\W]*\].*',r'\1',t).strip()
                            if var not in post_lines:
                                post_lines.append(var)
        return post_lines


    def fix_code(self, dirs):

        for file in self.getFiles(dirs):
            self.appendvars(file, self.find_post_vars(file))


if __name__ == "__main__":

    codefix = CodeFix()

    codefix.fix_code(sys.argv[1])
