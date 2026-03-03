package components;

import org.objectweb.asm.*;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class BytecodeExtractor {
    public static byte[] getMethodBytecode(String classFilePath, String methodName, String methodDescriptor) throws IOException {
        // Load the .class file
        InputStream classFileStream = Files.newInputStream(Paths.get(classFilePath));
        
        // List to store bytecode of the method
        List<Byte> bytecodeList = new ArrayList<>();
        
        // Set up ASM to read the .class file and look for the method
        ClassReader classReader = new ClassReader(classFileStream);
        classReader.accept(new ClassVisitor(Opcodes.ASM9) {
            @Override
            public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                // Check if this is the method we want
                if (name.equals(methodName) && descriptor.equals(methodDescriptor)) {
                    return new MethodVisitor(Opcodes.ASM9) {
                        @Override
                        public void visitCode() {
                            // Called at the start of the method
                            super.visitCode();
                        }

                        @Override
                        public void visitInsn(int opcode) {
                            // Collect the opcode in the bytecode list
                            bytecodeList.add((byte) opcode);
                            super.visitInsn(opcode);
                        }

                        @Override
                        public void visitIntInsn(int opcode, int operand) {
                            // Collect instruction and operand
                            bytecodeList.add((byte) opcode);
                            bytecodeList.add((byte) operand);
                            super.visitIntInsn(opcode, operand);
                        }

                        // Implement other visit* methods as needed for different instruction types.
                        // Each instruction has different parameters and requires handling accordingly.

                        @Override
                        public void visitMaxs(int maxStack, int maxLocals) {
                            super.visitMaxs(maxStack, maxLocals);
                        }

                        @Override
                        public void visitEnd() {
                            super.visitEnd();
                        }
                    };
                }
                return null; // Ignore other methods
            }
        }, 0);

        // Convert List<Byte> to byte[]
        byte[] bytecodeArray = new byte[bytecodeList.size()];
        for (int i = 0; i < bytecodeList.size(); i++) {
            bytecodeArray[i] = bytecodeList.get(i);
        }
        return bytecodeArray;
    }
    
    public static int levenshteinDistance(byte[] a, byte[] b) {
        int[][] dp = new int[a.length + 1][b.length + 1];

        // Initialize the dp table
        for (int i = 0; i <= a.length; i++) dp[i][0] = i;
        for (int j = 0; j <= b.length; j++) dp[0][j] = j;

        // Fill the dp table
        for (int i = 1; i <= a.length; i++) {
            for (int j = 1; j <= b.length; j++) {
                int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
                dp[i][j] = Math.min(dp[i - 1][j] + 1,      // Deletion
                            Math.min(dp[i][j - 1] + 1,     // Insertion
                                     dp[i - 1][j - 1] + cost)); // Substitution
            }
        }
        return dp[a.length][b.length];
    }
    
    public static double euclideanDistance(byte[] a, byte[] b) {
        if (a.length != b.length) {
            throw new IllegalArgumentException("Byte arrays must be of equal length");
        }

        int sum = 0;
        for (int i = 0; i < a.length; i++) {
            int diff = a[i] - b[i];
            sum += diff * diff;
        }
        return Math.sqrt(sum);
    }
    
    public static List<BinaryBytecode> getAllBytecodeMethods(String testcasesFile, String testType) throws IOException
    {
    	List<BinaryBytecode> allMethods = new ArrayList<BinaryBytecode>();
    	
    	String methodDescriptor = "()V";
    	String bytecodeFile = "";
    	String className = "";
    	String methodName = "";
    	// Regular expression to match the desired format
        String regex = "^test\\d+$";
    	
    	try (BufferedReader fileReader = new BufferedReader(new FileReader(testcasesFile))) {
			List<Object> allLines = fileReader.lines().collect(Collectors.toList());
			
			// start parsing the test cases
			for(int i=0;i<allLines.size();i++)
			{	
				String curLine = ((String)allLines.get(i)).trim();
				if(curLine.startsWith("Bytecode File: "))
				{
					// Get the path of the .class file
					int colPos = curLine.indexOf("/resources/subjects");
					bytecodeFile = "/home/islam/MyWork/New-work-2023/DBT-workbench" + curLine.substring(colPos).trim();
				}
				else if(curLine.startsWith("Class name: "))
				{
					// Get the name of the class
					int colPos = curLine.indexOf(':');
					className = curLine.substring(colPos+1).trim();
				}
				else if(curLine.startsWith("Method name: "))
				{
					// Get the name of the method
					int colPos = curLine.indexOf(':');
					methodName = curLine.substring(colPos+1).trim();
				}
				else if(curLine.startsWith("Method source code:"))
				{
					if(testType.equals("Randoop") && !className.startsWith("RegressionTest"))
						continue;
					else if(testType.equals("Evosuite") && !className.endsWith("_ESTest"))
						continue;
					else if(testType.equals("Developer") && (methodName.matches(regex) && (className.endsWith("_ESTest") || className.startsWith("RegressionTest"))))
						continue;
					// Parse the method and reset for next method
					BinaryBytecode curObj = new BinaryBytecode(bytecodeFile, methodName, className);
					curObj.loadMethod(methodDescriptor);
					allMethods.add(curObj);
					
				}
			}
		}
    	return allMethods;
    }
    
    public static Map<String, Object> getSimMatrix(List<BinaryBytecode> allMethods)
    {
    	// Build the dictionary
    	Map<String, Object> matrix=new HashMap<String, Object>();
    	for(BinaryBytecode mtd1 : allMethods)
    	{
    		Map<String, Integer> record=new HashMap<String, Integer>();
    		for(BinaryBytecode mtd2 : allMethods)
        	{
    			record.put(mtd2.getCell(), 0);
        	}
    		matrix.put(mtd1.getCell(), record);
    	}
    	
    	for(int i = 0; i<allMethods.size();i++)
    	{
    		String curMethod = allMethods.get(i).getCell();
    		for (int j = i; j<allMethods.size();j++)
    		{
    			
    			if(i!=j)
    			{
    				String otherMethod = allMethods.get(j).getCell();
    				int distance = levenshteinDistance(allMethods.get(i).getBytecode(), allMethods.get(j).getBytecode());
    				
    				Map<String, Integer> record1 = (Map<String, Integer>) matrix.get(curMethod);    				
    				record1.put(otherMethod, distance);
    				
    				Map<String, Integer> record2 = (Map<String, Integer>) matrix.get(otherMethod);    				
    				record2.put(curMethod, distance);
    			}
    		}
    	}
    	
    	return matrix;
    }
    
    public static String getHeader(Map<String, Object> matrix)
    {
    	TreeSet<String> myTreeSet = new TreeSet<String>(matrix.keySet());
    	String header = ":,";
    	for(String key : myTreeSet)
    		header += key + ",";
    	
    	return header;
    }
    
    public static String getRecord(Map<String, Object> matrix, String recordKey)
    {
    	TreeSet<String> myTreeSet = new TreeSet<String>(matrix.keySet());
    	Map<String, Integer> record = (Map<String, Integer>) matrix.get(recordKey);
    	String line = recordKey + " ,";
    	for(String key : myTreeSet)
    	{
    		 line += record.get(key) + ",";
    	}

    	return line;
    }
    
    public static void writeMatrixToCSV(Map<String, Object> matrix, String csvFile)
    {
    	TreeSet<String> myTreeSet = new TreeSet<String>(matrix.keySet());
    	File csvOutputFile = new File(csvFile);
        try (PrintWriter pw = new PrintWriter(csvOutputFile)) {
        	pw.println(getHeader(matrix));
        	
        	for(String key : myTreeSet)
        	{
        		// Get that record
        		String line = getRecord(matrix, key);
        		pw.println(line);
        	}
        } catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }

    public static void main(String[] args) {
    	String prj = "lang";
    	String testType = "Developer";
    	String [] projects = new String[0];
    	
    	if(prj == "math")
    	    projects = new String[] {"4", "5", "6", "9", "13", "14", "17", "18", "19", 
    	                "20", "21", "23", "24", "25", "26", "27", "28", 
    	                "30", "32", "33", "37", "42", "47", "49", "50", 
    	                "51", "52", "54", "56", "58", "61", "64", "65", 
    	                "67", "68", "69", "70", "73", "78", "76", "80", "81"};

    	// jsoup projects:
    	else if (prj == "jsoup")
    	    projects = new String[] {"4", "15", "16", "19", "20", "26", "27", "29", 
    	                "30", "33", "35", "36", "37", "38", "39", "40"};

    	// lang projects:
    	else if (prj == "lang")
    	    projects = new String[] {"4", "6", "15", "16", "17", "19", "22", "23", 
    	    		"24", "25", "27", "28", "31", "33", "35"};

    	// time projects:
    	else if (prj == "time")
    		projects = new String[] {"11","13"};

    	// cli projects:
    	else if (prj == "cli")
    	    projects = new String[] {"30","31","32","33","34"};

    	// csv projects:
    	else if (prj == "csv")
    	    projects = new String[] {"2", "3", "4", "5", "7", "8", "10", "11", "12", "16"};

    	// compress projects:
    	else if (prj == "compress")
    	    projects = new String[] {"1", "11", "16", "22", "24", "26", "27"};
    	
    	double totalTimeForProject = 0;
    	for(String ver : projects)
    	{
    		double totalInSecs = 0;
    		String filePath = "/home/islam/MyWork/New-work-2023/DBT-workbench/resources/similarity/" + prj + "/" + prj + "." + ver + "f.test-cases.txt";
    		String csvPath = "/home/islam/MyWork/New-work-2023/DBT-workbench/resources/similarity/" + prj + "/" + prj + "." + testType + "." + ver + "f.byteCodeSimilarity.bytes.csv";
    		try {
    			long startTime = System.currentTimeMillis();
    			List<BinaryBytecode> allMethods = getAllBytecodeMethods(filePath, testType);
    			double estimatedTime = (System.currentTimeMillis() - startTime)/1000.;
    			totalInSecs += estimatedTime;
    			
    			//System.out.println("Time of collecting bytecode: " + (estimatedTime) + " sec");
    			
    			/*for(BinaryBytecode mtd : allMethods)
    				System.out.println(mtd);*/

    			startTime = System.currentTimeMillis();
    			Map<String, Object> matrix = getSimMatrix(allMethods);
    			estimatedTime = (System.currentTimeMillis() - startTime)/1000.;
    			//System.out.println("Time of constructing sim matrix: " + (estimatedTime/1000.) + " sec");
    			totalInSecs += estimatedTime;
    			
    			totalTimeForProject += totalInSecs;
    			writeMatrixToCSV(matrix, csvPath);

    		} catch (IOException e) {
    			// TODO Auto-generated catch block
    			e.printStackTrace();
    		}
    		System.out.println(ver + " is complete in " + totalInSecs + " sec");
//    		try {
//				TimeUnit.SECONDS.sleep(3);
//			} catch (InterruptedException e) {
//				// TODO Auto-generated catch block
//				e.printStackTrace();
//			}
    	}
    	
    	System.out.println("Done in total of " + totalTimeForProject + " sec");
//        try {
//            // Specify the path to the .class file, method name, and descriptor
//            String classFilePath = "/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/test-classes/org/joda/time/format/RegressionTest0.class";
//            String methodName1 = "test110";  // Replace with the method name
//            String methodName2 = "test014";  // Replace with the method name
//            String methodName3 = "test080";  // Replace with the method name
//            String methodDescriptor = "()V";      // Replace with the correct descriptor, e.g., "(I)V" for a method with int param and void return
//
//            byte[] bytecode1 = getMethodBytecode(classFilePath, methodName1, methodDescriptor);
//            byte[] bytecode2 = getMethodBytecode(classFilePath, methodName2, methodDescriptor);
//            byte[] bytecode3 = getMethodBytecode(classFilePath, methodName3, methodDescriptor);
//
//            
//            int distance = levenshteinDistance(bytecode1, bytecode2);
//            System.out.println("Levenshtein Distance (test110 and test014): " + distance);
//            
//            distance = levenshteinDistance(bytecode2, bytecode3);
//            System.out.println("Levenshtein Distance (test014 and test080): " + distance);
//        } catch (IOException e) {
//            e.printStackTrace();
//        }
    }
}
