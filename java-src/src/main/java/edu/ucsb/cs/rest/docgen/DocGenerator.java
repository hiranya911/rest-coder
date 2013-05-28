package edu.ucsb.cs.rest.docgen;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.io.Writer;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.Velocity;
import org.apache.velocity.exception.MethodInvocationException;
import org.apache.velocity.exception.ParseErrorException;
import org.apache.velocity.exception.ResourceNotFoundException;

import edu.ucsb.cs.rest.api.API;
import edu.ucsb.cs.rest.api.Field;
import edu.ucsb.cs.rest.api.Header;
import edu.ucsb.cs.rest.api.NamedInputBinding;
import edu.ucsb.cs.rest.api.NamedTypeDef;
import edu.ucsb.cs.rest.api.Operation;
import edu.ucsb.cs.rest.api.Parameter;
import edu.ucsb.cs.rest.api.Resource;
import edu.ucsb.cs.rest.parser.APIDescriptionParser;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;



public class DocGenerator {

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException {
		
		API api = APIDescriptionParser.parseFromFile(args[0]); //APIDescriptionParser.parseFromFile("input/starbucks.json");
		PrintWriter out = new PrintWriter(new FileWriter(args[1]));//new PrintWriter(new FileWriter("/home/stratos/apiProxy/public/index.html"));
		Writer writer = new StringWriter();
		Velocity.init();
		
		Template headerTemplate = Velocity.getTemplate("templates/velocity/header.vm");
		Template resourceTemplate = Velocity.getTemplate("templates/velocity/resource.vm");
		Template resourceEndTemplate = Velocity.getTemplate("templates/velocity/resourceEnd.vm");
		Template operationTemplate = Velocity.getTemplate("templates/velocity/operation.vm");
		Template footerTemplate = Velocity.getTemplate("templates/velocity/footer.vm");
		
		String resourceName, path = "";
		NamedInputBinding[] namedInputBindings;
		NamedTypeDef[] namedTypeDefs = api.getDataTypes();
		List<InputParameter> inputParameters; //Input parameters per operations. Formed with the inputBindings
		String baseUrl = api.getBase()[0];
		
		//\\\\\\\\\\\\\\ Building the Header \\\\\\\\\\\\\\
		VelocityContext headerContext = new VelocityContext();
		headerContext.put("apiName", api.getName());
		headerTemplate.merge(headerContext, writer);
		
		try
		{
			for (Resource resource : api.getResources())
			{
				resourceName = resource.getName();
				path = resource.getPath();
				namedInputBindings = resource.getInputBindings();
				
				VelocityContext resourceContext = new VelocityContext();
				
				resourceContext.put("resourceName", resourceName);
				resourceContext.put("path", path);
				resourceContext.put("inputBindings", namedInputBindings);

				resourceTemplate.merge(resourceContext, writer);
				
				//Print list of operations
				int number = 0; //Number of operation for this particular resource
				for (Operation operation : resource.getOperations())
				{
					inputParameters = new ArrayList<InputParameter>();//The parameters array to pass on velocity
					
					
					VelocityContext operationContext = new VelocityContext();
					
					operationContext.put("operationName", operation.getName());
					operationContext.put("resourceName", resourceName);
					operationContext.put("description", operation.getDescription());
					operationContext.put("path", path);
					operationContext.put("errors", operation.getErrors());
					operationContext.put("httpMethod", operation.getMethod().toLowerCase());
					operationContext.put("input", operation.getInput());
					operationContext.put("number", number);
					operationContext.put("baseUrl", baseUrl);
					number++;
					
					try
					{
						//1. Search if there is defined a type for the input and if it matches to a defined Data type
						if(operation.getInput().getType() != null)
						{
							for (NamedTypeDef namedTypeDef: namedTypeDefs)
							{
								if (namedTypeDef.getName().equals(operation.getInput().getType()))
								{					
									for (Field field : namedTypeDef.getFields())
										inputParameters.add(new InputParameter(field, operation.getInput().getContentType()));
								}
							}
						}
						
						//2. Search if there are parameters and if they match with the bindings specified by the resource
						if (operation.getInput().getParams() != null)
						{
							for (Parameter param : operation.getInput().getParams())
							{
								for (NamedInputBinding inputBinding: namedInputBindings)
								{
									if (inputBinding.getId().equals(param.getBinding()))
									{
										inputParameters.add(new InputParameter(inputBinding, param));			

									}
								}
							}
						}
						
						if(!inputParameters.isEmpty())
							operationContext.put("inputParameters", inputParameters);
						
					}
					catch (NullPointerException npe)
					{
						//Do nothing
					}
					operationContext.put("output", operation.getOutput());
					operationTemplate.merge(operationContext, writer);

				}
				
				VelocityContext resourceEndContext = new VelocityContext();
				resourceEndTemplate.merge(resourceEndContext, writer);
			}
			
			//\\\\\\\\\\\\\\ Building the Footer \\\\\\\\\\\\\\
			VelocityContext footerContext = new VelocityContext();
		
			footerContext.put("baseUrls", api.getBase());
			footerContext.put("license", api.getLicense());
			footerContext.put("community", api.getCommunity());
			//Get Owners
			//Get Security
			//Get SLAs
			footerTemplate.merge(footerContext, writer);
	
			out.print(writer);
			out.close();
			//System.out.println(writer);
			System.out.println("Code successfully generated!");
		}
		catch (ResourceNotFoundException rnfe)
		{
			//couldn't find the template
		}
		catch (ParseErrorException pee)
		{
			// syntax error : problem parsing the template
		}
		catch (MethodInvocationException mie)
		{
			// Sth invoked in the template threw an exception
		}
		
	}

}
