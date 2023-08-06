goog.provide('webapi.discovery.DirectoryItem');
goog.require('goog.string.path');

/** @constructor */
webapi.discovery.DirectoryItem = function(data){
  this.data = new goog.structs.Map(data); 
}

webapi.discovery.DirectoryItem.prototype.getName = function(){
  return this.data.get('name')
}

webapi.discovery.DirectoryItem.prototype.getId = function(){
  return this.data['id']
}

webapi.discovery.DirectoryItem.prototype.getVersion = function(){
  return this.data.get('version')
}

webapi.discovery.DirectoryItem.prototype.getDiscoveryRestUrl = function(){
  return this.data['discoveryRestUrl']
}

webapi.discovery.DirectoryItem.prototype.getDiscoveryLink_ = function(){
  return /** @type{string} */this.data.get('discoveryLink')
}

webapi.discovery.DirectoryItem.prototype.getDiscoveryLink = function(){
  return '/'+goog.string.path.normalizePath(this.getDiscoveryLink_())
}

webapi.discovery.DirectoryItem.prototype.getDescription = function(){
  return this.data['description']
}

webapi.discovery.DirectoryItem.prototype.getIcon = function(size){
  return this.data['icons']['x'+size]
}

webapi.discovery.DirectoryItem.prototype.getIsPreferred = function(){
  return this.data['preferred']
}
