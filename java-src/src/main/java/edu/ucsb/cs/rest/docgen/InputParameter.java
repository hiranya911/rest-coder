package edu.ucsb.cs.rest.docgen;

import edu.ucsb.cs.rest.api.Field;
import edu.ucsb.cs.rest.api.NamedInputBinding;
import edu.ucsb.cs.rest.api.Parameter;

public class InputParameter {

	String name;
	String mode;
	Object type;
	String description;
	boolean optional;
	String[] contentType;

	public InputParameter(String name, String mode, Object type, String description, boolean optional, String[] contentType) {
		this.name = name;
		this.mode = mode;
		this.type = type;
		this.description = description;
		this.optional = optional;
		this.contentType = contentType;
	}
	
	public InputParameter(NamedInputBinding inputBinding, Parameter parameter)
	{
		this.name = inputBinding.getName();
		this.mode = inputBinding.getMode();
		this.type = inputBinding.getType();
		this.description = parameter.getDescription();
		this.optional = parameter.isOptional();
		
	}
	
	public InputParameter(Field field, String[] contentType)
	{
		this.name = field.getName();
		this.mode = ""; //No relevant attribute on Field
		this.type = field.getType();
		this.description = field.getDescription();
		this.optional = field.isOptional();
		this.contentType = contentType;
	}
	
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getMode() {
		return mode;
	}
	public void setMode(String mode) {
		this.mode = mode;
	}
	public Object getType() {
		return type;
	}
	public void setType(Object type) {
		this.type = type;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}

	public boolean isOptional() {
		return optional;
	}

	public void setOptional(boolean optional) {
		this.optional = optional;
	}

	public String[] getContentType() {
		return contentType;
	}

	public void setContentType(String[] contentType) {
		this.contentType = contentType;
	}

	
	
}


