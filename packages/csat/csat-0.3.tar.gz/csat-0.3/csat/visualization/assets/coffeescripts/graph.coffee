parseIds = (id, onlyLast=false) ->
    tokens = id.split('::')

    if onlyLast
        parseInt(tokens[tokens.length-1].replace(/^n|g|d|e/, ''))
    else
        tokens.map((el) ->
            parseInt(el.replace(/^n|g|d|e/, ''))
        )


class NeighborsIterator
    constructor: (@node) ->
        @directed = true
        @index = 0

    next: =>
        if @directed
            if @index < @node._outEdges.length
                return @node._outEdges[@index++].dst
            else
                @directed = false
                @index = 0

        if @index < @node._edges.length
            edge = @node._edges[@index++]
            if edge.dst == @node
                return edge.src
            else
                return edge.dst

        throw StopIteration


class Node
    constructor: (@model, @domain, id, @attributes, @_globalId) ->
        @fqid = parseIds(id)
        @id = @fqid.last()
        @_offset = new THREE.Vector3(0, 0, 0)
        @_position = new THREE.Vector3(0, 0, 0)
        @_absPosition = new THREE.Vector3(0, 0, 0)
        @_degree = 0
        @_inDegree = 0
        @_outDegree = 0
        @_selfloops = 0
        @_size = 10
        @_color = new THREE.Color(0xffffff)
        @_opacity = 1.0
        @_visible = true
        @_label = @fqid.join(',')

        @_inEdges = []
        @_outEdges = []
        @_edges = []

        @neighbors = new IteratorFactory(NeighborsIterator, [this])

    getAbsoluteID: ->
        @fqid.join('::')

    setOffset: (o) ->
        ###
        Sets the offset to be applied to the node after its domain-relative
        position has been defined.
        ###
        @_offset = o
        @updatePosition()

    setPosition: (p) ->
        ###
        Sets the position of the node relative to the absolute coordinates of
        the domain node.
        ###
        @_position.x = p.x
        @_position.y = p.y
        @_position.z = p.z
        @updatePosition()

    getPosition: ->
        ###
        Gets the position of the node relative to the domain.
        ###
        return @_position

    getAbsolutePosition: ->
        ###
        Gets the position of the node relative to the origin of the coordinate
        system, by including any offset due to the domain position.
        ###
        return @_absPosition

    updatePosition: ->
        ###
        Updates the absolute position of the object by applying the offset to
        the position.
        ###

        # Use a matrix transformation here to be able to do generic affine
        # transformations in the future (mainly to include plane rotations
        # for domains).
        transformation = new THREE.Matrix4(
            1, 0, 0, @_offset.x,
            0, 1, 0, @_offset.y,
            0, 0, 1, @_offset.z,
            0, 0, 0, 1,
        )
        transformed = @_position.clone().applyMatrix4(transformation)
        @_absPosition.copy(transformed)

    getSize: -> @_size
    setSize: (@_size) ->
        @domain.nodeSizes[@id] = @_size
        return @

    getColor: -> @_color
    setColor: (color) ->
        @domain.nodeColors[@id] = @_color = new THREE.Color(color)
        return @

    getOpacity: -> @_opacity
    setOpacity: (@_opacity) ->
        @domain.nodeOpacity[@id] = @_opacity
        return @

    getDegree: -> @_degree

    getLabel: -> @_label
    setLabel: (label) ->
        @_label = "#{label}"
        return @

    getAttr: (key) ->
        switch key
            when 'domain'
                if @domain
                    return @domain.getAttr('domain')
                else
                    return @attributes['domain']
            when 'totdegree'
                return @_degree + @_inDegree + @_outDegree + 2 * @_selfloops
            when 'degree'
                return @_degree
            when 'selfloops'
                return @_selfloops
            when 'indegree'
                return @_inDegree
            when 'outdegree'
                return @_outDegree
            else
                return @attributes[key]

    isVisible: -> @_visible
    hide: ->
        @_visible = false
        @domain.nodeVisibility[@id] = 0.0
        return @
    show: ->
        @_visible = true
        @domain.nodeVisibility[@id] = 1.0
        return @

