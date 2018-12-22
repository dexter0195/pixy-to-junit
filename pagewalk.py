import os
import re
from pprint import pprint
import json


class SourceTreeNavigator:
    index = "index.php"
    rootDir = "/home/alessio/schoolmate-dir"
    jsonFile = "/home/alessio/my_repos/code_gen/result.json"

    switchRe = re.compile(r'.*switch\ *\(.*')

    cacheData = {}

    pathFound = False

    tree = {}

    def __init__(self):
        try:
            with open(self.jsonFile, "r") as f:
                self.cacheData = json.load(f)
        except FileNotFoundError:
            pass

    def walk(self, file, useCache=False):

        if useCache:
            return self.cacheData


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
                        if childNode != {}:
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

        if tree["PageName"] == pagename:
            return {
                tree["varName"]: tree["varValue"]
            }
        else:
            for i in tree["children"]:
                temp = self.findPathToPage(i, pagename)
                if temp is not None:
                    self.pathFound = True
                    if tree["varName"] == "page":
                        return {
                            "page": tree["varValue"],
                            "page2": temp["page2"]
                        }
                    else:
                        return temp


    def walksite(self, useCache=False):

        result = self.walk(self.index, useCache=useCache)
        if not useCache:
            with open(self.jsonFile, "w+") as jsonOut:
                json.dump(result, jsonOut)

        return result


