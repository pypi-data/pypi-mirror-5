

function waitfor(msg,until,limit,todo) {
    if (until()) {
      console.log("Done",msg);
      todo(true);
      return;
    };
    if (limit <= 0) {
      console.log("Giving up",msg);
      todo(false);
      //~ task_done(msg,false);
      return;
    };
    console.log('Retry',msg,'('+String(limit),"attempts left)");
    window.setTimeout(function() { waitfor(msg,until,limit-1,todo)},1000);
};

var output = 'gen/screenshots/de/cal.CalendarPanel.jpg';
var address = 'http://127.0.0.1:8000/api/cal/CalendarPanel?lng=de';


var page = require('webpage').create();
// page.settings = { userName: 'alicia', password: '%(password)s'};
page.customHeaders = { REMOTE_USER: 'alicia'};
page.viewportSize = { width: 1024, height: 768};
page.onConsoleMessage = function (msg) { console.log(msg); };
page.onError = function (msg, trace) {
    console.log(msg);
    trace.forEach(function(item) {
        console.log('  ', item.file, ':', item.line);
    })
}

var loaded = function () { 
  return page.evaluate(function() { 
        //~ return !Ext.Ajax.isLoading();
        if (Lino && Lino.current_window) {
            return !Lino.current_window.main_item.is_loading();
        }
    }
  );
};

var todo = function (ok) { 
    console.log("Rendering to",output,ok);
    page.render(output);
    phantom.exit();
    
};

var on_opened = function (status) { 
    if (status !== 'success') {
        console.log('Unable to load ',address,status);
    } else {
        waitfor(output,loaded,3,todo);
    }
};

console.log("Loading",address,'to',output);

page.open(address,on_opened);