class Edge
    constructor: (@model, @domain, @id, @src, @dst, @attributes, real=true) ->
        if attributes._directed?
            direction = attributes._directed
        else
            if domain?
                direction = domain.edgedefault
            else
                direction = model.edgedefault
        switch direction
            when 'true', 'directed'
                @directed = true
            when 'false', 'undirected'
                @directed = false
            else
                throw "Invalid direction #{direction}"

        if real
            if @directed
                @src._outEdges.push(@)
                @dst._inEdges.push(@)
            else
                @src._edges.push(@)
                @dst._edges.push(@)

        @_weight = 1
        @_color = new THREE.Color(0x000000)
        @_opacity = 0.5
        @_visible = true

        if not @domain?
            @domain = @model

        if @src == @dst
            @src._selfloops += 1
        else
            if @directed
                @src._outDegree += 1
                @dst._inDegree += 1
            else
                @src._degree += 1
                @dst._degree += 1


    other: (node) ->
        if node == @src
            return @dst

        if node == @dst
            return @src

        throw 'Node not linked by this edge'

    getWeight: -> @_weight
    setWeight: (@_weight) ->
        @domain.edgeWeights[@_index * 2] = @_weight
        @domain.edgeWeights[@_index * 2 + 1] = @_weight
        return @

    getColor: -> @_color
    setColor: (color) ->
        @domain.edgeColors[@_index * 2] = @_color = new THREE.Color(color)
        @domain.edgeColors[@_index * 2 + 1] = @_color
        return @

    getOpacity: -> @_opacity
    setOpacity: (@_opacity) ->
        @domain.edgeOpacity[@_index * 2] = @_opacity
        @domain.edgeOpacity[@_index * 2 + 1] = @_opacity
        return @

    isVisible: -> @_visible
    hide: ->
        @_visible = false
        @domain.edgeVisibility[@_index * 2] = 0.0
        @domain.edgeVisibility[@_index * 2 + 1] = 0.0
        return @
    show: ->
        @_visible = true
        @domain.edgeVisibility[@_index * 2] = 1.0
        @domain.edgeVisibility[@_index * 2 + 1] = 1.0
        return @


class Domain extends Node
    constructor: (@model, id, @attributes) ->
        super(@model, undefined, id, @attributes)
        @texture = THREE.ImageUtils.loadTexture('/static/images/node-textures/ball2.png')
        #uniforms.texture.value.wrapS = uniforms.texture.value.wrapT = THREE.RepeatWrapping

        @nodes = []
        @edges = []

        @nodeSizes = []
        @nodeOpacity = []
        @nodeColors = []
        @nodeVisibility = []
        @nodePositions = []

        @edgeWeights = []
        @edgeColors = []
        @edgeOpacity = []
        @edgeVisibility = []
        @edgeVertices = []

    rebuildAttributeMappings: =>
        @nodeSizes.length = 0
        @nodeColors.length = 0
        @nodePositions.length = 0

        @nodes.iter((n, i) =>
            @nodeSizes[i] = n.getSize()
            @nodeOpacity[i] = n.getOpacity()
            @nodeColors[i] = n.getColor()
            @nodeVisibility[i] = n.isVisible()
            @nodePositions[i] = n.getAbsolutePosition()
        )

        @edgeVertices.length = 0
        @edgeWeights.length = 0
        @edgeColors.length = 0
        @edgeOpacity.length = 0
        @edgeVisibility.length = 0

        @edges.iter((e, i) =>
            @edgeVertices[i * 2] = e.src.getAbsolutePosition()
            @edgeVertices[i * 2 + 1] = e.dst.getAbsolutePosition()

            @edgeWeights[i * 2] = e.getWeight()
            @edgeWeights[i * 2 + 1] = e.getWeight()

            @edgeColors[i * 2] = e.getColor()
            @edgeColors[i * 2 + 1] = e.getColor()

            @edgeOpacity[i * 2] = e.getOpacity()
            @edgeOpacity[i * 2 + 1] = e.getOpacity()

            @edgeVisibility[i * 2] = e.isVisible()
            @edgeVisibility[i * 2 + 1] = e.isVisible()
        )

    setTexture: (url) ->
        @texture = THREE.ImageUtils.loadTexture(url)

    addNode: (el) ->
        attrs = this.model._getAttributes(el)
        node = new Node(@model, @, el.attr('id'), attrs)
        @nodes[node.id] = node
        node.setOffset(@getAbsolutePosition())
        return node

    addEdge: (el) ->
        attrs = this.model._getAttributes(el)
        attrs._directed = el.attr('directed')
        src = parseIds(el.attr('source'))
        dst = parseIds(el.attr('target'))

        if src[0] != dst[0] or src[0] != @id
            throw "Invalid edge definition"

        src = this.nodes[src[1]]
        dst = this.nodes[dst[1]]

        edge = new Edge(this.model, this, el.attr('id'), src, dst, attrs)
        edge._index = this.edges.length
        this.edges.push(edge)
        return edge


