import re
import os
from pprint import pprint
from pagewalk import SourceTreeNavigator


class CodeGen:

    srcRootDir = "/home/alessio/schoolmate-dir"
    pagewalk = None

    def __init__(self):
        self.pagewalk = SourceTreeNavigator()

    def buildCode(self, data):

        todo = ""
        checkit = False



# TODO: fix the package according to the directory structure!!
        imports = '''
package project.tests.'''+data["role"]+'''.Test'''+data["testNum"]+''';

import org.junit.*;
import static org.junit.Assert.*;
import project.tests.'''+data["role"]+'''.'''+data["role"]+'''BaseTest;
        
'''

        funcDeclaration = '''public class Test'''+data["testNum"]+'''From'''+\
                          data["startPage"]+str(data["row"])+''' extends '''+data["role"]+'''BaseTest { '''

        testFuncHeaderAndLogin = '''


    @Test
    public void test() {

        String taintedVar = "'''+data["varToTaint"]+'''";
        String formName = "myform";
        String targetForm = "'''+data["targetForm"]+'''";

        //login
        goToLoginPage();
        assertTrue(isLoginPage());
        login(getUsername(),getPassword());
        assertTrue(isLoggedIn());
        
        //create the custom form with navigation to target page'''

        createForm = '''
        utils.createMyForm();
        '''
        pageAndPage2Vars = ""
        for var in ["page", "page2"]:
            pageAndPage2Vars += '''utils.addFieldToMyFormWithValue("'''+var+'''","'''+data[var]+'''");
        '''
        addFormFields = ""
        for i in data["postVars"]:
            if i == "page" or i == "page2":
                continue

            todo += "\n// TODO: check added field: "+i+"\n"

            if data["varToTaint"] == i:

                if "delete" not in i:
                    addFormFields += '''utils.addFieldToMyFormWithValue("'''+i+'''","1");
            '''
                else:
                    addFormFields += '''//utils.addFieldToMyFormWithValue("'''+i+'''","1");
            '''
                    todo += '''// TODO: there is a delete, check it and do the restore
                '''

            else:
                addFormFields += '''//utils.addFieldToMyFormWithValue("'''+i+'''","1");
        '''



        attack = '''
        //ATTACK
        utils.inject("'''+data["varToTaint"]+'''",formName);
        '''
        assertions = '''
        assertTrue(utils.isTitleEqualsTo("'''+data["pageTitle"]+'''"));
        assertFalse(utils.isMaliciousLinkPresentInForm(targetForm));
        '''

        for i in data.keys():
            if data[i] == "":
                todo += '''// TODO: check field missing:'''+i+'''
        '''


        closingBrackets = '''
    }
}
        '''

        code = imports\
               + funcDeclaration\
               + testFuncHeaderAndLogin\
               + createForm\
               + pageAndPage2Vars\
               + addFormFields\
               + attack\
               + assertions\
               + todo\
               + closingBrackets

        return code
        # print(code)

    def getCredentials(self, page):
        users = {
            "1": {
                "role": "Admin",
                "username": "schoolmate",
                "password": "schoolmate"
            },
            "2": {
                "role": "Teacher",
                "username": "teacher",
                "password": "teacher"
            },
            "3": {
                "role": "Substitute",
                "username": "substitute",
                "password": "substitute"
            },
            "4": {
                "role": "Student",
                "username": "student",
                "password": "student"
            },
            "5": {
                "role": "Parent",
                "username": "parent",
                "password": "parent"
            }
        }

        try:
            return users[page]
        except KeyError:
            return {
                "username": "",
                "password": "",
                "role": ""
            }

    def removeDupForm(self, forms):
        if not forms:
            return []
        seen = set()
        forms = [x for x in forms if x not in seen and not seen.add(x)]
        return forms

    def findFormName(self, file):

        path = os.path.join(self.srcRootDir, file)
        lines = []
        forms = []
        with open(path, "r") as rootSource:
            lines = rootSource.readlines()
        for i in lines:
            if "<form name" in i:
                form = re.sub(r'.*name=\'([\S]+)\'.*',r'\1',i).strip()
                if form != "":
                    forms.append(form)

        forms = self.removeDupForm(forms)

        if len(forms) > 1:
            # print("multiple forms found")
            # print(forms)
            return ""
        elif len(forms) == 0:
            # print("no forms found")
            return ""
        else:
            # print("the form is")
            # print(forms[0])
            return forms[0]

    def findPageTitle(self, file):
        path = os.path.join(self.srcRootDir, file)
        lines = []
        h1 = ""
        with open(path, "r") as rootSource:
            lines = rootSource.readlines()
        for i in lines:
            if "<h1>" in i:
                h1 = re.sub(r'[^<]*<h1>([^<]*)</h1>.*',r'\1',i).strip()
                # print("header is ", h1)
        return h1

    def findPostVars(self, file):
        path = os.path.join(self.srcRootDir, file)
        lines = []
        vars = []
        with open(path, "r") as rootSource:
            lines = rootSource.readlines()
        for i in lines:
            if "$_POST[" in i:
                var = re.sub(r'.*\$_POST\[[\W]*(\w*)[\W]*].*',r'\1',i).strip()
                if var not in vars:
                    vars.append(var)
        return vars

    def findFormFields(self, file, formName):

        formFields = []

        with open(os.path.join(self.srcRootDir,file), "r") as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                prova = lines[i]
                if re.match("\s*<form.*name=\\\'"+formName,lines[i]):
                    while "</form>" not in lines[i]:

                        if re.match(r'\s*<input\ *type=\'hidden\'.*',lines[i]):
                            formField = re.sub(r'.*name=\'(\S*)\'.*',r'\1',lines[i]).strip()
                            formFields.append(formField)
                        i += 1

                else:
                    i += 1
        return formFields

    def evaluatetree(self, file):

        lines = []
        root = {}
        leafs = []
        formName = ""

        with open(file, "r") as dotFile:
            lines = dotFile.readlines()

        for i in lines:
            if "doubleoctagon" in i:
                file = re.sub(r'.*label=\"([a-zA-Z]*\.php).*',r'\1',i).strip()
                row = int(re.sub(r'.*:\ ([0-9]+).*',r'\1', i).strip())
                postvars = self.findPostVars(file)
                formName = self.findFormName(file)
                formFields = self.findFormFields(file, formName)
                root = {
                    "file": file,
                    "row": row,
                    "varPath": self.pagewalk.findPathToPage(self.pagewalk.walksite(useCache=True), file),
                    "postVars": postvars,
                    "pageTitle": self.findPageTitle(file),
                    "form": {
                        "targetForm": formName,
                        "formFields": formFields
                    }
                }
            if "filled" in i:
                if "ellipse" not in i:
                    file = re.sub(r'.*label=\"([a-zA-Z]*\.php).*',r'\1',i).strip()
                    row = int(re.sub(r'.*:\ ([0-9]+).*',r'\1', i).strip())
                    var = re.sub(r'.*POST\[(\S*)\].*',r'\1', i).strip()
                    # if formName == "" or formFields == []:
                    #     return {}
                    leafs.append({
                        "file": file,
                        "row": row,
                        "var": var,
                    })
        return {
            "root": root,
            "leafs": leafs
        }


    def getFiles(self, dir):


        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(dir):
            path = root.split(os.sep)
            for file in files:
                if ".dot" in file:
                    if ".jpg" not in file:
                        f = os.path.join(root,file)
                        yield f

    def output(self, data, code, overwrite=False):

        basedir = "/home/alessio/my_repos/sectest_proj_generated/sectest/src/test/java/project/tests/"
        roledir = data["role"]
        testdir = "Test"+data["testNum"]

        directory = os.path.join(basedir,roledir)
        if not os.path.isdir(directory):
            print("creating directory: ", directory)
            os.mkdir(directory)

        directory = os.path.join(directory,testdir)
        if not os.path.isdir(directory):
            print("creating directory: ", directory)
            os.mkdir(directory)

        file = os.path.join(directory,data["outputJavaFile"])
        if not overwrite:
            if not os.path.isfile(file):
                with open(file ,"w+") as f:
                    f.write(code)
                print("creating file ", file)
        else:
            with open(file ,"w+") as f:
                f.write(code)
            print("overwriting file ", file)


    def doAllTheStuff(self, path):

        count = 0
        if os.path.isdir(path):
            for file in self.getFiles(path):
                for tree in self.buidInfoTree(file):
                    if tree["username"] != "":
                        # pprint(i)
                        self.output(tree, self.buildCode(tree), overwrite=True)
                        # print("=========================")
                        count += 1
        else:
            for tree in self.buidInfoTree(path):
                self.output(tree, self.buildCode(tree), overwrite=True)
                count += 1

        return count


    def buidInfoTree(self, file):

        leafs = []

        tree = self.evaluatetree(file)
        if tree != {}:
            for leaf in tree["leafs"]:
                if "page" in tree["root"]["varPath"].keys():
                    page = tree["root"]["varPath"]["page"]
                else:
                    page = ""
                if "page2" in tree["root"]["varPath"].keys():
                    page2 = tree["root"]["varPath"]["page2"]
                else:
                    page2 = "0"

                credentials = self.getCredentials(page)
                testNum = re.sub(r'.*xss_index\.php_([0-9]*)_min\.dot',r'\1',file)
                startPage = re.sub(r'\.php', r'', leaf["file"])
                prunedTree = {
                    "targetPage": re.sub(r'\.php', r'', tree["root"]["file"]),
                    "targetForm": tree["root"]["form"]["targetForm"],
                    "formFields": tree["root"]["form"]["formFields"],
                    "username": credentials["username"],
                    "password": credentials["password"],
                    "role": credentials["role"],
                    "page2": page2,
                    "page": page,
                    "varToTaint": leaf["var"],
                    "startPage": startPage,
                    "testNum": testNum,
                    "row": leaf["row"],
                    "postVars": tree["root"]["postVars"],
                    "outputJavaFile": "Test"+testNum+"From"+startPage+str(leaf["row"])\
                                      + ".java",
                    "pageTitle": tree["root"]["pageTitle"]
                }
                yield prunedTree

        # pprint(self.pagewalk.findPathToPage(self.pagewalk.walksite(), "ViewAssignments.php"))


