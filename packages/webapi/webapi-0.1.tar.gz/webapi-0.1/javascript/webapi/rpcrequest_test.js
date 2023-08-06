goog.require('webapi.RpcRequest');
goog.require('goog.testing.TestQueue');
goog.require('goog.testing.net.XhrIo');


function testRpcRequest(){
  // test that rpc requests are created properly
  var RPC_URL = 'http://example.com/rpc';
  var queue = new goog.testing.TestQueue();
  var xhr = new goog.testing.net.XhrIo(queue);
  var request = new webapi.RpcRequest(xhr, RPC_URL, {'test': 'test'});
  
  DeferredTestCase.waitForDeferred("Wait for request", request.execute());
  
  var requestEvent = queue.dequeue();
  assertEquals(RPC_URL, requestEvent[2]);
  assertEquals("GET", requestEvent[3]);
  assertEquals("{\"jsonrpc\":\"2.0\",\"method\":{\"test\":\"test\"}}", requestEvent[4]) 
}


