class Base64Binary
    @_keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

    @decodeArrayBuffer: (input) ->
        bytes = (input.length/4) * 3
        ab = new ArrayBuffer(bytes)
        Base64Binary.decode(input, ab)
        return ab

    @decode: (input, arrayBuffer) ->
        lkey1 = Base64Binary._keyStr.indexOf(input.charAt(input.length-1))
        lkey2 = Base64Binary._keyStr.indexOf(input.charAt(input.length-2))

        bytes = (input.length/4) * 3

        if lkey1 == 64
            bytes--

        if lkey2 == 64
            bytes--

        if (arrayBuffer)
            uarray = new Uint8Array(arrayBuffer)
        else
            uarray = new Uint8Array(bytes)

        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "")
        j = 0

        for i in [0..bytes] by 3
            enc1 = Base64Binary._keyStr.indexOf(input.charAt(j++))
            enc2 = Base64Binary._keyStr.indexOf(input.charAt(j++))
            enc3 = Base64Binary._keyStr.indexOf(input.charAt(j++))
            enc4 = Base64Binary._keyStr.indexOf(input.charAt(j++))

            chr1 = (enc1 << 2) | (enc2 >> 4)
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2)
            chr3 = ((enc3 & 3) << 6) | enc4

            uarray[i] = chr1
            if enc3 != 64
                uarray[i+1] = chr2
            if enc4 != 64
                uarray[i+2] = chr3

        return uarray

class EventDispatcher
    constructor: ->
        @_callbacks = {}

    on: (event, handler) =>
        if not @_callbacks[event]?
            @_callbacks[event] = $.Callbacks()
        @_callbacks[event].add(handler)
        @

    off: (event, handler) =>
        if @_callbacks[event]?
            @_callbacks[event].remove(handler)
        @

    fire: (event, args...) =>
        if @_callbacks[event]?
            @_callbacks[event].fire.apply(this, args)
        @


flatten = (args...) ->
    new IteratorFactory(FlattenIterator, [args])

today = ->
    d = new Date()
    "#{d.getFullYear()}-#{d.getMonth()}-#{d.getDate()}"


getColor = (x, y, w, h, pixels) ->
    pixel = (x + y * w) * 4
    color = [
        pixels.data[pixel + 0],
        pixels.data[pixel + 1],
        pixels.data[pixel + 2],
        pixels.data[pixel + 3],
    ]
    color
