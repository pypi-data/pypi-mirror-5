goog.require('webapi.Loader');
goog.require('goog.testing.net.XhrIoPool');
goog.require('goog.testing.recordFunction');
goog.require('goog.testing.TestQueue');
goog.require('goog.net.XhrManager');

/** @type {goog.net.XhrManager} */
var xhrManager;

/** @type {goog.testing.net.XhrIo} */
var xhrIo;

var TestApiLoader;

var testQueue;

var TEST_DIRECTORY = {
 "kind": "discovery#directoryList",
 "discoveryVersion": "v1",
 "items": [
  {
   "kind": "discovery#directoryItem",
   "id": "example:v1",
   "name": "example",
   "version": "v1",
   "description": "example API",
   "discoveryRestUrl": "https://webapis-discovery.appspot.com/_ah/api/discovery/v1/apis/example/v1/rest",
   "discoveryLink": "./apis/example/v1/rest",
   "icons": {
    "x16": "http://www.google.com/images/icons/product/search-16.gif",
    "x32": "http://www.google.com/images/icons/product/search-32.gif"
   },
   "preferred": true
  }
 ]
}

var TEST_DISCOVERY_DOCUMENT = {
 "kind": "discovery#rpcDescription",
 "etag": "\"wez405KDp3av28PdV0g9gQEA_Kk/qeEXUf50rPDZXLQRu3FgZ99tynA\"",
 "discoveryVersion": "v1",
 "id": "example:v1",
 "name": "example",
 "version": "v1",
 "description": "example API",
 "ownerDomain": "google.com",
 "ownerName": "Google",
 "icons": {
  "x16": "http://www.google.com/images/icons/product/search-16.gif",
  "x32": "http://www.google.com/images/icons/product/search-32.gif"
 },
 "protocol": "rpc",
 "rootUrl": "https://example.com/_ah/api/",
 "rpcUrl": "https://example.com/_ah/api/rpc",
 "rpcPath": "/_ah/api/rpc",
 "parameters": {
  "alt": {
   "type": "string",
   "description": "Data format for the response.",
   "default": "json",
   "enum": [
    "json"
   ],
   "enumDescriptions": [
    "Responses with Content-Type of application/json"
   ],
   "location": "query"
  },
  "fields": {
   "type": "string",
   "description": "Selector specifying which fields to include in a partial response.",
   "location": "query"
  },
  "key": {
   "type": "string",
   "description": "API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token.",
   "location": "query"
  },
  "oauth_token": {
   "type": "string",
   "description": "OAuth 2.0 token for the current user.",
   "location": "query"
  },
  "prettyPrint": {
   "type": "boolean",
   "description": "Returns response with indentations and line breaks.",
   "default": "true",
   "location": "query"
  },
  "quotaUser": {
   "type": "string",
   "description": "Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Overrides userIp if both are provided.",
   "location": "query"
  },
  "userIp": {
   "type": "string",
   "description": "IP address of the site where the request originates. Use this if you want to enforce per-user limits.",
   "location": "query"
  }
 },
 "auth": {
  "oauth2": {
   "scopes": {
    "https://www.googleapis.com/auth/userinfo.email": {
     "description": "View your email address"
    }
   }
  }
 },
 "schemas": {
  "Request": {
   "id": "Request",
   "type": "object",
   "properties": {
    "id": {
     "type": "string"
    },
   }
  },
  "Response": {
   "id": "Response",
   "type": "object",
   "properties": {
    "id": {
     "type": "string"
    },
    "title": {
     "type": "string"
    }
   }
  }
 },
 "methods": {
  "example.resource.get": {
   "id": "example.resource.get",
   "description": "Full text search for MediaItems in a library.",
   "parameters": {
    "resource": {
     "$ref": "Request"
    }
   },
   "parameterOrder": [
    "resource"
   ],
   "returns": {
    "$ref": "Response"
   },
   "scopes": [
    "https://www.googleapis.com/auth/userinfo.email"
   ]
  },
  "example.info": {
   "id": "example.info",
   "description": "Get account information",
   "parameters": {
    "resource": {
     "$ref": "DriveboxEndpointsPlaylistapiInfoRequest"
    }
   },
   "parameterOrder": [
    "resource"
   ],
   "returns": {
    "$ref": "DriveboxEndpointsPlaylistapiInfoResponse"
   },
   "scopes": [
    "https://www.googleapis.com/auth/userinfo.email"
   ]
  }
 }
}


function setUp() {
  testQueue = new goog.testing.TestQueue();
  xhrIo = new goog.testing.net.XhrIo(testQueue);
  xhrManager = new goog.net.XhrManager();
  xhrManager.xhrPool_ = new goog.testing.net.XhrIoPool(xhrIo);
  
    
  TestLoader = function(){
    goog.base(this, xhrManager);
  }
  goog.inherits(TestLoader, webapi.Loader);
  
  TestLoader.prototype.makeGetRequest_ = function(url){
    console.log('Request', url);
    
    setTimeout(goog.bind(function(){
      
      //console.log(testQueue.dequeue())
      
    }, this), 1000);
    
    
    var deferred = goog.base(this, 'makeGetRequest_', url);
    
    switch(url){
        case 'http://example.com/discovery/v1/apis':
          console.log('simulate directory')
          xhrIo.simulateResponse(200, goog.json.serialize(TEST_DIRECTORY), {'Content-Type':'application/json'});  // Do this to make tearDown() happy.
          break;
        case 'http://example.com/discovery/v1/apis/example/v1/rest':
          console.log('simulate rest')
          xhrIo.simulateResponse(200, goog.json.serialize(TEST_DISCOVERY_DOCUMENT), {'Content-Type':'application/json'});  // Do this to make tearDown() happy.
          break;
      }  
    
    return deferred;
  }  
  
}

function tearDown() {
  xhrManager.dispose()
}




function testFull(){
  
  var loader = new TestLoader()
  var loadRequest = loader.load('example', 'v1', 'http://example.com');
  
  AsyncTestCase.waitForAsync('wait for directory and description to load');
  
  var restDescription = null;
  
  var callback = goog.testing.recordFunction(function(desc) {
      console.log('Continue testing')
      restDescription = desc;
      AsyncTestCase.continueTesting()
  });
  
  loadRequest.addCallback(callback);
  
  assertEquals(1, callback.getCallCount());
  
  assertEquals(2, restDescription.getMethodIds().length);
  
  // TODO: listen for the errback
}
