(function($) {
  return $(function() {
    var broker, workerNode;
    console.log('spreadscript starting');
    broker = new Broker();
    workerNode = new WebWorkerNode({
      'test': '/static/scripts/spread.method.test.js',
      'test2': '/static/scripts/spread.method.test.js'
    });
    workerNode.bind(broker);
    return broker.execute('test', ['ciao', 'bello'], function(result) {
      return console.log('Result', result);
    });
  });
})(jQuery);
