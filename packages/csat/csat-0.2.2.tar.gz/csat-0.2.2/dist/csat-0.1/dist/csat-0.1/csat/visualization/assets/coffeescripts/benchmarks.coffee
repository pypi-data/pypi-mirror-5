randchoice = (seq) ->
    index = Math.floor(Math.random() * seq.length)
    return seq[index]


class Console
    constructor: (@container) ->
        this.log('Log opened.')

    log: (text) ->
        this.last = $('<li/>').text(text).appendTo(this.container)
        return this

    llog: (text) ->
        this.last.text(text)

(($) ->
    $ ->
        context = {}

        graphRenderer = undefined

        loadContext = () ->
            s = []
            $('.actions label').each(->
                name = $(this).attr('class')
                input = $('input', this)
                if input.attr('type') == 'checkbox'
                    value = input.is(':checked')
                else
                    value = input.val()
                context[name] = value
                s.push("#{name}=#{value}")
            )
            return s

        timings = []

        callbacks = {
            save: () ->
                measure = {
                    case: 'rendering',
                    commit: '34a844f96499cb5f8242038a2d81b6fe88a0752d',
                    data: JSON.stringify({
                        domains: context.domains,
                        nodes: context.nodes,
                        edges: context.edges,
                        intra: context.intra,
                        seed: context.seed,
                    }),
                    iterations: context.iter,
                    timings: timings,
                }
                $.post(window.location, measure, ->
                    webconsole.log('Benchmark saved to the server.')
                )

            run: () ->
                while scene.children.length > 1
                    scene.remove(scene.children[1])

                s = loadContext()

                timings = []
                webconsole.log("Creating random graph (#{s.join(', ')})")

                rest = ->
                    callbacks.generate()
                    repeat = context.repeat
                    iter = 1
                    webconsole.log("Starting benchmark session repeated #{repeat} times...")
                    webconsole.log("> [#{iter}/#{repeat}] Rendering #{context.iter} frames...")
                    bench = ->
                        start = Date.now()
                        viewportRenderer.stats.begin()
                        for i in [0...context.iter]
                            #graphRenderer.runLayoutStep()
                            graphRenderer.nodes.geometry.__dirtyVertices = true
                            viewportRenderer.render()
                        duration = viewportRenderer.stats.end() - start
                        fps = context.iter / duration * 1000.0
                        timings.push(duration)
                        if duration >= 1000
                            d = "#{Math.round(duration / 10) / 100} s"
                        else
                            d = "#{duration} ms"
                        webconsole.llog("* [#{iter}/#{repeat}] Rendered #{context.iter} frames in #{d} (#{Math.round(fps*10)/10} fps)")
                        if iter < repeat
                            iter += 1
                            webconsole.log("> [#{repeat}/#{repeat}] Rendering #{context.iter} frames...")
                            setTimeout(bench, 10)
                        else
                            webconsole.log("Done.")
                            if context.save
                                callbacks.save()
                    setTimeout(bench, 0)
                setTimeout(rest, 0)

            animate: ->
                viewportRenderer.animate()

            generate: () ->
                Math.seedrandom(context.seed)
                model = new GraphModel()
                for d in [0...context.domains]
                    domain = new Domain(model, "n#{d}", {})
                    model.domains.push(domain)

                    for n in [0...context.nodes/context.domains]
                        node = new Node(model, domain, "n#{d}::n#{n}", {})
                        domain.nodes.push(node)

                for e in [0...context.edges]
                    src_domain = randchoice(model.domains)

                    if Math.random() < context.intra_rate
                        dst_domain = src_domain
                    else
                        dst_domain = randchoice(model.domains)

                    src_node = randchoice(src_domain.nodes)
                    dst_node = randchoice(dst_domain.nodes)

                    edge = new Edge(model, "e#{e}", src_node, dst_node, {})
                    model.edges.push(edge)

                # The model view offers a view of the graph model by exposing a
                # filtering interface which does not modify the underlying model.
                #modelView = new GraphModelView(this.model)

                # The layout defines how the nodes and edges have to be laid out in
                # the plane (2D) or space (3D). Simply put, defines the positions.
                #layout = new FruchtermanReingoldLayout()
                layouts = []
                for i in model.domains
                    layouts.push(new FruchtermanReingoldLayout({
                        k: 100,
                        iterations: 500,
                        initialTemperature: 2,
                        radius: 70,
                    }))

                # The graph rendered is responsible to populate the scene with objects
                # representing the graph nodes and edges by respecting the imposed
                # layout.
                graphRenderer = new GraphRenderer(model, layouts[0])
                _graphRenderer = new PartitionedGraphRenderer(model, layouts,
                    new FruchtermanReingoldLayout({
                        k: 300,
                        iterations: 500,
                        initialTemperature: 6,
                        radius: 1000,
                    }))
                graphRenderer.draw(scene)

                #graphRenderer.runLayout()
                graphRenderer.runLayoutStep()
                viewportRenderer.render()
        }

        webconsole = new Console($('.console'))

        # This is the HTML element which contains the canvas element used by
        # WebGL
        container = $('.viewport')
        camera = new THREE.PerspectiveCamera(1000, 1, 0.1, 1000)
        controls = new THREE.OrbitControls(camera, container.get(0))
        controls.userRotateSpeed = -1.0
        controls.userZoomSpeed = -1.0

        # The scene is the drawing board provided by WebGL. It is used by the
        # graph renderer to draw the graph.
        scene = new THREE.Scene()
        light = new THREE.DirectionalLight(0xffffff)
        light.position.set(200, 200, 0)
        #scene.add(light)

        # The vieport is a point of view of the scene.
        viewport = new Viewport({
            x: 0, y: 0,
            width: 1, height: 1,
            camera: camera,
            controls: controls,
        })

         # The viewport renderer takes a scene and actually displays it in the
        # document.
        viewportRenderer = new MultipleViewportsRenderer(
            container, scene, [viewport])

        $('button[data-action]').click(->
            callbacks[$(this).data('action')]()
        )

)(jQuery)
