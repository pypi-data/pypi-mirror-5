webapi
######

A framework to build web (json-rpc) APIs.


Quick Start
###########

Defining messages and a service::
    
    class TestRequest(messages.Message):
        string = messages.StringField(1)

    class TestResponse(messages.Message):
        string = messages.StringField(1)
    
    @webapi.package('examplepackage')
    class ExampleService(object):
        
        @webapi.method(TestRequest, TestResponse, 'examplemethod')
        def test(self, request):
            """ an identity function"""
            assert isinstance(request, TestRequest)
            return TestResponse(string=request.string)
            
            
Building a wsgi application::


    API = webapi.api([ExampleService], 'exampleapi', 'v1')
    
    routes = [
        webapp2.Route('/rpc', webapi.rpc_handler(API))
    ]
    app = webapp2.WSGIApplication(routes)
    
   
The api should be available at /rpc. 

A method exampleapi.examplepackage.examplemethod should be available to callers.


Exporting a discovery application
#################################


Define in python::

        API = webapi.api([TestService], 'testapi', 'v1')
        
        api_directory_app = webapi.APIDirectory([API])

Register with app.yaml to match the path /discovery/.*.

Using the javascript client.
############################

Using the basic client
######################

Include the compiled script.


Installing::

    var RPC_URL = '/rpc';
    
    webapi.client.install(new webapi.RpcClient(RPC_URL));


Calling a method::

    var METHOD = 'exampleapi.examplepackage.examplemethod'
    
    var req = webapi.client.rpc(METHOD, {'string': 'test'});
     
    req.addCallback(function(resp){
        // this should return "test"
        console.log(resp)
    }); 
    
    req.addErrback(function(resp){
        // jsonrpc error objects can be handled here
        console.error(resp)
    });


Using the directory client
##########################

Include the compiled script.


Installing::

    var RPC_URL = '/rpc';
    
    webapi.client.install(new webapi.DiscoveryClient());


Loading an api (from a directory)::

    webapi.client.load(apiName, apiVersion, root)

Loading a rest description (from a json object)::

    webapi.client.loadDescription(rawRestDescription)
    
After loading an api its methods will be exported to the webapi namespace. For example::

    var request = webapi.apiname.package.method();
    
Executing an rpc method (manually)::

    var request = webapi.client.rpc(methodId, params);

