geo2line = (geo) ->
    geometry = new THREE.Geometry()
    vertices = geometry.vertices

    for i in [0..geo.faces.length]
        face = geo.faces[i]
        if face instanceof THREE.Face3
            a = geo.vertices[ face.a ].clone()
            b = geo.vertices[ face.b ].clone()
            c = geo.vertices[ face.c ].clone()
            vertices.push(a, b, b, c, c, a)
        else if face instanceof THREE.Face4
            a = geo.vertices[ face.a ].clone()
            b = geo.vertices[ face.b ].clone()
            c = geo.vertices[ face.c ].clone()
            d = geo.vertices[ face.d ].clone()
            vertices.push( a,b, b,c, c,d, d,a )

    geometry.computeLineDistances()
    return geometry

makeCircle = (radius, opacity, axis) ->
    geometry = new THREE.Geometry()
    dashMaterial = new THREE.LineBasicMaterial({
        color:  0x000000,
        opacity: opacity,
        dashSize: .2,
        gapSize: 5,
        transparent: true,
    })
    resolution = radius * 2 * Math.PI
    size = 360 / resolution
    for i in [0...resolution]
        segment = i * size  * Math.PI / 180
        c1 = Math.cos(segment) * radius
        c2 = Math.sin(segment) * radius
        if axis == 2
            [x, y, z] = [c1, c2, 0]
        else if axis == 1
            [x, y, z] = [c1, 0, c2]
        else if axis == 0
            [x, y, z] = [0, c1, c2]
        geometry.vertices.push(new THREE.Vector3(x, y, z))
    geometry.vertices.push(geometry.vertices[0].clone())
    new THREE.Line(geometry, dashMaterial)

makeCirclePlane = (radius, axis, step=10, slices=10) ->
    obj = new THREE.Object3D()
    r = radius - 10
    obj.add(makeCircle(radius, 0.2, axis))
    while r > 0
        obj.add(makeCircle(r, 0.07, axis))
        r -= step
    seps = new THREE.Geometry()
    dashMaterial = new THREE.LineBasicMaterial({
        color:  0x000000,
        opacity: .07,
        dashSize: .2,
        gapSize: 5,
        transparent: true,
    })
    slices = 10
    size = 360 / slices
    for i in [0...slices]
        segment = i * size  * Math.PI / 180
        c1 = Math.cos(segment) * radius
        c2 = Math.sin(segment) * radius
        if axis == 2
            [x, y, z] = [c1, c2, 0]
        else if axis == 1
            [x, y, z] = [c1, 0, c2]
        else if axis == 0
            [x, y, z] = [0, c1, c2]
        seps.vertices.push(new THREE.Vector3(0, 0, 0))
        seps.vertices.push(new THREE.Vector3(x, y, z))
    obj.add(new THREE.Line(seps, dashMaterial, THREE.LinePieces))
    obj


later = (ms, cb) ->
    setTimeout(cb, ms)


class DomainNodesObject extends THREE.ParticleSystem
    @vertexShader = [
        'attribute float size;'

        'attribute vec3 nodeColor;'
        'varying vec3 vColor;'

        'attribute float nodeOpacity;'
        'varying float vOpacity;'

        'attribute float nodeVisibility;'
        'varying float visible;'

        'void main() {'
        '    vColor = nodeColor;'
        '    vOpacity = nodeOpacity;'
        '    visible = nodeVisibility;'
        '    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);'
        '    gl_PointSize = size * (300.0 / length( mvPosition.xyz));'
        '    gl_Position = projectionMatrix * mvPosition;'
        '}'
    ].join('\n')

    @fragmentShader = [
        'uniform vec3 color;'
        'uniform sampler2D texture;'
        'varying vec3 vColor;'
        'varying float vOpacity;'
        'varying float visible;'
        'void main() {'
        '    if (visible == 0.0) discard;'
        '    gl_FragColor = vec4(vColor * color, 1.0);'
        '    gl_FragColor = gl_FragColor * texture2D(texture, vec2(gl_PointCoord.x, 1.0 - gl_PointCoord.y));'
        '    gl_FragColor.a *= vOpacity;'
        '}'
    ].join('\n')

    constructor: (@model) ->
        geometry = new THREE.Geometry()
        model.setPosition(new THREE.Vector3(0, 0, 0))
        model.nodes.iter((node) => node.updatePosition())
        geometry.vertices = model.nodePositions

        attributes = {
            size: {type: 'f', value: model.nodeSizes}
            nodeColor: {type: 'c', value: model.nodeColors}
            nodeOpacity: {type: 'f', value: model.nodeOpacity}
            nodeVisibility: {type: 'f', value: model.nodeVisibility}
        }

        uniforms = {
            color: {type: "c", value: new THREE.Color(0xffffff)}
            texture: {type: "t", value: model.texture}
        }

        material = new THREE.ShaderMaterial({
            uniforms: uniforms
            attributes: attributes
            vertexShader: DomainNodesObject.vertexShader
            fragmentShader: DomainNodesObject.fragmentShader
            transparent: true
            #depthWrite: false
            combine: THREE.MixOperation
        })
        material.alphaTest = 0.5
        material.blending = THREE.AdditiveAlphaBlending

        THREE.ParticleSystem.call(this, geometry, material)
        @sortParticles = true

    updateTexture: ->
        @material.uniforms['texture'].value = @model.texture
        @material.uniforms['texture'].needsUpdate = true

    updateColors: ->
        @material.attributes['nodeColor'].needsUpdate = true


