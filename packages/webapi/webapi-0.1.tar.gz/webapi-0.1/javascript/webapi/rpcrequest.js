goog.provide('webapi.RpcRequest');
goog.require('webapi.HttpRequest');



/** Encapsulates an rpc request
  
    http://www.jsonrpc.org/specification
*/
webapi.RpcRequest = function (xhr, url, methodId, opt_httpMethod, opt_id) {
  var url = new goog.Uri(url);
  url.setPath(url.getPath()+'/'+methodId);

  goog.base(this, xhr, url.toString(), opt_httpMethod || 'POST');
  this.methodId = methodId;
  this.id = opt_id || null;
  this.params = null;
  this.upload = null;
};
goog.inherits(webapi.RpcRequest, webapi.HttpRequest);


/** @type {string|number|null} */
webapi.RpcRequest.prototype.id;


/** @type {goog.net.XhrIo} */
webapi.RpcRequest.prototype.xhr;


/** @type {string} */
webapi.RpcRequest.prototype.url;


/** @type {string} */
webapi.RpcRequest.prototype.methodId;


/** @type {[*]} */
webapi.RpcRequest.prototype.params;


webapi.RpcRequest.prototype.setParams = function (params) {
  this.params = params;
};

webapi.RpcRequest.prototype.setUpload = function (file) {
  // TODO: should be able to use a pointer to a input element (for html5, and legacy)
  // legacy browsers will need to use external forces (flash/silverlight/otherwise)
  // to extract the filename and return a proper File-like object

  // http://www.w3.org/TR/FileAPI/#dfn-file
  if(!(file instanceof File)){
    throw goog.debug.Error('Unsupported upload type');
  }
  this.upload = file;
}


webapi.RpcRequest.prototype.encodeBody_ = function () {

  var body = {
    'jsonrpc': '2.0',
    'method': this.methodId
  }

  if (this.params !== null) {
    body['params'] = this.params;
  }

  if (this.id !== null) {
    body['id'] = this.id;
  }

  if(this.upload === null){
    return JSON.stringify(body);
  }


  if(!webapi.RpcRequest.FORMDATA_SUPPORT){
    /*

    TODO: we should be able to shim this object (build a http request with boundary; base64 encode)

    ie:

    var boundary = '-------314159265358979323846';
    var delimiter = "\r\n--" + boundary + "\r\n";
    var close_delim = "\r\n--" + boundary + "--";
    var base64Data = btoa(reader.result);

    var body = [
      delimiter,
      'Content-Type: application/json\r\n\r\n',
      JSON.stringify(body),
      delimiter,
      'Content-Type: ' + contentType + '\r\n',
      'Content-Transfer-Encoding: base64\r\n',
      '\r\n',
      base64Data,
      close_delim
    ];

    return body.join('');*/
    throw goog.debug.Error("Uploads are not supported without formdata.");
  }

  var body = new FormData();
  body.append('request', JSON.stringify(body));
  body.append('upload', this.upload);
  return body;
};


webapi.RpcRequest.prototype.handleComplete = function (deferred, e) {
  var response = e.target.getResponseJson();

  if (goog.isDef(response['error'])) {
    this.handleError(deferred, response);
    return
  }

  this.handleResult(deferred, response);
};


webapi.RpcRequest.prototype.handleResult = function (deferred, response) {
  deferred.callback(response['result'])
};


webapi.RpcRequest.prototype.handleError = function (deferred, response) {
  deferred.errback(response['error'])
};


webapi.RpcRequest.prototype.execute = function () {
  // encode the body before sending
  var request = this.buildRequest();
  return request;
};


webapi.RpcRequest.FORMDATA_SUPPORT = false;

if (goog.isFunction(goog.global['FormData']) && goog.global['File']){
  console.log("File API available, formData available");
  webapi.RpcRequest.FORMDATA_SUPPORT = true;
}