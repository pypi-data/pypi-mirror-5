$ ->
    $('.available-collectors li').draggable({
        cursor: 'move',
        helper: ->
            $(this).clone(true).addClass('drag-helper')
        revert: 'invalid',
        revertDuration: 200,
        scope: 'collector-config',
        snapMode: 'inner',
        snapTolerance: 50,
    }).click(->
        collector = makeCollectorConfig($(this).data('form_action'))
        $('.configured-collectors .collector-config-placeholder')
            .before(collector)
    )

    # TODO: Listen on startdrag and make a single droppable <li>
    $('.configured-collectors .collector-config-placeholder').droppable({
        scope: 'collector-config',
        tolerance: 'pointer',
        activeClass: 'visible'
        over: (e, ui) ->
            $(this).addClass('active')
        out: (e, ui) ->
            $(this).removeClass('active')
        drop: (e, ui) ->
            $(this).removeClass('active').before(
                makeCollectorConfig(
                    ui.helper.data('form_action')))
    })

    $('.acquisition-session-config .session-save-link').click((e)->
        e.preventDefault()
        url = $(this).attr('href')
        saveSession($(this)).done(->
            window.location = url
        )
    )

    $('.acquisition-session-config .session-save').click(->
        saveSession($(this))
    )

    saveSession = (btn) ->
        btn
            .text('Saving...')
            .attr('disabled', true)
            .next('.dropdown-toggle')
            .attr('disabled', true)

        session = btn.closest('.acquisition-session-config')

        callbacks = []

        mainform = $('> form', session)
        mainspinner = $('<div/>')
            .addClass('loading-overlay hidden')
            .append($.spinner())
            .appendTo(mainform)
        show = -> mainspinner.removeClass('hidden')
        setTimeout(show, 0)

        callbacks.push($.post(
            mainform.attr('action'),
            mainform.serialize(), (r) ->
                parent = mainform.parent()
                mainform.replaceWith(r)
                mainform = parent.find('> form')
                errors += mainform.find('.control-group.error').size()
        ))

        errors = 0

        $('.collector-config form', session).each(->
            form = $(this)

            spinner = $('<div/>')
                .addClass('loading-overlay hidden')
                .append($.spinner())
                .insertAfter(form)

            show = -> spinner.removeClass('hidden')
            hide = -> spinner.addClass('hidden')
            remove = -> spinner.remove()
            setTimeout(show, 0)

            callbacks.push($.post(
                form.attr('action'),
                form.serialize(), (r) ->
                    parent = form.parent()
                    form.replaceWith(r)
                    form = parent.find('> form')
                    errors += form.find('.control-group.error').size()
                    setTimeout(hide, 0)
                    setTimeout(remove, 300)
            ))
        )

        done = $.Deferred()
        deferred_done = =>
            $.when(callbacks...).done(->
                btn.text('Save')
                    .attr('disabled', false)
                    .next('.dropdown-toggle')
                    .attr('disabled', false)

                if errors
                    done.reject()
                else
                    done.resolve()
            )
        # Introduce an artifical minimum time for saving operations in
        # order to let the user notice the visual feedback
        setTimeout(deferred_done, 500)
        return done

makeCollectorConfig = (form_action) ->
    src = $('<li/>')
        .addClass('collector-config flip-panel loading')
        .flipPanel({
            width: 500,
            height: 100,
        })

    front = $('<div/>')
        .addClass('front-panel')
        .append($.spinner())
        .appendTo(src)

    $.ajax({
        url: form_action,
    }).done((data) ->
        $('.spinner', src).remove()
        src.removeClass('loading').html(data)
    )

    return src

makeRemoveConfirmPrompt = ->
    container = $('<div/>').addClass('confirm-overlay hidden')

    ok = $('<button/>')
        .addClass('btn btn-danger btn-small')
        .text('Remove')
        .click(->
            form = container.prev('form')
            p.remove()
            ok.remove()
            nok.remove()
            $.spinner().appendTo(container)

            url = form.data('deleteurl')

            if not url
                form.closest('.collector-config').remove()
                return

            val = $('input:hidden[name^="csrfmiddlewaretoken"]', form).val()

            $.post(url, {csrfmiddlewaretoken: val}).done(->
                form.closest('.collector-config').remove()
            ).fail(->
                # TODO
                console.log 'Failed to remove component'
            )
        )

    nok = $('<button/>')
        .addClass('btn btn-small')
        .text('Cancel')
        .click(->
            container.remove()
        )

    p = $('<p/>')
        .text('Are you sure you want to remove this collector?')

    container.append($('<div/>').append(p).append(nok).append(ok))

    show = ->
        container.removeClass('hidden')
    setTimeout(show, 0)

    return container


