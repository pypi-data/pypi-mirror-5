goog.provide('webapi.Client');
goog.provide('webapi.RpcClient');
goog.provide('webapi.DiscoveryClient');
goog.provide('webapi.client');
goog.provide('webapi.client.rpc');
goog.provide('webapi.client.install');
goog.require('goog.net.XhrManager');
goog.require('webapi.discovery.RestDescription');
goog.require('webapi.RpcRequest');




/**
 @constructor
 */
webapi.HttpClient = function(){  
  this.xhr = new goog.net.XhrManager();
};



/**
 @constructor
 */
webapi.RpcClient = function(rpcUrl){  
  goog.base(this);
  this.rpcUrl = rpcUrl;
};
goog.inherits(webapi.RpcClient, webapi.HttpClient);

webapi.RpcClient.prototype.getMethodRpcUrl = function (methodId) {
  return this.rpcUrl;
};

webapi.RpcClient.prototype.executeMethod = function (methodId, opt_params) {
  var xhr = this.xhr;
  var rpcUrl = this.getMethodRpcUrl(methodId);
  var request = new webapi.RpcRequest(xhr, rpcUrl, methodId);

  if (goog.isDef(opt_params)) {
    request.setParams([opt_params]);
  }

  return request.execute();
};




/**
 @constructor
 */
webapi.DiscoveryClient = function () {
  goog.base(this);
  this.loader = new webapi.Loader();
  this.methodMap = new goog.structs.Map();
};
goog.inherits(webapi.DiscoveryClient, webapi.RpcClient);

// one discovery client should do the job
goog.addSingletonGetter(webapi.DiscoveryClient);

/** @type {webapi.Loader} */
webapi.DiscoveryClient.loader;


/** @const */
webapi.DiscoveryClient.PREFIX = 'webapi';


webapi.DiscoveryClient.prototype.getPrefix = function() {
  return webapi.Client.PREFIX;
};


webapi.DiscoveryClient.prototype.registerMethod = function(restDescription, methodName) {
  console.log('Register method', methodName);
  this.methodInformation.set(methodName, restDescription);
};


webapi.DiscoveryClient.prototype.getRestDescriptionForMethod = function(methodId) {
  return this.methodMap.get(methodId);
};


webapi.DiscoveryClient.prototype.getMethodRpcUrl = function (methodId) {
  var restDescription = this.getRestDescriptionForMethod(methodId);
  return restDescription.getRootUrl() + restDescription.getServicePath();
};


webapi.DiscoveryClient.prototype.exportMethod = function (restDescription, methodName) {
  //var api = goog.getObjectByName(method, osapi);
  //goog.exportSymbol(method, api);

  // a function that returns a fully constructed/executed webapi.RpcRequest 
  var apiMethod = goog.bind(function (params) {
    return this.executeMethod(methodName, params);
  }, this);

  // create a local method, eg apiclient.apiname.resource.method
  goog.exportSymbol(this.getPrefix() + methodName, apiMethod);
};


/** Loads an api from a directory root.
    @return {goog.async.Deferred} Called back when the api is loaded.
*/
webapi.DiscoveryClient.prototype.load = function(apiName, apiVersion, root) {
  var request = this.loader.load(apiName, apiVersion, root);
  
  return request.addCallback(function(restDescription){
    this.loadRestDescription(restDescription);    
  }, this);
};


/** Loads a RestDescription document; registering its methods.
    @param {webapi.discovery.RestDescription} restDescription 
*/
webapi.DiscoveryClient.prototype.loadRestDescription = function(restDescription) {  
  // TODO: use more information to register methods
  goog.array.map(restDescription.getMethodIds(), function(methodId){
    this.registerMethod(restDescription, methodId);  
  }, this);
};



/** Creates and executes an rpc request.
    @return {goog.async.Deferred} 
*/
webapi.client.rpc = function(methodId, opt_params, opt_file){
  // TODO: if the file object is supported
  var client = webapi.client.getClient_();
  return client.executeMethod(methodId, opt_params)
};



/** Load an api into the namespace. */
webapi.client.load = function (apiName, apiVersion, root) {
  var client = webapi.client.getClient_();
  // TODO: make sure is a discovery client
  return client.load(apiName, apiVersion, root)
};


/** Load an raw rest description into the namespace. */
webapi.client.loadDescription = function (rawRestDescription) {
  var client = webapi.client.getClient_();
  var restDescription = new webapi.discovery.RestDescription(rawRestDescription);
  // TODO: make sure is a discovery client
  client.loadRestDescription(restDescription);
};



webapi.client_ = null;


webapi.client.getClient_ = function(client){
  if(webapi.client_ === null){
    throw goog.debug.Error("No webapi client installed.")
  }
  return webapi.client_ 
};


webapi.client.install = function(client){
  webapi.client_ = client;
};
  