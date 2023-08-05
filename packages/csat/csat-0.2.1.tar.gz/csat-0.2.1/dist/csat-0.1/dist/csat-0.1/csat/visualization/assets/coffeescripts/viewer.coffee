Object.defineProperty(Array.prototype, 'last', {
    value: ->
        this[this.length - 1]
    enumerable: false
})

class Panel
    constructor: ->
        @container = $('<div/>').addClass('panel')
    getTitle: -> '<Title>'
    getClass: ->
    getContent: ->
    collapse: =>
        @container.addClass('closed')
        return this
    expand: =>
        @container.removeClass('closed')
        return this
    getElement: (@name) ->
        title = $('<h2/>').text(@getTitle()).click(->
            $(this).closest('.panel').toggleClass('closed')
        )

        @contentPanel = $('<div/>')
            .addClass('panel-content')
            .append(@getContent())

        @container
            .addClass(@getClass())
            .attr('id', "panel-#{@name}")
            .append(title)
            .append($('<div/>')
                .addClass('panel-content-wrapper')
                .append(@contentPanel))
        @container


class BasicInfoPanel extends Panel
    constructor: (@viewer) ->
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        super

    getTitle: -> 'Basic information'
    getContent: ->
        $('<dl/>').addClass('dl-horizontal')
    getClass: -> 'basic'

    _graphLoadedCb: (url, model) =>
        edges = (d.edges.length for d in model.domains).reduce(((t, s) -> t + s), 0)
        nodes = (d.nodes.length for d in model.domains).reduce(((t, s) -> t + s), 0)

        $('dl', @container).empty()
            .append($('<dt/>').text('Data source'))
            .append($('<dd/>').html($('<code/>').text(url)))
            .append($('<dt/>').text('Domains'))
            .append($('<dd/>').text(model.domains.length))
            .append($('<dt/>').text('Nodes'))
            .append($('<dd/>').text(nodes))
            .append($('<dt/>').text('Edges'))
            .append($('<dd/>').text(model.superedges.length + edges))


makeSettingsTab = (container, id, title) ->
    tabs = $('> ul', container)
    num = tabs.find('> li').size()
    $('<li/>').append($('<a/>').text(title).attr('href', "##{id}")).appendTo(tabs)
    panel = $('<div/>').attr('id', id).appendTo(container).addClass('settings-wrapper')
    wrapper = $('<div/>').addClass('domain-settings').appendTo(panel)
    if num == 0
        container.tabs({
            active: 0
        })
    else
        container.tabs('refresh')
    wrapper


removeSettingsTab = (container, id) ->
    $("a[href=##{id}]", container).remove()
    tab = $("##{id}", container)
    tab.remove()
    if tab.attr('aria-hidden') == 'false'
        container.tabs('option', 'active', 0)


class DomainsPanel extends Panel
    constructor: (@viewer) ->
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        super

    getTitle: -> 'Domains'
    getClass: -> 'domains'
    getContent: ->
        $('.sidebar', @viewer.container).scroll(->
            top = $(this).scrollTop()
            $('.domains .pop-out', this).css('margin-top', - top - 62 + 'px')
        )
        $('<ul/>')

    _graphLoadedCb: (url, model) =>
        ul = $('ul', @container).empty()
        model.domains.iter((domain, i) ->
            open = (panel) ->
                panel.addClass('open')
                $('body').one('keyup.domainconfig', (e) ->
                    switch e.keyCode
                        when 27      # Esc
                            close(panel)
                        when 37, 38  # Left and up
                            close(panel)
                            panel = panel.closest('li').prev('li').find('.pop-out')
                            if panel.size()
                                open(panel)
                        when 39, 40  # Right and down
                            close(panel)
                            panel = panel.closest('li').next('li').find('.pop-out')
                            if panel.size()
                                open(panel)
                ).on('click.domainconfig', (e) ->
                    t = $(e.target)
                    if t.closest('.pop-out').size()
                        return
                    close(panel)
                    if t.closest('.domains').size()
                        item = t.closest('li')
                        if item.not(panel.closest('li')).size()
                            open(item.find('.pop-out'))
                )

            close = (panel) ->
                panel.removeClass('open')
                $('body').off('keyup.domainconfig', 'click.domainconfig')

            info = $('<div/>')
                .text(domain.attributes.domain)
                .append(
                    $('<span/>')
                        .addClass('muted')
                        .text(" — #{domain.nodes.length} nodes")
                )
                .append($('<a class="settings" href="#"><i class="icon-wrench"/></a>').click((e)->
                    e.stopPropagation()
                    e.preventDefault()
                    panel = $(this).closest('li').find('.pop-out')
                    allPanels = $(this).closest('ul').find('.pop-out').not(panel)
                    allPanels.removeClass('open')
                    if panel.hasClass('open')
                        close(panel)
                    else
                        open(panel)
                ))

            settings = $('<div/>')
                .addClass('pop-out')
                .append($('<span/>').addClass('pointer'))
                .append($('<ul/>'))

            #makeSettingsTab(settings, "edge-settings-#{i}", 'Edges').text('edges')
            #makeSettingsTab(settings, "label-settings-#{i}", 'Labels').text('labels')

            $("<li/>")
                .append(info)
                .append(settings)
                .appendTo(ul)
        )