class DomainEdgesObject extends THREE.Line
    @vertexShader = [
        'attribute vec3 edgeColor;'
        'varying vec3 color;'

        'attribute float edgeOpacity;'
        'varying float opacity;'

        'attribute float edgeVisibility;'
        'varying float visible;'

        'void main() {'
        '    color = edgeColor;'
        '    opacity = edgeOpacity;'
        '    visible = edgeVisibility;'
        '    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);'
        '    gl_PointSize = 4.0;'
        '    gl_Position = projectionMatrix * mvPosition;'
        '}'
    ].join('\n')

    @fragmentShader = [
        'varying vec3 color;'
        'varying float opacity;'
        'varying float visible;'
        'void main() {'
        '    if (visible == 0.0) discard;'
        '    gl_FragColor = vec4(color, opacity);'
        '}'
    ].join('\n')

    constructor: (@model) ->
        geometry = new THREE.Geometry()
        geometry.vertices = @model.edgeVertices

        attributes = {
            edgeWeight: {type: 'f', value: model.edgeWeights}
            edgeColor: {type: 'c', value: model.edgeColors}
            edgeOpacity: {type: 'f', value: model.edgeOpacity}
            edgeVisibility: {type: 'f', value: model.edgeVisibility}
        }

        uniforms = {
        }

        material = new THREE.ShaderMaterial({
            uniforms: uniforms
            attributes: attributes
            vertexShader: DomainEdgesObject.vertexShader
            fragmentShader: DomainEdgesObject.fragmentShader
            transparent: true
            linewidth: 1
            #depthWrite: false
            #combine: THREE.MixOperation
        })

        THREE.Line.call(this, geometry, material, THREE.LinePieces)

    update: ->
        @material.attributes['edgeWeight'].needsUpdate = true
        @material.attributes['edgeColor'].needsUpdate = true
        @material.attributes['edgeOpacity'].needsUpdate = true
        @material.attributes['edgeVisibility'].needsUpdate = true


class DomainEdgesDirectionObject extends DomainEdgesObject
    constructor: ->
        super
        @material.linewidth = @material.linewidth * 1.5 + 1
        @geometry.vertices = []
        @updateGeometry()

    updateGeometry: ->
        vs = @geometry.vertices
        vs.length = 0
        @model.edges.iter((e) =>
            if e.directed
                vs.push(@_getDirectionStart(
                    e.src.getAbsolutePosition(),
                    e.dst.getAbsolutePosition(),
                    Math.sqrt(e.dst.getSize() - 2) / 2 + 1
                ))
                vs.push(e.dst.getAbsolutePosition())
        )
        @geometry.verticesNeedUpdate = true

    _getDirectionStart: (src, dst, l) ->
        v = dst.clone().sub(src)
        v.setLength(Math.min(l, v.length()))
        dst.clone().sub(v)


