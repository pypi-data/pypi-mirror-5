var Task, checkComplete, loadTasks, makeCollectorConfig, makeRemoveConfirmPrompt, sortTasks;

$(function() {
  var saveSession;
  $('.available-collectors li').draggable({
    cursor: 'move',
    helper: function() {
      return $(this).clone(true).addClass('drag-helper');
    },
    revert: 'invalid',
    revertDuration: 200,
    scope: 'collector-config',
    snapMode: 'inner',
    snapTolerance: 50
  }).click(function() {
    var collector;
    collector = makeCollectorConfig($(this).data('form_action'));
    return $('.configured-collectors .collector-config-placeholder').before(collector);
  });
  $('.configured-collectors .collector-config-placeholder').droppable({
    scope: 'collector-config',
    tolerance: 'pointer',
    activeClass: 'visible',
    over: function(e, ui) {
      return $(this).addClass('active');
    },
    out: function(e, ui) {
      return $(this).removeClass('active');
    },
    drop: function(e, ui) {
      return $(this).removeClass('active').before(makeCollectorConfig(ui.helper.data('form_action')));
    }
  });
  $('.acquisition-session-config .session-save-link').click(function(e) {
    var url;
    e.preventDefault();
    url = $(this).attr('href');
    return saveSession($(this)).done(function() {
      return window.location = url;
    });
  });
  $('.acquisition-session-config .session-save').click(function() {
    return saveSession($(this));
  });
  return saveSession = function(btn) {
    var callbacks, deferred_done, done, errors, mainform, mainspinner, session, show,
      _this = this;
    btn.text('Saving...').attr('disabled', true).next('.dropdown-toggle').attr('disabled', true);
    session = btn.closest('.acquisition-session-config');
    callbacks = [];
    mainform = $('> form', session);
    mainspinner = $('<div/>').addClass('loading-overlay hidden').append($.spinner()).appendTo(mainform);
    show = function() {
      return mainspinner.removeClass('hidden');
    };
    setTimeout(show, 0);
    callbacks.push($.post(mainform.attr('action'), mainform.serialize(), function(r) {
      var parent;
      parent = mainform.parent();
      mainform.replaceWith(r);
      mainform = parent.find('> form');
      return errors += mainform.find('.control-group.error').size();
    }));
    errors = 0;
    $('.collector-config form', session).each(function() {
      var form, hide, remove, spinner;
      form = $(this);
      spinner = $('<div/>').addClass('loading-overlay hidden').append($.spinner()).insertAfter(form);
      show = function() {
        return spinner.removeClass('hidden');
      };
      hide = function() {
        return spinner.addClass('hidden');
      };
      remove = function() {
        return spinner.remove();
      };
      setTimeout(show, 0);
      return callbacks.push($.post(form.attr('action'), form.serialize(), function(r) {
        var parent;
        parent = form.parent();
        form.replaceWith(r);
        form = parent.find('> form');
        errors += form.find('.control-group.error').size();
        setTimeout(hide, 0);
        return setTimeout(remove, 300);
      }));
    });
    done = $.Deferred();
    deferred_done = function() {
      return $.when.apply($, callbacks).done(function() {
        btn.text('Save').attr('disabled', false).next('.dropdown-toggle').attr('disabled', false);
        if (errors) {
          return done.reject();
        } else {
          return done.resolve();
        }
      });
    };
    setTimeout(deferred_done, 500);
    return done;
  };
});

makeCollectorConfig = function(form_action) {
  var front, src;
  src = $('<li/>').addClass('collector-config flip-panel loading').flipPanel({
    width: 500,
    height: 100
  });
  front = $('<div/>').addClass('front-panel').append($.spinner()).appendTo(src);
  $.ajax({
    url: form_action
  }).done(function(data) {
    $('.spinner', src).remove();
    return src.removeClass('loading').html(data);
  });
  return src;
};

makeRemoveConfirmPrompt = function() {
  var container, nok, ok, p, show;
  container = $('<div/>').addClass('confirm-overlay hidden');
  ok = $('<button/>').addClass('btn btn-danger btn-small').text('Remove').click(function() {
    var form, url, val;
    form = container.prev('form');
    p.remove();
    ok.remove();
    nok.remove();
    $.spinner().appendTo(container);
    url = form.data('deleteurl');
    if (!url) {
      form.closest('.collector-config').remove();
      return;
    }
    val = $('input:hidden[name^="csrfmiddlewaretoken"]', form).val();
    return $.post(url, {
      csrfmiddlewaretoken: val
    }).done(function() {
      return form.closest('.collector-config').remove();
    }).fail(function() {
      return console.log('Failed to remove component');
    });
  });
  nok = $('<button/>').addClass('btn btn-small').text('Cancel').click(function() {
    return container.remove();
  });
  p = $('<p/>').text('Are you sure you want to remove this collector?');
  container.append($('<div/>').append(p).append(nok).append(ok));
  show = function() {
    return container.removeClass('hidden');
  };
  setTimeout(show, 0);
  return container;
};

