goog.provide('webapi.discovery.RestDescription');
goog.require('goog.structs.Map');
goog.require('webapi.discovery.Method');


/** A representation state transfer description of an API.

    https://developers.google.com/discovery/v1/reference/apis
 
    todo: process schema references
    todo: process required arguments
    todo: rest descriptions are handled slightly different than rpc (undocumented)
 
    @constructor 
*/
webapi.discovery.RestDescription = function (data) {
  this.sourceData = data;
  this.data = new goog.structs.Map(data);
  this.methods = new goog.structs.Map();
  this.init()
};


webapi.discovery.RestDescription.prototype.init = function () {
  this.processRoot_(this.sourceData)
};


webapi.discovery.RestDescription.prototype.getOauthScopes = function () {
  return goog.object.getKeys(this.data['auth']['oauth2']['scopes'])
};


webapi.discovery.RestDescription.prototype.getName = function () {
  return this.data.get('name');
};


webapi.discovery.RestDescription.prototype.getVersion = function () {
  return this.data.get('version');
};


webapi.discovery.RestDescription.prototype.getBatchPath = function () {
  return this.data.get('batchPath');
};


webapi.discovery.RestDescription.prototype.getServicePath = function () {
  return this.data.get('servicePath');
};


webapi.discovery.RestDescription.prototype.getRootUrl = function () {
  return this.data.get('rootUrl')
};


webapi.discovery.RestDescription.prototype.getMethodIds = function () {
  return this.methods.getKeys();
};


webapi.discovery.RestDescription.prototype.registerMethod = function (method) {
  this.methods.set(method.getId(), method)
};


webapi.discovery.RestDescription.prototype.processRoot_ = function(root){  
  for (var name in root) {
    if (!root.hasOwnProperty(name)) {
      continue;
    }
    
    if (name === 'methods') {
      
      this.processMethods_(root[name]);
    } 
    else if (name === 'resources') {
      for (var resource in root[name]) {
        if(root[name].hasOwnProperty(resource)) {
          this.processResources_(root[name][resource]);
        }
      }
    }
  }
};


webapi.discovery.RestDescription.prototype.processResources_ = function(resp){
  for (var name in resp['resources']) {
    if (!resp['resources'].hasOwnProperty(name)) {
      continue;
    }
    var resource = resp['resources'][name];
    
    if (resource['methods']) {
      
      this.processMethods_(resource['methods']);
    } 
    else if (name === 'resources') {
      for (var resourceName in resp[name]) {
        if(resp[name].hasOwnProperty(resourceName)) {
          this.processResources_(resp[name][resourceName]);
        }
      }
    }
  }
};


webapi.discovery.RestDescription.prototype.processMethods_ = function (resp) {
  console.log('Process methods', resp);
  for (var name in resp) {
    if (!resp.hasOwnProperty(name)) {
      continue;
    }
    this.registerMethod(new webapi.discovery.Method(resp[name]));
  }
};

