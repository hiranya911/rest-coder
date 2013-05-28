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