$(function() {
  $(document).on('click', '.front-panel .remove', function(e) {
    e.preventDefault();
    return makeRemoveConfirmPrompt().insertAfter($(this).closest('form'));
  });
  $(document).on('click', '.front-panel .advanced', function(e) {
    var form;
    e.preventDefault();
    form = $(this).closest('form');
    form.data('oldvalues', form.serializeArray());
    return $(this).closest('.flip-panel').flipPanelOpen();
  });
  $(document).on('click', '.back-panel .form-actions .btn-primary', function(e) {
    e.preventDefault();
    return $(this).closest('.flip-panel').flipPanelClose();
  });
  $(document).on('click', '.back-panel .form-actions :not(.btn-primary)', function(e) {
    var form, values;
    e.preventDefault();
    $(this).closest('.flip-panel').flipPanelClose();
    form = $(this).closest('form');
    values = form.data('oldvalues');
    return $.each(values, function(i, val) {
      return form.find("[name^=" + val.name + "]").val(val.value);
    });
  });
  return $('.collector-config.loading').each(function() {
    var front, src;
    src = $(this).addClass('flip-panel').flipPanel({
      width: 500,
      height: 100
    });
    front = $('<div/>').addClass('front-panel').append($.spinner()).appendTo(src);
    return $.ajax({
      url: $(this).data('loadurl')
    }).done(function(data) {
      $('.spinner', src).remove();
      return src.removeClass('loading').html(data);
    });
  });
});

Task = (function() {

  function Task() {}

  Task.fromData = function(data) {
    var task;
    task = new Task;
    task.build(data.uuid).update(data);
    return task;
  };

  Task.fromElement = function(el) {
    var task;
    task = new Task;
    task.el = el;
    return task;
  };

  Task.prototype.appendTo = function(container) {
    this.el.appendTo(container);
    return this;
  };

  Task.prototype.setProgress = function(progress) {
    var status;
    status = this.el.data('status');
    this.setProgressStatus(progress, status);
    return this;
  };

  Task.prototype.setStatus = function(status) {
    var progress;
    progress = this.el.data('progress');
    this.setProgressStatus(progress, status);
    return this;
  };

  Task.prototype.setProgressStatus = function(progress, status) {
    var $bar, $percentage, $progress;
    this.el.data('progress', progress);
    this.el.data('status', status);
    progress = progress * 100;
    $bar = $('.bar', this.el);
    $progress = $('.progress', this.el);
    $percentage = $('.percentage', this.el);
    $progress.attr('class', 'progress');
    if (progress >= 0) {
      $percentage.text("" + (Math.round(progress)) + "%");
      $bar.css('width', "" + progress + "%");
    } else {
      $progress.addClass('progress-striped');
      $percentage.text('');
      $bar.css('width', '100%');
    }
    switch (status) {
      case 0:
        $bar.width(0);
        $percentage.text('');
        break;
      case 1:
        $progress.addClass('active');
        break;
      case 2:
        $progress.addClass('inactive');
        break;
      case 3:
        $progress.removeClass('progress-striped');
        $progress.addClass('progress-success');
        break;
      case 4:
        $progress.removeClass('progress-striped');
        $progress.addClass('progress-danger');
    }
    return this;
  };

  Task.prototype.setOrder = function(order) {
    this.el.attr('data-order', order);
    return this;
  };

  Task.prototype.setName = function(name) {
    $('> p:first-child', this.el).text(name);
    return this;
  };

  Task.prototype.setStatusText = function(text) {
    $('> p.status', this.el).text(text);
    return this;
  };

  Task.prototype.update = function(data) {
    this.setProgressStatus(data.progress, data.status);
    this.setName(data.name);
    this.setStatusText(data.statusText);
    return this;
  };

  Task.prototype.build = function(uuid, elementType) {
    var bar, el, indicator;
    if (elementType == null) {
      elementType = 'li';
    }
    el = $("<" + elementType + "/>").attr('id', "task-" + uuid).addClass('task');
    $('<p/>').appendTo(el);
    bar = $('<div/>').addClass('progress').appendTo(el);
    indicator = $('<div/>').addClass('bar').appendTo(bar);
    $('<span/>').addClass('percentage').appendTo(indicator);
    $('<p/>').addClass('status').appendTo(el);
    this.el = el;
    return this;
  };

  return Task;

})();

