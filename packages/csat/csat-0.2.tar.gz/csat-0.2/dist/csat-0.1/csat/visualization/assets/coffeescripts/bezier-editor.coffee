class BezierEditor
    constructor: (width, height, @min, @max) ->
        @_overscale = 2
        @_handleRadius = 8

        @minY = 2
        @maxY = 10

        @padding = [20, 40, 120, 40]

        @changed = $.Callbacks()

        @width = width * @_overscale
        @height = height * @_overscale
        @framewidth = @width - @padding[1] - @padding[3]
        @frameheight = @height - @padding[0] - @padding[2]

        @c1 = [@framewidth * 0.6666, @frameheight * 0.1]
        @c2 = [@framewidth * 0.3333, @frameheight * 0.9]

        @_build()

    setInterval: (@min, @max) ->
        @_redraw(@ctx)
        @changed.fire(@getFunction())
        @

    getFunction: ->
        w = @framewidth
        h = @frameheight
        max = @max
        min = @min
        maxY = @maxY
        minY = @minY

        c1x = @c1[0] * 1.0 / w * (max - min) + min
        c2x = @c2[0] * 1.0 / w * (max - min) + min
        c1y = @c1[1] * 1.0 / h * (maxY - minY) + minY
        c2y = @c2[1] * 1.0 / h * (maxY - minY) + minY

        b_t_y = (t) ->
            t1 = 1 - t
            t2 = t1 * t1
            t3 = t1 * t2

            p0 = t3 * minY
            p1 = 3 * t2 * t * c1y
            p2 = 3 * t1 * t * t * c2y
            p3 = t * t * t * maxY

            p0 + p1 + p2 + p3

        b_t_x = (t) ->
            t1 = 1 - t
            t2 = t1 * t1
            t3 = t2 * t1

            p0 = t3 * min
            p1 = 3 * t2 * t * c1x
            p2 = 3 * t1 * t * t * c2x
            p3 = t * t * t * max

            p0 + p1 + p2 + p3

        b_x = (x) ->
            ta = 0.0
            tb = 1.0
            e = Infinity
            i = 500
            x *= 1.0
            while e > 0.0000001 and i > 0
                t = (tb + ta) / 2.0
                xt = b_t_x(t)
                if xt > x
                    tb = t
                else
                    ta = t
                e = Math.abs(x - xt)
                i--
            b_t_y(t)

    setMin: (@minY) =>
        @changed.fire(@getFunction())

    setMax: (@maxY) =>
        @changed.fire(@getFunction())

    _positionFromEvent: (e) =>
        o = @canvas.offset()
        inside = true

        x = (e.pageX - o.left) * @_overscale - @padding[3]

        if x < 0 or x > @framewidth
            inside = false

        x = Math.min(@framewidth - 2.5, x)
        x = Math.max(2.5, x)

        y = (@height - (e.pageY - o.top) * @_overscale) - @padding[2]

        if y < 0 or y > @height - @padding[2] - @padding[0]
            inside = false

        y = Math.min(@frameheight - 2.5, y)
        y = Math.max(2.5, y)

        [[x, y], inside]

    _buildCanvas: ->
        distSq = (p1, p2) ->
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dx * dx + dy * dy

        $('<canvas/>')
            .width(@width / @_overscale)
            .height(@height / @_overscale)
            .on('mousedown', (e) =>
                e.preventDefault()
                [p, inside] = @_positionFromEvent(e)

                if not inside
                    return

                d1 = distSq(p, @c1)
                d2 = distSq(p, @c2)

                if d1 < d2
                    d = d1
                    candidate = @c1
                else
                    d = d2
                    candidate = @c2

                if 1 or d < Math.pow(100 * @_overscale, 2)
                    @_target = candidate
                else
                    @_target = undefined

                [@_target[0], @_target[1]] = p

                if @_target
                    $(window).on('mousemove.bezier', (e) =>
                        e.preventDefault()
                        [@_target[0], @_target[1]] = @_positionFromEvent(e)[0]
                        @_redraw(@ctx)
                    ).on('mouseup.bezier', =>
                        e.preventDefault()
                        @_target = undefined
                        @_redraw(@ctx)
                        $(window).off('mousemove.bezier').off('mouseup.bezier')
                        f = @getFunction()
                        @changed.fire(f)
                    )
                    @_redraw(@ctx)
            )

    _buildForm: ->
        Form.makeForm(
            'nodes-display-settings',
            {
                minsize: {
                    label: 'Min'
                    type: 'float'
                    initial: @minY
                    setter: 'setMin'
                }
                maxsize: {
                    label: 'Max'
                    type: 'float'
                    initial: @maxY
                    setter: 'setMax'
                }
            },
            (key, val, field) =>
                @[field.setter](val)
        ).width(@width / @_overscale)

    _build: ->
        @canvas = @_buildCanvas()

        canvas = @canvas.get(0)
        canvas.width = @width
        canvas.height = @height

        @ctx = canvas.getContext('2d')
        @ctx.webkitImageSmoothingEnabled = true
        #@ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

        @form = @_buildForm()
        @element = $('<div/>')
            .addClass('bezier-editor')
            .append(@canvas)
            .append(@form)

        @_redraw(@ctx)

    _reset: ->
        @canvas.get(0).width = @canvas.get(0).width

    _redraw: (ctx) =>
        @_reset()

        drawGrid = (ctx, x, y, w, h, min, max) =>
            ctx.fillStyle = "#fff"
            ctx.fillRect(x + 0.5, y + 0.5, w - 1, h - 1)

            ctx.beginPath()
            cols = 3
            for col in [1...cols]
                p = Math.round((max - min) * col / cols + min)
                xi = Math.round(col * w/cols) + x
                ctx.moveTo(xi, y)
                ctx.lineTo(xi, y + h)
                ctx.fillStyle = '#888888'
                ctx.font = "normal #{12 * @_overscale}px menlo"
                ctx.textBaseline = 'top'
                ctx.textAlign = "center"
                ctx.fillText(p, xi, h + y + 1)

            rows = 3
            for row in [1...rows]
                yi = 0.5 + Math.round(row * h/cols) + y
                ctx.moveTo(x, yi)
                ctx.lineTo(x + w, yi)

            ctx.fillStyle = '#888888'
            ctx.textAlign = "left"
            ctx.font = "normal #{12 * @_overscale}px menlo"
            ctx.fillText(min, x, y + h + 1)
            ctx.textAlign = "right"
            ctx.fillText(max, x + w, y + h + 1)
            ctx.strokeStyle = "#ddd"
            ctx.stroke()

        drawIndicators = (ctx, x, y, w, h, height) =>
            ctx.beginPath()

            ctx.moveTo(x - 8,                   y + h - 0.5)
            ctx.lineTo(Math.round(x / 2) - 2.5, y + h - 0.5)
            ctx.lineTo(Math.round(x / 2) - 2.5, y + h - 0.5 + height)
            ctx.lineTo(x + 8.5,                 y + h - 0.5 + height)
            ctx.moveTo(x + 8.5,                 y + h - 18.5 + height)
            ctx.lineTo(x + 8.5,                 y + h + 16 + height)

            ctx.moveTo(x + w + 8,                       y + 0.5)
            ctx.lineTo(x + w + Math.round(x / 2) + 2.5, y + 0.5)
            ctx.lineTo(x + w + Math.round(x / 2) + 2.5, y + h - 0.5 + height)
            ctx.lineTo(x + w - 8,                       y + h - 0.5 + height)
            ctx.moveTo(x + w - 8.5,                     y + h - 18.5 + height)
            ctx.lineTo(x + w - 8.5,                     y + h + 16 + height)

            ctx.strokeStyle = "#666"
            ctx.stroke()

        drawFrame = (ctx, x, y, w, h) =>
            ctx.strokeStyle = "#999"
            ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1)

        drawFunction = (ctx, x, y, w, h, c1, c2) =>
            ctx.beginPath()
            ctx.moveTo(x + 2.5, y + h - 1.5)
            ctx.bezierCurveTo(
                x + c1[0], y + h - c1[1],
                x + c2[0], y + h - c2[1],
                x + w - 1.5, y + 2.5)
            ctx.strokeStyle = "#2c9cd7"
            ctx.lineWidth = 5
            ctx.stroke()

        drawHandles = (ctx, x, y, w, h, c1, c2) =>
            drawHandle = (x1, y1, x2, y2, active) =>
                r = if active then @_handleRadius + 5 else @_handleRadius
                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.lineWidth = 3
                ctx.strokeStyle = "#cccccc"
                ctx.stroke()

                ctx.beginPath()
                ctx.moveTo(x2, y2)
                ctx.arc(x2, y2, r + 5, 0, 2 * Math.PI)
                ctx.closePath()
                ctx.fillStyle = '#ffffff'
                ctx.fill()

                ctx.beginPath()
                ctx.moveTo(x2, y2)
                ctx.arc(x2, y2, r + 2, 0, 2 * Math.PI)
                ctx.closePath()
                ctx.fillStyle = '#999999'
                ctx.fill()

                ctx.beginPath()
                ctx.moveTo(x2, y2)
                ctx.arc(x2, y2, r - 2, 0, 2 * Math.PI)
                ctx.closePath()
                ctx.fillStyle = '#ffffff'
                ctx.fill()

            drawHandle(x + 2.5, y + h - 1.5, x + c1[0], y + h - c1[1], @_target == c1)
            drawHandle(x + w - 2.5, y + 2.5, x + c2[0], y + h - c2[1], @_target == c2)

        drawGrid(ctx, @padding[3], @padding[0], @framewidth, @frameheight, @min, @max)
        drawFrame(ctx, @padding[3], @padding[0], @framewidth, @frameheight)
        drawIndicators(ctx, @padding[3], @padding[0], @framewidth, @frameheight, 79)
        drawFunction(ctx, @padding[3], @padding[0], @framewidth, @frameheight, @c1, @c2)
        drawHandles(ctx, @padding[3], @padding[0], @framewidth, @frameheight, @c1, @c2)

    getElement: ->
        return @element


class BezierColorEditor extends BezierEditor
    constructor: (width, height, @min, @max) ->
        super
        @minY = 0
        @maxY = 1

        @c1 = [@framewidth * 0.3333, @frameheight * 0.3333]
        @c2 = [@framewidth * 0.6666, @frameheight * 0.6666]

    _buildForm: ->
        @form = Form.makeForm(
            'nodes-color-settings',
            {
                gradient: {
                    label: 'Gradient'
                    type: 'colorGradient'
                }
            },
            (key, val, field) =>
                @g = val
                @changed.fire(@getFunction())
        ).width(@width / @_overscale)

    getFunction: ->
        f = super
        g = @g
        if not g?
            g = Form.getValue(@form, 'gradient', {type: 'colorGradient'})
        func = (t) ->
            g(f(t))
