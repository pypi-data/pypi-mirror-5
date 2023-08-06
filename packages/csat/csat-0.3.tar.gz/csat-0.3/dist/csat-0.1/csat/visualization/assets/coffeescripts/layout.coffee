# {{{ Base classes
class LayoutFactory
    getName: -> ''
    getSettings: -> []
    buildLayout: ->

class Layout
    constructor: ->
        @callbacks = {
            started: $.Callbacks()
            step: $.Callbacks()
            done: $.Callbacks()
            paused: $.Callbacks()
            resumed: $.Callbacks()
        }

    _fire: (event, args...) ->
        @callbacks[event].fire.apply(this, args)

    _run: ->

    # External interface
    run: (@nodes, @edges) ->
        @setup()
        @_fire('started')
        @_run()
        @teardown()
        @_fire('done')

    setScene: (@scene) ->

    runStep: (nodes, edges) ->
        @run(nodes, edges)

    stop: ->

    pause: ->
        @stop()

    reset: ->

    # Internal interface
    setup: ->
    teardown: ->
    isRunning: -> false
    isPaused: -> false

class IterativeLayout extends Layout
    constructor: ->
        super
        @_interval = 1
        @_initialized = false
        @_running = false
        @_paused = false

    run: (@nodes, @edges) ->
        if not @_initialized
            @setup()
            @_initialized = true

        @_stop = false
        @_running = true

        if @_paused
            @_paused = false
            @_fire('resumed')
        else
            @_fire('started')

        run = =>
            if @_stop or @_paused
                @_running = false
                if @_paused
                    @_fire('paused')
                else
                    @_initialized = false
                    @_fire('done')
                return
            @step()
            @_fire('step')
            @currentIteration -= 1
            if @currentIteration <= 0
                @_stop = true
            setTimeout(run, @_interval)
        run()

    stop: ->
        @_stop = true
        @_paused = false

    pause: ->
        @_stop = true
        @_paused = true

    runStep: (@nodes, @edges) ->
        if not @_initialized
            @setup()
            @_initialized = true
        @step()
        @_fire('step')

    isRunning: -> @_running
    isPaused: -> @_paused

    reset: ->
        @teardown()
        @_initialized = false

    # This is called before the first step is executed
    setup: ->

    # Implement this method in your layout algorithm
    step: ->

    # This is called after the last step has executed
    teardown: ->

class WorkerLayout extends Layout
    constructor: (@implementation) ->
        @worker = new Worker(window.layoutWorkers[@implementation])
        @worker.onmessage = @handleMessage
        super

    handleMessage: (msg) =>
        method = "remote_#{msg.data[0]}"
        args = msg.data.slice(1)
        func = @[method]
        if not func?
            throw "Invalid method: #{method}"
        func.apply(@, args)

    remote_started: ->
        @_running = true
        @_fire('started')

    remote_stopped: (done) ->
        @_paused = not done
        @_running = false
        if done
            @_fire('done')
        else
            @_fire('paused')

    remote_updatePositions: (posx, posy, posz) ->
        posx = new Float32Array(posx)
        posy = new Float32Array(posy)
        posz = new Float32Array(posz)

        @nodes.iter((n, i) ->
            p = new THREE.Vector3(posx[i], posy[i], posz[i])
            n.setPosition(p)
        )
        @_fire('step')

    sendMessage: (method, args=[], transfer=[]) ->
        msg = args.slice(0)
        msg.unshift(method)
        @worker.postMessage(msg, transfer)

    stop: ->
        @sendMessage('stop')

    pause: ->
        @sendMessage('pause')

    reset: ->

    # Internal interface
    setup: ->
        @updateModel()

    run: (@nodes, @edges) ->
        @_running = false
        @_paused = false
        @setup()
        @sendMessage('run')

    runStep: (@nodes, @edges) ->
        @setup()
        @sendMessage('step')

    teardown: ->
        #@sendMessage('teardown')

    isRunning: -> @_running
    isPaused: -> @_paused


    updateModel: ->
        makeArray = (type, length) ->
            buffer = new ArrayBuffer(type.BYTES_PER_ELEMENT * length)
            new type(buffer)

        c = 0
        @nodes.iter(-> c++)

        dom = makeArray(Uint8Array, c)
        posx = makeArray(Float32Array, c)
        posy = makeArray(Float32Array, c)
        posz = makeArray(Float32Array, c)

        nodeMap = {}

        @nodes.iter((n, i) ->
            p = n.getPosition()
            dom[i] = n.domain.id
            posx[i] = p.x
            posy[i] = p.y
            posz[i] = p.z
            nodeMap[n.fqid] = i
        )

        @sendMessage('updateNodes', [
            dom.buffer, posx.buffer, posy.buffer, posz.buffer
        ], [
            dom.buffer, posx.buffer, posy.buffer, posz.buffer
        ])

        c = 0
        @edges.iter(-> c++)

        src = makeArray(Uint32Array, c)
        dst = makeArray(Uint32Array, c)

        @edges.iter((e, i) ->
            src[i] = nodeMap[e.src.fqid]
            dst[i] = nodeMap[e.dst.fqid]
        )

        @sendMessage('updateEdges', [src.buffer, dst.buffer], [src.buffer, dst.buffer])