$ ->
    $(document).on('click', '.front-panel .remove', (e) ->
        e.preventDefault()
        makeRemoveConfirmPrompt()
            .insertAfter($(this).closest('form'))
    )

    $(document).on('click', '.front-panel .advanced', (e) ->
        e.preventDefault()
        form = $(this).closest('form')
        form.data('oldvalues', form.serializeArray())
        $(this).closest('.flip-panel').flipPanelOpen()
    )

    $(document).on('click', '.back-panel .form-actions .btn-primary', (e) ->
        e.preventDefault()
        $(this).closest('.flip-panel').flipPanelClose()
    )

    $(document).on('click', '.back-panel .form-actions :not(.btn-primary)', (e) ->
        e.preventDefault()
        $(this).closest('.flip-panel').flipPanelClose()
        form = $(this).closest('form')
        values = form.data('oldvalues')
        $.each(values, (i, val) ->
            form.find("[name^=#{val.name}]").val(val.value)
        )
    )

    $('.collector-config.loading').each(->
        src = $(this)
            .addClass('flip-panel')
            .flipPanel({
                width: 500,
                height: 100,
            })

        front = $('<div/>')
            .addClass('front-panel')
            .append($.spinner())
            .appendTo(src)

        $.ajax({
            url: $(this).data('loadurl'),
        }).done((data) ->
            $('.spinner', src).remove()
            src.removeClass('loading').html(data)
        )
    )


class Task
    @fromData: (data) ->
        task = new Task
        task.build(data.uuid).update(data)
        return task

    @fromElement: (el) ->
        task = new Task
        task.el = el
        return task

    appendTo: (container) ->
        this.el.appendTo(container)
        return this

    setProgress: (progress) ->
        status = this.el.data('status')
        this.setProgressStatus(progress, status)
        return this

    setStatus: (status) ->
        progress = this.el.data('progress')
        this.setProgressStatus(progress, status)
        return this

    setProgressStatus: (progress, status) ->
        #if status != this.el.data('status'):
        #	if status == 3  # Changed to success
        #
        #	else if status == 4  # Changed to failed

        this.el.data('progress', progress)
        this.el.data('status', status)

        progress = progress * 100

        $bar = $('.bar', this.el)
        $progress = $('.progress', this.el)
        $percentage = $('.percentage', this.el)

        $progress.attr('class', 'progress')

        if progress >= 0
            $percentage.text("#{Math.round(progress)}%")
            $bar.css('width', "#{progress}%")
        else
            $progress.addClass('progress-striped')
            $percentage.text('')
            $bar.css('width', '100%')

        switch status
            when 0
                # Inactive, bar width is 0% and text is hidden
                $bar.width(0)
                $percentage.text('')
            when 1  # Running
                $progress.addClass('active')
            when 2  # Paused
                $progress.addClass('inactive')
            when 3  # Success
                $progress.removeClass('progress-striped')
                $progress.addClass('progress-success')
            when 4  # Failed
                $progress.removeClass('progress-striped')
                $progress.addClass('progress-danger')
        return this

    setOrder: (order) ->
        this.el.attr('data-order', order)
        return this

    setName: (name) ->
        $('> p:first-child', this.el).text(name)
        return this

    setStatusText: (text) ->
        $('> p.status', this.el).text(text)
        return this

    update: (data) ->
        this.setProgressStatus(data.progress, data.status)
        this.setName(data.name)
        this.setStatusText(data.statusText)
        return this

    build: (uuid, elementType='li')->
        el = $("<#{elementType}/>")
            .attr('id', "task-#{uuid}")
            .addClass('task')

        $('<p/>').appendTo(el)
        bar = $('<div/>').addClass('progress').appendTo(el)
        indicator = $('<div/>').addClass('bar').appendTo(bar)
        $('<span/>').addClass('percentage').appendTo(indicator)
        $('<p/>').addClass('status').appendTo(el)
        this.el = el
        return this