class LayoutConfigPanel extends Panel
    constructor: (@strategyConfig) ->
        super
    getTitle: -> 'Layout engine'
    getClass: -> 'layout'
    getContent: ->
        @strategyConfig.getForm()


class GenericOptionsPanel extends Panel
    constructor: (@viewer) ->
        @viewer.callbacks.graphRendererChanged.add(@_rendererChangedCb)
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        super

    _rendererChangedCb: (@renderer) =>
        @viewer.getPanel('generic').element.find('input').trigger('change')

    _graphLoadedCb: (url, @model) =>

    getTitle: -> 'Generic options'
    getClass: -> 'generic'

    getContent: ->
        Form.makeForm('generic-options', {
            background: {
                label: 'Background color',
                type: 'color',
                initial: '#ffffff'
                setter: 'setBackground',
            }
            labelcolor: {
                label: 'Labels color',
                type: 'color',
                initial: '#000000'
                setter: 'setLabelColor',
            }
            edgecolor: {
                label: 'Edge color',
                type: 'color',
                initial: '#888888',
                setter: 'setEdgeColor',
            }
            direction: {
                label: 'Edge directions',
                type: 'boolean',
                initial: true,
                setter: 'setEdgeDirectionVisibility',
            }
            transparency: {
                label: 'Edge transparency',
                type: 'boolean',
                initial: true,
                setter: 'setEdgeTransparency',
            }
            thickness: {
                label: 'Edge weight',
                type: 'float',
                initial: 1.0,
                min: 1.0,
                max: 10.0,
                step: 0.1,
                setter: 'setEdgeWeight',
            }
            position: {
                label: 'Axis indicator',
                type: 'boolean',
                initial: true,
                setter: 'setAxisVisibility'
            }
        }, (key, val, field) =>
            @[field.setter](val)
        )

    setEdgeWeight: (val) ->
        @renderer.domainObjects.iter((d) ->
            d.edges.material.linewidth = val
            d.edgesDirection.material.linewidth = val * 1.5 + 1
        )
        @renderer.interEdges.material.linewidth = val
        @renderer.interEdgesDirection.material.linewidth = val * 1.5 + 1

    setLabelColor: (val) ->
        @renderer.domainObjects.iter((d) ->
            d.labels.updateColor(val)
        )

    setEdgeColor: (val) ->
        @model.edges.iter((e) -> e.setColor(val))
        @renderer.domainObjects.iter((d) ->
            d.edges.update()
            d.edgesDirection.update()
        )
        @renderer.interEdges.update()
        @renderer.interEdgesDirection.update()


    setAxisVisibility: (val) ->
        if val
            @viewer.scene.add(@viewer.positionIndicator)
        else
            @viewer.scene.remove(@viewer.positionIndicator)

    setBackground: (val) ->
        @viewer.viewportRenderer.renderer.setClearColor(val, 1)

    setEdgeDirectionVisibility: (val) ->
        @renderer.setEdgeDirectionVisibility(val)

    setEdgeTransparency: (val) ->
        @renderer.setEdgeTransparency(val)


class ExportPanel extends Panel
    constructor: (@viewer) ->
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        super
    getTitle: -> 'Export'
    getClass: -> 'export'
    getContent: ->
        [
            $('<a/>')
                .attr('download', 'graph.png')
                .addClass('btn disabled')
                .attr('href', '#')
                .text('Download image'),
            $('<a/>')
                .attr('download', 'graph.gexf')
                .addClass('btn disabled')
                .attr('href', '#')
                .text('Download GEXF')
        ]

    _graphLoadedCb: (url, model) =>
        viewer = @viewer
        $('a:first-child', @container)
            .removeClass('disabled')
            .click(->
                canvas = $('canvas', viewer.container).get(0)
                data = canvas.toDataURL("image/png")
                $(this).attr('href', data)
            )
        $('a:last-child', @container)
            .removeClass('disabled')
            .click((e) ->
                exporter = new GEXFExporter(model)
                data = exporter.toDataURL()
                $(this).attr('href', data)
            )


class StatsPanel extends Panel
    constructor: (@viewer) ->
        super
    getTitle: -> 'Visualization statistics'
    getClass: -> 'stats'
    getContent: ->
        el = $(@viewer.stats.domElement)
        $('<div/>').append(el)
        el.attr('style', '').find('> div')