# }}}



class FruchtermanReingoldLayout2D extends IterativeLayout
    setup: ->
        @redrawArea()
        @_updateAxis()
        @nodes.iter((node) =>
            o = new THREE.Vector3(
                Math.random() - 0.5,
                Math.random() - 0.5,
                Math.random() - 0.5,
            )
            o.setComponent(@axis, 0)

            p = node.getPosition()
            p.add(o)
            node.setPosition(p)
        )
        @currentIteration = @iterations

    setTemperature: (@temperature) ->
    setK: (@k) -> @_resume()
    setIterations: (@iterations) -> @_resume()
    setAreaVisible: (areaVisible) ->
        if not @scene
            @areaVisible = areaVisible
            return
        if not areaVisible
            @scene.remove(@_circleObject)
        else if areaVisible
            @scene.add(@_circleObject)
        @areaVisible = areaVisible
    setRadius: (@radius) ->
        @redrawArea()
        @_resume()
    setOnlyVisible: (@onlyVisible) ->

    setScene: (@scene) ->
        @redrawArea()

    redrawArea: ->
        if @scene and @areaVisible and @_circleObject
            @scene.remove(@_circleObject)
        @_circleObject = makeCirclePlane(@radius, @axis)
        if @scene and @areaVisible
            @scene.add(@_circleObject)

    setAxis: (axis) ->
        @_oldAxis = @axis
        @axis = axis
        @redrawArea()

    _resume: ->
        @currentIteration = @iterations

    step: ->
        @count = 0
        @_calculateForces()
        @_applyPositions()

    run: ->
        if not @_paused
            @_resume()
        super
        @redrawArea()

    _calculateRepulsion: ->
        f_r = (d) =>
            -@k * @k / d

        @nodes.iter((v) =>
            if @onlyVisible and not v.isVisible()
                return
            v._force = new THREE.Vector3(0, 0, 0)
            @nodes.iter((u) =>
                if u == v
                    return
                if @onlyVisible and not u.isVisible()
                    return
                d = v.getPosition().clone().sub(u.getPosition())
                if d.length() == 0
                    d = new THREE.Vector3(Math.random(), Math.random(), Math.random())
                    d.setComponent(@axis, 0)
                f = f_r(d.length())
                v._force.sub(d.normalize().multiplyScalar(f))
            )
            @count++
        )

    _calculateAttraction: ->
        f_a = (d) =>
            d * d / @k

        @edges.iter((e) =>
            if @onlyVisible and not e.isVisible()
                return
            [u, v] = [e.src, e.dst]
            d = v.getPosition().clone().sub(u.getPosition())
            if d.length() == 0
                d = new THREE.Vector3(Math.random(), Math.random(), Math.random())
                d.setComponent(@axis, 0)
            f = f_a(d.length()) * 2
            f = d.normalize().multiplyScalar(f)
            v._force.sub(f)
            u._force.add(f)
            @count++
        )

    _updateAxis: ->
        if @_oldAxis != undefined
            @nodes.iter((node) =>
                p = node.getPosition()
                p.setComponent(@_oldAxis, p.getComponent(@axis))
                p.setComponent(@axis, 0)
                node.setPosition(p)
            )
            @_oldAxis = undefined

    _calculateForces: ->
        @_updateAxis()
        @_calculateRepulsion()
        @_calculateAttraction()

    _applyPositions: ->
        fmax = @radius / 2
        fmax2 = fmax * fmax
        temp = @currentIteration / @iterations * @temperature

        @nodes.iter((node) =>
            if @onlyVisible and not node.isVisible()
                return
            d = node._force.normalize().multiplyScalar(temp)
            if d.lengthSq() > fmax2
                d.setLength(fmax)
            p = node.getPosition().clone().add(d)
            if p.lengthSq() > @radius * @radius
                p.setLength(@radius)
            p.setComponent(@axis, 0)
            node.setPosition(p)
        )