class GraphModel extends EventDispatcher
    @fromGraphML: (data) ->
        xml = $(data)
        graph = new GraphModel()
        graph.edgedefault = $('graphml > graph', xml).attr('edgedefault')
        $('graphml > key', xml).each((i) ->
            graph.addAttribute($(this))
        )
        graph._attributes = graph._getAttributes($('graphml > graph', xml))
        $('graphml > graph > node', xml).each((i) ->
            domain = graph.addDomain($(this))
            domain.edgedefault = $('> graph', this).attr('edgedefault')
            $('> graph > node', this).each(->
                domain.addNode($(this))
            )
            $('> graph > edge', this).each(->
                domain.addEdge($(this))
            )
            domain.rebuildAttributeMappings()
        )
        $('graphml > graph > edge', xml).each(->
            graph.addEdge($(this))
        )
        graph.rebuildAttributeMappings()
        return graph

    constructor: ->
        super
        this.nextNodeId = 0
        this.nextEdgeId = 0
        this.domains = []
        this.superedges = []
        this.attributes = {
            node: {},
            graph: {},
            edge: {},
            all: {},
            _by_id: {},
        }

        @edgeWeights = []
        @edgeColors = []
        @edgeOpacity = []
        @edgeVisibility = []
        @edgeVertices = []

        @nodes = new IteratorFactory(ArrayPropertyIterator, [this.domains, 'nodes'])
        @edges = new IteratorFactory(FlattenIterator, [[
            @superedges,
            new IteratorFactory(ArrayPropertyIterator, [this.domains, 'edges'])
        ]])

    rebuildAttributeMappings: =>
        @edgeVertices.length = 0
        @edgeWeights.length = 0
        @edgeColors.length = 0
        @edgeOpacity.length = 0
        @edgeVisibility.length = 0

        @superedges.iter((e, i) =>
            @edgeVertices[i * 2] = e.src.getAbsolutePosition()
            @edgeVertices[i * 2 + 1] = e.dst.getAbsolutePosition()

            @edgeWeights[i * 2] = e.getWeight()
            @edgeWeights[i * 2 + 1] = e.getWeight()

            @edgeColors[i * 2] = e.getColor()
            @edgeColors[i * 2 + 1] = e.getColor()

            @edgeOpacity[i * 2] = e.getOpacity()
            @edgeOpacity[i * 2 + 1] = e.getOpacity()

            @edgeVisibility[i * 2] = e.isVisible()
            @edgeVisibility[i * 2 + 1] = e.isVisible()
        )


    getNodeAttributes: ->
        $.extend({}, @attributes.node, @attributes.all)

    _getAttributes: (el) ->
        data = {}
        attrs = this.attributes._by_id
        $('> data', el).each(->
            el = $(this)
            data[attrs[el.attr('key')].name] = el.text()
        )
        return data

    addAttribute: (el) ->
        id = el.attr('id')
        name = el.attr('attr.name')
        type = el.attr('attr.type')
        domain = el.attr('for')
        def = {
            id: id,
            name: name,
            type: type,
            domain: domain,
        }
        this.attributes._by_id[id] = def
        this.attributes[domain][name] = def

    addDomain: (el) ->
        domain = new Domain(this, el.attr('id'), this._getAttributes(el))
        this.domains[domain.id] = domain

    addEdge: (el) ->
        attrs = this._getAttributes(el)
        attrs._directed = el.attr('directed')
        src = parseIds(el.attr('source'))
        dst = parseIds(el.attr('target'))

        src = this.domains[src[0]].nodes[src[1]]
        dst = this.domains[dst[0]].nodes[dst[1]]

        src._degree += 1
        dst._degree += 1

        edge = new Edge(this, undefined, el.attr('id'), src, dst, attrs)
        edge._index = @superedges.length
        this.superedges.push(edge)
        return edge

    numNodes: ->
        total = 0
        for d in this.domains
            total += d.nodes.length
        return total

    getAttr: (name) ->
        @_attributes[name]
