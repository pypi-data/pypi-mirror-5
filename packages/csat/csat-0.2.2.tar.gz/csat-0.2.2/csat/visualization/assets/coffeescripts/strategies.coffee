class Strategy
    getName: -> '<Abstract strategy>'
    activate: (@viewer) ->
    deactivate: ->
    setScene: (@scene) ->
    getForm: ->
        $('<div/>')
            .addClass('strategy-config')
            .append($('<p class="muted">No settings for this strategy</p>'))


class SingleStrategy extends Strategy
    constructor: (@layoutFactories) ->
        @config = new LayoutConfigurator(@layoutFactories)
        @config.callbacks.layoutChanged.add(@_layoutChangedCb)

    getName: -> 'Single graph'
    getForm: ->
        @runButton = $('<button/>')
            .addClass('btn btn-primary')
            .text('Run')
            .one('click', => @renderer.run())

        menu = $('<ul/>').addClass('dropdown-menu')
        menu.append($('<li/>').append($('<a href="#"/>').text('Restart all').click(=>
            @renderer.stop()
            @renderer.run()
        )))

        dropdown = $('<div/>')
            .addClass('btn-group')
            .append(@runButton)
            .append($('<button class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>'))
            .append(menu)

        @mainStatus = $('<div/>')
            .addClass('status')
            .append($.spinner(20, 'small'))
            .append($('<div/>'))

        $('<div/>').addClass('strategy-config')
            .append(@config.getForm())
            .append($('<div/>')
                .addClass('form-actions')
                .append(@mainStatus)
                .append(dropdown))

    _layoutStartedCb: =>
        @mainStatus.addClass('running').find('div').text('Running...')
        @runButton.text('Pause').off('click').one('click', => @renderer.pause())

    _layoutPausedCb: =>
        @mainStatus.removeClass('running').find('div').text('Paused')
        @runButton.text('Resume').off('click').one('click', => @renderer.run())

    _layoutDoneCb: =>
        if @_switchingLayout
            @mainStatus.removeClass('running').find('div').text('')
            @_switchingLayout = false
        else
            @mainStatus.removeClass('running').find('div').text('Done.')
        @runButton.text('Run').off('click').one('click', => @renderer.run())

    _layoutChangedCb: (factory) =>
        if @renderer
            @_switchingLayout = true
            if not @renderer.layout or not @renderer.isRunning()
                @_layoutDoneCb()
            @renderer.setLayout(@_getLayout())
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
            return

    _getLayout: ->
        layout = @config.getLayout()
        layout.callbacks.started.add(@_layoutStartedCb)
        layout.callbacks.resumed.add(@_layoutStartedCb)
        layout.callbacks.paused.add(@_layoutPausedCb)
        layout.callbacks.done.add(@_layoutDoneCb)
        layout

    activate: (@viewer) ->
        if not @renderer
            @renderer = new GraphRenderer(@viewer.model, @viewer)
            @_layoutChangedCb()
        else
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
        @renderer.step()
        @renderer

    deactivate: ->
        if @renderer
            @renderer.pause()


class ClusteredStrategy extends SingleStrategy
    getName: -> 'Clustered'
    activate: (@viewer) ->
        if not @renderer
            @renderer = new ClusteredGraphRenderer(@viewer.model, @viewer)
            @_layoutChangedCb()
        else
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
        @renderer.step()
        @renderer



