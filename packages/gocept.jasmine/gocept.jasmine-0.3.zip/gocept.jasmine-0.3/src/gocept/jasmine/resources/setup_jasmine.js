(function() {
  var jasmineEnv = jasmine.getEnv();
  jasmineEnv.updateInterval = 1000;

  var htmlReporter = new jasmine.HtmlReporter();

  jasmineEnv.addReporter(htmlReporter);

  jasmineEnv.specFilter = function(spec) {
    return htmlReporter.specFilter(spec);
  };

  var currentWindowOnload = window.onload;

  window.onload = function() {
    if (currentWindowOnload) {
      currentWindowOnload();
    }
    execJasmine();
  };

  function execJasmine() {
    jasmineEnv.execute();
  }

jasmine.Suite.prototype.finish = function(onComplete) {
  // XXX This code was copied from jasmine.js :-(
  this.env.reporter.reportSuiteResults(this);
  this.finished = true;
  if (typeof(onComplete) == 'function') {
    onComplete();
  }
  if (!document.getElementsByClassName('runningAlert').length) {
    var div = document.createElement('DIV');
    div.appendChild(document.createTextNode('gocept.jasmine.tests.finished'));
    document.body.appendChild(div);
  }
};

})();

