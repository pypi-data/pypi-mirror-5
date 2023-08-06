goog.provide('webapi.Loader');
goog.require('webapi.Cache');
goog.require('webapi.discovery.DirecoryList');
goog.require('webapi.discovery.RestDescription');
goog.require('goog.async.Deferred');
goog.require('goog.Uri');

/*

X-ClientDetails:appVersion=5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.31%20(KHTML%2C%20like%20Gecko)%20Chrome%2F26.0.1410.63%20Safari%2F537.31&platform=Linux%20x86_64&userAgent=Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.31%20(KHTML%2C%20like%20Gecko)%20Chrome%2F26.0.1410.63%20Safari%2F537.31
X-Goog-Encode-Response-If-Executable:base64
X-JavaScript-User-Agent:google-api-javascript-client/1.1.0-beta
X-Origin:http://localhost:1234
X-Referer:http://localhost:1234
Origin:http://localhost:1234
*/

/** Loads an api directory for the client.
    @constructor 
*/
webapi.Loader = function(xhr) {
  this.xhr = xhr;
  this.cache_ = new webapi.Cache();
};
goog.addSingletonGetter(webapi.Loader);


/** the location of the discovery#directoryList from this.root 
    @const 
*/
webapi.Loader.DISCOVERY_DIRECTORY_PREFIX = '/discovery/v1/apis';


/** @type {goog.net.XhrIo} */
webapi.Loader.prototype.xhr_;


/** @type {webapi.Cache} */
webapi.Loader.prototype.cache_;


webapi.Loader.prototype.getHeaders = function() {
  var headers = {
    //'X-Origin': 'http://localhost:1234',
    //'X-ClientDetails:appVersion': '1234',
    //'X-Goog-Encode-Response-If-Executable': 'base64',
    'X-JavaScript-User-Agent': 'google-api-javascript-client/1.1.0-beta'
  };
  return headers;
};


webapi.Loader.prototype.makeGetRequest_ = function(url) {
  var deferred = new goog.async.Deferred();
  
  var callback = function(e){
    
    if(e.target.getStatus() == 200){
      deferred.callback(e.target.getResponseJson());
    }
    else {
      deferred.errback(e.target.getStatus())    
    }
      
    // TODO: handle errbacks
  };
  var headers = this.getHeaders();
  
  this.xhr.send('api-loader-request', url, 'GET', null, headers, null, callback);
  
  return deferred;
}

webapi.Loader.prototype.requestDirectoryList = function(root) {
  var requestDirectoryList = new goog.async.Deferred();
  
  // the directory list is not cached....
  // download the directory list, and eventually callback requestDirectoryList
  var directoryListUrl = this.buildDirectoryListUrl(root);
  
  var request = this.makeGetRequest_(directoryListUrl);
  
  request.addCallback(function(response){
    console.log('Processing directory response', response);
    
    
    var directoryList = new webapi.discovery.DirecoryList(response);
    
    console.log(this.cache_)
    // cache the directory list for later
    this.cache_.putDirectoryList(root, directoryList);
    
    requestDirectoryList.callback(directoryList);
  }, this);
  
  request.addErrback(function(response){
     console.error('Error loading directory', response);
    requestDirectoryList.errback()
  });
  
  return requestDirectoryList;
}

webapi.Loader.prototype.requestRestDescription = function(root, apiName, apiVersion) {
  
}

/** Returns a deferred called back with webapi.RestDescription.
 * 
    @param {string} apiName The api name.
    @param {string} apiVersion The api version.
    @param {string} root  The base url to load the directory list from.
    @return {goog.async.Deferred} Called back with a RestDescription. 
*/
webapi.Loader.prototype.load = function(apiName, apiVersion, root) {
  // check if the document is in the cache so we dont have to download
  var restDescription = this.cache_.getRestDescription(apiName, apiVersion);
  
  if(restDescription !== null){
    return goog.async.Deferred.succeed(restDescription);
  }
  
  var directoryList = this.cache_.getDirectoryList(root);
  
  var requestDirectoryList;
  
  if(directoryList !== null){
    requestDirectoryList = goog.async.Deferred.succeed(directoryList);
  }
  else {
    // the rest description is not cached........
    // download the discovery directory list
    requestDirectoryList = this.requestDirectoryList(root);  
  }
  
  var requestRestDescription = new goog.async.Deferred();
  
  // downloads the rest description
  var directoryListCallback = goog.bind(function(directoryList) {
    console.log('Loading api from directory', directoryList, apiName, apiVersion);
    
    // get directory info for the api
    var directoryItem = directoryList.getByNameAndVersion(apiName, apiVersion);
    
    // no item by this name/version
    if (directoryItem === null) {
      requestRestDescription.errback();
    }
    else {
      // download and cache the rest description document
      var url = this.buildRestDescriptionUrl(root, apiName, apiVersion);
      var request = this.makeGetRequest_(url);
      
      request.addCallback(function(resp) {
          console.log('Processing rest description', apiName, apiVersion);
        
          var restDescription = new webapi.discovery.RestDescription(resp);
        
          // store the document in the cache
          this.cache_.putRestDescription(restDescription);
        
          requestRestDescription.callback(restDescription);
      }, this);
      
      request.addErrback(function(error) {
        console.error('Error loading document', error);
        requestRestDescription.errback(error);
      })  
    }
  }, this);
  
  requestDirectoryList.addCallback(directoryListCallback);

  return requestRestDescription;
};

webapi.Loader.prototype.getDirectoryPrefix = function() {
  return webapi.Loader.DISCOVERY_DIRECTORY_PREFIX;
};


/** Build a url to discovery a discovery#directoryList
*/
webapi.Loader.prototype.buildDirectoryListUrl = function(root) {
  var url = new goog.Uri(root + this.getDirectoryPrefix());
  return url.toString();
};
 

/** Build a url to discovery a discovery#restDescription
*/
webapi.Loader.prototype.buildRestDescriptionUrl = function(root, apiName, apiVersion) {
  var url = new goog.Uri(root + this.getDirectoryPrefix() + '/' + apiName + '/' + apiVersion + '/rest');
  //directoryListUri.setParameterValue('fields', 'methods/*/id')
  //directoryListUri.setParameterValue('pp', '0')
  return url.toString();
};