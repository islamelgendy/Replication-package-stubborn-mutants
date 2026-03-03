#!/usr/bin/python3

import javalang

from utils.utilsIO import getAllFilesEndingWith, getExactFile
from utils.mutant import Mutant, getCSVKillMap

# Function to recursively find the maximum line number in a node's body
def find_max_line(node):
    max_line = node.position.line if hasattr(node, 'position') and node.position else 0

    # Traverse child nodes
    if hasattr(node, 'children'):
        for child in node.children:
            if isinstance(child, (list, tuple)):
                for item in child:
                    if isinstance(item, javalang.tree.Node):
                        max_line = max(max_line, find_max_line(item))
            elif isinstance(child, javalang.tree.Node):
                max_line = max(max_line, find_max_line(child))

    return max_line

# Function to get the start and end lines of a method or constructor
def get_method_lines(node):
    start_line = node.position.line  # Starting line of the method/constructor
    end_line = find_max_line(node)   # Ending line of the method/constructor
    return start_line, end_line

def find_method_by_name(tree, method_name, lineno):
    """
    Find the method node by its name.
    """
    for path, node in tree:
        # if method_name == '&lt;init&gt;' and isinstance(node, javalang.tree.ConstructorDeclaration) and node.position.line == lineno:
        if method_name == '&lt;init&gt;' and isinstance(node, javalang.tree.ConstructorDeclaration) and node.position:
            # endLine = node.position.line + len(node.body) + 1
            start_line, endLine = get_method_lines(node)
            if lineno >= node.position.line and lineno <= endLine:
                return node
        elif isinstance(node, javalang.tree.MethodDeclaration) and node.name == method_name:
            return node
    return None

def get_method_info(method_node):
    """
    Get the access modifier and return type of a method.
    """
    # Get the access modifier
    access_modifier = "package-private"  # Default if no modifier is specified
    if "public" in method_node.modifiers:
        access_modifier = "public"
    elif "private" in method_node.modifiers:
        access_modifier = "private"
    elif "protected" in method_node.modifiers:
        access_modifier = "protected"

    if isinstance(method_node, javalang.tree.ConstructorDeclaration):
        is_void = 'Constructor'
    else:
        # Check if the method is void
        is_void = 'Void' if method_node.return_type == None else 'Non-void'

    # Check if the method is static
    is_static = "static" in method_node.modifiers

    return access_modifier, is_void, is_static

def checkLineInfo(javaFile:str, mutatedMethod:str, lineNo:int, mutator:str):
    with open(javaFile, "r", encoding="latin-1") as f:
        contents = f.readlines()

    javaFileStr = "".join(contents)

    tree = javalang.parse.parse(javaFileStr)
    # if mutatedMethod == '&lt;init&gt;':
    #     lineNo=237
    method_node = find_method_by_name(tree, mutatedMethod, lineNo)
    # lineNo = 684
    info = {}
   
    for path, node in tree:
        if hasattr(node, 'position') and node.position:
            if node.position.line == lineNo:  # Line number
                line_type = get_line_type(tree, lineNo, mutator)
                # cc = calculate_cyclomatic_complexity(method_node, lineNo)
                nesting_level = find_nesting_level(tree, lineNo)
                access_modifier, is_void, is_static = get_method_info(method_node)
                info['Type of node'] = line_type
                info['Nesting level'] = nesting_level
                if nesting_level >= 5:
                    deubg = True
                # info['Cyclomatic complexity'] = cc
                info['Access modifier'] = access_modifier
                info['Is void'] = is_void
                info['Is static'] = is_static
                break
                # if nesting_level is not None:
                #     print(f"Nesting level at line {lineNo}: {nesting_level}")
                #     print(f"Cyclomatic Complexity of line {lineNo}: {cc}")
                # else:
                #     print(f"No node found at line {lineNo}.")
                # if isinstance(node, javalang.tree.IfStatement):
                #     print("This is an if statement.")
    
    return info

