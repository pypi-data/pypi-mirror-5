class Form
    @makeForm: (baseId, fields, callback) ->
        panel = $('<form/>').addClass('form-horizontal').attr('id', baseId)
        $.each(fields, (key) ->
            Form.makeInput("#{baseId}-input-#{key}", key, this, callback)
                .appendTo(panel)
            return true
        )
        panel

    @makeInput: (id, key, field, callback) ->
        label = $('<label/>')
            .addClass('control-label')
            .text(field.label)
            .attr('for', id)

        input = Form["_getInput_#{field.type}"](field)
            .attr('id', id)
            .attr('name', key)

        if callback
            input.change(->
                el = $(this)
                val = Form.getValue(el.parent(), el.attr('name'), field)
                callback(key, val, field, el)
            )

        $('<div/>')
            .addClass('control-group')
            .append(label)
            .append(input)

    @getValue: (form, key, field) ->
        input = $("[name=#{key}]", form)
        Form["_getValue_#{field.type}"](field, input)

    @_getInput_colorGradient: (field) ->
        picker = undefined

        ctx = $('<div/>')

        input = $('<div/>')
            .addClass('gradient-editor')
            .append(ctx.append($('<div/>').addClass('gradient-preview')))

        makeColorSelector = ->
            $('<div/>')
                .addClass('color-selector')
                .append('')

        makeStop = (input, color, position) ->
            stop = $('<div/>').addClass('color-stop')
            stop.append($('<span/>').addClass('tip').css('border-bottom-color', color))
                .append($('<input/>').attr('type', 'text'))
                .css({
                    'background-color': color
                    'left': "#{position * 100}%"
                    'position': 'absolute'
                }).draggable({
                    axis: 'x',
                    containment: $('.gradient-preview', input),
                    drag: (e, ui) ->
                        $this = $(this)
                        if $this.hasClass('open')
                            $('.gradient-color-picker').css({
                                left: $this.offset().left,
                            })
                        updateGradient($(this).closest('.gradient-editor'))
                }).bind('contextmenu', (e) ->
                    e.stopPropagation()
                    e.preventDefault()
                    editor = $(this).closest('.gradient-editor')
                    if $(this).hasClass('open')
                        picker.hidePicker()
                    $(this).remove()
                    updateGradient(editor)
                ).click((e) ->
                    if $(this).hasClass('open')
                        return
                    e.stopPropagation()
                    e.preventDefault()
                    $('.color-stop.open').removeClass('open')
                    stop = $(this).addClass('open')
                    col = stop.css('background-color').replace(/[^\d ]+/g, '').split(' ')
                    col = (parseInt(c)/255 for c in col)
                    picker = new jscolor.color($('input', stop).get(0), {
                        onImmediateChange: (e) ->
                            stop.css('background', "##{this.toString()}")
                            stop.find('span').css('border-bottom-color', "##{this.toString()}")
                            updateGradient(stop.closest('.gradient-editor'))
                    })
                    picker.fromRGB(col[0], col[1], col[2])
                    picker.showPicker()
                    $(jscolor.picker.boxB).css({
                        top: stop.offset().top + stop.height(),
                        left: stop.offset().left,
                    })
                        .addClass('color-picker gradient-color-picker')
                        .click((e) -> e.stopPropagation())
                        .mousedown((e) -> e.preventDefault())

                    $('body').one('click', ->
                        stop.removeClass('open')
                        $(jscolor.picker.boxB).removeClass('gradient-color-picker')
                        picker.hidePicker()
                    )
                ).dblclick((e) -> e.stopPropagation())

        updateGradient = (editor) ->
            width = editor.find('> div').width()
            colors = []
            $('.color-stop', editor).each(->
                left = $(this).get(0).style.left
                if left.endswith('%')
                    left = parseInt(left) / 100
                else if left.endswith('px')
                    left = parseInt(left) / width

                colors.push([left, $(this).css('background-color')])
            )
            colors.sort()
            colors.reverse()
            colors = ("color-stop(#{c[0]}, #{c[1]})" for c in colors)
            gradient = "-webkit-gradient(linear, left bottom, right bottom, #{colors.join(', ')})"
            $('.gradient-preview', editor).css('background-image', gradient)
            editor.trigger('change')

        ctx.dblclick((e) ->
            editor = $(this)
            ctx = editor.find('> div')
            position = (e.pageX - ctx.offset().left) / ctx.width()
            editor.append(makeStop(editor, 'green', position))
            updateGradient(editor)
        )

        makeStop(input, '#1f201a', 0).appendTo(ctx)
        makeStop(input, '#41b3a5', 0.5).appendTo(ctx)
        makeStop(input, '#b4ff49', 1).appendTo(ctx)
        updateGradient(input)

        input

    @_getValue_colorGradient: (field, input) ->
        width = input.find('> div').width()
        colors = []
        $('.color-stop', input).each(->
            left = $(this).get(0).style.left
            if left.endswith('%')
                left = parseInt(left) / 100
            else if left.endswith('px')
                left = parseInt(left) / width
            col = $(this).css('background-color').replace(/[^\d ]+/g, '').split(' ')
            col = (parseInt(c) for c in col)
            colors.push([left, col])
        )
        colors.sort()

        colors.unshift([0, colors[0][1]])
        colors.push([1, colors[colors.length-1][1]])

        func = (p) ->
            a = 0
            b = colors.length - 1

            if b == 0
                return
            maxiter = colors.length
            while maxiter > 0
                i = Math.floor((b + a) / 2)
                if colors[i][0] > p
                    b = i
                else if colors[i][0] < p
                    a = i
                else
                    return colors[i][1]
                if b == a + 1
                    break
                maxiter--
            if not maxiter
                throw "Iteration limit reached."

            c1 = colors[a][1]
            c2 = colors[b][1]
            p = (p - colors[a][0]) / (colors[b][0] - colors[a][0])

            toHex = (c) ->
                c = Math.round(c)
                c = Math.min(c, 255)
                c = Math.max(c, 0)
                hex = c.toString(16)
                if hex.length == 1 then '0' + hex else hex

            '#' + [
                toHex(Math.round(c1[0] + (c2[0] - c1[0]) * p)),
                toHex(Math.round(c1[1] + (c2[1] - c1[1]) * p)),
                toHex(Math.round(c1[2] + (c2[2] - c1[2]) * p)),
            ].join('')

    @_getInput_color: (field) ->
        input = Form._getInput_string(field)
        picker = new jscolor.color(input.get(0), {
            onImmediateChange: (e) ->
                input.trigger('change')
        })
        input.on('focus', ->
            $(jscolor.picker.boxB).addClass('color-picker')
        )
        input

    @_getValue_color: (field, input) ->
        parseInt(input.val(), 16)

    @_getInput_list: (field) ->
        selector = $('<select/>')
        $.each(field.values or [], (i) ->
            $('<option/>')
                .val(this[0])
                .text(this[1])
                .appendTo(selector)
            return true
        )
        if field.values.length <= 1
            selector.attr('disabled', 'disabled')
        selector

    @_getValue_list: (field, input) ->
        Form["_getValue_#{field.valueType}"](field, input)

    @_getInput_boolean: (field) ->
        $('<input/>')
            .attr('type', 'checkbox')
            .val(1)
            .attr('checked', field.initial)

    @_getValue_boolean: (field, input) -> input.is(':checked')

    @_getInput_integer: (field) ->
        $('<input/>')
            .attr('type', 'number')
            .attr('min', field.min)
            .attr('max', field.max)
            .attr('step', Math.round(field.step or 1))
            .val(field.initial)

    @_getValue_integer: (field, input) ->
        parseInt(input.val())

    @_getInput_string: (field) ->
        $('<input/>').val(field.initial)

    @_getValue_string: (field, input) ->
        input.val()

    @_getInput_float: (field) ->
        input =
        $('<input/>')
            .attr('type', if field.range then 'range' else 'number')
            .attr('min', field.min)
            .attr('max', field.max)
            .attr('step', field.step or 0.01)
            .val(field.initial)

    @_getValue_float: (field, input) ->
        parseFloat(input.val())


