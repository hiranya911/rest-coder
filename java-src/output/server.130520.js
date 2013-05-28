var http = require('http'),
fs = require('fs'),
connect = require('connect'),
getOrders = require('./getOrders.js');

fs.readFile('/home/stratos/docgen/output/index.html', function (err, htmlContent)
{

    connect.createServer(function (req, res) {
	console.log('request received');
	
	
	  if (req.url === '/getOrders') {
	    res.writeHead(200, {'Content-Type': 'text/json'});
	    res.end(JSON.stringify(getOrders));
	  } 
	else {
	
	    res.writeHead(200, {'Content-Type': 'text/html'});
	    res.end(htmlContent);  
	}
	
	//res.writeHead(200, {'Content-Type': 'appplication/json'});
	//console.log(getOrders);
	//res.end(getOrders);
	//res.end('_testcb(\'{"message": "Hello world!"}\')');
    }).listen(8124);
    console.log('Server running at http://127.0.0.1:8124/');
});
/*
var http = require('http'),
    ajaxResponse = { 'hello': 'world' },
    htmlContent;

htmlContent  = "<html><title></title><head>";
htmlContent += "<script src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js'></script>";
htmlContent += "<script>$(function() {$.ajax({url:'/ajax',success:function(data){alert('success!');console.log(data);},error:function(data){alert('error!');}});});</script>";
htmlContent += "</head><body><h1>Hey there</h1>";
htmlContent += "<div class='test'></div>"
htmlContent +="</body></html>";

http.createServer(function (req, res) {   
  if (req.url === '/ajax') {
    res.writeHead(200, {'Content-Type': 'text/json'});
    res.end(JSON.stringify(ajaxResponse));
  } else {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(htmlContent);  
  }  
}).listen(1337, '127.0.0.1');
console.log('Server running at http://127.0.0.1:1337/');
*/
/*
var request = require("request");
request({
  uri: "http://localhost:8080/starbucks-1.0-SNAPSHOT/starbucks/",
  method: "GET",
  timeout: 10000,
  followRedirect: true,
  maxRedirects: 10
}, function(error, response, body) {
  console.log(body);
});

*/