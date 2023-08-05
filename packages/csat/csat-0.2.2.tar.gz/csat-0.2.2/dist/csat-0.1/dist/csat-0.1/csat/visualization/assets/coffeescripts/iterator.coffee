class StopIteration extends Error


Object.defineProperty(Object.prototype, 'iter', {
    value: (cb) ->
        iterator = this.__iterator__()
        i = 0
        while true
            try
                cb(iterator.next(), i)
                i += 1
            catch e
                if e == StopIteration
                    break
                else
                    throw e
        return
    enumerable: false
})


Object.defineProperty(String.prototype, 'endswith', {
    value: (suffix) ->
        @indexOf(suffix, @length - suffix.length) != -1
    enumerable: false
})


class IteratorFactory
    constructor: (@iteratorClass, @arguments) ->
    __iterator__: ->
        construct = (iterClass, args) ->
            iterClass.apply(this, args)
        construct.prototype = @iteratorClass.prototype
        return new construct(@iteratorClass, @arguments)


class ArrayIterator
    constructor: (@array) ->
        @index = 0

    next: ->
        if @index >= @array.length
            throw StopIteration
        else
            return @array[@index++]


Object.defineProperty(Array.prototype, '__iterator__', {
    value: ->
        new ArrayIterator(this)
    enumerable: false
})


class ArrayPropertyIterator
    constructor: (@array, @property) ->
        @itemIndex = 0
        @subitemIndex = 0

    next: ->
        while @itemIndex < @array.length
            subitems = @array[@itemIndex][@property]
            if @subitemIndex >= subitems.length
                @itemIndex += 1
                @subitemIndex = 0
            else
                return subitems[@subitemIndex++]
        throw StopIteration


class FlattenIterator
    constructor: (@iterators) ->
        @currentIteratorIndex = 0

    next: ->
        while true
            if @currentIteratorIndex >= @iterators.length
                throw StopIteration
            if not @currentIterator
                @currentIterator = @iterators[@currentIteratorIndex].__iterator__()
            try
                return @currentIterator.next()
            catch e
                if e == StopIteration
                    @currentIteratorIndex++
                    @currentIterator = undefined
                    continue
                else
                    throw e