class FRLayout2DFactory extends LayoutFactory
    getName: -> 'Fruchterman-Reingold (2D)'
    buildLayout: -> new FruchtermanReingoldLayout2D()
    getSettings: ->
        {
            k: {
                label: 'Optimal distance'
                type: 'integer'
                min: 1
                initial: 10
                setter: 'setK'
            }
            temperature: {
                label: 'Initial temperature'
                type: 'float'
                max: 1
                min: 0
                initial: 1
                step: 0.01
                setter: 'setTemperature'
            }
            iterations: {
                label: 'Iterations'
                type: 'integer'
                min: 1
                initial: 500
                setter: 'setIterations'
            }
            radius: {
                label: 'Maximal radius'
                type: 'integer'
                min: 1
                initial: 150
                setter: 'setRadius'
            }
            axis: {
                label: 'Plane'
                type: 'list'
                valueType: 'integer'
                values: [
                    [2, 'X-Y']
                    [1, 'X-Z']
                    [0, 'Y-Z']
                ]
                setter: 'setAxis'
            }
            area: {
                label: 'Show surface'
                type: 'boolean'
                initial: true
                setter: 'setAreaVisible'
            }
            visible: {
                label: 'Only visible'
                type: 'boolean'
                initial: false
                setter: 'setOnlyVisible'
            }
        }



class FRLayout2DAsync extends WorkerLayout
    constructor: ->
        super('fr2d')

    setK: (k) ->
        @sendMessage('setProperty', ['k', k])

    setIterations: (iterations) ->
        @sendMessage('setProperty', ['iterations', iterations])

    setRadius: (@radius) ->
        @sendMessage('setProperty', ['radius', radius])
        @redrawArea()

    setAxis: (@axis) ->
        @sendMessage('setProperty', ['axis', axis])
        @redrawArea()

    setTemperature: (temp) ->
        @sendMessage('setProperty', ['temperature', temp])

    setScene: (@scene) ->
        @redrawArea()

    setAreaVisible: (areaVisible) ->
        if not @scene
            @areaVisible = areaVisible
            return
        if not areaVisible
            @scene.remove(@_circleObject)
        else if areaVisible
            @scene.add(@_circleObject)
        @areaVisible = areaVisible

    redrawArea: ->
        if @scene and @areaVisible and @_circleObject
            @scene.remove(@_circleObject)
        @_circleObject = makeCirclePlane(@radius, @axis)
        if @scene and @areaVisible
            @scene.add(@_circleObject)


class FRLayout2DAsyncFactory extends FRLayout2DFactory
    getName: -> 'Fruchterman-Reingold (2D, async)'
    buildLayout: -> new FRLayout2DAsync()
    getSettings: ->
        settings = $.extend({}, super())
        delete settings['visible']
        settings



class DomainFruchtermanReingoldLayout2D extends FruchtermanReingoldLayout2D
    setInterDomainEdgeWeight: (w) ->
        if w > 0
            w *= @k * 2
        @interWeight = w + 1

    _calculateRepulsion: ->
        f_r = (d) =>
            -@k * @k / d

        @nodes.iter((v) =>
            if @onlyVisible and not v.isVisible()
                return
            v._force = new THREE.Vector3(0, 0, 0)
            @nodes.iter((u) =>
                if u == v
                    return
                if u.domain.id != v.domain.id
                    return
                if @onlyVisible and not u.isVisible()
                    return
                d = v.getPosition().clone().sub(u.getPosition())
                if d.length() == 0
                    d = new THREE.Vector3(Math.random(), Math.random(), Math.random())
                    d.setComponent(@axis, 0)
                f = f_r(d.length())
                v._force.sub(d.normalize().multiplyScalar(f))
            )
            @count++
        )

    _calculateAttraction: ->
        f_a = (d) =>
            d * d / @k

        @edges.iter((e) =>
            if @onlyVisible and not e.isVisible()
                return
            [u, v] = [e.src, e.dst]
            d = v.getPosition().clone().sub(u.getPosition())
            l = d.length()
            if e.src.domain.id != e.dst.domain.id
                l *= @interWeight
            f = f_a(l) * 2
            f = d.normalize().multiplyScalar(f)
            v._force.sub(f)
            u._force.add(f)
            @count++
        )