# Function to collect all node types for a target line
def get_node_types_for_line(tree, target_line):
    node_types = set()  # List to store node types

    def _traverse(node):
        # Check if the node is at the target line
        if hasattr(node, 'position') and node.position and node.position.line == target_line:
            node_types.add(type(node).__name__)  # Add the node type to the list

        # Recursively traverse child nodes
        if hasattr(node, 'children'):
            for child in node.children:
                if isinstance(child, (list, tuple)):
                    for item in child:
                        if isinstance(item, javalang.tree.Node):
                            _traverse(item)
                elif isinstance(child, javalang.tree.Node):
                    _traverse(child)

    # Start traversal from the root of the AST
    _traverse(tree)
    return node_types

def get_line_type(tree, target_line, mutOperator):
    """
    Get the type of the highest-level node at the target line.
    """
    # List of node types to check (ordered from highest to lowest level)
    node_types = [
        javalang.tree.IfStatement,
        javalang.tree.ForStatement,
        javalang.tree.WhileStatement,
        javalang.tree.SwitchStatement,
        javalang.tree.TryStatement,
        javalang.tree.ReturnStatement,
        javalang.tree.ThrowStatement,
        javalang.tree.VariableDeclaration,
        javalang.tree.BinaryOperation,  
        javalang.tree.MethodInvocation,
        javalang.tree.Literal,
        javalang.tree.MemberReference,
        javalang.tree.StatementExpression,
        javalang.tree.TernaryExpression  
]

    # Mapping of mutators to likely node types
    mutator_to_node_type = {
        'NegateConditionalsMutator': [javalang.tree.IfStatement, javalang.tree.BinaryOperation, javalang.tree.TernaryExpression],
        'MathMutator': [javalang.tree.BinaryOperation],
        'VoidMethodCallMutator': [javalang.tree.MethodInvocation],
        'ConditionalsBoundaryMutator': [javalang.tree.IfStatement, javalang.tree.BinaryOperation, javalang.tree.TernaryExpression],
        'EmptyObjectReturnValsMutator': [javalang.tree.ReturnStatement],
        'PrimitiveReturnsMutator': [javalang.tree.ReturnStatement],
        'NullReturnValsMutator': [javalang.tree.ReturnStatement],
        'BooleanTrueReturnValsMutator': [javalang.tree.ReturnStatement],
        'IncrementsMutator': [javalang.tree.BinaryOperation],
        'BooleanFalseReturnValsMutator': [javalang.tree.ReturnStatement]
    }

    if target_line == 2175:
        begu = True

    # Get the likely node types for the given mutator
    likely_node_types = mutator_to_node_type.get(mutOperator, node_types)
    all_node_types = get_node_types_for_line(tree, target_line)

    for path, node in tree:
        # Check if the node is at the target line
        if hasattr(node, 'position') and node.position and node.position.line == target_line:
            # Check the node type
            # for node_type in node_types:
            #     if isinstance(node, node_type):
            #         if node_type.__name__ == 'ForStatement' or node_type.__name__ == 'Literal' or node_type.__name__ == 'MemberReference' or node_type.__name__ == 'WhileStatement':
            #             debug = True
            #             break
            for node_type in likely_node_types:
                if isinstance(node, node_type):
                    return node_type.__name__  # Return the type name
            
            # If no exact match, check nested nodes for the likely type                    
            if hasattr(node, 'children'):
                for child in node.children:
                    if isinstance(child, (list, tuple)):
                        for item in child:
                            if isinstance(item, javalang.tree.Node) and isinstance(item, tuple(likely_node_types)):
                                return type(item).__name__
                    elif isinstance(child, javalang.tree.Node) and isinstance(child, tuple(likely_node_types)):
                        return type(child).__name__
    
    elem = getNodeType(all_node_types, mutOperator)
    return elem
    # return node_type.__name__ if node_type.__name__ else "Unknown"
    # return "Unknown"  # If no matching node is found