class DomainStrategy extends Strategy
    constructor: (@domainLayoutFactories, @globalLayoutFactories) ->
        @globalLayoutConfig = new LayoutConfigurator(@globalLayoutFactories)
        @globalLayoutConfig.callbacks.layoutChanged.add(@_globalLayoutChangedCb)

    getName: -> 'Multi-level (per domain)'
    getForm: ->
        @runButton = $('<button/>')
            .addClass('btn btn-primary')
            .text('Run')
            .one('click', => @renderer.run())

        menu = $('<ul/>').addClass('dropdown-menu')
        menu.append($('<li/>').append($('<a href="#"/>').text('Restart all').click(=>
            @renderer.stop()
            @renderer.run()
        )))

        dropdown = $('<div/>')
            .addClass('btn-group')
            .append(@runButton)
            .append($('<button class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>'))
            .append(menu)

        @mainStatus = $('<div/>')
            .addClass('status')
            .append($.spinner(20, 'small'))
            .append($('<div/>'))

        config = @globalLayoutConfig.getForm()
        $('.algorithm-select label', config).text('Outer algorithm')
        $('<div/>').addClass('strategy-config')
            .append(config)
            .append(
                $('<p/>')
                    .addClass('muted')
                    .text('Domain-specific layout algorithms can be configured in the domain settings.')
            )
            .append($('<div/>')
                .addClass('form-actions')
                .append(@mainStatus)
                .append(dropdown))

    setupDomain: (domainModel, i) =>
        el = $(".sidebar .domains li:nth-child(#{i + 1})", @viewer.container)

        config = new LayoutConfigurator(@domainLayoutFactories)

        actions = $('<div/>')
            .addClass('actions')
            .append($('<a href="#"/>')
                .append($('<i class="icon-pause"/>'))
                .append($('<i class="icon-play"/>'))
                .one('click', (e) =>
                    e.preventDefault()
                    @renderer.runPartition(i)
                ))
            .append($.spinner(20, 'mini'))

        domain = {
            id: i
            element: el
            config: config
            actions: actions
            form: config.getForm()
        }

        config.callbacks.layoutChanged.add((factory) =>
            @_domainLayoutChangedCb(factory, domain)
        )

        domain

    _getGlobalLayout: ->
        layout = @globalLayoutConfig.getLayout()
        layout.callbacks.started.add(@_layoutStartedCb)
        layout.callbacks.resumed.add(@_layoutStartedCb)
        layout.callbacks.paused.add(@_layoutPausedCb)
        layout.callbacks.done.add(@_layoutDoneCb)
        layout

    _getDomainLayout: (domain) ->
        layout = domain.config.getLayout()
        layout.callbacks.started.add(=> @_layoutStartedCb(domain))
        layout.callbacks.resumed.add(=> @_layoutStartedCb(domain))
        layout.callbacks.paused.add(=> @_layoutPausedCb(domain))
        layout.callbacks.done.add(=> @_layoutDoneCb(domain))
        layout

    _layoutStartedCb: (domain) =>
        if domain
            domain.element.addClass('running').removeClass('paused')
            domain.actions.find('a').off('click').one('click', (e) =>
                e.preventDefault()
                @renderer.pausePartition(domain.id)
            )

        if @renderer.someLayoutsRunning()
            @mainStatus.addClass('running').find('div').text('Running...')
            @runButton.text('Pause').off('click').one('click', => @renderer.pause())

    _layoutPausedCb: (domain) =>
        if domain
            domain.element.addClass('paused').removeClass('running')
            domain.actions.find('a').off('click').one('click', (e) =>
                e.preventDefault()
                @renderer.runPartition(domain.id)
            )

        if not @renderer.someLayoutsRunning()
            if @renderer.someLayoutsPaused()
                @mainStatus.removeClass('running').find('div').text('Paused')
                @runButton.text('Resume').off('click').one('click', => @renderer.resume())
            else
                @mainStatus.removeClass('running').find('div').text('Done')
                @runButton.text('Resume').off('click').one('click', => @renderer.run())

    _layoutDoneCb: (domain) =>
        if domain
            domain.element.removeClass('paused').removeClass('running')
            domain.actions.find('a').off('click').one('click', (e) =>
                e.preventDefault()
                @renderer.runPartition(domain.id)
            )

        if not @renderer.someLayoutsRunning()
            if not @renderer.someLayoutsPaused()
                @mainStatus.removeClass('running').find('div').text('Done.')
                @runButton.text('Run').off('click').one('click', => @renderer.run())
            else
                @mainStatus.removeClass('running').find('div').text('Paused.')
                @runButton.text('Resume').off('click').one('click', => @renderer.resume())

    _globalLayoutChangedCb: (factory) =>
        if @renderer
            running = @renderer.globalLayout and @renderer.globalLayout.isRunning()
            @renderer.setGlobalLayout(@_getGlobalLayout())
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
            if running
                @renderer.runGlobal()
            return

    _domainLayoutChangedCb: (factory, domain) =>
        if @renderer
            @renderer.stopPartition(domain.id)
            layout = @_getDomainLayout(domain)
            running = @renderer.allLayoutsRunning()
            @renderer.setPartitionLayout(domain.id, layout)
            if running
                later(10, => @renderer.runPartition(domain.id))
            return

    activate: (@viewer) ->
        if not @renderer
            @renderer = new PartitionedGraphRenderer(@viewer.model, @viewer)
            @renderer.setGlobalLayout(@_getGlobalLayout())

            @domains = []
            @viewer.model.domains.iter((domainModel, i) =>
                domain = @setupDomain(domainModel, i)
                @renderer.setPartitionLayout(i, @_getDomainLayout(domain))
                @domains.push(domain)
            )
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
        else
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)

        @domains.iter((domain, i) =>
            domain.element.find('a.settings').before(domain.actions)
            settings = domain.element.find('.pop-out')
            tab = makeSettingsTab(settings, "layout-settings-#{i}", 'Layout')
            tab.append(domain.form)
            settings.tabs('refresh')
        )

        @renderer.step()
        @renderer

    deactivate: ->
        @renderer.stop()
        @domains.iter((domain, i) =>
            domain.actions.detach()
            domain.form.detach()
            removeSettingsTab(domain.element.find('.pop-out'), "layout-settings-#{i}")
        )