class ThumbnailPanel extends Panel
    @width = @height = 200
    @overscale = 2

    constructor: (@viewer) ->
        @viewer.callbacks.graphRendererChanged.add(@_rendererChangedCb)
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        super

    _rendererChangedCb: (@renderer) =>

    _graphLoadedCb: (url, @model) =>
        thumb = @model.getAttr('thumbnail')
        if thumb
            img = new Image()
            img.src = thumb
            img.onload = =>
                context = @canvas.getContext('2d')
                context.drawImage(img, 0, 0)

    redraw: =>
        if not (@canvas and @renderer and @model)
            return

        graphImage = $('canvas', @viewer.getViewport()).get(0)

        w = graphImage.width
        h = graphImage.height

        r = window.devicePixelRatio

        tw = ThumbnailPanel.width * r * ThumbnailPanel.overscale
        th = ThumbnailPanel.height * r * ThumbnailPanel.overscale

        @canvas.width = @canvas.width
        context = @canvas.getContext('2d')

        sx = @selector.offset().left * r
        sy = @selector.offset().top * r
        sw = @selector.width() * r
        sh = @selector.height() * r

        context.webkitImageSmoothingEnabled = true
        context.drawImage(graphImage, sx, sy, sw, sh, 0, 0, tw, th)

        url = @canvas.toDataURL()
        hex = url.split(',')[1]

        data = Base64Binary.decode(hex)

        blob = new Blob([data], {
            type: 'image/png'
        })

        formData = new FormData()
        formData.append('thumbnail', blob)
        $.ajax({
            url: @model.getAttr('thumbnail')
            type: 'POST'
            data: formData
            processData: false
            contentType: false
        })

    getTitle: -> 'Thumbnail'
    getClass: -> 'graph-thumbnail'
    getContent: ->
        w = ThumbnailPanel.width
        h = ThumbnailPanel.height
        r = window.devicePixelRatio
        canvas = $('<canvas/>')
        @canvas = canvas.get(0)
        @canvas.width = w * r * ThumbnailPanel.overscale
        @canvas.height = h * r * ThumbnailPanel.overscale
        canvas.width(w).height(h)

        @selector = $('<div/>')
            .addClass('cropper')
            .appendTo(@viewer.getViewport())
            .draggable({
                containment: 'parent'
            })
            .resizable({
                containment: 'parent'
                aspectRatio: true
                handles: 'sw, se, ne, nw'
            })
            .append($('<button/>')
                .text('Set')
                .click(=>
                    @viewer.controls.disabled = false
                    @redraw()
                    @selector.removeClass('active')
                )
            )
            .width(w)
            .height(h)
            .css({
                top: (@viewer.getViewport().height() + h) / 2 + 'px'
                left: (@viewer.getViewport().width() + w) / 2 + 'px'
            })

        $('<div/>')
            .append(canvas)
            .append($('<button/>').text('Select'))
            .click(=>
                @viewer.controls.disabled = true
                @selector.addClass('active')
            )
            .width(w)
            .height(h)


