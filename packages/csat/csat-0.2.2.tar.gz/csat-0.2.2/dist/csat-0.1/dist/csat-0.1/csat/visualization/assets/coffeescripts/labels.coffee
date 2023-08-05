$ ->
    scene = new THREE.Scene()
    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000)

    container = $('#playground')
    renderer = new THREE.WebGLRenderer()
    renderer.setSize(500, 500)
    #renderer.setClearColor(0x000000)
    container.append(renderer.domElement)

    sphere = new THREE.Mesh(
        new THREE.SphereGeometry(1, 10, 10),
        new THREE.MeshBasicMaterial({
            color: 0xcc0000
        })
    )
    #sphere.overdraw = true
    scene.add(sphere)

    camera.position.z = 5
    camera.lookAt(scene.position)

    animate = ->
        requestAnimationFrame(animate)
        renderer.render(scene, camera)
        return
    animate()
    return