class DomainLabelsObject extends THREE.Mesh
    @vertexShader = [
        'varying vec2 vUv;'
        'varying float fontSize;'
        'attribute float nodeSize;'
        'attribute float char;'
        'uniform float nodeSizeFactor;'
        'uniform float baseSize;'
        'uniform float sizeRatio;'
        'uniform float widthRatio;'

        'attribute float labelOpacity;'
        'varying float opacity;'

        'attribute float labelVisibility;'
        'varying float visible;'

        'void main() {'
        #'    vColor = ca;'
        #'    gl_PointSize = 300.0 * ( 300.0 / length( position.xyz ) );'
        #'    vec4 offset = vec4();'

        # Define font size
        '    fontSize = nodeSize * nodeSizeFactor + baseSize * sizeRatio / 10.0;'
        '    float charWidth = fontSize * 0.2;'
        '    float charHeight = charWidth * 2.0;'
        '    charWidth /= widthRatio;'

        # Offset from the center of the node due to node size
        '    float offset = nodeSize / 23.0 / widthRatio * sizeRatio;'

        # Get the projected position and apply sizing
        '    vec4 pos = projectionMatrix * modelViewMatrix * vec4(position, 1.0);'
        '    pos.x += offset;'
        '    pos.x += floor((floor(char / 2.0) + 1.0) / 2.0) * charWidth;'
        '    pos.y += (mod(char, 2.0) - 0.5) * charHeight;'

        # Assign to external variable
        '    visible = labelVisibility;'
        '    opacity = labelOpacity;'
        '    gl_Position = pos;'
        '    vUv = uv;'
        '}'
    ].join('\n')

    @fragmentShader = [
        'uniform vec3 color;'
        'uniform sampler2D texture;'
        'varying vec2 vUv;'
        'varying float opacity;'
        'varying float fontSize;'
        'varying float visible;'
        'void main() {'
        '    if (visible == 0.0) discard;'
        #'    if (fontSize < 7.0) discard;'
        '    gl_FragColor = vec4(color, 1.0);'
        '    gl_FragColor = gl_FragColor * texture2D(texture, vUv);'
        '    gl_FragColor.a *= opacity;'
        '}'
    ].join('\n')

    @makeTexture: ->
        fontSize = DomainLabelsObject.fontSize
        lettersPerSide = DomainLabelsObject.lettersPerSide
        c = document.createElement('canvas')
        c.width = c.height = sz = fontSize * lettersPerSide
        ctx = c.getContext('2d')
        ctx.font = (fontSize - 10) + 'px menlo'
        ctx.fillStyle = "#ffffff"
        yOffset = -0.25

        for y in [0...lettersPerSide]
            for x in [0...lettersPerSide]
                ch = String.fromCharCode(y * lettersPerSide + x)
                ctx.textAlign = "center"
                ctx.fillText(ch, (x + .5) * fontSize,  (yOffset + y + 1) * fontSize)

        texture = new THREE.Texture(c)
        texture.needsUpdate = true
        texture

    @lettersPerSide = 16
    @fontSize = 70

    constructor: (@model) ->
        @nodeSizeFactor = 0
        @baseSize = 10
        @labelOpacity = []
        @color = new THREE.Color(0x000000)
        @labelVisibility = []
        chars = @chars = []
        sizes = @sizes = []

        $(window).resize(=>
            @updateRatio()
        )

        attributes = {
            char: {type: 'f', value: @chars}
            nodeSize: {type: 'f', value: @sizes}
            labelOpacity: {type: 'f', value: @labelOpacity}
            labelVisibility: {type: 'f', value: @labelVisibility}
        }

        uniforms = {
            texture: {type: "t", value: DomainLabelsObject.makeTexture()}
            widthRatio: {type: 'f', value: 1.0}
            sizeRatio: {type: 'f', value: 1.0}
            nodeSizeFactor: {type: 'f', value: @nodeSizeFactor}
            baseSize: {type: 'f', value: @baseSize / window.devicePixelRatio}
            color: {type: 'c', value: @color}
        }

        material = new THREE.ShaderMaterial({
            uniforms: uniforms
            attributes: attributes
            vertexShader: DomainLabelsObject.vertexShader
            fragmentShader: DomainLabelsObject.fragmentShader
            transparent: true
            depthWrite: false
            combine: THREE.MixOperation
        })

        geometry = new THREE.Geometry()

        @repopulate(geometry)
        THREE.Mesh.call(this, geometry, material)
        @updateRatio()

    updateRatio: =>
        w = $('.viewport').width()
        h = $('.viewport').height()
        @material.uniforms['widthRatio'].value = w / h
        @material.uniforms['widthRatio'].needsUpdate = true

        @material.uniforms['sizeRatio'].value = 7000 / h
        @material.uniforms['sizeRatio'].needsUpdate = true

    repopulate: (geometry) =>
        @chars.length = 0
        @sizes.length = 0

        geometry.vertices.length = 0
        geometry.faces.length = 0
        geometry.faceVertexUvs[0].length = 0

        textureCharWidth = DomainLabelsObject.fontSize * 0.5
        textureCharHeight = DomainLabelsObject.fontSize

        globalCharIndex = 0
        fontSize = DomainLabelsObject.fontSize
        lettersPerSide = DomainLabelsObject.lettersPerSide

        ow = textureCharWidth / (fontSize * lettersPerSide)
        oh = textureCharHeight / (fontSize * lettersPerSide)

        @model.nodes.iter((n, i) =>
            p = n.getAbsolutePosition()
            s = n.getSize()
            label = n.getLabel()
            show = n.isVisible()
            op = n.getOpacity()

            for char, j in label
                charCode = char.charCodeAt(0)

                charX = charCode % lettersPerSide
                charY = Math.floor(charCode / lettersPerSide)

                ox = (charX + 0.5) / lettersPerSide - ow / 2.0
                oy = (lettersPerSide - charY - .5) / lettersPerSide - oh / 2.0

                geometry.vertices.push(p, p, p, p)
                geometry.faces.push(new THREE.Face4(
                    globalCharIndex * 4,
                    globalCharIndex * 4 + 1,
                    globalCharIndex * 4 + 2,
                    globalCharIndex * 4 + 3
                ))
                @chars.push(j * 4 + 1, j * 4 + 0, j * 4 + 2, j * 4 + 3)
                @sizes.push(s, s, s, s)
                @labelOpacity.push(op, op, op, op)
                @labelVisibility.push(show, show, show, show)
                geometry.faceVertexUvs[0].push([
                    new THREE.Vector2(ox, oy + oh),
                    new THREE.Vector2(ox, oy),
                    new THREE.Vector2(ox + ow, oy),
                    new THREE.Vector2(ox + ow, oy + oh),
                ])

                globalCharIndex++
        )
        geometry.verticesNeedUpdate = true
        geometry.elementsNeedUpdate = true
        geometry.uvsNeedUpdate = true
        geometry.dynamic = true

    updateColor: (color) =>
        @color = new THREE.Color(color)
        @material.uniforms['color'].value = @color
        @material.uniforms['color'].needsUpdate = true

    updateFontSize: (@baseSize, @nodeSizeFactor) =>
        @material.uniforms['baseSize'].value = @baseSize / window.devicePixelRatio
        @material.uniforms['baseSize'].needsUpdate = true
        @material.uniforms['nodeSizeFactor'].value = @nodeSizeFactor
        @material.uniforms['nodeSizeFactor'].needsUpdate = true

    updateFromNode: =>
        c = 0
        @model.nodes.iter((n, i) =>
            v = n.isVisible()
            s = n.getSize()
            o = n.getOpacity()
            l = n.getLabel()
            for char in l
                @sizes[c * 4] = s
                @sizes[c * 4 + 1] = s
                @sizes[c * 4 + 2] = s
                @sizes[c * 4 + 3] = s
                @labelVisibility[c * 4] = v
                @labelVisibility[c * 4 + 1] = v
                @labelVisibility[c * 4 + 2] = v
                @labelVisibility[c * 4 + 3] = v
                @labelOpacity[c * 4] = o
                @labelOpacity[c * 4 + 1] = o
                @labelOpacity[c * 4 + 2] = o
                @labelOpacity[c * 4 + 3] = o
                c++
        )
        @material.attributes['labelVisibility'].needsUpdate = true
        @material.attributes['nodeSize'].needsUpdate = true
        @material.attributes['labelOpacity'].needsUpdate = true

    updateLabels: =>
        @repopulate(@geometry)
        @material.attributes['char'].needsUpdate = true


