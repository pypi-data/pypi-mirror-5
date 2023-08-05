var DIALOGS_ANIMATION_DURATION,
  __slice = [].slice;

(function($) {
  var oldXHR;
  oldXHR = $.ajaxSettings.xhr;
  return $.ajaxSettings.xhr = function() {
    var xhr;
    xhr = oldXHR();
    if (xhr instanceof window.XMLHttpRequest) {
      xhr.addEventListener('progress', this.progress, false);
    }
    if (xhr.upload) {
      xhr.upload.addEventListener('progress', this.progress, false);
    }
    return xhr;
  };
})(jQuery);

DIALOGS_ANIMATION_DURATION = 700;

(function($) {
  $.fn.flipBoxFlip = function() {
    return this.toggleClass('flipped');
  };
  $.fn.flipBoxOpen = function() {
    return this.addClass('flipped');
  };
  return $.fn.flipBoxClose = function() {
    return this.removeClass('flipped');
  };
})(jQuery);

DIALOGS_ANIMATION_DURATION = 700;

(function($) {
  $.fn.twostepsShow = function(cb) {
    var invoke, show,
      _this = this;
    this.addClass('active');
    show = function() {
      return _this.addClass('visible');
    };
    setTimeout(show, 0);
    if (cb != null) {
      invoke = function() {
        return cb.apply(_this);
      };
      setTimeout(invoke, DIALOGS_ANIMATION_DURATION);
    }
    return this;
  };
  $.fn.twostepsHide = function(cb) {
    var hide,
      _this = this;
    this.removeClass('visible');
    hide = function() {
      _this.removeClass('active');
      if (cb != null) {
        return cb.apply(_this);
      }
    };
    setTimeout(hide, DIALOGS_ANIMATION_DURATION);
    return this;
  };
  $.fn.modalGet = function() {
    var modal;
    modal = $('body > .modal-background');
    if (!modal.size()) {
      modal = $('<div/>').addClass('modal-background').appendTo($('body'));
    }
    return modal;
  };
  $.fn.modalShow = function() {
    var modal;
    modal = this.modalGet();
    return modal.twostepsShow();
  };
  $.fn.modalHide = function(cb) {
    return this.modalGet().twostepsHide(cb);
  };
  $.fn.scrollingLock = function() {
    var scrollLeft, scrollTop, _ref;
    _ref = [this.scrollTop(), this.scrollLeft()], scrollTop = _ref[0], scrollLeft = _ref[1];
    return this.data({
      'scroll-position-top': scrollTop,
      'scroll-position-left': scrollLeft,
      'previous-overflow': this.css('overflow')
    }).css('overflow', 'hidden').scrollTop(scrollTop).scrollLeft(scrollLeft);
  };
  $.fn.scrollingUnlock = function() {
    return this.css('overflow', this.data('previous-overflow')).scrollTop(this.data('scroll-position-top')).scrollLeft(this.data('scroll-position-left'));
  };
  $.fn.flipPanelOpen = function() {
    var ch, cl, ct, cw, oh, ol, open, ot, ow, style,
      _this = this;
    $('html').scrollingLock();
    cw = this.outerWidth();
    ch = this.outerHeight();
    ct = this.offset().top;
    cl = this.offset().left;
    ow = Math.min(this.data('width'), $(window).width() - 40);
    oh = Math.min(this.data('height'), $(window).height() - 40);
    ot = ($(window).height() - oh) / 2 + $('body').scrollTop();
    ol = ($(window).width() - ow) / 2 + $('body').scrollLeft();
    $("<" + (this.get(0).tagName) + "/>").addClass('flip-panel-placeholder').width(cw).height(ch).css({
      'display': 'block'
    }).insertAfter(this);
    style = $("<style>\n    .flip-panel.closed {\n        width: " + cw + "px;\n        height: " + ch + "px;\n        top: " + ct + "px;\n        left: " + cl + "px;\n    }\n        .flip-panel.open {\n            width: " + ow + "px;\n        height: " + oh + "px;\n        top: " + ot + "px;\n        left: " + ol + "px;\n    }\n</style>").appendTo(this);
    this.modalShow();
    this.addClass('closed');
    open = function() {
      return _this.addClass('open visible').removeClass('closed');
    };
    setTimeout(open, 0);
    return this;
  };
  $.fn.flipPanelClose = function() {
    var _this = this;
    $('html').scrollingUnlock();
    this.removeClass('open').addClass('closed');
    this.modalHide(function() {
      _this.removeClass('visible closed');
      _this.find('style').remove();
      return _this.next('.flip-panel-placeholder').remove();
    });
    return this;
  };
  return $.fn.flipPanel = function(settings) {
    if (settings == null) {
      settings = {};
    }
    return this.data(settings);
  };
})(jQuery);