class DomainFRLayout2DFactory extends FRLayout2DFactory
    getName: -> 'Domain Fruchterman-Reingold (2D)'
    buildLayout: -> new DomainFruchtermanReingoldLayout2D()
    getSettings: ->
        settings = super()
        settings.interWeight = {
            label: 'Inter-/intra-domain edge clarity tradeoff'
            type: 'float'
            initial: 0
            range: true
            min: -1
            max: 1
            setter: 'setInterDomainEdgeWeight'
        }
        return settings



class FruchtermanReingoldLayout3D extends FruchtermanReingoldLayout2D
    _wireframe: ->
        sphereGeometry = new THREE.SphereGeometry(@radius, 20, 20)
        dashMaterial = new THREE.LineBasicMaterial({
            color:  0x000000,
            opacity: .07,
            dashSize: .2,
            gapSize: 5,
            transparent: true,
        })
        wireframe = new THREE.Line(geo2line(sphereGeometry), dashMaterial,
                                   THREE.LinePieces)
        wireframe.position.set(0, 0, 0)
        return wireframe

    drawWireframe: ->
        @_wireframeObject = @_wireframe()
        if @scene and @wireframe
            @scene.add(@_wireframeObject)

    setup: ->
        @nodes.iter((node) =>
            p = node.getPosition()
            p.add(new THREE.Vector3(
                Math.random() / 1000,
                Math.random() / 1000,
                Math.random() / 1000,
            ))
            node.setPosition(p)
        )
        @currentIteration = @iterations

    setWireframe: (@wireframe) ->
        if not @scene
            @wireframe = wireframe
            return

        if not @wireframe
            @scene.remove(@_wireframeObject)
        else if @wireframe
            @scene.add(@_wireframeObject)

    setRadius: (@radius) ->
        if @scene
            if @wireframe
                @scene.remove(@_wireframeObject)
            @_wireframeObject = @_wireframe()
            if @wireframe
                @scene.add(@_wireframeObject)
        @_resume()

    setScene: (@scene) ->
        @drawWireframe()

    _calculateForces: ->
        @_calculateRepulsion()
        @_calculateAttraction()

    _calculateAttraction: ->
        f_a = (d) =>
            d * d / @k

        @edges.iter((e) =>
            if @onlyVisible and not e.isVisible()
                return
            [u, v] = [e.src, e.dst]
            d = v.getPosition().clone().sub(u.getPosition())
            if d.length() == 0
                d = new THREE.Vector3(Math.random(), Math.random(), Math.random())
            f = f_a(d.length()) * 2
            f = d.normalize().multiplyScalar(f)
            v._force.sub(f)
            u._force.add(f)
            @count++
        )

    _calculateRepulsion: ->
        f_r = (d) =>
            -@k * @k / d

        @nodes.iter((v) =>
            if @onlyVisible and not v.isVisible()
                return
            v._force = new THREE.Vector3(0, 0, 0)
            @nodes.iter((u) =>
                if u == v
                    return
                if @onlyVisible and not u.isVisible()
                    return
                d = v.getPosition().clone().sub(u.getPosition())
                if d.length() == 0
                    d = new THREE.Vector3(Math.random(), Math.random(), Math.random())
                f = f_r(d.length())
                v._force.sub(d.normalize().multiplyScalar(f))
            )
            @count++
        )

    _applyPositions: ->
        fmax = @radius / 2
        fmax2 = fmax * fmax
        temp = @currentIteration / @iterations * @temperature / @count

        @nodes.iter((node) =>
            if @onlyVisible and not node.isVisible()
                return
            d = node._force.normalize().multiplyScalar(temp)
            if d.lengthSq() > fmax2
                d.setLength(fmax)
            p = node.getPosition().clone().add(d)
            if p.lengthSq() > @radius * @radius
                p.setLength(@radius)
            node.setPosition(p)
        )

