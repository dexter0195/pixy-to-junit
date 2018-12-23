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



        imports = '''
        package project.tests.TeachersPage.Roles.Admin.Test186;

        import org.junit.*;
        import static org.junit.Assert.*;
        import project.tests.TeachersPage.Roles.Admin.TeacherAdminBaseTest;
        '''

        funcDeclaration = '''public class Test'''+data["testNum"]+'''From'''+\
                          data["startPage"]+data["row"]+''' extends TeacherAdminBaseTest { '''

        testFuncHeaderAndLogin = '''


            @Test
            public void test() {

                String taintedVar = "'''+data["varToTaint"]+'''";
                String formName = "'''+data["formName"]+'''";

                //navigation
                //login
                goToLoginPage();
                assertTrue(isLoginPage());
                login("'''+data["username"]+"\", \""+data["password"]+'''");
                assertTrue(isLoggedIn());
                //go to target page
        '''
        addFormFields = ''''''

        attack = '''
                //ATTACK
                utils.inject(taintedVar,formName);
                assertFalse(utils.isMaliciousLinkPresentInForm(formName));
            }
        }
        '''

        code = imports+funcDeclaration+testFuncHeaderAndLogin+addFormFields+attack

        print(code)

    def getCredentials(self, page):
        users = {
            "1" : {
                # Admin
                "user": "schoolmate",
                "password": "schoolmate"
            }
        }

        try:
            return users[page]["user"], users[page]["password"]
        except KeyError:
            return "", ""

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
                formName = self.findFormName(file)
                formFields = self.findFormFields(file, formName)
                if formName == "" or formFields == []:
                    return {}
                root = {
                    "file": file,
                    "row": row,
                    "form": {
                        "formname": formName,
                        "formFields": formFields
                    },
                    "varPath": self.pagewalk.findPathToPage(self.pagewalk.walksite(useCache=True), file)
                }
            if "filled" in i:
                if "ellipse" not in i:
                    file = re.sub(r'.*label=\"([a-zA-Z]*\.php).*',r'\1',i).strip()
                    row = int(re.sub(r'.*:\ ([0-9]+).*',r'\1', i).strip())
                    var = re.sub(r'.*POST\[(\S*)\].*',r'\1', i).strip()
                    leafs.append({
                        "file": file,
                        "row": row,
                        "var": var
                    })
                    return {
                        "root": root,
                        "leafs": leafs
                    }
                else:
                    #we found a persistent xss injection on mysql variables which is not handled
                    return {}


    def getFiles(self, dir):


        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(dir):
            path = root.split(os.sep)
            for file in files:
                if ".dot" in file:
                    if ".jpg" not in file:
                        f = os.path.join(root,file)
                        yield f


    def doAllTheStuff(self, dir):

        for file in self.getFiles(dir):
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
                        page2 = ""

                    username, password = self.getCredentials(page)
                    prunedTree = {
                        "targetPage": re.sub(r'\.php', r'', tree["root"]["file"]),
                        "formName": tree["root"]["form"]["formname"],
                        "formFields": tree["root"]["form"]["formFields"],
                        "username": username,
                        "password": password,
                        "page2": page2,
                        "varToTaint": leaf["var"],
                        "startPage": re.sub(r'\.php', r'', leaf["file"]),
                        "testNum": "",
                        "row": ""
                    }
                    yield prunedTree

        # pprint(self.pagewalk.findPathToPage(self.pagewalk.walksite(), "ViewAssignments.php"))


