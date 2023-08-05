E = (doc, name, attrs, children...) ->
    el = doc.createElement(name)

    setattrs(doc, el, attrs)

    children.iter((c) ->
        if not c?
            return
        if typeof c == 'string'
            c = doc.createTextNode(c)
        el.appendChild(c)
    )

    el

setattrs = (doc, el, attrs) ->
    for key, value of attrs
        attr = doc.createAttribute(key)
        attr.value = value
        el.setAttributeNode(attr)

class GEXFExporter
    @namespace = 'http://www.gexf.net/1.2draft'
    @namespaces = {
        viz: 'http://www.gexf.net/1.2draft/viz'
    }

    constructor: (@model) ->
        @edgeid = 0

    nodeToXML: (doc, node) ->
        attrs = E(doc, 'attvalues')
        for key, value of node.attributes
            try
                id = @model.attributes.node[key].id
            catch e
                try
                    id = @model.attributes.all[key].id
                catch e
                    continue
            attrs.appendChild(E(doc, 'attvalue', {
                for: id
                value: "#{value}"
            }))
            attrset = true
        if not attrset?
            attrs = undefined

        color = node.getColor()
        position = node.getAbsolutePosition()

        el = E(doc, 'node', {
            id: node.getAbsoluteID()
            label: node.getLabel()
        }, attrs, E(doc, 'viz:color', {
            r: Math.round(color.r * 255)
            g: Math.round(color.g * 255)
            b: Math.round(color.b * 255)
            a: node.getOpacity()
        }), E(doc, 'viz:position', {
            x: position.x * 10
            y: position.y * 10
            z: position.z * 10
        }), E(doc, 'viz:size', {
            value: node.getSize() / 3
        }))

        el

    edgeToXML: (doc, e) ->
        attrs = E(doc, 'attvalues')
        for key, value of e.attributes
            try
                id = @model.attributes.node[key].id
            catch e
                try
                    id = @model.attributes.all[key].id
                catch e
                    continue
            attrs.appendChild(E(doc, 'attvalue', {
                for: id
                value: "#{value}"
            }))
            attrset = true
        if not attrset?
            attrs = undefined

        color = e.getColor()

        E(doc, 'edge', {
            id: @edgeid++
            source: e.src.getAbsoluteID()
            target: e.dst.getAbsoluteID()
            weight: e.getWeight()
            type: if e.directed then 'directed' else 'undirected'
        }, attrs, E(doc, 'viz:color', {
            r: Math.round(color.r * 255)
            g: Math.round(color.g * 255)
            b: Math.round(color.b * 255)
            a: e.getOpacity()
        }), E(doc, 'viz:thickness', {
            value: e.getWeight()
        }))


    domainToXML: (doc, domain) ->
        nodes = E(doc, 'nodes')
        #edges = E(doc, 'edges')

        domain.nodes.iter((n) =>
            if n.isVisible()
                nodes.appendChild(@nodeToXML(doc, n))
        )

        #domain.edges.iter((e) =>
        #    edges.appendChild(@edgeToXML(doc, e))
        #)

        node = @nodeToXML(doc, domain)
        node.appendChild(nodes)
        #node.appendChild(edges)
        node

    toXMLDocument: ->
        doc = document.implementation.createDocument(GEXFExporter.namespace, 'gexf', null)
        root = doc.documentElement

        setattrs(doc, root, {
            version: '1.2'
        })

        for k, v of GEXFExporter.namespaces
            root.setAttribute("xmlns:#{k}", v)

        root.appendChild(E(doc, 'meta',
            {
                lastmodifieddate: today()
            },
            E(doc, 'creator', {}, 'CSAT'),
            E(doc, 'description', {}, 'Exported from CSAT'),
        ))

        nodeAttrs = E(doc, 'attributes', {
            class: 'node'
        })
        edgeAttrs = E(doc, 'attributes', {
            class: 'edge'
        })
        for key, value of @model.attributes._by_id
            attr = E(doc, 'attribute', {
                id: value.id
                title: value.name
                type: value.type
            })
            d = value.domain
            if d == 'node' or d == 'all'
                nodeAttrs.appendChild(attr)
            if d == 'edge' or d == 'all'
                edgeAttrs.appendChild(attr)

        nodes = E(doc, 'nodes')
        @model.domains.iter((d) =>
            if d.isVisible()
                nodes.appendChild(@domainToXML(doc, d))
        )

        edges = E(doc, 'edges')
        @model.edges.iter((e) =>
            if e.isVisible()
                edges.appendChild(@edgeToXML(doc, e))
        )

        root.appendChild(E(doc, 'graph', {
            defaultedgetype: @model.edgedefault
        }, nodeAttrs, edgeAttrs, nodes, edges))

        doc

    toXMLString: ->
        doc = new XMLSerializer().serializeToString(@toXMLDocument())
        '<?xml version="1.0" encoding="utf-8" ?>\n' + doc

    toDataURL: ->
        mime = 'application/xml'
        encoding = 'utf8'
        data = btoa(@toXMLString())
        "data:#{mime};charset=#{encoding};base64,#{data}"