class GraphRenderer
    constructor: (@model, @viewer) ->
        @layouts = []
        @edgeDirectionVisible = true
    setLayout: (layout) ->
        if @layout
            if @layout.isRunning()
                @layout.stop()
            @layout.callbacks.step.remove(@_layoutStepCb)
            @layout.callbacks.done.remove(@_layoutStepCb)
        @layout = layout
        @layout.callbacks.step.add(@_layoutStepCb)
        @layout.callbacks.done.add(@_layoutStepCb)
        @layouts = [@layout]

    draw: (@scene, @camera) ->
        @oldDomainObjects = @domainObjects
        @domainObjects = ({} for _ in @model.domains)
        @_clear(@scene)
        @layouts.iter((l) => l.setScene(@scene))
        @_draw()

    _draw: ->
        @_drawLabels(@scene)
        @_drawNodes(@scene)
        @_drawEdges(@scene)

    step: -> @layout.runStep(@model.nodes, @model.edges)
    run: -> @layout.run(@model.nodes, @model.edges)
    resume: ->
        if @layout.isPaused()
            @layout.run(@model.nodes, @model.edges)
    pause: -> l.pause() for l in @layouts
    stop: -> l.stop() for l in @layouts
    reset: -> l.reset() for l in @layouts

    isRunning: -> @allLayoutsRunning()
    allLayoutsRunning: -> @layouts.every((l) -> l.isRunning())
    allLayoutsPaused: -> @layouts.every((l) -> l.isPaused())
    someLayoutsRunning: -> @layouts.some((l) -> l.isRunning())
    someLayoutsPaused: -> @layouts.some((l) -> l.isPaused())

    setEdgeTransparency: (enabled) ->
        @domainObjects.iter((d) ->
            d.edges.material.transparent = enabled
            d.edgesDirection.material.transparent = enabled
        )
        @interEdges.material.transparent = enabled
        @interEdgesDirection.material.transparent = enabled

    _layoutStepCb: =>
        @domainObjects.iter((d) ->
            d.nodes.geometry.verticesNeedUpdate = true
            d.labels.geometry.verticesNeedUpdate = true
            d.edges.geometry.verticesNeedUpdate = true
            d.edgesDirection.updateGeometry()
        )
        @interEdges.geometry.verticesNeedUpdate = true
        @interEdgesDirection.updateGeometry()

    _drawLabels: (scene) ->
        @labelsObject = new THREE.Object3D()
        scene.add(@labelsObject)
        @domainLabelsObjects = []
        @model.domains.iter((domain, i) =>
            try
                old = @oldDomainObjects[i].labels
            catch e
                old = undefined
            object = new DomainLabelsObject(domain)
            if old
                object.material.uniforms['color'].value = old.material.uniforms['color'].value
            @labelsObject.add(object)
            @domainObjects[i].labels = object
        )

    _drawNodes: (scene) ->
        @nodesObject = new THREE.Object3D()
        scene.add(@nodesObject)
        @model.domains.iter((domain, i) =>
            object = new DomainNodesObject(domain)
            @nodesObject.add(object)
            @domainObjects[i].nodes = object
        )

        viewport = $('.viewport')
        viewport.off('mousemove.graphcbs').on('mousemove.graphcbs', (e) =>
            if @viewer.controls.disabled or @viewer.controls.dragging
                return
            ray = new THREE.Raycaster()
            offset = viewport.offset()
            width = viewport.width()
            height = viewport.height()
            x = Math.max(0, Math.min(width, e.pageX - offset.left))
            y = Math.max(0, Math.min(height, e.pageY - offset.top))

            r = @camera._ratio * window.devicePixelRatio
            x = (x - width * .5) * r
            y = -(y - height * .5) * r

            projector = new THREE.Projector()
            vector = new THREE.Vector3(x, y, 0)

            origin = @camera.position
            direction = vector.clone().sub(@camera.position).normalize()

            ray.threshold = 10
            ray.set(origin, direction)

            candidates = []
            @model.domains.iter((domain, i) =>
                intersect = ray.intersectObjects([@domainObjects[i].nodes])
                for obj in intersect
                    n = domain.nodes[obj.vertex]
                    if n.isVisible()
                        if obj.distance <= n.getSize() * (r + 0.05)
                            p = n.getAbsolutePosition().clone()
                            p.applyMatrix4(@domainObjects[i].nodes.matrixWorld)
                            candidates.push([p.z, n])
            )

            if candidates.length
                candidates.sort()
                node = candidates[candidates.length - 1][1]
                if node != @hoverNode
                    if @hoverNode?
                        @model.fire('nodeout', @hoverNode)
                    @hoverNode = node
                    @model.fire('nodehover', @hoverNode)
            else
                if @hoverNode?
                    @model.fire('nodeout', @hoverNode)
                    @hoverNode = undefined
        ).off('click.graphcbs').on('click.graphcbs', =>
            if @viewer.controls.disabled or @viewer.controls.dragging
                return
            if @hoverNode?
                @model.fire('nodeclick', @hoverNode)
        )

    _drawEdges: (scene) ->
        @edgesObject = new THREE.Object3D()
        scene.add(@edgesObject)

        @edgesDirectionObject = new THREE.Object3D()
        if @edgeDirectionVisible
            scene.add(@edgesDirectionObject)

        @model.domains.iter((domain, i) =>
            try
                old = @oldDomainObjects[i].edges
            catch e
                old = undefined

            object = new DomainEdgesObject(domain)
            @edgesObject.add(object)
            @domainObjects[i].edges = object

            if old
                object.material.transparent = old.material.transparent
                object.material.linewidth = old.material.linewidth

            object = new DomainEdgesDirectionObject(domain)
            @edgesDirectionObject.add(object)
            @domainObjects[i].edgesDirection = object

            if old
                object.material.transparent = old.material.transparent
                object.material.linewidth = old.material.linewidth * 1.5 + 1
        )

        old = @interEdges

        @interEdges = new DomainEdgesObject(@model)
        @edgesObject.add(@interEdges)

        if old
            @interEdges.material.transparent = old.material.transparent
            @interEdges.material.linewidth = old.material.linewidth

        @interEdgesDirection = new DomainEdgesDirectionObject(@model)
        @edgesDirectionObject.add(@interEdgesDirection)

        if old
            @interEdgesDirection.material.transparent = old.material.transparent
            @interEdgesDirection.material.linewidth = old.material.linewidth * 1.5 + 1

    setEdgeDirectionVisibility: (@edgeDirectionVisible) ->
        if @edgeDirectionVisible
            @scene.add(@edgesDirectionObject)
        else
            @scene.remove(@edgesDirectionObject)

    _clear: (obj) ->
        while obj.children.length
            obj.remove(obj.children[0])


