

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
    // console.log('Retry',msg,'('+String(limit),"attempts left)");
    window.setTimeout(function() { waitfor(msg,until,limit-1,todo)},1000);
};

var output = '/home/luc/hgwork/welfare/lino_welfare/demo/settings/media/cache/screenshots/de/cbss.RetrieveTIGroupsRequests.detail.jpg';
var address = 'http://127.0.0.1:8000/api/cbss/RetrieveTIGroupsRequests/1?an=detail';


// phantom.addCookie({ username: 'rolf', password: '1234'});

var data = 'username=rolf&password=1234';
var page = require('webpage').create();
page.open('http://127.0.0.1:8000/auth','post',data,function (status) {
    // console.log('opened auth!');
    if (status !== 'success') {
        console.log('Unable to authenticate!');
        phantom.exit();
    }});

var page = require('webpage').create();
// page.settings = { userName: 'rolf', password: '1234'};
// page.customHeaders = { None: 'rolf'};
// page.customHeaders = { 'HTTP_None': 'rolf'};

page.viewportSize = { width: 1400, height: 800};
// page.viewportSize = { width: 1024, height: 768};
// page.viewportSize = { width: 1366, height: 744};
// page.viewportSize = { width: 800, height: 600};
page.onConsoleMessage = function (msg) { console.log(msg); };
page.onError = function (msg, trace) {
    console.log(msg);
    trace.forEach(function(item) {
        console.log('  ', item.file, ':', item.line);
    })
}

var is_loaded = function() { 
  return page.evaluate(function() { 
      // console.log('evaluate()');
        // return !Ext.Ajax.isLoading();
        // return (document.readyState == 'complete');
        if (typeof Lino != "undefined") {
            if (Lino.current_window) {
                if (!Lino.current_window.main_item.is_loading())
                    return true;
                // console.log("Lino.current_window still loading in ",document.documentElement.innerHTML);
                // console.log("Lino.current_window", Lino.current_window.main_item,"still loading." );
                // return true;
            }
        }
        // console.log("No Lino in ",document.documentElement.innerHTML);
        // console.log("No Lino in response");
        return false;
    }
  );
};

var todo = function(ok) { 
    console.log("Rendering to",output,ok);
    page.render(output);
    if (ok) 
        phantom.exit();
    else
        phantom.exit(2);
};

var on_opened = function(status) { 
    if (status !== 'success') {
        console.log('Unable to load ',address,'status is:',status);
        phantom.exit(1);
    } else {
        waitfor(output,is_loaded,6,todo);
    }
};

console.log("Loading",address,'to',output);

page.open(address,on_opened);