class NodeInfoPanel extends Panel
    constructor: (@viewer) ->
        @viewer.callbacks.graphRendererChanged.add(@_rendererChangedCb)
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)
        @depth = 0
        super

    _rendererChangedCb: (@renderer) =>

    _graphLoadedCb: (url, @model) =>
        @model.on('nodehover', (node) =>
            if not node._active
                node._inactiveColor = node.getColor()
            node._hover = true
            @_updateNode(node)
            @viewer.getViewport().css('cursor', 'pointer')
        ).on('nodeout', (node) =>
            node._hover = false
            @_updateNode(node)
            @viewer.getViewport().css('cursor', 'default')
        ).on('nodeclick', (node) =>
            if @_oldNode
                if @_oldNode == node
                    # Unselect
                    @model.fire('activenodechanged', node, undefined)
                    @_oldNode = undefined
                else
                    # Unselect old
                    @model.fire('activenodechanged', @_oldNode, node)
                    @_oldNode = node
            else
                # Event
                @model.fire('activenodechanged', undefined, node)
                @_oldNode = node
        ).on('activenodechanged', (oldNode, newNode) =>
            if oldNode?
                oldNode._active = false
                @_updateNode(oldNode)
            if newNode?
                newNode._active = true
                @_updateNode(newNode)
                @showInfo(newNode)
            else
                @container.find('.neighbors-filter').remove()
                @contentPanel.empty().append(@placeholder)
        ).on('activenodechanged', (oldNode, newNode) =>
            @selectedNode = newNode
            @filterByNode()
        )

    _updateNode: (node) =>
        if node._active
            node.setColor(0xff0000)
        else if node._hover
            node.setColor(0x990000)
        else
            node.setColor(node._inactiveColor)

    filterByNode: =>
        if @selectedNode? and @depth > 0
            # Hide all
            @model.nodes.iter((n) ->
                n.hide().setOpacity(1.0)
                n.__distance = Infinity
            )
            @model.edges.iter((e) -> e.hide().setOpacity(1.0))

            showNeighbors = (n, distance, maxdepth) ->
                if n.__distance <= distance
                    return
                n.__distance = distance
                opacity = 0.7 / Math.pow(2, distance) + 0.3
                n.show().setOpacity(opacity)
                if distance < maxdepth
                    flatten(n._outEdges, n._edges).iter((e) ->
                        showNeighbors(e.other(n), distance + 1, maxdepth)
                        e.show().setOpacity(opacity)
                    )
                else
                    flatten(n._outEdges, n._edges).iter((e) ->
                        if e.other(n).isVisible()
                            e.show().setOpacity(opacity)
                    )

            # Recursively show by dept-first search
            showNeighbors(@selectedNode, 0, @depth)
        else
            @model.nodes.iter((n) -> n.show().setOpacity(1.0))
            @model.edges.iter((e) -> e.show().setOpacity(1.0))

        @renderer.domainObjects.iter((d) ->
            d.edges.update()
            d.edgesDirection.update()
            d.labels.updateFromNode()
        )
        @renderer.interEdges.update()
        @renderer.interEdgesDirection.update()

    showInfo: (node) =>
        info = $('<table/>')

        urlPattern = /(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/

        add = (label, val) ->
            label = label.replace('_', ' ')
            label = label.charAt(0).toUpperCase() + label.substr(1)
            row = $('<tr/>').appendTo(info)
            row.append($('<th/>').text(label))
            if urlPattern.test(val)
                el = $('<a target="_blank"/>').attr('href', val).text(val)
                row.append($('<td/>').append(el))
            else
                row.append($('<td/>').text(val))

        add('FQID', node.fqid)
        add('Domain', node.domain.getAttr('domain'))
        add('Degree', node.getAttr('degree'))
        add('In-degree', node.getAttr('indegree'))
        add('Out-degree', node.getAttr('outdegree'))

        for key, val of node.attributes
            add(key, val)

        @contentPanel.empty().append($('<div class="table-wrapper">').append(info))

        modes = [
            [0, 'Show whole graph']
            [1, 'Show 1st order neighbors']
            [2, 'Show 2nd order neighbors']
            [3, 'Show 3rd order neighbors']
        ]

        buttonGroup = $('<div/>').addClass('btn-group')

        current = $('<button/>')
            .addClass('btn dropdown-toggle')
            .append($('<span/>').text(modes[@depth][1]))
            .append($('<i/>').addClass('caret'))
            .appendTo(buttonGroup)

        dropdown = $('<ul/>').addClass('dropdown-menu').appendTo(buttonGroup)
        this_ = @
        for [f, t] in modes
            btn = $('<a/>').attr('href', '#').text(t).data('filter', f)
                .click(->
                    this_.setFilter(parseInt($(this).data('filter')))
                    current.find('span').text($(this).text())
                )
            $('<li/>').append(btn).appendTo(dropdown)

        current.dropdown()

        div = $('<div/>').addClass('neighbors-filter').append(buttonGroup)

        @contentPanel.append(div)
    setFilter: (f) ->
        @depth = f
        @filterByNode()

    getTitle: -> 'Node information'
    getClass: -> 'nodeinfo'
    getContent: ->
        @placeholder = $('<p/>')
            .addClass('muted')
            .text('Click on a node to visualize additional details here.')


class LabelsDisplaySettings
    constructor: (@viewer) ->
        @viewer.callbacks.graphRendererChanged.add(@_rendererChangedCb)
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)

    _rendererChangedCb: (@renderer) =>
        forms = @viewer.getPanel('domains').element.find('.panel-content > ul > li .pop-out form')
        forms.find('input, select').each(->
            $(this).trigger('change')
        )

    _graphLoadedCb: (url, @model) =>
        attributes = NodesDisplaySettings.genericNodeAttributes.slice(0)
        for key, val of @model.getNodeAttributes()
            name = key.replace('_', ' ')
            name = name.charAt(0).toUpperCase() + name.substr(1)
            attributes.push([key, name])

        domains = @viewer.getPanel('domains').element.find('.panel-content > ul > li')
        @model.domains.iter((domain, i) =>
            labelsForm = Form.makeForm(
                "labels-#{i}",
                {
                    content: {
                        label: 'Content',
                        type: 'list',
                        valueType: 'string',
                        values: attributes,
                        setter: 'setContent',
                    }
                    visible: {
                        label: 'Show labels',
                        type: 'boolean',
                        initial: true,
                        setter: 'setVisibility',
                    }
                    size: {
                        label: 'Font size',
                        type: 'float',
                        step: '0.5',
                        min: 5.0,
                        max: 20.0,
                        initial: 10.0,
                        setter: 'setSize',
                    }
                    nodeSizeFactor: {
                        label: 'Node size factor',
                        type: 'float',
                        initial: 0.0,
                        step: 0.1,
                        setter: 'setNodeSizeFactor'
                    }
                },
                (key, val, field) =>
                    @[field.setter](i, val)
            )
            tab = makeSettingsTab(
                domains.eq(i).find('.pop-out'),
                "label-settings-#{i}",
                'Labels'
            )

            tab.append(labelsForm)
        )

    setSize: (i, size) =>
        if @renderer
            l = @renderer.domainObjects[i].labels
            l.updateFontSize(size, l.nodeSizeFactor)

    setNodeSizeFactor: (i, size) =>
        if @renderer
            l = @renderer.domainObjects[i].labels
            l.updateFontSize(l.baseSize, size)

    setVisibility: (i, visible) =>
        if @renderer
            if visible
                @renderer.labelsObject.add(@renderer.domainObjects[i].labels)
            else
                @renderer.labelsObject.remove(@renderer.domainObjects[i].labels)

    setContent: (i, p) ->
        @model.domains[i].nodes.iter((n) =>
            l = n.getAttr(p)
            n.setLabel("#{l}")
        )

        if @renderer
            old = @renderer.domainObjects[i].labels
            @renderer.labelsObject.remove(old)
            object = new DomainLabelsObject(@model.domains[i])
            object.material.uniforms['color'].value = old.material.uniforms['color'].value
            @renderer.domainObjects[i].labels = object
            @renderer.labelsObject.add(object)


