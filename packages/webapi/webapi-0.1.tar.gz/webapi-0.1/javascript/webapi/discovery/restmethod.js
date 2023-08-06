goog.provide('webapi.discovery.Method');
goog.require('goog.structs.Map');

/** @constructor */
webapi.discovery.Method = function (data) {
  this.data = new goog.structs.Map(data);
};


webapi.discovery.Method.prototype.getId = function (data) {
  return this.data.get('id')
};


/* returns true if this method supports media upload */
webapi.discovery.Method.prototype.supportsMediaUpload = function () {
  return this.data.get('supportsMediaUpload', false)
};


/* returns the mediaupload information */
webapi.discovery.Method.prototype.getMediaUpload = function () {
  return new goog.structs.Map(this.data.get('mediaUpload'))
};


/* return a list of accepted types */
webapi.discovery.Method.prototype.getMediaUploadAcceptTypes = function () {
  return this.getMediaUpload().get('accept')
};


/* Returns the max size of the media upload.. Eg 10gb */
webapi.discovery.Method.prototype.getMediaUploadMaxSize = function () {
  return this.getMediaUpload().get('maxSize')
};


webapi.discovery.Method.prototype.getMediaUploadProtocols = function () {
  return goog.object.getKeys(this.getMediaUpload().get('protocols'))
};


webapi.discovery.Method.prototype.getMediaUploadPath = function (protocol) {
  return this.getMediaUpload().get('protocols')[protocol]['path'];
};


webapi.discovery.Method.prototype.supportsSubscription = function () {
  return this.data.get('supportsSubscription', false)
};


webapi.discovery.Method.prototype.getScopes = function () {
  return this.data.get('scopes', []);
};