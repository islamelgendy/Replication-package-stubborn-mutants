#!/usr/bin/python3

import re

def modifyPom(pomFile, extra = False, targetClasses=[], testClasses=[]):
    try:
        with open(pomFile, "r") as f:
            contents = f.readlines()

        # Check if the pom file already has the evosuite plugin
        if checkEvoSuite(contents):
            return True

        # Find the right place for the new plugins and insert them
        pluginPos = findIndexForPlugins(contents)
        plugins = getPluginsLines(extra, targetClasses, testClasses)
        insertListIntoList(contents, plugins, pluginPos)

        # Find the right place for the new dependencies and insert them
        dependencyPos = findIndexForDependencies(contents)
        dependencies = getDependcyLines(extra)
        insertListIntoList(contents, dependencies, dependencyPos)

        # Find the right place for the new pluginRepositories and insert them
        pluginRepositoryPos = findIndexForPluginRepositories(contents)
        pluginRepository = getPluginRepositoriesLines()
        insertListIntoList(contents, pluginRepository, pluginRepositoryPos)

        # Make sure the Junit version is 4.13.1
        fixJunitDependencyVersion(contents)

        # Make sure the maven-surefire-plugin version is 2.12.3
        fixMavenSurefireVersion(contents)

        # Make sure the jacoco version is 0.8.5
        fixJacocoVersion(contents)

        # Make sure the Maven Compile Source is 1.8
        fixMavenCompileSource(contents)

        with open(pomFile, "w") as f:
            contents = "".join(contents)
            f.write(contents)
        
        return True
        
    except:
        return False

def insertListIntoList(orgList, insertList, pos):
    for i in range(len(insertList)):
        orgList.insert(i + pos, insertList[i])

def findIndexForPlugins(contents):
    buildPos = 0

    for i, x in enumerate(contents):
        if "<build>" in x:
            buildPos = i
            break

    for i, x in enumerate(contents, buildPos):
        if "<plugins>" in contents[i]:
            pos = i
            break

    return pos + 1

def findIndexForPluginRepositories(contents):
    for i, x in enumerate(contents, len(contents)-10):
        if "</project>" in contents[i]:
            pos = i
            break

    return pos

def findIndexForDependencies(contents):
    for i, x in enumerate(contents):
        if "<dependencies>" in x:
            pos = i
            break

    return pos + 1

def findIndexForProperties(contents):
    for i, x in enumerate(contents):
        if "</properties>" in x:
            pos = i
            break

    return pos - 1

def fixJunitDependencyVersion(contents):
    for i, x in enumerate(contents):
        if "<groupId>junit</groupId>" in x:
            Junitpos = i
            break

    for i, x in enumerate(contents, Junitpos):
        if "<version>" in contents[i]:
            startpos = contents[i].find("<version>")
            endpos = contents[i].find("</version>")
            contents[i] = contents[i][0:startpos+9] + '4.13.1' + contents[i][endpos:] 
            break

        
def fixMavenCompileSource(contents):
    for i, x in enumerate(contents):
        if "<maven.compile.source>" in x:
            startpos = contents[i].find(">")
            endpos = contents[i].find("</maven.compile.source>")
            contents[i] = contents[i][0:startpos+1] + '1.8' + contents[i][endpos:]
        
        if "<maven.compile.target>" in x:
            startpos = contents[i].find(">")
            endpos = contents[i].find("</maven.compile.target>")
            contents[i] = contents[i][0:startpos+1] + '1.8' + contents[i][endpos:]

def fixMavenSurefireVersion(contents):
    surefirepos = -1 # -1 means no MavenSurefire plugin present

    for i, x in enumerate(contents):
        if "<artifactId>maven-surefire-plugin</artifactId>" in x:
            surefirepos = i
            break

    # if no MavenSurefire plugin present, add the plugin
    if surefirepos == -1:
        # Find the right place for the new maven-surefire-plugin and insert them
        pluginPos = findIndexForPlugins(contents)
        plugins = getSurefireLines()
        insertListIntoList(contents, plugins, pluginPos)
        return

    # This counter is to check if the version tag is present. 
    # If it is, you should find it no latter than 4 positions after surefirepos
    counter = 0

    for i, x in enumerate(contents, surefirepos):
        # if counter is more than 3, that means that version tag is not present
        if counter > 3:
            insertListIntoList(contents, ["\t\t<version>2.12.3</version>\n"], surefirepos+1)
            break
        if "<version>" in contents[i]:
            startpos = contents[i].find("<version>")
            endpos = contents[i].find("</version>")
            contents[i] = contents[i][0:startpos+9] + '2.12.3' + contents[i][endpos:] 
            break
        counter += 1