class NodesDisplaySettings
    @genericNodeAttributes = [
        ['degree', 'Degree'],
        ['indegree', 'In-degree'],
        ['outdegree', 'Out-degree'],
    ]

    @textures = [
        ['/static/images/node-textures/ball2.png', 'Sphere 1']
        ['/static/images/node-textures/ball.png', 'Sphere 2']
        ['/static/images/node-textures/square.png', 'Plain square']
        ['/static/images/node-textures/rect.png', 'Bordered square']
        ['/static/images/node-textures/disc.png', 'Disc']
        ['/static/images/node-textures/lego.png', 'Lego figure']
        ['/static/images/node-textures/lego-brick.png', 'Lego brick']
    ]

    constructor: (@viewer) ->
        @viewer.callbacks.graphRendererChanged.add(@_rendererChangedCb)
        @viewer.callbacks.graphLoaded.add(@_graphLoadedCb)

    _rendererChangedCb: (@renderer) =>

    _graphLoadedCb: (url, @model) =>
        numerical = ['int', ]

        attributes = NodesDisplaySettings.genericNodeAttributes.slice(0)
        domains = @viewer.getPanel('domains').element.find('.panel-content > ul > li')

        for key, val of @model.getNodeAttributes()
            if $.inArray(val.type, numerical) > -1
                name = key.replace('_', ' ')
                name = name.charAt(0).toUpperCase() + name.substr(1)
                attributes.push([key, name])

        @coloring = []
        @sizing = []

        @model.domains.iter((domain, i) =>
            textures = ([j, t[1]] for t, j in NodesDisplaySettings.textures)
            textureForm = Form.makeForm(
                "nodes-texture-#{i}",
                {
                    property: {
                        label: 'Texture',
                        type: 'list',
                        valueType: 'integer',
                        values: textures,
                    },
                },
                (key, val, field) =>
                    val = NodesDisplaySettings.textures[val][0]
                    @model.domains[i].setTexture(val)
                    if @renderer
                        @renderer.domainObjects[i].nodes.updateTexture()
            )
            sizingForm = Form.makeForm(
                "nodes-sizing-attribute-#{i}",
                {
                    property: {
                        label: 'Sizing property',
                        type: 'list',
                        valueType: 'string',
                        values: attributes,
                    },
                },
                (key, val, field) =>
                    @sizing[i].attr = val
                    [min, max] = @getAttrRange(i, val)
                    @sizing[i].editor.setInterval(min, max)
            )
            coloringForm =  Form.makeForm(
                "nodes-coloring-attribute-#{i}",
                {
                    property: {
                        label: 'Coloring property',
                        type: 'list',
                        valueType: 'string',
                        values: attributes,
                    },
                },
                (key, val, field) =>
                    @coloring[i].attr = val
                    [min, max] = @getAttrRange(i, val)
                    @coloring[i].editor.setInterval(min, max)
            )

            tab = makeSettingsTab(
                domains.eq(i).find('.pop-out'),
                "node-settings-#{i}",
                'Nodes'
            )

            [min, max] = @getAttrRange(i, attributes[0][0])

            sizingEditor = new BezierEditor(350, 170, min, max)
            sizingEditor.changed.add((f) =>
                @sizing[i].func = f
                @setSize(i)
            )

            coloringEditor = new BezierColorEditor(350, 170, min, max)
            coloringEditor.changed.add((f) =>
                @coloring[i].func = f
                @setColor(i)
            )

            tab.append(textureForm)

            tab.append(sizingForm)
            tab.append(sizingEditor.getElement())

            tab.append(coloringForm)
            tab.append(coloringEditor.getElement())

            @sizing.push({
                attr: attributes[0][0]
                func: undefined
                editor: sizingEditor
            })

            @coloring.push({
                attr: attributes[0][0]
                func: undefined
                editor: coloringEditor
            })

            sizingEditor.setInterval(min, max)
            coloringEditor.setInterval(min, max)
        )

    getAttrRange: (i, p) ->
        min = Infinity
        max = -Infinity
        @model.domains[i].nodes.iter((n) ->
            val = n.getAttr(p)
            if val?
                min = Math.min(min, val)
                max = Math.max(max, val)
        )
        [min, max]

    setColor: (i) ->
        {attr, func} = @coloring[i]

        if not @model or not func
            return

        @model.domains[i].nodes.iter((n) =>
            n.setColor(func(n.getAttr(attr)))
        )


    setSize: (i) ->
        {attr, func} = @sizing[i]

        if not @model or not func
            return

        @model.domains[i].nodes.iter((n) =>
            n.setSize(func(n.getAttr(attr)))
        )
        if @renderer
            @renderer._layoutStepCb()
            @renderer.domainObjects[i].labels.updateFromNode()

    setTexture: (id) ->
        loader = new THREE.ImageLoader()
        loader.load(@textures[id], (image) =>
            @renderer.domains.iter((d) ->
                d.texture.image = image
                d.texture.needsUpdate = true
            )
        )


