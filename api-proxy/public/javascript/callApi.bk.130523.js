
submitOperation = function ( event ){

var requestObj =
{
	url: 'http://localhost:3000/',
	type:"POST",
	data: {
		baseUrl: "http://localhost:8888/starbucks-1.0-SNAPSHOT/starbucks/", 
		path: "",
		payload:{drink: "fredoccino"}
		},
        cache: false,
        timeout: 5000,
        success: function(payload) {
	
		$(".request_url").append(payload.request_url);
		$(".response_body").append(syntaxHighlight(payload.body));
		$(".response_code").append(payload.code);
		$(".response_headers").append(syntaxHighlight(payload.headers));
        
	},
        error: function(jqXHR, textStatus, errorThrown) {
		//alert(jqXHR);
		//$(".request_url").append(jqXHR.request_url);
		$(".response_code").append(jqXHR.status);
		$(".response_body").append(syntaxHighlight(jqXHR.responseText));
		$(".response_headers").append(syntaxHighlight(jqXHR.getResponseHeader));
	
        }

};

jQuery.ajax(requestObj);

};


/*
submitOperation = function( event ) {

    $.ajax({
        url: "http://localhost:3000/",
	dataType: "json",
        type: "POST",
	data: { drink: "frappessss"},
	cache: false,
        timeout: 5000,
        success: function(payload) {
	
            $(".response_body").append(payload.body);
	    $(".response_code").append(payload.code);
	    $(".response_headers").append(payload.headers);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert('error ' + textStatus + " " + errorThrown);
        }
    });
};

/*
 $.ajax({
        url: 'http://localhost:3000/',
        dataType: "json",
	type:"GET",
	data: {path: "1ca0c4a9-9e91-4496-b15a-b65cac69cbd3"},
        cache: false,
        timeout: 5000,
        success: function(payload) {
	
		$(".request_url").append(payload.request_url);
		$(".response_body").append(syntaxHighlight(payload.body));
		$(".response_code").append(payload.code);
		$(".response_headers").append(syntaxHighlight(payload.headers));
        
	},
        error: function(jqXHR, textStatus, errorThrown) {
		//alert(jqXHR);
		//$(".request_url").append(jqXHR.request_url);
		$(".response_code").append(jqXHR.status);
		$(".response_body").append(syntaxHighlight(jqXHR.responseText));
		$(".response_headers").append(syntaxHighlight(jqXHR.getResponseHeader));
        
		
        }
    });


--------------------------------------

obj = {
          type: this.model.httpMethod,
          url: invocationUrl,
          headers: headerParams,
          data: bodyParam,
          dataType: 'json',
          processData: false,
          error: function(xhr, textStatus, error) {
            return _this.showErrorStatus(xhr, textStatus, error);
          },
          success: function(data) {
            return _this.showResponse(data);
          },
          complete: function(data) {
            return _this.showCompleteStatus(data);
          }
        };
        if (obj.type.toLowerCase() === "post" || obj.type.toLowerCase() === "put" || obj.type.toLowerCase() === "patch") {
          obj.contentType = "application/json";
        }
        if (isFileUpload) {
          obj.contentType = false;
        }
        paramContentTypeField = $("td select[name=contentType]", $(this.el)).val();
        if (paramContentTypeField) {
          obj.contentType = paramContentTypeField;
        }
        responseContentTypeField = $('.content > .content-type > div > select[name=contentType]', $(this.el)).val();
        if (responseContentTypeField) {
          obj.headers = obj.headers != null ? obj.headers : {};
          obj.headers.accept = responseContentTypeField;
        }
        jQuery.ajax(obj);

----------------------------------------
obj = 
        type: @model.httpMethod
        url: invocationUrl
        headers: headerParams
        data: bodyParam
        contentType: consumes
        dataType: 'json'
        processData: false
        error: (xhr, textStatus, error) =>
          @showErrorStatus(xhr, textStatus, error)
        success: (data) =>
          @showResponse(data)
        complete: (data) =>
          @showCompleteStatus(data)

*/

function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

cleanResponse = function(response) {
      var prettyJson;
      prettyJson = JSON.stringify(response, null, "\t").replace(/\n/g, "<br>");
      return escape(prettyJson);
    };
