goog.provide('webapi.HttpRequest');
goog.require('goog.async.Deferred');



/** Encapsulates an http request
*/
webapi.HttpRequest = function (xhr, url, opt_httpMethod, opt_body) {
  this.xhr = xhr;
  this.url = url;
  this.httpMethod = opt_httpMethod || 'GET';
  this.body = opt_body || null;
  this.requestId = goog.string.getRandomString();
  this.headers = null;
};


webapi.HttpRequest.prototype.setHeaders = function (headers) {
  this.headers = headers;
};

webapi.HttpRequest.prototype.encodeBody_ = function () {
  return this.body;
}


webapi.HttpRequest.prototype.handleComplete = function (deferred, event) {
  // TODO: we might need more info in the callbacks than just the body
  if (event.target.getStatus() == 200) {
    deferred.callback(event.target.getResponseBody());
  }
  else {
    deferred.errback(event.target.getResponseBody());
  }
};


webapi.HttpRequest.prototype.buildRequest = function () {
  var request = new goog.async.Deferred();
  var callback = goog.partial(goog.bind(this.handleComplete, this), request);
  var body = this.encodeBody_();
  this.xhr.send('httprequest' + this.requestId, this.url, this.httpMethod, body, this.headers, null, callback);
  return request;
}


webapi.HttpRequest.prototype.execute = function () {
  var request = this.buildRequest();
  return request;
};


