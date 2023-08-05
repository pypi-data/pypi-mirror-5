var Broker, BrokerCallbacks, NodeBusy, WebWorkerNode,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

NodeBusy = (function(_super) {

  __extends(NodeBusy, _super);

  function NodeBusy() {
    return NodeBusy.__super__.constructor.apply(this, arguments);
  }

  return NodeBusy;

})(Error);

BrokerCallbacks = (function() {

  function BrokerCallbacks(broker) {}

  BrokerCallbacks.prototype.nodeConnected = function() {};

  BrokerCallbacks.prototype.nodeDisconnected = function() {};

  return BrokerCallbacks;

})();

Broker = (function() {

  function Broker() {
    this.nodes = {};
  }

  Broker.prototype.bindNode = function(methods, node) {
    var k, l, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = methods.length; _i < _len; _i++) {
      k = methods[_i];
      l = this.nodes[k];
      if (!(l != null)) {
        l = this.nodes[k] = [];
      }
      _results.push(l.push(node));
    }
    return _results;
  };

  Broker.prototype.execute = function(method, args, cbResult, ebResult) {
    var cbSpawned, ebSpawned, nodes,
      _this = this;
    nodes = this.nodes[method];
    if (!nodes) {
      throw new Error("No nodes supporting the '" + method + "' call");
    }
    cbSpawned = function(result) {
      return console.log('Calc started with ID', result);
    };
    ebSpawned = function(error) {
      return console.log('Error received');
    };
    return nodes[0].execute(method, args, cbSpawned, ebSpawned, cbResult, ebResult);
  };

  return Broker;

})();

WebWorkerNode = (function() {

  function WebWorkerNode(methods) {
    this.methods = methods;
    this._busy = false;
  }

  WebWorkerNode.prototype.bind = function(broker) {
    return broker.bindNode(Object.keys(this.methods), this);
  };

  WebWorkerNode.prototype.execute = function(method, args, cbSpawned, ebSpawned, cbResult, ebResult) {
    var source,
      _this = this;
    if (this._busy) {
      ebSpawned(NodeBusy);
      return;
    }
    this._busy = true;
    this._callback = cbResult;
    this._errback = ebResult;
    source = this.methods[method];
    if (!source) {
      throw new Error("The method '" + method + "' is not supported by this node");
    }
    this._worker = new Worker(source);
    this._worker.onmessage = function(event) {
      return cbResult(event.data);
    };
    this._worker.onclose = function(event) {
      _this._busy = false;
      return _this._worker = void 0;
    };
    this._resultId = Math.random();
    cbSpawned("" + this._resultId);
    return this._worker.postMessage(args);
  };

  return WebWorkerNode;

})();