def getNodeType(all_node_types:set, mutOperator:str):
    if 'ForStatement' in all_node_types:
        return 'ForStatement'
    elif 'WhileStatement' in all_node_types:
        return 'WhileStatement'
    elif 'SwitchStatement' in all_node_types:
        return 'SwitchStatement'
    if mutOperator == 'NegateConditionalsMutator' or mutOperator == 'MathMutator' or mutOperator == 'IncrementsMutator' or mutOperator == 'ConditionalsBoundaryMutator':
        return 'BinaryOperation'
    elif 'MethodInvocation' in all_node_types:
        return 'MethodInvocation'
    else:
        return next(iter(all_node_types))
    
def find_nesting_level(tree, target_line):
    """
    Traverse the AST and find the nesting level of the node at the target line.
    """
    def _traverse(node, level):
        # Check if the node has a position attribute and matches the target line
        if hasattr(node, 'position') and node.position and node.position.line == target_line:
            return level  # Return the current nesting level

        # Recursively traverse child nodes
        if isinstance(node, javalang.tree.Node):
            for child in node.children:
                if isinstance(child, (javalang.tree.Node, list)):
                    result = _traverse(child, level + 1 if isinstance(child, javalang.tree.Node) else level)
                    if result is not None:
                        return result
        elif isinstance(node, list):
            for child in node:
                result = _traverse(child, level)
                if result is not None:
                    return result
        return None

    # Start traversal from the root of the AST
    return _traverse(tree, 0)

def calculate_cyclomatic_complexity(method_node, target_line):
    """
    Calculate the cyclomatic complexity for a given method.
    """
    complexity = 1  # Start with a base complexity of 1

    def _traverse(node):
        nonlocal complexity
        # Check if the node is a decision point
        if isinstance(node, (javalang.tree.IfStatement, javalang.tree.ForStatement,
                            javalang.tree.WhileStatement, javalang.tree.SwitchStatement,
                            javalang.tree.CatchClause)):
            complexity += 1  # Increment complexity for each decision point

        # Check if the node matches the target line
        if hasattr(node, 'position') and node.position and node.position.line >= target_line:
            return True  # Stop traversal when the target line is found
        
        # Recursively traverse child nodes
        if isinstance(node, javalang.tree.Node):
            for child in node.children:
                if isinstance(child, (javalang.tree.Node, list)):
                    if _traverse(child):
                        return True
        elif isinstance(node, list):
            for child in node:
                if _traverse(child):
                    return True

    # Traverse the method's AST
    _traverse(method_node)
    return complexity

def parseMutationsXML(xmlFile, csvFile):
    with open(xmlFile, "r") as f:
        contents = f.readlines()

    mutantsList = list()
    # Parse the file line by line
    for i, x in enumerate(contents):
        if x.startswith('<mutation '):
            mut = Mutant()
            
            # Split the packageLine to get the right folder
            mut.parse(x)
            mutantsList.append(mut)

    killMapContents = getCSVKillMap(mutantsList)

    with open(csvFile, "w") as f:
        killMapContents = "".join(killMapContents)
        f.write(killMapContents)

def parseMutantFromXML(folder, xmlFile, mutant):
    with open(xmlFile, "r") as f:
        contents = f.readlines()

    mut_info = None
    # Parse the file line by line
    for i, x in enumerate(contents):
        if x.startswith('<mutation '):
            mut = Mutant()
            
            # Split the packageLine to get the right folder
            mut.parse(x)
            if(mut.equals(mutant)):
                # Loop through all files in the test directory of the project and store the java files in a list
                # javaFile = getAllFilesEndingWith(folder + "/src", mut.sourceFile)[0]
                javaFile = getExactFile(folder + "/src", mut.sourceFile, mut.mutatedClass)
                mut_info = checkLineInfo(javaFile, mut.mutatedMethod, int(mut.lineNumber), mut.mutator)
                mut_info['Mutator'] = mut.mutator
                break
                

    return mut_info

# Testing the code
# xmlFile = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/pit-reports/mutations.xml'
# csvfilePath = "../resources/mutation/time.13f.mutation.csv"

# parseMutationsXML(xmlFile, csvfilePath)