class ExtrudedStrategy extends Strategy
    constructor: (@domainsLayoutFactories, @nodesLayoutFactories) ->
        @domainsLayoutConfig = new LayoutConfigurator(@domainsLayoutFactories)
        @nodesLayoutConfig = new LayoutConfigurator(@nodesLayoutFactories)

        @domainsLayoutConfig.callbacks.layoutChanged.add(@_domainsLayoutChangedCb)
        @nodesLayoutConfig.callbacks.layoutChanged.add(@_nodesLayoutChangedCb)

    _domainsLayoutChangedCb: (factory) =>
        if @renderer
            @renderer.domainsLayout.stop()
            @_layoutDoneCb()
            @renderer.setDomainsLayout(@_getLayout(@domainsLayoutConfig))
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)

    _nodesLayoutChangedCb: (factory) =>
        if @renderer
            @renderer.nodesLayout.stop()
            @_layoutDoneCb()
            @renderer.setNodesLayout(@_getLayout(@nodesLayoutConfig))
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)

    _layoutStartedCb: =>
        @mainStatus.addClass('running').find('div').text('Running...')
        @runButton.text('Pause').off('click').one('click', => @renderer.pause())

    _layoutPausedCb: =>
        if not @renderer.someLayoutsRunning()
            @mainStatus.removeClass('running').find('div').text('Paused')
            @runButton.text('Resume').off('click').one('click', => @renderer.resume())

    _layoutDoneCb: =>
        if @renderer.someLayoutsPaused()
            @mainStatus.removeClass('running').find('div').text('Paused.')
            @runButton.text('Resume').off('click').one('click', => @renderer.resume())
        else if @renderer.someLayoutsRunning()
            @runButton.text('Pause').off('click').one('click', => @renderer.pause())
        else  # All done
            @mainStatus.removeClass('running').find('div').text('Done.')
            @runButton.text('Run').off('click').one('click', => @renderer.run())

    _getLayout: (config) ->
        layout = config.getLayout()
        layout.callbacks.started.add(@_layoutStartedCb)
        layout.callbacks.resumed.add(@_layoutStartedCb)
        layout.callbacks.paused.add(@_layoutPausedCb)
        layout.callbacks.done.add(@_layoutDoneCb)
        layout

    activate: (@viewer) ->
        if not @renderer
            @renderer = new ExtrudedGraphRenderer(@viewer.model, @viewer)
            @renderer.setDomainsLayout(@_getLayout(@domainsLayoutConfig))
            @renderer.setNodesLayout(@_getLayout(@nodesLayoutConfig))
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
        else
            @renderer.draw(@viewer.getCleanScene(), @viewer.camera)
        @renderer.step()
        @renderer

    deactivate: ->
        if @renderer
            @renderer.pause()

    getName: -> 'Extruded'

    getForm: ->
        @runButton = $('<button/>')
            .addClass('btn btn-primary')
            .text('Run')
            .one('click', => @renderer.run())

        menu = $('<ul/>').addClass('dropdown-menu')
        menu.append($('<li/>').append($('<a href="#"/>').text('Restart all').click(=>
            @renderer.stop()
            @renderer.run()
        )))

        dropdown = $('<div/>')
            .addClass('btn-group')
            .append(@runButton)
            .append($('<button class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>'))
            .append(menu)

        @mainStatus = $('<div/>')
            .addClass('status')
            .append($.spinner(20, 'small'))
            .append($('<div/>'))

        domainsConfig = @domainsLayoutConfig.getForm()
        $('.algorithm-select label', domainsConfig).text('Domains algorithm')

        nodesConfig = @nodesLayoutConfig.getForm()
        $('.algorithm-select label', nodesConfig).text('Nodes algorithm')

        $('<div/>').addClass('strategy-config extruded')
            .append(domainsConfig)
            .append(nodesConfig)
            .append($('<div/>')
                .addClass('form-actions')
                .append(@mainStatus)
                .append(dropdown))