class ObjectControls
    constructor: (@viewer) ->
        @rotationSpeed = .3
        @panSpeed = .8
        @zoomSpeed = .1
        @disabled = false

        @getViewport().on('mousedown', (e) =>
            if @disabled
                return
            e.preventDefault()
            $(window).on('mousemove.controls', (e) =>
                e.preventDefault()
                @dragging = true
                pos = @positionFromEvent(e)
                offset = @offsetFromLastEvent(e)
                @mousemove(pos, offset)
                @updateIndicator()
            ).on('mouseup.controls', (e) =>
                $(window).off('mousemove.controls').off('mouseup.controls')
                @dragging = false
                pos = @positionFromEvent(e)
                @_lastEvent = undefined
                @mouseup(pos)
                @updateIndicator()
            )
            if not e.metaKey
                @action = 'pan'
            else
                @action = 'rotate'
            pos = @positionFromEvent(e)
            offset = @offsetFromLastEvent(e)
            @mousedown(pos)
            @updateIndicator()
        ).on('dblclick', =>
            @reset()
            @updateIndicator()
        ).on('mousewheel', (e) =>
            pos = @positionFromEvent(e)
            direction = e.originalEvent.wheelDelta / 120

            if e.shiftKey
                @rotate(new THREE.Vector3(1 * direction * 10, 0, 0))
            else if e.altKey
                @rotate(new THREE.Vector3(0, 1 * direction * 10, 0))
            else if e.metaKey
                @rotate(new THREE.Vector3(0, 0, 1 * direction * 10))
            else
                @zoom(pos, direction)
            @updateIndicator()
        )

    updateIndicator: =>
        @viewer.positionIndicator.rotation = @viewer.getCurrentObject().rotation

    getViewport: =>
        @viewer.container.find('.viewport')

    offsetFromLastEvent: (e) =>
        if @_lastEvent?
            offset = new THREE.Vector3(
                e.pageX - @_lastEvent.pageX,
                e.pageY - @_lastEvent.pageY,
                0
            )
        else
            offset = new THREE.Vector3(0, 0, 0)
        @_lastEvent = e
        offset

    positionFromEvent: (e) =>
        offset = @getViewport().offset()
        width = @getViewport().width()
        height = @getViewport().height()
        x = Math.max(0, Math.min(width, e.pageX - offset.left))
        y = Math.max(0, Math.min(height, e.pageY - offset.top))
        new THREE.Vector2(x, y)

    mousedown: (pos, offset) =>

    mouseup: (pos, offset) =>

    mousemove: (pos, offset) =>
        if @action == 'pan'
            @pan(offset)
        else
            @rotate(offset)

    reset: ->
        @viewer.getCurrentScene().scale = new THREE.Vector3(1, 1, 1)
        @viewer.getCurrentObject().rotation = new THREE.Vector3(0, 0, 0)
        @viewer.getCurrentScene().position = new THREE.Vector3(0, 0, 0)

    pan: (offset) ->
        translation = new THREE.Matrix4()
        translation.makeTranslation(
            offset.x * @panSpeed / 10,
            -offset.y * @panSpeed / 10,
            0
        )
        @viewer.getCurrentScene().applyMatrix(translation)

    zoom: (pos, direction) ->
        camera = @viewer.camera
        scene = @viewer.getCurrentScene()

        d = Math.abs(camera.position.z - scene.position.z)
        offset = -direction * @zoomSpeed * (d / 10 + 1)

        # Too far
        if d - offset >= camera.far
            return

        # Too near
        if d - offset < 1
            return

        ax = pos.x - @viewer.container.find('canvas').width() / 2
        ay = pos.y - @viewer.container.find('canvas').height() / 2

        tx = ax * (offset - 1) * @viewer.ratio
        ty = -ay * (offset - 1) * @viewer.ratio

        translation = new THREE.Matrix4()
        translation.makeTranslation(0, 0, offset)
        scene.applyMatrix(translation)

    rotate: (offset) ->
        rotationY = new THREE.Matrix4()
        rotationY.makeRotationY(offset.x * @rotationSpeed / 100)
        rotationX = new THREE.Matrix4()
        rotationX.makeRotationX(offset.y * @rotationSpeed / 100)
        rotationZ = new THREE.Matrix4()
        rotationZ.makeRotationZ(offset.z * @rotationSpeed / 100)

        rotation = new THREE.Matrix4().multiplyMatrices(rotationX, rotationY)
        rotation.multiply(rotationZ)

        @viewer.getCurrentObject().applyMatrix(rotation)


