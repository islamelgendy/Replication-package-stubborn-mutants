import os

def parse_method_source(file_path, testType = 'any'):
    result = {}
    current_class = None
    current_method = None
    source_code = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()

            # Extract Class name
            if line.startswith("Class name:"):
                current_class = line.split("Class name:")[1].strip()

            # Extract Method name
            elif line.startswith("Method name:"):
                current_method = line.split("Method name:")[1].strip()

            # Start collecting "Method source code"
            elif line.startswith("Method source code:"):
                source_code = []  # Reset source code collection
            elif current_class and current_method and source_code is not None:
                if testType == 'Randoop' and not current_class.startswith('RegressionTest'):
                    continue
                elif testType == 'Evosuite' and not current_class.endswith('_ESTest'):
                    continue
                elif testType == 'Developer' and (current_class.endswith('_ESTest') or current_class.startswith('RegressionTest')):
                    continue
                # End of method source code block
                if line.startswith("Method byte code:"):
                    # Store the collected method source as a single line
                    method_key = f"{current_class}::{current_method}"
                    result[method_key] = ' '.join(source_code).replace('\n', ' ').replace('  ', ' ').strip()
                    source_code = None  # Stop collecting source code
                elif source_code is not None:
                    source_code.append(line)

    return result

def createFolder(path):
    # Check whether the specified path exists or not
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)

# usage
if __name__ == "__main__":
    prj = "jsoup"
    testType = 'Developer'
    
    if prj == 'math':
        projects = ['4', '5', '6', '9', '13', '14', '18', '17', '19',
                '20', '21', '23', '24', '25', '26', '27', '28', 
                '30', '32', '33', '37', '42', '47', '49', '50', 
                '51', '52', '54', '56', '58', '61', '64', '65', 
                '67', '68', '69', '70', '73', '78', '76', '80', '81']

    # jsoup projects:
    # prj = 'jsoup'
    elif prj == 'jsoup':
        projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                    '30', '33', '35', '36', '37', '38', '39', '40']

    # lang projects:
    # prj = 'lang'
    elif prj == 'lang':
        projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']

    # time projects:
    # prj = 'time'
    elif prj == 'time':
        projects = ['11','13']

    # cli projects:
    # prj = 'cli'
    elif prj == 'cli':
        projects = ['30','31','32','33','34']

    # csv projects:
    # prj = 'csv'
    elif prj == 'csv':
        projects = ['2', '3', '4', '5', '7', '8', '10', 
                    '11', '12', '16']

    # Codec jacoco coverage is not generating, so it is not working
    # codec projects:
    # prj = 'codec'
    # projects = ['11', '12', '15', '16']

    # compress projects:
    # prj = 'compress'
    elif prj == 'compress':
        projects = ['1', '11', '16', '22', '24', '26', '27']
    for ver in projects:
        # Replace with your actual file path    
        input_file_path = f"/home/islam/MyWork/New-work-2023/DBT-workbench/resources/similarity/{prj}/{prj}.{ver}f.test-cases.txt"  
        
        keys_file_path = "/home/islam/MyWork/Code/FAST-replication/input/{}_v{}/{}-keys-{}.txt".format(prj, ver, prj, testType)  # File to store the keys
        values_file_path = "/home/islam/MyWork/Code/FAST-replication/input/{}_v{}/{}-bbox-{}.txt".format(prj, ver, prj, testType)  # File to store the values
        createFolder("/home/islam/MyWork/Code/FAST-replication/input/{}_v{}".format(prj,ver))
        parsed_data = parse_method_source(input_file_path, testType)
        
        # Write keys to one file
        with open(keys_file_path, 'w') as keys_file:
            for key in parsed_data.keys():
                if parsed_data[key] == "":
                    debug = True
                keys_file.write(key + '\n')
        
        # Write values to another file
        
        with open(values_file_path, 'w') as values_file:
            for value in parsed_data.values():
                values_file.write(value + '\n')
