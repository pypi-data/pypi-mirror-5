setup = (container) ->
	[width, height] = [container.width(), container.height()]

	i = 0

	width /= 2
	height /= 2

	scene = new THREE.Scene()
	camera = new THREE.PerspectiveCamera(
		80,
		width / height,
		0.1,
		1000
	)
	camera2 = new THREE.OrthographicCamera(
		-width/20,
		width/20,
		height/20,
		-height/20,
		0.1,
		1000
	)

	controls = new THREE.OrbitControls(camera)

	renderer = new THREE.WebGLRenderer()
	renderer.setSize(width*2, height*2)
	renderer.setClearColor(new THREE.Color(0xffffcc))
	renderer.setViewport(width, 0, width, height)
	renderer.setScissor(width, 0, width, height)
	renderer.enableScissorTest(true)
	container.append(renderer.domElement)

	light = new THREE.PointLight(0xffffff)
	light.position.set(50, 50, 50)
	scene.add(light)

	light = new THREE.PointLight(0xffffff)
	light.position.set(-50, -50, 50)
	scene.add(light)

	return [scene, camera, renderer, controls]

generateNodes = (n) ->
	material = new THREE.MeshNormalMaterial()
	group = new THREE.Object3D()

	minSize = 0.1
	maxSize = 1
	domains = 3
	domainSpread = 10
	domainDistance = 30
	radius = 40
	maxDegree = 3

	nodes = []
	for i in [0...domains]
		nodes[i] = []

	for i in [0...n]
		size = Math.random() * (maxSize - minSize) + minSize
		resolution = Math.floor(Math.sqrt(size) * 10)
		domain = Math.floor(Math.random() * domains)
		offset = Math.random() * domainSpread - domainSpread/2
		posz = domain * domainDistance - (domains-1)/2 * domainDistance + offset
		angle = Math.random() * 360
		distance = Math.sqrt(Math.random()) * radius
		posx = Math.sin(angle) * distance
		posy = Math.cos(angle) * distance

		geometry = new THREE.SphereGeometry(size, resolution, resolution, false)
		mesh = new THREE.Mesh(geometry, material)

		mesh.position.x = posx
		mesh.position.z = posy
		mesh.position.y = posz

		mesh.rotation.x = Math.random()
		mesh.rotation.y = Math.random()

		mesh.matrixAutoUpdate = false
		mesh.updateMatrix()
		group.add(mesh)

		nodes[domain].push(mesh)

	makeEdge = (src, dst) ->
		edge_seg = new THREE.Geometry(5)
		edge_seg.vertices.push(src.position)
		edge_seg.vertices.push(dst.position)
		new THREE.Line(
			edge_seg,
			new THREE.LineBasicMaterial({
				color: Math.random() * 0xffffff,
				opacity: .8,
				linewidth: 2,
			})
		)

	for domain in nodes
		for src in domain
			for j in [0...maxDegree]
				prob = Math.random()
				if prob < .25
					# Inside connection
					dst = domain[Math.floor(Math.random() * domain.length)]
					if dst == src
						continue
					group.add(makeEdge(src, dst))
				else if prob < .29
					# Outside connection
					otherdomain_i = Math.floor(Math.random() * domains)
					otherdomain = nodes[otherdomain_i]
					dst = otherdomain[Math.floor(Math.random() * otherdomain.length)]
					if dst == src
						continue
					group.add(makeEdge(src, dst))
				else
					continue

	return group

$ ->
	$('.scene-3d').each(->
		[scene, camera, renderer] = setup($(this))

		mouseX = 0
		mouseY = 0
		width = $('.scene').width()
		height = $('.scene').height()

		nodes = generateNodes(200)
		scene.add(nodes)

		geometry = new THREE.CubeGeometry(10,10,10)
		material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } )
		cube = new THREE.Mesh( geometry, material )
		#scene.add( cube )

		camera.position.z = 90

		$('body').mousemove((e) ->
			mouseX = event.pageX - width/2
			mouseY = event.pageY - height/2
		)

		animate = ->
			requestAnimationFrame(animate)
			render()

		render = ->
			#camera.position.z += (mouseX * 0.1 - camera.position.z)
			camera.position.y += (mouseY * 0.2 - camera.position.y) * .06
			nodes.rotation.y += 0.005
			camera.lookAt(scene.position)
			renderer.render(scene, camera)

		animate()
	)