class LayoutConfigurator
    constructor: (@factories) ->
        @callbacks = {
            layoutChanged: $.Callbacks()
        }

    getForm: ->
        this_ = this
        baseId = "config-#{Math.round(Math.random()*10e6)}"

        @container = $('<div/>')
            .attr('id', baseId)
            .addClass('algorithm-configurator form-horizontal')

        # Option selector
        i = 0
        Form.makeInput("#{baseId}-algo", 'algo', {
            label: 'Algorithm'
            type: 'list'
            valueType: 'integer'
            values: ([i++, f.getName()] for f in @factories)
        }, this_._switchConfig)
            .addClass('algorithm-select')
            .appendTo(this_.container)
        $.each(@factories, (i) ->
            Form.makeForm(
                "#{baseId}-factory-#{i}",
                this.getSettings(),
                this_._updateConfig
            ).addClass('algorithm-config').appendTo(this_.container)
        )
        @_switchConfig('', 0, undefined, $('.algorithm-select select', @container))
        @container

    getLayout: ->
        this_ = this
        selected = $('.algorithm-select select', @container).val()
        form = $('.algorithm-config', @container).eq(selected)
        config = form.serializeArray()
        settings = @currentFactory.getSettings()
        layout = @currentFactory.buildLayout()
        $.each(settings, (key) ->
            val = Form.getValue(form, key, this)
            layout[this.setter](val)
            return true
        )
        @currentLayout = layout

    _switchConfig: (key, val, field, select) =>
        @currentFactory = @factories[val]
        @callbacks.layoutChanged.fire(@currentFactory)
        $('.algorithm-config', select.closest('.algorithm-configurator'))
            .addClass('hidden')
            .eq(val)
            .removeClass('hidden')

    _updateConfig: (key, val, field, el) =>
        if not @currentLayout
            return
        form = el.closest('form')
        t = form.attr('id').split('-')
        if parseInt(t[t.length - 1]) != @factories.indexOf(@currentFactory)
            return
        @currentLayout[field.setter](val)


class StrategyConfigurator
    constructor: (@strategies, @viewer) ->

    getForm: ->
        this_ = this
        @container = $('<div/>')
            .addClass('strategy-configurator form-horizontal')

        # Option selector
        i = 0
        Form.makeInput("strategy", 'strategy', {
            label: 'Strategy'
            type: 'list'
            valueType: 'integer',
            values: ([i++, f.getName()] for f in @strategies)
        }, this_._switchConfig)
            .addClass('strategy-select').appendTo(this_.container)

        $.each(@strategies, (i) ->
            this.getForm().appendTo(this_.container)
            return true
        )
        @container.find('.strategy-config').addClass('hidden')
        @container

    enable: ->
        @_switchConfig('', 0, undefined, $('.strategy-select select', @container))

    _switchConfig: (key, val, field, select) =>
        if @currentStrategy
            @currentStrategy.deactivate()
        @currentStrategy = @strategies[val]
        #@currentLayout = undefined
        $('.strategy-config', select.closest('.strategy-configurator'))
            .addClass('hidden')
            .eq(val)
            .removeClass('hidden')
        @viewer.setRenderer(@currentStrategy.activate(@viewer))
