goog.provide('webapi.Cache');
goog.require('goog.structs.Map');



webapi.Cache = function () {
  this.map_ = new goog.structs.Map();
  this.directoryLists = new goog.structs.Map();
};
goog.addSingletonGetter(webapi.Cache);


webapi.Cache.prototype.getDirectoryList = function (root) {
  return this.directoryLists.get(root, null)
};


webapi.Cache.prototype.putDirectoryList = function (root, directoryList) {
  return this.directoryLists.set(root, directoryList);
};


webapi.Cache.prototype.getRestDescription = function (apiName, version) {
  var version_map = this.map_.get(apiName, null);

  if (version_map === null) {
    return null
  }

  return version_map.get(version, null);
};


webapi.Cache.prototype.putRestDescription = function (restDescription) {
  var apiName = restDescription.getName();
  var version = restDescription.getVersion();
  var version_map = this.map_.get(apiName, null);

  if (version_map === null) {
    version_map = new goog.structs.Map();
    this.map_.set(apiName, version_map)
  }

  version_map.set(version, restDescription);
};