class Node
	constructor: (@model, @id) ->
		this.data = {}
		this.position = new THREE.Vector3(0, 0, 0)
		this._force = new THREE.Vector3(0, 0, 0)

	getMesh: ->
		if not this.mesh?
			size = .4
			radius = 40
			resolution = Math.floor(Math.sqrt(size) * 8)
			material = new THREE.MeshLambertMaterial({
				color: 0xffffff * Math.random()
			})
			geometry = new THREE.SphereGeometry(size, resolution, resolution, false)

			vertexMesh = new THREE.Mesh(geometry, material)

			vertexMesh.position.x = this.position.x
			vertexMesh.position.z = this.position.z
			vertexMesh.position.y = this.position.y

			vertexMesh.matrixAutoUpdate = true
			#mesh.updateMatrix()
			this.vertexMesh = vertexMesh
			this.forceMesh = new THREE.ArrowHelper(
				this._force.normalize(),
				this.position,
				this._force.length() * .5,
				material.color,
			)

			this.mesh = new THREE.Object3D()
			#this.mesh.add(this.forceMesh)
			this.mesh.add(this.vertexMesh)
		return this.mesh

	updateMesh: ->
		mesh = this.getMesh()
		mesh.position.x = this.position.x
		mesh.position.z = this.position.z
		mesh.position.y = this.position.y

		this.forceMesh.setLength(this._force.length() * 0.2)
		this.forceMesh.setDirection(this._force.normalize())


class Edge
	constructor: (@model, @id, @src, @dst) ->
		this.data = {}

	getMesh: ->
		if not this.mesh?
			seg = new THREE.Geometry(5)
			seg.vertices.push(this.src.getMesh().position)
			seg.vertices.push(this.dst.getMesh().position)
			this.mesh = new THREE.Line(
				seg,
				new THREE.LineBasicMaterial({
					color: 0,
					opacity: .5,
					linewidth: 1,
				})
			)
		return this.mesh

	updateMesh: ->
		mesh = this.getMesh()
		mesh.geometry.vertices[0] = this.src.getMesh().position
		mesh.geometry.vertices[1] = this.dst.getMesh().position
		mesh.geometry.verticesNeedUpdate = true


class GraphModel
	@fromGraphML: (data) ->
		xml = $(data)
		graph = new GraphModel()
		id_map = {}
		$('node', xml).each((i) ->
			id = $(this).attr('id')
			node = graph.addNode()
			id_map[id] = node
			node.data['id'] = id
		)
		$('edge', xml).each((i) ->
			edge = $(this)
			graph.addEdge(id_map[edge.attr('source')], id_map[edge.attr('target')])
		)
		return graph

	constructor: ->
		this.nextNodeId = 0
		this.nextEdgeId = 0
		this.nodes = []
		this.edges = []

	addNode: ->
		n = new Node(this, this.nextNodeId)
		this.nextNodeId += 1
		this.nodes.push(n)
		return n

	addEdge: (src, dst) ->
		e = new Edge(this, this.nextEdgeId, src, dst)
		this.nextEdgeId += 1
		this.edges.push(e)
		return e

	getNodes: ->
		return this.nodes

	getEdges: ->
		return this.edges

class GraphModelView
	"""
	Applies filters to the linked GraphModel
	"""
	constructor: (@model) ->

	getNodes: ->
		return this.model.getNodes()

	getEdges: ->
		return this.model.getEdges()


class Layout
	construct: ->
		this.d3 = true

	run: (@view, callback) ->
		this._stop = false
		this.start()

		runstep = =>
			console.log 'tick'
			this._calculateForces()
			this._applyPositions()
			callback()

		run = =>
			runstep()
			if not this._stop
				setTimeout(run, 1)
		run()

	stop: ->
		this._stop = true


class FruchtermanReingoldLayout extends Layout
	start: (@view) ->

	layout: ->