makePositionAxis = (text, size, color) ->
    axis = new THREE.Object3D()
    material = new THREE.LineBasicMaterial({color: color, linewidth: 10})

    line = new THREE.Mesh(
        new THREE.CylinderGeometry(.08, .08, size, 5, 5, false),
        material
    )
    line.position.y = size / 2
    axis.add(line)

    arrow = new THREE.Mesh(
        new THREE.CylinderGeometry(0, .3, 1.2, 10, 5, false),
        material
    )
    arrow.position.y = size
    axis.add(arrow)

    labelGeometry = new THREE.TextGeometry(text, {
        size: 1.5
        height: .1
        font: 'helvetiker'
        curveSegments: 10
        bevelThickness: 10
        bevelSize: 1.5
        bevelEnabled: false
        material: 0
        extrudeMaterial: 1
    })
    labelGeometry.computeBoundingBox()
    labelGeometry.computeVertexNormals()
    labelMaterial = new THREE.MeshFaceMaterial([
        new THREE.MeshPhongMaterial({color: color, shading: THREE.FlatShading}),
        new THREE.MeshPhongMaterial({color: color, shading: THREE.SmoothShading})
    ])
    label = new THREE.Mesh(labelGeometry, labelMaterial)
    label.position.y = size + 1
    label.position.x = -.5
    axis.add(label)
    axis


makePositionIndicator = ->
    size = 5
    position = new THREE.Object3D()

    x = makePositionAxis('X', size, 0xff0000)
    x.rotation.z = -Math.PI / 2
    x.rotation.x = -Math.PI / 2
    position.add(x)

    y = makePositionAxis('Y', size, 0x00ff00)
    y.rotation.z = 0
    position.add(y)

    z = makePositionAxis('Z', size, 0x0000ff)
    z.rotation.x = -Math.PI / 2
    position.add(z)

    sphere = new THREE.Mesh(
        new THREE.SphereGeometry(.4, 20, 20),
        new THREE.MeshBasicMaterial({
            color: 0x000000
        })
    )
    position.add(sphere)

    sphereGeometry = new THREE.SphereGeometry(2, 10, 10)
    wireframeMaterial = new THREE.LineBasicMaterial({
        color:  0x000000,
        opacity: .05,
        transparent: true,
    })
    wireframe = new THREE.Line(
        geo2line(sphereGeometry),
        wireframeMaterial,
        THREE.LinePieces
    )
    position.add(wireframe)
    position