class DomainEdgesIterator
    constructor: (@domainNodes, @nodes) ->
        @nodesIter = @nodes.__iterator__()

    next: ->
        node = @nodesIter.next()
        domain = @domainNodes[node.fqid[0]]


class ClusteredGraphRenderer extends GraphRenderer
    constructor: (model, viewer) ->
        super(model, viewer)

        domainNodes = (new Node(d.model, d, '') for d in @model.domains)
        domainEdges = []
        model.nodes.iter((n) ->
            e = new Edge(n.domain.model, n.domain, '', n, domainNodes[n.fqid[0]], {}, false)
            domainEdges.push(e)
        )

        @nodes = new IteratorFactory(FlattenIterator, [[model.nodes, domainNodes]])
        @edges = new IteratorFactory(FlattenIterator, [[model.edges, domainEdges]])

    step: ->
        @layout.runStep(@nodes, @edges)

    run: ->
        @layout.run(@nodes, @edges)

    resume: ->
        if @layout.isPaused()
            @layout.run(@nodes, @edges)


class PartitionedGraphRenderer extends GraphRenderer
    constructor: (model, viewer) ->
        super(model, viewer)
        @partitionLayouts = (undefined for _ in model.domains)

    _allDomainsSet: ->
        @globalLayout != undefined and @partitionLayouts.every((p) -> p != undefined)

    setGlobalLayout: (layout) ->
        if @globalLayout
            if @globalLayout.isRunning()
                @globalLayout.stop()
            @globalLayout.callbacks.step.remove(@_globalLayoutStepCb)
            @globalLayout.callbacks.done.remove(@_globalLayoutStepCb)
        @globalLayout = layout
        @globalLayout.callbacks.step.add(@_globalLayoutStepCb)
        @globalLayout.callbacks.done.add(@_globalLayoutStepCb)
        @layouts[0] = @globalLayout

    setPartitionLayout: (i, layout) ->
        oldLayout = @partitionLayouts[i]
        if oldLayout
            if oldLayout.isRunning()
                oldLayout.stop()
            oldLayout.callbacks.step.remove(@_layoutStepCb)
            oldLayout.callbacks.done.remove(@_layoutStepCb)
        @partitionLayouts[i] = layout
        if @partitions
            partition = @partitions[i]
            @scene.remove(partition.scene)
            partition.layout = layout
            partition.scene = new THREE.Object3D()
            partition.scene.position = partition.domain.getAbsolutePosition()
            @scene.add(partition.scene)
            layout.setScene(partition.scene)
        layout.callbacks.step.add(@_layoutStepCb)
        layout.callbacks.done.add(@_layoutStepCb)
        @layouts[i + 1] = layout

    _globalLayoutStepCb: =>
        n.updatePosition() for n in @model.domains
        for p in @partitions
            if not p.layout.isRunning()
                n.updatePosition() for n in p.domain.nodes
        @_layoutStepCb()

    _placePartitions: ->
        @partitions = []

        @model.domains.iter((domain, i) =>
            partition = {
                domain: domain
                scene: new THREE.Object3D()
                layout: @partitionLayouts[i]
            }
            partition.scene.position = domain.getAbsolutePosition()
            @scene.add(partition.scene)
            @partitions.push(partition)
        )

        @edges = []
        @model.superedges.iter((e) =>
            @edges.push(new Edge(e.model, undefined, '', e.src.domain, e.dst.domain, {}, false))
        )

    draw: (@scene, @camera) ->
        @oldDomainObjects = @domainObjects
        @domainObjects = ({} for _ in @model.domains)
        @_clear(@scene)
        @_placePartitions()
        @partitions.iter((p) => p.layout.setScene(p.scene))
        @_draw()

    step: ->
        @globalLayout.runStep(@model.domains, @edges)
        @partitions.iter((partition) ->
            partition.layout.runStep(partition.domain.nodes, partition.domain.edges)
        )

    run: ->
        @globalLayout.run(@model.domains, @edges)
        @partitions.iter((partition) ->
            partition.layout.run(partition.domain.nodes, partition.domain.edges)
        )

    runGlobal: ->
        @globalLayout.run(@model.domains, @edges)

    runPartition: (id) ->
        partition = @partitions[id]
        partition.layout.run(partition.domain.nodes, partition.domain.edges)

    pausePartition: (id) ->
        partition = @partitions[id]
        partition.layout.pause()

    stopPartition: (id) ->
        partition = @partitions[id]
        partition.layout.stop()

    resume: ->
        if @globalLayout.isPaused()
            @globalLayout.run(@model.domains, @edges)
        @partitions.iter((partition) ->
            if partition.layout.isPaused()
                partition.layout.run(partition.domain.nodes, partition.domain.edges)
        )

