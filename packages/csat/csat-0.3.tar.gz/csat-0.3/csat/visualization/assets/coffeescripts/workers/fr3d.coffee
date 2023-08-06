class FR3DWorker extends IterativeLayoutWorker
    constructor: ->
        super
        @iterations = Infinity
        @temperature = 1
        @nodes = []
        @edges = []

    initialize: ->
        @nodes.iter((node) =>
            node.position.add(new Vector3(
                Math.random() / 1000,
                Math.random() / 1000,
                Math.random() / 1000,
            ))
        )

    step: ->
        @count = 0
        @calculateForces(@k)
        @applyPositions(@radius)

    remote_setProperty: (name, value) ->
        switch name
            when 'k'
                @k = value
            when 'iterations'
                @iterations = value
            when 'radius'
                @radius = value
            when 'temperature'
                @temperature = value

    calculateRepulsion: (k) ->
        k = k * k

        @nodes.iter((v) =>
            v.force = f = new Vector3(0, 0, 0)
            @nodes.iter((u) =>
                if u == v
                    return
                d = v.position.clone().sub(u.position)
                l = d.length()
                if l == 0
                    d = new Vector3(Math.random(), Math.random(), Math.random())
                    l = d.length()
                f.sub(d.setLength(-k / l))
            )
            @count++
        )

    calculateAttraction: (k) ->
        k = 2 / k
        @edges.iter(([u, v]) =>
            d = v.position.clone().sub(u.position)
            l = d.length()
            f = d.setLength(l * l * k)
            v.force.sub(d)
            u.force.add(f)
            @count++
        )

    calculateForces: (k) ->
        @calculateRepulsion(k)
        @calculateAttraction(k)

    applyPositions: (radius) ->
        r = radius * radius

        fmax = radius / 2
        fmax2 = Math.pow(fmax, 2)
        temp = (1 - @iteration / @iterations) * @temperature
        temp2 = temp * temp

        @nodes.iter((node) =>
            #d = node.force.multiplyScalar(temp)
            #if d.lengthSq() > fmax2
            #    d.setLength(fmax)
            d = node.force
            if d.lengthSq() > temp2
                d = d.setLength(temp)
            p = node.position.add(d)
            if p.lengthSq() > r
                p.setLength(radius)
        )

onmessage = new FR3DWorker().handleMessage
