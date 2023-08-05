var Edge, FruchtermanReingoldLayout, GraphModel, GraphModelView, GraphRenderer, Layout, Node, RandomLayout, generateNodes, setup,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

(function($) {
  return $.getGraph = function(url) {
    return $.ajax({
      url: url,
      datatType: 'xml',
      progress: function(e) {
        var pct;
        if (e.lengthComputable) {
          pct = e.loaded / e.total;
          return console.log(pct);
        } else {
          return console.warn('Content Length not reported!');
        }
      },
      success: function(data) {
        var layout, model, renderer, view, viewportsRenderer;
        console.log('Data received, constructing graph');
        model = GraphModel.fromGraphML(data);
        console.log('Done.');
        view = new GraphModelView(model);
        layout = new RandomLayout();
        console.log('Initializing renderer');
        renderer = new GraphRenderer(view, layout);
        viewportsRenderer = new MultipleViewportsRenderer($('#viewport'), renderer.createScene(), [
          new RotatingViewport({
            x: 0,
            y: 0,
            width: 1,
            height: 1,
            radius: 90,
            speed: .5,
            axis: 'x',
            camera: new THREE.PerspectiveCamera(1000, 1, 0.1, 1000)
          })
        ]);
        console.log('Starting layout');
        renderer.runLayout();
        console.log('Running animation');
        return viewportsRenderer.animate();
      }
    });
  };
})(jQuery);

(function($) {
  return $(function() {
    if ($('#viewport.scene').size()) {
      return $.getGraph($.urlParam('url'));
    }
  });
})(jQuery);

setup = function(container) {
  var camera, camera2, controls, height, i, light, renderer, scene, width, _ref;
  _ref = [container.width(), container.height()], width = _ref[0], height = _ref[1];
  i = 0;
  width /= 2;
  height /= 2;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(80, width / height, 0.1, 1000);
  camera2 = new THREE.OrthographicCamera(-width / 20, width / 20, height / 20, -height / 20, 0.1, 1000);
  controls = new THREE.OrbitControls(camera);
  renderer = new THREE.WebGLRenderer();
  renderer.setSize(width * 2, height * 2);
  renderer.setClearColor(new THREE.Color(0xffffcc));
  renderer.setViewport(width, 0, width, height);
  renderer.setScissor(width, 0, width, height);
  renderer.enableScissorTest(true);
  container.append(renderer.domElement);
  light = new THREE.PointLight(0xffffff);
  light.position.set(50, 50, 50);
  scene.add(light);
  light = new THREE.PointLight(0xffffff);
  light.position.set(-50, -50, 50);
  scene.add(light);
  return [scene, camera, renderer, controls];
};