class Viewer
    constructor: (@container, @strategies) ->
        @stats = new Stats()
        @stats.setMode(0)
        @panels = {}
        @callbacks = {
            graphLoaded: $.Callbacks()
            graphRendererChanged: $.Callbacks()
        }

        @scene = new THREE.Scene()
        @strategyConfig = new StrategyConfigurator(@strategies, this)
        @addPanel('basic', new BasicInfoPanel(this))
        @addPanel('generic', new GenericOptionsPanel(this)).collapse()
        @addPanel('nodeinfo', new NodeInfoPanel(this))
        @addPanel('domains', new DomainsPanel(this))
        @addPanel('layout', new LayoutConfigPanel(@strategyConfig))
        @addPanel('stats', new StatsPanel(this)).collapse()
        @addPanel('thumbnail', new ThumbnailPanel(this)).collapse()
        #@addPanel('nodes-display', new NodesDisplayPanel(this).collapse())
        @addPanel('export', new ExportPanel(this))

        new NodesDisplaySettings(this)
        new LabelsDisplaySettings(this)

        $('.sidebar', @container).sortable({
            handle: '> h2'
            placeholder: 'drop-placeholder'
            forcePlaceholderSize: true
            axis: 'y'
            start: (e, ui) ->
                ui.placeholder.height(ui.item.height())
        })

        if document.referrer
            @container.append($('<a href="#" id="backlink" class="icon-arrow-left">Back</a>').click((e) ->
                e.preventDefault()
                history.back()
            ))

        console.log 'New viewer instance created'

    setRenderer: (@graphRenderer) ->
        @callbacks.graphRendererChanged.fire(@graphRenderer)

    getCleanScene: =>
        if @_currentScene?
            @scene.remove(@_currentScene)

        @_internalObject = new THREE.Object3D()
        @_currentScene = new THREE.Object3D()
        @_currentScene.add(@_internalObject)
        @scene.add(@_currentScene)
        @_internalObject

    getCurrentScene: =>
        @_currentScene

    getCurrentObject: =>
        @_internalObject

    addPanel: (name, panel) ->
        if @panels[name]
            @panels[name].element.detach()

        @panels[name] = {
            panel: panel
            element: panel.getElement(name)
        }

        $('.sidebar', @container).append(@panels[name].element)
        panel

    getPanel: (name) ->
        @panels[name]

    getViewport: =>
        @container.find('.viewport')

    load: (@url) ->
        console.log "Loading graph data from #{url}"
        div = $('<div/>').append($.spinner())
        p = $('<p>Loading graph data...</p>').appendTo(div)
        #this._overlay(div)
        $.ajax(
            url: this.url,
            datatType: 'xml',
            progress: (e) ->
                if (e.lengthComputable)
                    pct = (e.loaded / e.total)
                    p.text("Loading graph data, #{Math.round(pct * 100)}% completed...")
                else
                    console.warn('Content Length not reported!')
            success: (data) =>
                p.text('Data received, preparing graph...')
                @_loadFromData(data)
                p.text('Graph creation complete, preparing scene...')
                @callbacks.graphLoaded.fire(@url, @model)

                #$('.overlay', this.container).addClass('scene-only')
                @_prepareScene()
        )

    _loadFromData: (data) ->
        @model = GraphModel.fromGraphML(data)
        domains = @model.domains.length
        nodes = @model.numNodes()
        edges = @model.edges.length
        console.log("Graph loaded: #{domains} domains, #{nodes} nodes, #{edges} edges.")
        if @strategy
            @strategy.render(@model)

    _prepareScene: ->
        # This is the HTML element which contains the canvas element used by
        # WebGL
        container = $('.viewport', this.container)

        @camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000)
        @camera.position.z = 90

        @controls = new ObjectControls(@)

        light = new THREE.DirectionalLight(0xffffff, 1.2)
        light.position.set(0, 1, 1).normalize()
        @scene.add(light)

        light = new THREE.DirectionalLight(0xffffff, 1.2)
        light.position.set(0, -1, -1).normalize()
        @scene.add(light)

        @positionIndicator = makePositionIndicator()

        height = Math.tan(@camera.fov / 2) * @camera.position.z * 2
        @ratio = height / container.height()

        setPosition = =>
            @positionIndicator.position = new THREE.Vector3(
                (-container.width() / 2) * @ratio + 8,
                (-container.height() / 2) * @ratio + 8,
                0
            )
        setInterval(setPosition, 100)
        @scene.add(@positionIndicator)

        # The vieport is a point of view of the scene.
        viewport = new Viewport({
            x: 0, y: 0,
            width: 1, height: 1,
            camera: @camera,
            controls: @controls,
        })

        @viewportRenderer = new MultipleViewportsRenderer(
            container, @scene, [viewport], @stats)
        @viewportRenderer.animate()

        @strategyConfig.enable()

        #@_overlay()

    _overlay: (el, sceneOnly=false) ->
        overlay = $('.overlay', this.container)
        if el?
            if sceneOnly
                overlay.addClass('scene-only')
            else
                overlay.removeClass('scene-only')
            $('> *', overlay).remove()
            overlay.append(el)
            overlay.twostepsShow()
        else
            overlay.twostepsHide(->
                $('*', this).remove()
            )


class ModalPanel
    constructor: ->

    open: =>

    close: =>


class VisualizationSettings extends ModalPanel


(($) ->
    $ ->
        $('body').click((e) ->
            picker = $('.color-picker')

            if not picker.size()
                return

            if $(e.target).closest('.color-picker').size()
                return

            if $(jscolor.picker.owner.valueElement).is(':focus')
                return

            delete jscolor.picker.owner
            picker.remove()
        )
        container = $('.graph-viewer')
        if container.size() != 1
            console.error("Incorrect number of graph viewer containers "
                          "found: #{container.size()}")
            return

        strategies = [
            new SingleStrategy([
                new RandomLayoutFactory(),
                new FRLayout2DAsyncFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
                new DomainFRLayout2DFactory()
            ]),
            new DomainStrategy([
                new FRLayout2DAsyncFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
            ], [
                new StackedLayoutFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
            ]),
            new ExtrudedStrategy([
                new StackedLayoutFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
            ], [
                new DomainFRLayout2DFactory()
                new FRLayout2DAsyncFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
            ]),
            new ClusteredStrategy([
                new FRLayout2DAsyncFactory(),
                new FRLayout2DFactory(),
                new FRLayout3DFactory(),
                new DomainFRLayout2DFactory()
            ]),
        ]

        # Build viewer
        viewer = new Viewer(container, strategies)
        viewer.load($.urlParam('url'))
)(jQuery)
