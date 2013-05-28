
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , http = require('http')
, path = require('path');

var app = express();

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.methodOverride());
app.use(express.cookieParser('your secret here'));
app.use(express.session());
app.use(app.router);
  app.use(require('stylus').middleware(__dirname + '/public'));
app.use(express.static(path.join(__dirname, 'public')));

/*
* Included js files
*/
var forwardRequest = require('./public/forwardRequest.js');
// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

//var engines = require('consolidate');
//app.get('/', routes.index);
//app.engine('.html', require('ejs'));

/*
app.get('/', function(req, res)
{
    res.render('public/index.html');
});
*/
/*
This will try to read the index.ejs file from the views directory
app.get('/', function(req, res){
    res.render('index');
});
*/


http.createServer(app).listen(app.get('port'), function(req, res){
  console.log('Express server listening on port ' + app.get('port'));

    //Gets all requests (POST, GET, DELETE etc)
    app.all ('/',function (req, res){
	
	var fullURL = req.param('baseUrl') + req.param('path'); //path usually contains a parameter

	// Look at the get request that arrived and form the object to forward
	var requestObj =
	 {
	     baseUrl: req.param('baseUrl'),
	     path: req.param('path'),
	     method:req.method,
	     //contentType:req.headers['accept'],
	     //headers:JSON.stringify(req.headers),
	     payload:req.body.payload
	     	     
	 };
	

	console.log("------ Printing Request Obj -----");
	for (prop in requestObj)
	{
	    console.log(prop + ": " + requestObj[prop]);
	}
	console.log("payload: " + requestObj.payload);
	console.log("path: " + requestObj.path);


	forwardRequest.generalRequest(requestObj, function(error, response, body){

	    res.writeHead(response.statusCode, {'Content-Type': 'text/json'});//TODO: Replace the hard-coded text/json

	    //Form the payload to return to the UI, after the server sends the response
	    var payload = 
	    {
		"request_url" : fullURL,
		"headers" : JSON.stringify(response.headers), 
		"code" : response.statusCode,
		"body" : body
	    }
	    
	    console.log("---------- Payload --------");
	    console.log(payload);
	    res.end(JSON.stringify(payload));	    

	});
    });
    
});