generateNodes = function(n) {
  var angle, distance, domain, domainDistance, domainSpread, domains, dst, geometry, group, i, j, makeEdge, material, maxDegree, maxSize, mesh, minSize, nodes, offset, otherdomain, otherdomain_i, posx, posy, posz, prob, radius, resolution, size, src, _i, _j, _k, _l, _len, _len1, _m;
  material = new THREE.MeshNormalMaterial();
  group = new THREE.Object3D();
  minSize = 0.1;
  maxSize = 1;
  domains = 3;
  domainSpread = 10;
  domainDistance = 30;
  radius = 40;
  maxDegree = 3;
  nodes = [];
  for (i = _i = 0; 0 <= domains ? _i < domains : _i > domains; i = 0 <= domains ? ++_i : --_i) {
    nodes[i] = [];
  }
  for (i = _j = 0; 0 <= n ? _j < n : _j > n; i = 0 <= n ? ++_j : --_j) {
    size = Math.random() * (maxSize - minSize) + minSize;
    resolution = Math.floor(Math.sqrt(size) * 10);
    domain = Math.floor(Math.random() * domains);
    offset = Math.random() * domainSpread - domainSpread / 2;
    posz = domain * domainDistance - (domains - 1) / 2 * domainDistance + offset;
    angle = Math.random() * 360;
    distance = Math.sqrt(Math.random()) * radius;
    posx = Math.sin(angle) * distance;
    posy = Math.cos(angle) * distance;
    geometry = new THREE.SphereGeometry(size, resolution, resolution, false);
    mesh = new THREE.Mesh(geometry, material);
    mesh.position.x = posx;
    mesh.position.z = posy;
    mesh.position.y = posz;
    mesh.rotation.x = Math.random();
    mesh.rotation.y = Math.random();
    mesh.matrixAutoUpdate = false;
    mesh.updateMatrix();
    group.add(mesh);
    nodes[domain].push(mesh);
  }
  makeEdge = function(src, dst) {
    var edge_seg;
    edge_seg = new THREE.Geometry(5);
    edge_seg.vertices.push(src.position);
    edge_seg.vertices.push(dst.position);
    return new THREE.Line(edge_seg, new THREE.LineBasicMaterial({
      color: Math.random() * 0xffffff,
      opacity: .8,
      linewidth: 2
    }));
  };
  for (_k = 0, _len = nodes.length; _k < _len; _k++) {
    domain = nodes[_k];
    for (_l = 0, _len1 = domain.length; _l < _len1; _l++) {
      src = domain[_l];
      for (j = _m = 0; 0 <= maxDegree ? _m < maxDegree : _m > maxDegree; j = 0 <= maxDegree ? ++_m : --_m) {
        prob = Math.random();
        if (prob < .25) {
          dst = domain[Math.floor(Math.random() * domain.length)];
          if (dst === src) {
            continue;
          }
          group.add(makeEdge(src, dst));
        } else if (prob < .29) {
          otherdomain_i = Math.floor(Math.random() * domains);
          otherdomain = nodes[otherdomain_i];
          dst = otherdomain[Math.floor(Math.random() * otherdomain.length)];
          if (dst === src) {
            continue;
          }
          group.add(makeEdge(src, dst));
        } else {
          continue;
        }
      }
    }
  }
  return group;
};

$(function() {
  return $('.scene-3d').each(function() {
    var animate, camera, cube, geometry, height, material, mouseX, mouseY, nodes, render, renderer, scene, width, _ref;
    _ref = setup($(this)), scene = _ref[0], camera = _ref[1], renderer = _ref[2];
    mouseX = 0;
    mouseY = 0;
    width = $('.scene').width();
    height = $('.scene').height();
    nodes = generateNodes(200);
    scene.add(nodes);
    geometry = new THREE.CubeGeometry(10, 10, 10);
    material = new THREE.MeshBasicMaterial({
      color: 0x00ff00
    });
    cube = new THREE.Mesh(geometry, material);
    camera.position.z = 90;
    $('body').mousemove(function(e) {
      mouseX = event.pageX - width / 2;
      return mouseY = event.pageY - height / 2;
    });
    animate = function() {
      requestAnimationFrame(animate);
      return render();
    };
    render = function() {
      camera.position.y += (mouseY * 0.2 - camera.position.y) * .06;
      nodes.rotation.y += 0.005;
      camera.lookAt(scene.position);
      return renderer.render(scene, camera);
    };
    return animate();
  });
});

Node = (function() {

  function Node(model, id) {
    this.model = model;
    this.id = id;
    this.data = {};
    this.position = new THREE.Vector3(0, 0, 0);
    this._force = new THREE.Vector3(0, 0, 0);
  }

  Node.prototype.getMesh = function() {
    var geometry, material, radius, resolution, size, vertexMesh;
    if (!(this.mesh != null)) {
      size = .4;
      radius = 40;
      resolution = Math.floor(Math.sqrt(size) * 8);
      material = new THREE.MeshLambertMaterial({
        color: 0xffffff * Math.random()
      });
      geometry = new THREE.SphereGeometry(size, resolution, resolution, false);
      vertexMesh = new THREE.Mesh(geometry, material);
      vertexMesh.position.x = this.position.x;
      vertexMesh.position.z = this.position.z;
      vertexMesh.position.y = this.position.y;
      vertexMesh.matrixAutoUpdate = true;
      this.vertexMesh = vertexMesh;
      this.forceMesh = new THREE.ArrowHelper(this._force.normalize(), this.position, this._force.length() * .5, material.color);
      this.mesh = new THREE.Object3D();
      this.mesh.add(this.vertexMesh);
    }
    return this.mesh;
  };

  Node.prototype.updateMesh = function() {
    var mesh;
    mesh = this.getMesh();
    mesh.position.x = this.position.x;
    mesh.position.z = this.position.z;
    mesh.position.y = this.position.y;
    this.forceMesh.setLength(this._force.length() * 0.2);
    return this.forceMesh.setDirection(this._force.normalize());
  };

  return Node;

})();

