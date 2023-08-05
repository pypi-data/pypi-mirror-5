
# {{{ jQuery plugins
(($) ->
	$.getGraph = (url) ->
		$.ajax(
			url: url,
			datatType: 'xml',
			progress: (e) ->
				if (e.lengthComputable)
					pct = (e.loaded / e.total)
					console.log(pct)
				else
					console.warn('Content Length not reported!')
			success: (data) ->
				console.log 'Data received, constructing graph'
				model = GraphModel.fromGraphML(data)
				console.log 'Done.'
				view = new GraphModelView(model)
				layout = new RandomLayout()
				console.log 'Initializing renderer'
				renderer = new GraphRenderer(view, layout)
				viewportsRenderer = new MultipleViewportsRenderer(
					$('#viewport'),
					renderer.createScene(),
					[
						new RotatingViewport({
							x: 0,
							y: 0,
							width: 1,
							height: 1,
							radius: 90,
							speed: .5,
							axis: 'x',
							camera: new THREE.PerspectiveCamera(
								1000,
								1,
								0.1,
								1000
							)
						}),
					]
				)
				console.log 'Starting layout'
				renderer.runLayout()

				console.log 'Running animation'
				viewportsRenderer.animate()
		)
)(jQuery)
# }}}


# {{ On load handler
(($) ->
	$ ->
		if $('#viewport.scene').size()
			$.getGraph($.urlParam('url'))
)(jQuery)
# }}}