class FRLayout3DFactory extends LayoutFactory
    getName: -> 'Fruchterman-Reingold (3D)'
    buildLayout: -> new FruchtermanReingoldLayout3D()
    getSettings: ->
        {
            k: {
                label: 'Optimal distance'
                type: 'integer'
                min: 1
                initial: 50
                setter: 'setK'
            }
            temperature: {
                label: 'Initial temperature'
                type: 'float'
                max: 1
                min: 0
                initial: 1
                step: 0.01
                setter: 'setTemperature'
            }
            iter: {
                label: 'Iterations'
                type: 'integer'
                min: 1
                initial: 500
                setter: 'setIterations'
            }
            radius: {
                label: 'Maximal radius'
                type: 'integer'
                min: 1
                initial: 15
                setter: 'setRadius'
            }
            wireframe: {
                label: 'Show wireframe'
                type: 'boolean'
                initial: true
                setter: 'setWireframe'
            }
            visible: {
                label: 'Only visible'
                type: 'boolean'
                initial: false
                setter: 'setOnlyVisible'
            }
        }



class RandomLayout extends Layout
    setWidth: (@width) -> @redraw()
    setHeight: (@height) -> @redraw()
    setDepth: (@depth) -> @redraw()

    redraw: ->
        if @scene
            if @wireframe
                @scene.remove(@wireframe)
            dashMaterial = new THREE.LineBasicMaterial({
                color:  0x000000,
                opacity: .15,
                dashSize: .2,
                gapSize: 5,
                transparent: true,
            })
            geom = new THREE.CubeGeometry(@width, @height, @depth)
            @wireframe = new THREE.Line(geo2line(geom), dashMaterial, THREE.LinePieces)
            @wireframe.position.set(0, 0, 0)

            if @showWireframe
                @scene.add(@wireframe)

    setScene: (@scene) ->
        @redraw()

    setWireframe: (@showWireframe) ->
        if @scene and @wireframe
            if @showWireframe
                @scene.add(@wireframe)
            else
                @scene.remove(@wireframe)

    _run: ->
        @redraw()
        @nodes.iter((node) =>
            node.setPosition(new THREE.Vector3(
                (Math.random() - 0.5) * @width,
                (Math.random() - 0.5) * @height,
                (Math.random() - 0.5) * @depth,
            ))
        )

class RandomLayoutFactory extends LayoutFactory
    getName: -> 'Random'
    buildLayout: -> new RandomLayout()
    getSettings: ->
        {
            width: {
                label: 'Width'
                type: 'integer'
                min: 0
                initial: 60
                max: 10000
                setter: 'setWidth'
            }
            height: {
                label: 'Height'
                type: 'integer'
                min: 0
                initial: 40
                max: 10000
                setter: 'setHeight'
            }
            depth: {
                label: 'Depth'
                type: 'integer'
                min: 0
                initial: 30
                max: 10000
                setter: 'setDepth'
            }
            wireframe: {
                label: 'Show wireframe'
                type: 'boolean'
                initial: true
                setter: 'setWireframe'
            }
        }



class StackedLayout extends Layout
    setX: (x) -> @x = -x
    setY: (y) -> @y = -y
    setZ: (z) -> @z = -z
    setScene: (@scene) ->

    _run: ->
        l = @nodes.length

        if l == undefined
            l = 0
            @nodes.iter(->l++)

        h = @y * (l - 1)
        w = @x * (l - 1)
        d = @z * (l - 1)

        @nodes.iter((node, i) =>
            node.setPosition(new THREE.Vector3(
                @x * i - w / 2,
                @y * i - h / 2,
                @z * i - d / 2,
            ))
        )

class StackedLayoutFactory extends LayoutFactory
    getName: -> 'Stacked'
    buildLayout: -> new StackedLayout()
    getSettings: ->
        {
            xoffset: {
                label: 'X-offset'
                type: 'integer'
                min: -100
                initial: 0
                max: 100
                setter: 'setX'
            }
            yoffset: {
                label: 'Y-offset'
                type: 'integer'
                min: -100
                initial: 10
                max: 100
                setter: 'setY'
            }
            zoffset: {
                label: 'Z-offset'
                type: 'integer'
                min: -100
                initial: 0
                max: 100
                setter: 'setZ'
            }
        }