Edge = (function() {

  function Edge(model, id, src, dst) {
    this.model = model;
    this.id = id;
    this.src = src;
    this.dst = dst;
    this.data = {};
  }

  Edge.prototype.getMesh = function() {
    var seg;
    if (!(this.mesh != null)) {
      seg = new THREE.Geometry(5);
      seg.vertices.push(this.src.getMesh().position);
      seg.vertices.push(this.dst.getMesh().position);
      this.mesh = new THREE.Line(seg, new THREE.LineBasicMaterial({
        color: 0,
        opacity: .5,
        linewidth: 1
      }));
    }
    return this.mesh;
  };

  Edge.prototype.updateMesh = function() {
    var mesh;
    mesh = this.getMesh();
    mesh.geometry.vertices[0] = this.src.getMesh().position;
    mesh.geometry.vertices[1] = this.dst.getMesh().position;
    return mesh.geometry.verticesNeedUpdate = true;
  };

  return Edge;

})();

GraphModel = (function() {

  GraphModel.fromGraphML = function(data) {
    var graph, id_map, xml;
    xml = $(data);
    graph = new GraphModel();
    id_map = {};
    $('node', xml).each(function(i) {
      var id, node;
      id = $(this).attr('id');
      node = graph.addNode();
      id_map[id] = node;
      return node.data['id'] = id;
    });
    $('edge', xml).each(function(i) {
      var edge;
      edge = $(this);
      return graph.addEdge(id_map[edge.attr('source')], id_map[edge.attr('target')]);
    });
    return graph;
  };

  function GraphModel() {
    this.nextNodeId = 0;
    this.nextEdgeId = 0;
    this.nodes = [];
    this.edges = [];
  }

  GraphModel.prototype.addNode = function() {
    var n;
    n = new Node(this, this.nextNodeId);
    this.nextNodeId += 1;
    this.nodes.push(n);
    return n;
  };

  GraphModel.prototype.addEdge = function(src, dst) {
    var e;
    e = new Edge(this, this.nextEdgeId, src, dst);
    this.nextEdgeId += 1;
    this.edges.push(e);
    return e;
  };

  GraphModel.prototype.getNodes = function() {
    return this.nodes;
  };

  GraphModel.prototype.getEdges = function() {
    return this.edges;
  };

  return GraphModel;

})();

GraphModelView = (function() {
  "Applies filters to the linked GraphModel";

  function GraphModelView(model) {
    this.model = model;
  }

  GraphModelView.prototype.getNodes = function() {
    return this.model.getNodes();
  };

  GraphModelView.prototype.getEdges = function() {
    return this.model.getEdges();
  };

  return GraphModelView;

})();

Layout = (function() {

  function Layout() {}

  Layout.prototype.construct = function() {
    return this.d3 = true;
  };

  Layout.prototype.run = function(view, callback) {
    var run, runstep,
      _this = this;
    this.view = view;
    this._stop = false;
    this.start();
    runstep = function() {
      console.log('tick');
      _this._calculateForces();
      _this._applyPositions();
      return callback();
    };
    run = function() {
      runstep();
      if (!_this._stop) {
        return setTimeout(run, 1);
      }
    };
    return run();
  };

  Layout.prototype.stop = function() {
    return this._stop = true;
  };

  return Layout;

})();

FruchtermanReingoldLayout = (function(_super) {

  __extends(FruchtermanReingoldLayout, _super);

  function FruchtermanReingoldLayout() {
    return FruchtermanReingoldLayout.__super__.constructor.apply(this, arguments);
  }

  FruchtermanReingoldLayout.prototype.start = function(view) {
    this.view = view;
  };

  FruchtermanReingoldLayout.prototype.layout = function() {};

  return FruchtermanReingoldLayout;

})(Layout);