def fixJacocoVersion(contents):
    Jacocopos = -1

    for i, x in enumerate(contents):
        if "<commons.jacoco.version>" in x:
            Jacocopos = i
            break

    # If the Jacoco property is not found, then add it
    if Jacocopos == -1:
        # Find the right place for the new pluginRepositories and insert them
        propertiesPos = findIndexForProperties(contents)
        jacocoVersionLines = getJacocoVersionLines()
        insertListIntoList(contents, jacocoVersionLines, propertiesPos)
        return
    
    for i, x in enumerate(contents, Jacocopos):
        if "<commons.jacoco.version>" in contents[i]:
            startpos = contents[i].find("<commons.jacoco.version>")
            endpos = contents[i].find("</commons.jacoco.version>")
            contents[i] = contents[i][0:startpos+len("<commons.jacoco.version>")] + '0.8.5' + contents[i][endpos:] 
            break


def checkEvoSuite(contents):
    for i, x in enumerate(contents):
        if "<groupId>org.evosuite</groupId>" in x:
            return True

    return False

def getTargetAndTestClasses(path):
    infoFile = path + '/defects4j.build.properties'

    with open(infoFile, "r") as f:
            contents = f.readlines()

    testClasses = list()

    for i, x in enumerate(contents):
        if "d4j.classes.modified" in x:
            # Get the modified classes
            modifiedClassList = re.split('=', x)[1].strip()
            modifiedClasses = re.split(',', modifiedClassList)
        elif "d4j.tests.trigger" in x:
            # Get the triger classes
            trigerClassList = re.split('=', x)[1].strip()
            trigerClasses = re.split(',', trigerClassList)      

    for modClass in modifiedClasses:
        className = getClassName(modClass)
        signature = getSignature(modClass, className)
        testClasses.append(signature + '.*' + className + '*')
    
    for trigerClass in trigerClasses:
            lastDotPos = trigerClass.rfind('.')
            colonPos = trigerClass.find('::')
            onlyTrigerClass = trigerClass[lastDotPos+1:colonPos]
            signature = getSignature(modClass, className)

            # Check if the triger class is not included
            included = False
            for testClass in testClasses:
                if onlyTrigerClass in testClass:
                    included = True
                    break
            
            if not included:
                testClasses.append(signature + '.' + onlyTrigerClass)
    
    testClasses.append(signature + '.RegressionTest')



    return modifiedClasses, testClasses, trigerClasses

def getClassName(modClass):
    tokens = re.split('\\.', modClass)

    return tokens[-1]

def getSignature(qualifiedClass, className):

    # get rid of the class name and keep the signature
    lastDotPos = qualifiedClass.rfind(className) - 1
    
    return qualifiedClass[0:lastDotPos]

