makeArray = (type, length) ->
    buffer = new ArrayBuffer(type.BYTES_PER_ELEMENT * length)
    new type(buffer)


class LayoutWorker
    remote_updateNodes: (dom, posx, posy, posz) ->
        domains = new Uint8Array(dom)
        posx = new Float32Array(posx)
        posy = new Float32Array(posy)
        posz = new Float32Array(posz)

        nodes = []
        for domain, i in domains
            position = new Vector3(posx[i], posy[i], posz[i])
            nodes.push({
                domain: domain
                position: position
            })

        @nodes = nodes

    remote_updateEdges: (src, dst) ->
        src = new Uint32Array(src)
        dst = new Uint32Array(dst)

        nodes = @nodes
        edges = []

        for s, i in src
            edges.push([
                nodes[src[i]],
                nodes[dst[i]]
            ])

        @edges = edges

    remote_setProperty: (name, value) ->

    remote_run: -> @run()
    remote_pause: -> @pause()
    remote_stop: -> @stop()

    sendUpdate: (force=false) ->
        if not force
            if @lastUpdate?
                if Date.now() - @lastUpdate < @minUpdateInterval
                    return

        nodes = @nodes

        posx = makeArray(Float32Array, nodes.length)
        posy = makeArray(Float32Array, nodes.length)
        posz = makeArray(Float32Array, nodes.length)

        @nodes.iter((n, i) ->
            posx[i] = n.position.x
            posy[i] = n.position.y
            posz[i] = n.position.z
        )

        @sendMessage('updatePositions', [
            posx.buffer, posy.buffer, posz.buffer
        ], [
            posx.buffer, posy.buffer, posz.buffer
        ])

        @lastUpdate = Date.now()

    handleMessage: (msg) =>
        method = "remote_#{msg.data[0]}"
        args = msg.data.slice(1)
        func = @[method]
        if not func?
            throw "Invalid method: #{method}"
        func.apply(@, args)

    sendMessage: (method, args=[], transfer=[]) ->
        msg = args.slice(0)
        msg.unshift(method)
        postMessage(msg, transfer)


class IterativeLayoutWorker extends LayoutWorker
    constructor: ->
        super
        @interval = 0
        @iterations = 100000

        # Minimum interval between updates, in milliseconds
        @minUpdateInterval = 50

    run: ->
        @stopRequested = false
        @pauseRequested = false
        @iteration = 0

        @sendMessage('started')

        @initialize()
        runloop = =>
            if @stopRequested
                @sendMessage('stopped', [true])
            else if @pauseRequested
                @sendMessage('stopped', [false])
            else
                @step()
                @iteration++
                @sendUpdate()
                if @iteration >= @iterations
                    @stop()
                setTimeout(runloop, @interval)
        runloop()

    initialize: ->

    step: ->

    stop: ->
        @stopRequested = true

    pause: ->
        @pauseRequested = true

    remote_step: ->
        @initialize()
        @iteration++
        @sendUpdate()
