function generalRequest(requestObj, callback)
{
	//var orderId = "1ca0c4a9-9e91-4496-b15a-b65cac69cbd3";
	//console.log("OrderId on forward request: " + JSON.stringify(orderId))
	var request = require("request");
	request({
	    	uri: requestObj.baseUrl+requestObj.path,
	    	method: requestObj.method,
		dataType: "json",
		headers: {'Content-Type' : 'application/json'},
		body: JSON.stringify(requestObj.payload),
	    	timeout: 10000,
	    	followRedirect: true,
	    	maxRedirects: 10
	}, function(error, res, body) {
	
	    console.log("submitOrder: " + body);
	    callback(error, res,  body);
	  
	});

}
exports.generalRequest = generalRequest;

function submitOrder(jsonPayload, callback)
{
	var request = require("request");
	request({
		uri: "http://localhost:8888/starbucks-1.0-SNAPSHOT/starbucks/",
	 	method: "POST",
         	dataType: "json",
	 	headers: {'Content-Type' : 'application/json'},
	 	body: JSON.stringify(jsonPayload),
		timeout: 10000,
	    	followRedirect: true,
	    	maxRedirects: 10

	}, function(error, res, body) {
	  	console.log("submitOrder: " + body);
		callback(error, res, body);
	});

}

exports.submitOrder = submitOrder;

function getOrders(path, callback)
{
	//var orderId = "1ca0c4a9-9e91-4496-b15a-b65cac69cbd3";
	//console.log("OrderId on forward request: " + JSON.stringify(orderId))
	var request = require("request");
	request({
	    	uri: "http://localhost:8888/starbucks-1.0-SNAPSHOT/starbucks/"+path,
	    	method: "GET",
		dataType: "json",
		//data: JSON.stringify(orderId),
		headers: {'Content-Type' : 'application/json'},
	    	timeout: 10000,
	    	followRedirect: true,
	    	maxRedirects: 10
	}, function(error, res, body) {
	
	//console.log('HEADERS: ' + JSON.stringify(res.headers));
	    callback(error, res,  body);
	  
	});

}
exports.getOrders = getOrders;

function deleteOrder(path, callback)
{
	//var orderId = "1ca0c4a9-9e91-4496-b15a-b65cac69cbd3";
	//console.log("OrderId on forward request: " + JSON.stringify(orderId))
	var request = require("request");
	request({
	    	uri: "http://localhost:8888/starbucks-1.0-SNAPSHOT/starbucks/"+path,
	    	method: "DELETE",
		dataType: "json",
		//data: JSON.stringify(orderId),
		headers: {'Content-Type' : 'application/json'},
	    	timeout: 10000,
	    	followRedirect: true,
	    	maxRedirects: 10
	}, function(error, res, body) {
	
	//console.log('HEADERS: ' + JSON.stringify(res.headers));
	    callback(error, res,  body);
	  
	});

}
exports.deleteOrder = deleteOrder;

