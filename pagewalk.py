import os
import re
from pprint import pprint
import json


class SourceTreeNavigator:
    index = "index.php"
    rootDir = "/home/alessio/schoolmate-dir"
    jsonFile = "/home/alessio/my_repos/code_gen/result.json"

    switchRe = re.compile(r'.*switch\ *\(.*')

    tree = {}

    def __init__(self):
        pass

    def walk(self, file):

        fullpath = os.path.join(self.rootDir,file)

        subtree = {
            "PageName": file,
            "varName" : "",
            "varValue" : "",
            "children": []
        }

        try:
            with open(fullpath, "r") as f:
                lines = [x.strip() for x in f.readlines()]
        except FileNotFoundError:
            return {}

        i = 0
        while i < len(lines):
            if self.switchRe.match(lines[i]):

                if subtree["varName"] == "":
                    varName = re.sub(r'\s*switch\ *\(\$(\S*)\).*',r'\1',lines[i])

                while "default:" not in lines[i] or "}" not in lines[i]:
                    if "require_once" in lines[i]:
                        nextNode = re.sub(r'\s*[^"]*\"(\S*)\".*',r'\1',lines[i])
                        childNode = self.walk(nextNode)
                        childNode["varValue"] = re.sub(r'\s*case\s*([0-9]+)+.*',r'\1',lines[i-1])
                        childNode["varName"] = varName
                        subtree["children"].append(childNode)

                    i += 1
                    if i >= len(lines):
                        break
            else:
                i += 1
        return subtree

    def findPathToPage(self, tree, pagename):
        path = {}
        if tree == {}:
            return
        else:
            #TODO: qui da errore quando gli passo una lista di figli
            if tree["PageName"] == pagename:
                return tree
            else:
                if len(tree["children"]) > 0:
                    for i in tree["children"]:
                        temp = self.findPathToPage(i, pagename)
                        if temp is not None:
                            return temp
                    return

    def walksite(self):

        result = self.walk(self.index)
        with open(self.jsonFile, "w+") as jsonOut:
            json.dump(result, jsonOut)

        return result


