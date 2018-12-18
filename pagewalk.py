import os
import re
from pprint import pprint
import json


class SourceTreeNavigator:
    index = "index.php"
    rootDir = "/home/alessio/schoolmate-dir"

    switchRe = re.compile(r'.*switch\ *\(.*')

    tree = {}

    def __init__(self):
        pass

    def walk(self, file):

        subtree = {
            "PageName": file,
            "varName" : "",
            "varValue" : "",
            "childs": []
        }

        try:
            with open(file, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return {}

        i = 0
        while i < len(lines):
            if self.switchRe.match(lines[i]):

                if subtree["varName"] == "":
                    subtree["varName"] = re.sub(r'\s*switch\ *\(\$(\S*)\).*',r'\1',lines[i]).strip()

                while "default:" not in lines[i] or "}" not in lines[i]:
                    if "require_once" in lines[i]:
                        nextNode = re.sub(r'\s*[^"]*\"(\S*)\".*',r'\1',lines[i]).strip()
                        subtree["childs"].append(self.walk(os.path.join(self.rootDir,nextNode)))
                        #TODO: call recursively on the next node

                    i += 1
                    if i >= len(lines):
                        break
            else:
                i += 1
        return subtree

    def walksite(self):
        path = os.path.join(self.rootDir, self.index)
        pprint(self.walk(path))


