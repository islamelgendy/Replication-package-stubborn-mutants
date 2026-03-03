class CoverageLineInfo:

    # Attr
    lineNumber = 1
    status = 'fc'
    branch = False

    # default constructor
    def __init__(self):
        self.lineNumber = 1
        self.status = 'fc'
        self.branch = False
    
    # parameterized constructor
    # def __init__(self, ln, st, branch):
    #     self.lineNumber = ln
    #     self.status = st
    #     self.branch = branch

    def setLineNumber(self, ln):
        if ln > 0:
            self.lineNumber = ln

    def setStatus(self, st):
        self.status = st

    def setAsBranch(self):
        self.branch = True

    def setAsLine(self):
        self.branch = False
    
    def printInfo(self):
        print('L', self.lineNumber, ' ' + self.status)

    def parseLine(self, line):
        # Get the line number
        idStartPos = line.find('id="') + 5
        idEndPos = line.find('"', idStartPos)
        idLine = line[idStartPos:idEndPos]
        self.lineNumber = int(idLine)

        # Get the class which is the status
        classStartPos = line.find('class="') + 7
        classEndPos = line.find('"', classStartPos)
        self.status = line[classStartPos:classEndPos]

        if 'branches' in line and 'title="' in line:
            self.branch = True
        else:
            self.branch = False

class CSV_HTML:
    htmlFileName = ''
    htmlPath = ''
    csvContents = list()

    def __init__(self):
        self.htmlFileName = 'dummy'
        self.htmlPath = '/'
        self.csvContents = list()

    def setFileName(self, fn):
        self.htmlFileName = fn

    def setFilePath(self, path):
        self.htmlPath = path

    def addLine(self, line):
        self.csvContents.append(line)

# Testing class
# l1 = CoverageLineInfo()
# l1.setLineNumber(37)
# l1.setStatus('nc')

# l1.printInfo()

# print(l1.lineNumber)