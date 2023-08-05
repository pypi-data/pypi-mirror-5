class Viewport
    ###
    An area of the renderer element which can be drawn independently. Uses
    the same global scene with independent cameras.
    ###
    constructor: (params) ->
        {@x, @y, @width, @height, @camera, @controls} = params

    prepareScene: (scene) ->
        @camera.lookAt(scene.position)

    getFov: (domHeight) =>
        if not @camera._ratio?
            height = Math.tan(@camera.fov / 2) * @camera.position.z * 2
            @camera._ratio = height / domHeight

        Math.atan(
            (domHeight * @camera._ratio) / (2 * @camera.position.z)
        ) * 2 / Math.PI * 180

    prepareRenderer: (renderer, width, height) ->
        fov = @getFov(height)

        x = Math.floor(width * this.x)
        y = Math.floor(height * this.y)
        w = Math.floor(width * this.width)
        h = Math.floor(height * this.height)
        @camera.aspect = w / h
        @camera.fov = fov
        renderer.setViewport(x, y, w, h)
        renderer.setScissor(x, y, w, h)
        renderer.enableScissorTest(true)


class RotatingViewport extends Viewport
    constructor: (params) ->
        {@radius, @speed, @axis} = params
        this.phi = 0
        super

    prepareRenderer: (renderer) ->
        #renderer.setClearColor(new THREE.Color(0xffffcc))
        super

    prepareScene: (scene) ->
        this.phi += this.speed

        if @axis == 'x'
            this.camera.position.x = this.radius * Math.sin(this.phi * Math.PI / 360)
            this.camera.position.z = this.radius * Math.cos(this.phi * Math.PI / 360)
        else if @axis == 'z'
            this.camera.position.y = this.radius * Math.sin(this.phi * Math.PI / 360)
            this.camera.position.z = this.radius * Math.cos(this.phi * Math.PI / 360)
        else if @axis == 'y'
            this.camera.rotation.x = this.phi
        super(scene)


class MultipleViewportsRenderer
    constructor: (@container, @scene, @viewports, @stats) ->
        @renderer = new THREE.WebGLRenderer({
            antialias: true,
            preserveDrawingBuffer: true
        })
        @renderer.setClearColor(0xffffff, 1)
        @container.append(this.renderer.domElement)

        @initialWidth = this.container.width()
        @initialHeight = this.container.height()
        @renderer.setSize(@initialWidth, @initialHeight)

    render: ->
        [width, height] = [this.container.width(), this.container.height()]

        @renderer.setSize(width, height)
        #@renderer.setViewport(-@initialWidth/2, -@initialHeight/2, @initialWidth, @initialHeight)

        width *= window.devicePixelRatio
        height *= window.devicePixelRatio

        for viewport in @viewports
            viewport.prepareScene(@scene)
            viewport.prepareRenderer(@renderer, width, height)
            viewport.camera.updateProjectionMatrix()
            @renderer.render(@scene, viewport.camera)

    animate: ->
        animate = =>
            requestAnimationFrame(animate)
            this.render()
            @stats.update()
        animate()