RandomLayout = (function(_super) {

  __extends(RandomLayout, _super);

  function RandomLayout() {
    return RandomLayout.__super__.constructor.apply(this, arguments);
  }

  RandomLayout.prototype.start = function() {
    var v, _i, _len, _ref;
    _ref = this.view.getNodes();
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      v = _ref[_i];
      v.position = new THREE.Vector3((Math.random() - 0.5) * 50, (Math.random() - 0.5) * 50, (Math.random() - 0.5) * 50);
    }
    this.temperature = 8.0;
    this.initialTemperature = this.temperature;
    this.iterations = 1000;
    return this.currentIteration = this.iterations;
  };

  RandomLayout.prototype._calculateForces = function() {
    var d, e, f, f_a, f_r, k, u, v, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2, _ref3, _results;
    k = 5;
    f_r = function(d) {
      return -k * k / d;
    };
    f_a = function(d) {
      return d * d / k;
    };
    _ref = this.view.getNodes();
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      v = _ref[_i];
      v._force = new THREE.Vector3(0, 0, 0);
      _ref1 = this.view.getNodes();
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        u = _ref1[_j];
        if (u === v) {
          continue;
        }
        d = v.position.clone().sub(u.position);
        f = f_r(d.length());
        v._force.sub(d.normalize().multiplyScalar(f));
      }
    }
    _ref2 = this.view.getEdges();
    _results = [];
    for (_k = 0, _len2 = _ref2.length; _k < _len2; _k++) {
      e = _ref2[_k];
      _ref3 = [e.src, e.dst], u = _ref3[0], v = _ref3[1];
      d = v.position.clone().sub(u.position);
      f = f_a(d.length()) * 2;
      f = d.normalize().multiplyScalar(f);
      v._force.sub(f);
      _results.push(u._force.add(f));
    }
    return _results;
  };

  RandomLayout.prototype._applyPositions = function() {
    var d, p, radius, v, _i, _len, _ref;
    _ref = this.view.getNodes();
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      v = _ref[_i];
      d = Math.min(v._force.length(), this.temperature);
      p = v.position.clone().add(v._force.normalize().multiplyScalar(d));
      radius = 60;
      if (p.lengthSq() > radius * radius) {
        p.setLength(radius);
      }
      v.position = p;
    }
    return this._updateTemperature();
  };

  RandomLayout.prototype._updateTemperature = function() {
    var A, temp;
    this.currentIteration -= 1;
    A = this.initialTemperature / Math.pow(this.iterations, 15);
    temp = function(iter) {
      return A * Math.pow(iter, 15) + .05;
    };
    this.temperature = temp(this.currentIteration);
    if (this.currentIteration <= 0) {
      return this.stop();
    }
  };

  RandomLayout.prototype.layout = function() {
    this._calculateForces();
    return this._applyPositions();
  };

  RandomLayout.prototype.stop = function() {
    return this._stop = true;
  };

  return RandomLayout;

})(Layout);