checkComplete = (container) ->
    if not $('.task .progress:not(.progress-success, .progress-danger)', container).size()
        $.get(window.location + '?' + Math.random(), (data) ->
            $('#session-results').replaceWith(data)
            $('#session-results tr[data-uuid]').each(->
                uuid = $(this).data('uuid')
                status = $(this).data('status')
                collector = $("#session-tasks div[data-uuid=#{uuid}]")

                if status != 2 and status != 3
                    return

                if not collector.size()
                    return

                if collector.hasClass('failed') or collector.hasClass('completed')
                    return

                if status == 3
                    collector.addClass('completed')
                    $('<i class="icon-ok icon-success icon-large"> </i>').prependTo(container)
                else if status == 2
                    collector.addClass('failed')
                    $('<i class="icon-warning-sign icon-danger icon-large"> </i>').prependTo(container)

                dismiss = $('<button type="button" class="close" data-dismiss="collector-monitor">&times;</button>')
                dismiss.insertAfter($('strong', collector)).click(->
                    container = $(this).closest('.collector-monitor')
                    p = container.parent()
                    container.remove()
                    if p.find('.collector-monitor').size() == 0
                        p.parent().remove()
                )
            )
        )

sortTasks = (container) ->
    tasks = $('.tasks .task', container).sort((a, b) ->
        $(a).data('order') - $(b).data('order')
    )
    $('.tasks .task', container).remove()
    $('.tasks', container).append(tasks)

loadTasks = (server) ->
    collector = $(this)
    uuid = collector.data('uuid')
    container = $('.tasks', collector)

    server.call('getTasksForCollector', uuid).done (tasks) ->
        $.each(tasks, (i, [order, data]) ->
            t = Task.fromData(data).setOrder(order).appendTo(container)
            #console.log order, t.el.data('order')
            sortTasks(collector)
        )
        checkComplete(collector)
        server.call(
            'broker.exclusiveQueueBind',
            'tasks',
            "task.#{uuid}.*",
            server.callback(([order, data]) ->
                item = $("#task-#{data.uuid}")
                if not item.size()
                    task = Task.fromData(data).setOrder(order)
                    task.appendTo(container)
                else
                    Task.fromElement(item).setOrder(order).update(data)
                checkComplete(collector)
                sortTasks(collector)
            ),
        )

$ ->
    if $('.session-list').size()
        setTilesSize = ->
            $('.session-list li').height($('.session-list li').width())
        setTilesSize()
        $(window).on('resize', setTilesSize)

        $('.session-list li.flip-box:not(.inactive)').click(->
            hash = window.location.hash
            if hash
                hash = hash.substring(1)
            id = $(this).attr('id')

            if id == hash
                # Close this dialog
                window.location.hash = ''
                $("##{hash}").flipBoxClose()
            else
                if hash
                    # Close previous dialog
                    $("##{hash}").flipBoxClose()
                # Open this dialog
                $(this).attr('id', '')
                fix = $('<div/>').attr('id', id).css({
                    position: 'absolute',
                    visibility: 'hidden',
                    top: $(document).scrollTop() + 'px'
                }).attr('id', id).appendTo(document.body)
                window.location.hash = '#' + id
                fix.remove()
                $(this).attr('id', id).flipBoxOpen()
        ).each(->
            bg = $(this).data('background')

            if not bg
                return

            color = [
                bg.substring(1,3)
                bg.substring(3,5)
                bg.substring(5)
            ]
            color = (parseInt(c, 16) for c in color)
            color1 = "rgba(#{color.join(',')},0)"
            color2 = "rgba(#{color.join(',')},0.8)"
            gradient = "linear-gradient(to bottom, #{color1} 0px, #{color2} 30px)"
            $('.front-panel > strong', this).css('background-image', gradient)
        )

        $('.session-list a').click((e) -> e.stopPropagation())

    if $('.collector-monitor').size()
        host = acquisitionServer['host']
        port = acquisitionServer['port']

        if not host
            host = window.location.hostname

            if not port
                port = window.location.port

        if port
            host = "#{host}:#{port}"

        ws = $.websocket("ws://#{host}/", {
            open: (->
                $('.collector-monitor').each(->
                    loadTasks.call(this, ws)
                )
            ),
            close: (->
            ),
            events: {
            }
        })