(function($) {
  return $.spinner = function(ticks, class_) {
    var i, spinner, _i;
    if (ticks == null) {
      ticks = 50;
    }
    if (class_ == null) {
      class_ = '';
    }
    spinner = $('<span/>').addClass("spinner " + class_);
    for (i = _i = 0; 0 <= ticks ? _i < ticks : _i > ticks; i = 0 <= ticks ? ++_i : --_i) {
      $('<span/>').appendTo(spinner);
    }
    return spinner;
  };
})(jQuery);

(function($) {
  return $.urlParam = function(name) {
    var regex, regexS, results;
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    regexS = "[\\?&]" + name + "=([^&#]*)";
    regex = new RegExp(regexS);
    results = regex.exec(window.location.search);
    if (results === null) {
      return "";
    } else {
      return decodeURIComponent(results[1].replace(/\+/g, " "));
    }
  };
})(jQuery);

String.prototype.hashCode = function() {
  var char, hash, i, _i, _ref;
  hash = 0;
  if (this.length === 0) {
    return hash;
  }
  for (i = _i = 0, _ref = this.length; 0 <= _ref ? _i < _ref : _i > _ref; i = 0 <= _ref ? ++_i : --_i) {
    char = this.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash;
};

(function($) {
  return $.extend({
    websocket: function(url, s, protocols) {
      var callbacks, req_id, settings, ws;
      if (protocols) {
        if (window['MozWebSocket']) {
          ws = new MozWebSocket(url, protocols);
        } else if (window['WebSocket']) {
          ws = new WebSocket(url, protocols);
        }
      } else {
        if (window['MozWebSocket']) {
          ws = new MozWebSocket(url);
        } else if (window['WebSocket']) {
          ws = new WebSocket(url);
        }
      }
      settings = {
        open: (function() {}),
        close: (function() {}),
        message: (function() {}),
        options: {},
        events: {},
        callbacks: {}
      };
      $.extend(settings, $.websocketSettings, s);
      if (ws) {
        callbacks = {};
        req_id = 0;
        $(ws).bind('open', settings.open).bind('close', settings.close).bind('message', settings.message).bind('message', function(e) {
          var callback, cb, jsonstr, length, match, message, pattern;
          pattern = /^(\d+):(.*),$/;
          message = e.originalEvent.data;
          match = pattern.exec(message);
          length = parseInt(match[1]);
          jsonstr = match[2];
          if (length !== jsonstr.length) {
            console.err("Wrong length");
            return;
          }
          message = JSON.parse(jsonstr);
          if (message.hasOwnProperty('error')) {
            console.error("Error " + message.id + " received");
            cb = callbacks[message.id];
            delete callbacks[message.id];
            cb.reject(message.error.code, message.error.message, message.error.data);
          }
          if (message.hasOwnProperty('result')) {
            cb = callbacks[message.id];
            delete callbacks[message.id];
            cb.resolve(message.result);
          }
          if (message.hasOwnProperty('method') && message.hasOwnProperty('id')) {
            console.error("Method invocations are not supported yet");
          }
          if (message.hasOwnProperty('method') && !message.hasOwnProperty('id')) {
            callback = settings.events[message.method];
            if (callback != null) {
              return callback.call.apply(callback, [this].concat(__slice.call(message.params)));
            }
          }
        });
        ws._send = ws.send;
        ws.send = function(type, data) {
          var m;
          m = {
            type: type
          };
          m = $.extend(true, m, $.extend(true, {}, settings.options, m));
          if (data) {
            m['data'] = data;
          }
          return this._send(JSON.stringify(m));
        };
        ws.call = function() {
          var args, cb, func, jsonstring, m, netstring;
          func = arguments[0], args = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
          m = {
            'method': func,
            'params': args,
            'id': req_id
          };
          jsonstring = JSON.stringify(m);
          netstring = "" + jsonstring.length + ":" + jsonstring + ",";
          cb = $.Deferred();
          callbacks[req_id] = cb;
          req_id += 1;
          this._send(netstring);
          return cb.promise();
        };
        ws.callback = function(func) {
          var name;
          name = '_callback_' + (func.toString().hashCode() + Math.pow(2, 31) - 1 + Math.random());
          settings.events[name] = func;
          return name;
        };
        $(window).unload(function() {
          ws.close();
          return ws = null;
        });
      }
      return ws;
    }
  });
})(jQuery);