GraphRenderer = (function() {

  function GraphRenderer(modelView, layout) {
    this.modelView = modelView;
    this.layout = layout;
    this.nodeViews = [];
  }

  GraphRenderer.prototype.createScene = function() {
    var light;
    this.scene = new THREE.Scene();
    light = new THREE.DirectionalLight(0xffffff);
    light.position.set(200, 200, 0);
    this.scene.add(light);
    light = new THREE.DirectionalLight(0xffffff);
    light.position.set(-200, -200, 0);
    this.scene.add(light);
    this.drawGraph();
    return this.scene;
  };

  GraphRenderer.prototype.drawGraph = function() {
    var cubeGeometry, dashMaterial, edge, edges, geo2line, lambertMaterial, node, nodes, sphere, sphereGeometry, wireframe, _i, _j, _len, _len1, _ref, _ref1;
    geo2line = function(geo) {
      var a, b, c, d, face, geometry, i, vertices, _i, _ref;
      geometry = new THREE.Geometry();
      vertices = geometry.vertices;
      for (i = _i = 0, _ref = geo.faces.length; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        face = geo.faces[i];
        if (face instanceof THREE.Face3) {
          a = geo.vertices[face.a].clone();
          b = geo.vertices[face.b].clone();
          c = geo.vertices[face.c].clone();
          vertices.push(a, b, b, c, c, a);
        } else if (face instanceof THREE.Face4) {
          a = geo.vertices[face.a].clone();
          b = geo.vertices[face.b].clone();
          c = geo.vertices[face.c].clone();
          d = geo.vertices[face.d].clone();
          vertices.push(a, b, b, c, c, d, d, a);
        }
      }
      geometry.computeLineDistances();
      return geometry;
    };
    cubeGeometry = new THREE.CubeGeometry(50, 50, 50);
    sphereGeometry = new THREE.SphereGeometry(60, 20, 20);
    dashMaterial = new THREE.LineBasicMaterial({
      color: 0x000000,
      opacity: .3,
      dashSize: .2,
      gapSize: 1
    });
    lambertMaterial = new THREE.MeshLambertMaterial({
      color: 0xffffff * Math.random()
    });
    wireframe = new THREE.Line(geo2line(sphereGeometry), dashMaterial, THREE.LinePieces);
    sphere = new THREE.Mesh(sphereGeometry, lambertMaterial);
    wireframe.position.set(0, 0, 0);
    sphere.position.set(0, 0, 0);
    nodes = new THREE.Object3D();
    _ref = this.modelView.getNodes();
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      node = _ref[_i];
      nodes.add(node.getMesh());
    }
    edges = new THREE.Object3D(edges);
    _ref1 = this.modelView.getEdges();
    for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
      edge = _ref1[_j];
      edges.add(edge.getMesh());
    }
    this.scene.add(nodes);
    return this.scene.add(edges);
  };

  GraphRenderer.prototype.runLayout = function() {
    var _this = this;
    return this.layout.run(this.modelView, function() {
      var edge, node, _i, _j, _len, _len1, _ref, _ref1, _results;
      _ref = _this.modelView.getNodes();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        node = _ref[_i];
        node.updateMesh();
      }
      _ref1 = _this.modelView.getEdges();
      _results = [];
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        edge = _ref1[_j];
        _results.push(edge.updateMesh());
      }
      return _results;
    });
  };

  return GraphRenderer;

})();

$(function() {
  var dst, i, layout, model, next, nodes, order, prev, renderer, scene, src, view, viewportsRenderer, _i, _j;
  scene = $('#scene0');
  if (scene.size() === 0) {
    return;
  }
  order = 100;
  model = new GraphModel();
  for (i = _i = 0; 0 <= order ? _i <= order : _i >= order; i = 0 <= order ? ++_i : --_i) {
    next = model.addNode();
    if (typeof prev !== "undefined" && prev !== null) {
      model.addEdge(prev, next);
    }
    prev = next;
  }
  model.addEdge(prev, model.getNodes()[0]);
  nodes = model.getNodes();
  for (i = _j = 0; _j <= 20; i = ++_j) {
    src = Math.round(Math.random() * order);
    dst = Math.round(Math.random() * order);
    console.log(src, dst);
    model.addEdge(nodes[src], nodes[dst]);
  }
  view = new GraphModelView(model);
  layout = new RandomLayout();
  renderer = new GraphRenderer(view, layout);
  viewportsRenderer = new MultipleViewportsRenderer(scene, renderer.createScene(), [
    new Viewport({
      x: 0,
      y: 0,
      width: .3,
      height: .5,
      camera: new THREE.PerspectiveCamera(1000, 1, 0.1, 1000)
    }), new Viewport({
      x: 0,
      y: .5,
      width: .3,
      height: .5,
      camera: new THREE.PerspectiveCamera(1000, 1, 0.1, 1000)
    }), new RotatingViewport({
      x: .3,
      y: 0,
      width: .7,
      height: 1,
      radius: 90,
      speed: .5,
      axis: 'x',
      camera: new THREE.PerspectiveCamera(1000, 1, 0.1, 1000)
    })
  ]);
  renderer.runLayout();
  return viewportsRenderer.animate();
});