class RandomLayout extends Layout
	start: ->
		for v in this.view.getNodes()
			v.position = new THREE.Vector3(
				(Math.random()-0.5) * 50,
				(Math.random()-0.5) * 50,
				(Math.random()-0.5) * 50,
			)
		this.temperature = 8.0
		this.initialTemperature = this.temperature
		this.iterations = 1000
		this.currentIteration = this.iterations

	_calculateForces: ->
		k = 5

		f_r = (d) ->
			-k * k / d

		f_a = (d) ->
			d * d / k

		for v in this.view.getNodes()
			v._force = new THREE.Vector3(0, 0, 0)
			for u in this.view.getNodes()
				if u == v
					continue
				d = v.position.clone().sub(u.position)
				f = f_r(d.length())
				v._force.sub(d.normalize().multiplyScalar(f))

		for e in this.view.getEdges()
			[u, v] = [e.src, e.dst]
			d = v.position.clone().sub(u.position)
			f = f_a(d.length()) * 2
			f = d.normalize().multiplyScalar(f)
			v._force.sub(f)
			u._force.add(f)

	_applyPositions: ->
		for v in this.view.getNodes()
			d = Math.min(v._force.length(), this.temperature)
			p = v.position.clone().add(v._force.normalize().multiplyScalar(d))

			# Spherical container
			radius = 60
			if p.lengthSq() > radius * radius
				p.setLength(radius)

			# Cubic container
			#[width, height, depth] = [50, 50, 50]
			#p.x = Math.min(width/2, Math.max(-width/2, p.x))
			#p.y = Math.min(height/2, Math.max(-height/2, p.y))
			#p.z = Math.min(depth/2, Math.max(-depth/2, p.z))

			v.position = p
		this._updateTemperature()

	_updateTemperature: ->
		this.currentIteration -= 1

		A = (this.initialTemperature / Math.pow(this.iterations, 15))

		temp = (iter) ->
			A * Math.pow(iter, 15) + .05

		this.temperature = temp(this.currentIteration)
		#console.log this.temperature
		if this.currentIteration <= 0
			this.stop()

	layout: () ->
		this._calculateForces()
		this._applyPositions()

	stop: ->
		this._stop = true


class GraphRenderer
	constructor: (@modelView, @layout) ->
		this.nodeViews = []

	createScene: ->
		this.scene = new THREE.Scene()

		light = new THREE.DirectionalLight(0xffffff)
		light.position.set(200, 200, 0)
		this.scene.add(light)

		light = new THREE.DirectionalLight(0xffffff)
		light.position.set(-200, -200, 0)
		this.scene.add(light)

		this.drawGraph()

		return this.scene

	drawGraph: () ->
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

		cubeGeometry = new THREE.CubeGeometry(50, 50, 50 )
		sphereGeometry = new THREE.SphereGeometry(60, 20, 20)

		dashMaterial = new THREE.LineBasicMaterial({
			color: 0x000000,
			opacity: .3,
			dashSize: .2,
			gapSize: 1,
		})
		lambertMaterial = new THREE.MeshLambertMaterial({
			color: 0xffffff * Math.random(),
		})
		wireframe = new THREE.Line( geo2line(sphereGeometry), dashMaterial, THREE.LinePieces )
		sphere = new THREE.Mesh(sphereGeometry, lambertMaterial)
		wireframe.position.set(0, 0, 0)
		sphere.position.set(0, 0, 0)
		#this.scene.add(wireframe)

		nodes = new THREE.Object3D()

		for node in this.modelView.getNodes()
			nodes.add(node.getMesh())

		edges = new THREE.Object3D(edges)

		for edge in this.modelView.getEdges()
			edges.add(edge.getMesh())

		this.scene.add(nodes)
		this.scene.add(edges)

	runLayout: ->
		this.layout.run(this.modelView, =>
			for node in this.modelView.getNodes()
				node.updateMesh()
			for edge in this.modelView.getEdges()
				edge.updateMesh()
		)

$ ->
	scene = $('#scene0')

	if scene.size() == 0
		return

	order = 100

	model = new GraphModel()
	for i in [0..order]
		next = model.addNode()
		if prev?
			model.addEdge(prev, next)
		prev = next
	model.addEdge(prev, model.getNodes()[0])

	nodes = model.getNodes()

	for i in [0..20]
		src = Math.round(Math.random() * order)
		dst = Math.round(Math.random() * order)
		console.log src, dst
		model.addEdge(nodes[src], nodes[dst])

	view = new GraphModelView(model)
	layout = new RandomLayout()

	renderer = new GraphRenderer(view, layout)

	viewportsRenderer = new MultipleViewportsRenderer(
		scene,
		renderer.createScene(),
		[
			new Viewport({
				x: 0,
				y: 0,
				width: .3,
				height: .5,
				camera: new THREE.PerspectiveCamera(
					1000,
					1,
					0.1,
					1000
				)
			}),
			new Viewport({
				x: 0,
				y: .5,
				width: .3,
				height: .5,
				camera: new THREE.PerspectiveCamera(
					1000,
					1,
					0.1,
					1000
				)
			}),
			new RotatingViewport({
				x: .3,
				y: 0,
				width: .7,
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
			})

		]
	)

	renderer.runLayout()
	viewportsRenderer.animate()
