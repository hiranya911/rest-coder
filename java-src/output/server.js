var express = require('express')
, http = require('http');

var app = express();
app.listen(3000);

app.configure(function (){
    app.use(express.static(__dirname + '/home/stratos/docgen/output/'));
});