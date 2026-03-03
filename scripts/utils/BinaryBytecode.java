package components;

import java.io.IOException;

public class BinaryBytecode {
	private String classFile;
	private String methodName;
	private String className;
	private byte [] bytecode;
	
	public BinaryBytecode(String file, String methodName, String className)
	{
		classFile = file;
		this.methodName = methodName;
		this.className = className;
	}
	
	public void loadMethod(String methodDescriptor) throws IOException
	{
		bytecode =  BytecodeExtractor.getMethodBytecode(classFile, methodName, methodDescriptor);
	}
	
	public String getMethodName()
	{
		return methodName;
	}
	
	public String getClassName()
	{
		return className;
	}
	
	public byte[] getBytecode()
	{
		return bytecode;
	}
	
	public String getCell()
	{
		return className + "::" + methodName;
	}
	
	public String toString()
	{
		StringBuilder output = new StringBuilder();
		output.append("Bytecode for " + getCell() + ": ");
		for (byte b : bytecode) {
			output.append( String.format("%02X ", b)) ;
        }
		return output.toString();
	}
}