class ExtrudedGraphRenderer extends GraphRenderer
    setDomainsLayout: (layout) ->
        if @domainsLayout
            if @domainsLayout.isRunning()
                @domainsLayout.stop()
            @domainsLayout.callbacks.step.remove(@_layoutStepCb)
            @domainsLayout.callbacks.done.remove(@_layoutStepCb)
        @domainsLayout = layout
        @domainsLayout.callbacks.step.add(@_layoutStepCb)
        @domainsLayout.callbacks.done.add(@_layoutStepCb)
        @layouts[0] = @domainsLayout

    setNodesLayout: (layout) ->
        if @nodesLayout
            if @nodesLayout.isRunning()
                @nodesLayout.stop()
            @nodesLayout.callbacks.step.remove(@_layoutStepCb)
            @nodesLayout.callbacks.done.remove(@_layoutStepCb)
        @nodesLayout = layout
        @nodesLayout.callbacks.step.add(@_layoutStepCb)
        @nodesLayout.callbacks.done.add(@_layoutStepCb)
        @layouts[1] = @nodesLayout

    draw: (@scene, @camera) ->
        @oldDomainObjects = @domainObjects
        @domainObjects = ({} for _ in @model.domains)
        @_clear(@scene)
        @edges = []
        @model.superedges.iter((e) =>
            @edges.push(new Edge(e.model, undefined, '', e.src.domain, e.dst.domain, {}, false))
        )
        @layouts.iter((l) => l.setScene(@scene))
        @_draw()

    step: ->
        @domainsLayout.runStep(@model.domains, @edges)
        @nodesLayout.runStep(@model.nodes, @model.edges)

    run: ->
        @domainsLayout.run(@model.domains, @edges)
        @nodesLayout.run(@model.nodes, @model.edges)

    resume: ->
        if @domainsLayout.isPaused()
            @domainsLayout.run(@model.domains, @edges)
        if @nodesLayout.isPaused()
            @nodesLayout.run(@model.nodes, @model.edges)