checkComplete = function(container) {
  if (!$('.task .progress:not(.progress-success, .progress-danger)', container).size()) {
    return $.get(window.location + '?' + Math.random(), function(data) {
      $('#session-results').replaceWith(data);
      return $('#session-results tr[data-uuid]').each(function() {
        var collector, dismiss, status, uuid;
        uuid = $(this).data('uuid');
        status = $(this).data('status');
        collector = $("#session-tasks div[data-uuid=" + uuid + "]");
        if (status !== 2 && status !== 3) {
          return;
        }
        if (!collector.size()) {
          return;
        }
        if (collector.hasClass('failed') || collector.hasClass('completed')) {
          return;
        }
        if (status === 3) {
          collector.addClass('completed');
          $('<i class="icon-ok icon-success icon-large"> </i>').prependTo(container);
        } else if (status === 2) {
          collector.addClass('failed');
          $('<i class="icon-warning-sign icon-danger icon-large"> </i>').prependTo(container);
        }
        dismiss = $('<button type="button" class="close" data-dismiss="collector-monitor">&times;</button>');
        return dismiss.insertAfter($('strong', collector)).click(function() {
          var p;
          container = $(this).closest('.collector-monitor');
          p = container.parent();
          container.remove();
          if (p.find('.collector-monitor').size() === 0) {
            return p.parent().remove();
          }
        });
      });
    });
  }
};

sortTasks = function(container) {
  var tasks;
  tasks = $('.tasks .task', container).sort(function(a, b) {
    return $(a).data('order') - $(b).data('order');
  });
  $('.tasks .task', container).remove();
  return $('.tasks', container).append(tasks);
};

loadTasks = function(server) {
  var collector, container, uuid;
  collector = $(this);
  uuid = collector.data('uuid');
  container = $('.tasks', collector);
  return server.call('getTasksForCollector', uuid).done(function(tasks) {
    $.each(tasks, function(i, _arg) {
      var data, order, t;
      order = _arg[0], data = _arg[1];
      t = Task.fromData(data).setOrder(order).appendTo(container);
      return sortTasks(collector);
    });
    checkComplete(collector);
    return server.call('broker.exclusiveQueueBind', 'tasks', "task." + uuid + ".*", server.callback(function(_arg) {
      var data, item, order, task;
      order = _arg[0], data = _arg[1];
      item = $("#task-" + data.uuid);
      if (!item.size()) {
        task = Task.fromData(data).setOrder(order);
        task.appendTo(container);
      } else {
        Task.fromElement(item).setOrder(order).update(data);
      }
      checkComplete(collector);
      return sortTasks(collector);
    }));
  });
};

$(function() {
  var setTilesSize, ws;
  if ($('.session-list').size()) {
    setTilesSize = function() {
      return $('.session-list li').height($('.session-list li').width());
    };
    setTilesSize();
    $(window).on('resize', setTilesSize);
    $('.session-list li.flip-box:not(.inactive)').click(function() {
      var fix, hash, id;
      hash = window.location.hash;
      if (hash) {
        hash = hash.substring(1);
      }
      id = $(this).attr('id');
      if (id === hash) {
        window.location.hash = '';
        return $("#" + hash).flipBoxClose();
      } else {
        if (hash) {
          $("#" + hash).flipBoxClose();
        }
        $(this).attr('id', '');
        fix = $('<div/>').attr('id', id).css({
          position: 'absolute',
          visibility: 'hidden',
          top: $(document).scrollTop() + 'px'
        }).attr('id', id).appendTo(document.body);
        window.location.hash = '#' + id;
        fix.remove();
        return $(this).attr('id', id).flipBoxOpen();
      }
    }).each(function() {
      var bg, c, color, color1, color2, gradient;
      bg = $(this).data('background');
      if (!bg) {
        return;
      }
      color = [bg.substring(1, 3), bg.substring(3, 5), bg.substring(5)];
      color = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = color.length; _i < _len; _i++) {
          c = color[_i];
          _results.push(parseInt(c, 16));
        }
        return _results;
      })();
      color1 = "rgba(" + (color.join(',')) + ",0)";
      color2 = "rgba(" + (color.join(',')) + ",0.8)";
      gradient = "linear-gradient(to bottom, " + color1 + " 0px, " + color2 + " 30px)";
      return $('.front-panel > strong', this).css('background-image', gradient);
    });
    $('.session-list a').click(function(e) {
      return e.stopPropagation();
    });
  }
  if ($('.collector-monitor').size()) {
    return ws = $.websocket("ws://" + acquisitionServer + "/", {
      open: (function() {
        return $('.collector-monitor').each(function() {
          return loadTasks.call(this, ws);
        });
      }),
      close: (function() {}),
      events: {}
    });
  }
});
