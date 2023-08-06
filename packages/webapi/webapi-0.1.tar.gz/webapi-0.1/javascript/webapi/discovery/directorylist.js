goog.provide('webapi.discovery.DirecoryList');
goog.require('webapi.discovery.DirectoryItem');
goog.require('goog.structs.Map');



/** An api directory list

    https://developers.google.com/discovery/v1/reference/apis/list
 
    @constructor
*/
webapi.discovery.DirecoryList = function(data) {
  this.data = new goog.structs.Map(data);
  this.items = [];
  this.index = new goog.structs.Map();
  this.init()
};


/** @return {string} */
webapi.discovery.DirecoryList.prototype.getName = function() {
  return this.data.get('name')
}


/** @return {webapi.discovery.DirectoryItem} */
webapi.discovery.DirecoryList.prototype.getByNameAndVersion = function(name, version) {
  if (!this.index.containsKey(name)) {
    return null;
  }
  var byVersion = this.index.get(name);
  return byVersion.get(version, null);
};


/** @param {webapi.discovery.DirectoryItem} item */
webapi.discovery.DirecoryList.prototype.addItem = function(item) {
  this.items.push(item);
  var name = item.getName();
  var version = item.getVersion();
  var byVersion = this.index.get(name, null);

  if (!this.index.containsKey(name)) {
    byVersion = new goog.structs.Map();
    this.index.set(name, byVersion);
  }

  byVersion.set(version, item);
};


webapi.discovery.DirecoryList.prototype.init = function() {
  var items = this.data.get('items', []);
  for (var item in items) {
    // directoryItem
    this.addItem(new webapi.discovery.DirectoryItem(items[item]));
  }
};
