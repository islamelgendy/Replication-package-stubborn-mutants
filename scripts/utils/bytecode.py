import subprocess

def parse_bytecode(class_file_path):
    try:
        # Run javap command to disassemble bytecode
        result = subprocess.run(['javap', '-c', class_file_path], capture_output=True, text=True)
        if result.returncode == 0:
            # Print the disassembled bytecode
            print(result.stdout)
        else:
            print("Error:", result.stderr)
    except FileNotFoundError:
        print("Error: 'javap' command not found. Please make sure Java JDK is installed.")
    
def parse_method_bytecode(class_file_path, method_name):
    try:
        # Run javap command to disassemble bytecode
        result = subprocess.run(['javap', '-c', class_file_path], capture_output=True, text=True)
        if result.returncode == 0:
            # Split the output into lines
            lines = result.stdout.split('\n')
            method_found = False
            bytecode = []

            # Iterate through the lines to find the bytecode of the specified method
            for line in lines:
                if method_found:
                    if line.strip() == '':
                        break
                    # process the line and filter it (i.e. remove comments or first line 'Code:')
                    commentPos = line.strip().find('//')
                    if line.strip() == 'Code:':
                        continue
                    elif commentPos >= 0:
                        line = line[0:commentPos]
                    bytecode.append(line.strip())
                elif line.strip().startswith('public') and method_name in line:
                    method_found = True
            
            if bytecode:
                # Print the bytecode of the specified method
                # print('\n'.join(bytecode))
                return bytecode
            else:
                print("Error: Method not found.")
        else:
            print("Error:", result.stderr)
    except FileNotFoundError:
        print("Error: 'javap' command not found. Please make sure Java JDK is installed.")

if __name__ == "__main__":
    
    bytecodeFile = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/classes/org/joda/time/Years.class'
    bytecodeTestFile = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/test-classes/org/joda/time/format/RegressionTest0.class'
    # parse_bytecode(bytecodeFile)
    method_name = 'test001'
    bytecodeInString = parse_method_bytecode(bytecodeTestFile, method_name)


