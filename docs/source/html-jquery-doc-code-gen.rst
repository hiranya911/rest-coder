HTML/ JQuery API Doc and Code Generator
=======================================

The HTML/ JQuery API doc and code generator autogenerates HTML code augmented with JQuery code to allow users to view API documentation an a clear HTML format and directly interact with the API invoking the various operations that it supports. The only input required is the JSON based API description as described earlier. The tool is consituted from 3 different parts:

* An html UI generator coded with JAVA
* A JQuery client who is able to get the posted user information from the UI, recognize the operation it belongs to and send it to the proxy server
* A proxy server builded with NodeJS that forwards the above request to the server that hosts the API

The html UI generator will output an index.html file that contains all the documentation. All the elements and placeholders are structured and named in such away that each HTTP request can be uniquely identified by the JQuery client. The JQuery client reads this information and makes an asynchronous call to the NodeJS server, who in turn also makes an asychronous HTTP request to the API server. When the necessary information is returned the NodeJS server pushes the information back to the JQuery client that finally injects it on the appropriate fields of the user interface.

Using the Doc Generator
-----------------------
To run the code you need to be on the java-lib directory and type the following command that runds the code and takes as argument the API description. ::

	~/rest-coder/java-lib$ ./jsgen.sh ../java-src/input/starbucks.json

and the expected output after you run this command should be: ::
 
	Code successfully generated!

Of course if you prefer you can setup the code in Eclipse or the IDE of your preference and run this code by specifing the necessary argument through the project properties.

Generated Code
---------------

The output of the above command writes all the documentation in a signle index.html file that is saved inside the api-proxy/public/ directory.
This directory contains all the necessary files (CSS, Javascript etc) that are needed to display the user interface. NodeJS serves our html code by reading from those directories. So it is important to maintain the same structure. 


Setting up NodeJS/ Express
--------------------------

To use the generated code you have to first install NodeJS which is the technology we used to build our reverse proxy server, required to overcome the same origin security policy constrain that doesn't allow us to directly send our requests from the user interface to the API server.

In order to install NodeJS and the requirements for this particular application you have to do the following: ::

	Install nodejs: http://howtonode.org/how-to-install-nodejs
	Install npm: http://howtonode.org/introduction-to-npm
	npm install request
	npm install jquery
	npm install jsdom
	npm install connect 
	npm install express 
	npm install consolidate

Using the Generated Code
-------------------------

After completing the step above all you have to do is to oper a browser and use http://localhost:3000/index.html as the address.
You should be able to see the resources of the starbucks API, and be able to expand them in order to see the different operations they support.


Contents:

.. toctree::
   :maxdepth: 2

   Installing NodeJS
  