def getPluginsLines(extra, targetClasses, testClasses):
    lines = ["\t<plugin>\n"]
    lines.append("\t\t<groupId>org.evosuite.plugins</groupId>\n")
    lines.append("\t\t<artifactId>evosuite-maven-plugin</artifactId>\n")
    lines.append("\t\t<version>1.0.6</version>\n")
    lines.append("\t\t<executions><execution>\n")
    lines.append("\t\t\t<goals> <goal> prepare </goal> </goals>\n")
    lines.append("\t\t\t<phase> process-test-classes </phase>\n")
    lines.append("\t\t</execution></executions>\n")
    lines.append("\t</plugin>\n")

    if extra:
        # Add extra plugin for PIT
        lines.append("\t<plugin>\n")
        lines.append("\t\t<groupId>org.pitest</groupId>\n")
        lines.append("\t\t<artifactId>pitest-maven</artifactId>\n")
        lines.append("\t\t<version>1.14.2</version>\n")
        lines.append("\t\t<configuration>\n")
        lines.append("\t\t\t<targetClasses>\n")
        for target in targetClasses:
            lines.append("\t\t\t\t<param>" + target + "</param>\n")
        lines.append("\t\t\t</targetClasses>\n")
        lines.append("\t\t\t<targetTests>\n")
        for target in testClasses:
            lines.append("\t\t\t\t<param>" + target + "</param>\n")
        lines.append("\t\t\t</targetTests>\n")
        lines.append("\t\t\t<fullMutationMatrix>true</fullMutationMatrix>\n")
        lines.append("\t\t\t\t<outputFormats>\n")
        lines.append("\t\t\t\t  <param>XML</param>\n")
        lines.append("\t\t\t\t</outputFormats>\n")
        lines.append("\t\t</configuration>\n")
        lines.append("\t</plugin>\n")

        # Add extra plugin for Jacococ
        lines.append("\t<plugin>\n")
        lines.append("\t\t<groupId>org.jacoco</groupId>\n")
        lines.append("\t\t<artifactId>jacoco-maven-plugin</artifactId>\n")
        lines.append("\t\t<version>0.8.2</version>\n")
        lines.append("\t\t<executions>\n")
        lines.append("\t\t\t<execution>\n")
        lines.append("\t\t\t\t<goals><goal>prepare-agent</goal></goals>\n")
        lines.append("\t\t\t</execution>\n")
        lines.append("\t\t\t<execution>\n")
        lines.append("\t\t\t\t<id>report</id>\n")
        lines.append("\t\t\t\t<phase>test</phase>\n")
        lines.append("\t\t\t\t<goals><goal>report</goal></goals>\n")
        lines.append("\t\t\t</execution>\n")
        lines.append("\t\t</executions>\n")
        lines.append("\t</plugin>\n")

        # Add extra plugin to produce the bytecode of tests
        lines.append("\t<plugin>\n")
        lines.append("\t\t<groupId>org.apache.maven.plugins</groupId>\n")
        lines.append("\t\t<artifactId>maven-compiler-plugin</artifactId>\n")
        lines.append("\t\t<version>3.8.1</version>\n")
        lines.append("\t\t<configuration>\n")
        lines.append("\t\t\t<source>1.8</source>\n")
        lines.append("\t\t\t<target>1.8</target>\n")
        lines.append("\t\t</configuration>\n")

        lines.append("\t\t<executions>\n")
        lines.append("\t\t\t<execution>\n")
        lines.append("\t\t\t\t<id>test-compile</id>\n")
        lines.append("\t\t\t\t<phase>test-compile</phase>\n")
        lines.append("\t\t\t\t<goals><goal>testCompile</goal></goals>\n")
        lines.append("\t\t\t\t<configuration>\n")
        lines.append("\t\t\t\t\t<includes>\n")
        lines.append("\t\t\t\t\t\t<include>**/*Test.java</include>\n")
        lines.append("\t\t\t\t\t\t<include>**/*Tests.java</include>\n")
        lines.append("\t\t\t\t\t</includes>\n")
        lines.append("\t\t\t\t</configuration>\n")
        lines.append("\t\t\t</execution>\n")
        lines.append("\t\t</executions>\n")
        lines.append("\t</plugin>\n")

    return lines

def getSurefireLines():
    lines = ["\t<plugin>\n"]
    lines.append("\t\t<groupId>org.apache.maven.plugins</groupId>\n")
    lines.append("\t\t<artifactId>maven-surefire-plugin</artifactId>\n")
    lines.append("\t\t<version>2.12.3</version>\n")
    lines.append("\t</plugin>\n")

    return lines

def getDependcyLines(extra):

    # Adding EvoSuite dependency
    lines = ["\t<dependency>\n"]
    lines.append("\t\t<groupId>org.evosuite</groupId>\n")
    lines.append("\t\t<artifactId>evosuite-standalone-runtime</artifactId>\n")
    lines.append("\t\t<version>1.0.6</version>\n")
    lines.append("\t\t<scope>test</scope>\n")
    lines.append("\t</dependency>\n")

    if extra:
        # Adding PIT dependency
        lines.append("\t<dependency>\n")
        lines.append("\t\t<groupId>org.pitest</groupId>\n")
        lines.append("\t\t<artifactId>pitest-maven</artifactId>\n")
        lines.append("\t\t<version>1.14.2</version>\n")
        lines.append("\t</dependency>\n")

        # Adding javassist dependency
        lines.append("\t<dependency>\n")
        lines.append("\t\t<groupId>org.javassist</groupId>\n")
        lines.append("\t\t<artifactId>javassist</artifactId>\n")
        lines.append("\t\t<version>3.29.2-GA</version>\n")
        lines.append("\t</dependency>\n")

    return lines

def getPluginRepositoriesLines():
    lines = ["\t<pluginRepositories>\n"]
    lines.append("\t\t<pluginRepository>\n")
    lines.append("\t\t\t<id>EvoSuite</id>\n")
    lines.append("\t\t\t<name>EvoSuite Repository</name>\n")
    lines.append("\t\t\t<url>http://www.evosuite.org/m2</url>\n")
    lines.append("\t\t</pluginRepository>\n")
    lines.append("\t</pluginRepositories>\n")

    return lines

def getJacocoVersionLines():
    lines = ["    <commons.jacoco.version>0.8.5</commons.jacoco.version>"]
    lines.append("\n")

    return lines


# pom = "/home/islam/MyWork/New-work-2023/DBT-workbench/subjects/buggy/3/pom.xml"
# modifyPom(pom)