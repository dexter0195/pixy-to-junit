import re
import os
from pprint import pprint
from pagewalk import SourceTreeNavigator


class CodeGen:

    srcRootDir = "/home/alessio/schoolmate-dir"
    pagewalk = None

    def __init__(self):
        self.pagewalk = SourceTreeNavigator()


    def buildCode(self):

        page2 = "ciao"
        admin = "CIAO"

        code = '''package project.tests.TeachersPage.Roles.Admin.Test186;

        import org.junit.*;
        import static org.junit.Assert.*;
        import project.tests.TeachersPage.Roles.Admin.TeacherAdminBaseTest;

        public class Test186FromAdminMain7 extends TeacherAdminBaseTest {


            @Test
            public void test() {

                String taintedVar = "'''+page2+'''";
                String formName = "'''+admin+'''";

                //navigation
                goToLoginPage();
                assertTrue(isLoginPage());
                login(username, password);
                assertTrue(isLoggedIn());
                clickTeacherButton();
                assertTrue(isTeacherPage());

                //ATTACK

                utils.inject(taintedVar,formName);

                assertFalse(utils.isMaliciousLinkPresentInForm(formName));

            }


        }
        '''

        print(code)

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
            print("multiple forms found")
            print(forms)
            return forms[0]
        elif len(forms) == 0:
            print("no forms found")
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
                        if "input" in lines[i] and "submit" not in lines[i]:
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

        with open(file,"r") as dotFile:
            lines = dotFile.readlines()

        for i in lines:
            if "doubleoctagon" in i:
                file = re.sub(r'.*label=\"([a-zA-Z]*\.php).*',r'\1',i).strip()
                row = int(re.sub(r'.*:\ ([0-9]+).*',r'\1', i).strip())
                formName = self.findFormName(file)
                formFields = self.findFormFields(file, formName)
                root = {
                    "file": file,
                    "row" : row,
                    "form": {
                        "formname": formName,
                        "form fields": formFields,
                        "varPath": ""
                    }
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
                    #we found a persistent xss injection on mysql variables
                    return {}


    def getFiles(self, dir):

        dotfiles = []

        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(dir):
            path = root.split(os.sep)
            for file in files:
                if ".dot" in file:
                    if ".jpg" not in file:
                        f = os.path.join(root,file)
                        dotfiles.append(f)

        return dotfiles

    def doAllTheStuff(self, dir):

        for i in self.getFiles(dir):
            print(i)
            pprint(self.evaluatetree(i))

        pprint(self.pagewalk.walksite())

        pprint(self.pagewalk.findPathToPage(self.pagewalk.walksite(), "ManageSchoolInfo.php"))


