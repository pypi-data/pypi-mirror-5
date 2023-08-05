String.prototype.hashCode = ->
	hash = 0

	if this.length == 0
		return hash

	for i in [0...this.length]
		char = this.charCodeAt(i)
		hash = ((hash << 5) - hash) + char
		hash = hash & hash

	return hash


(($)->
	$.extend({
		websocket: (url, s, protocols) ->
			if protocols
				if window['MozWebSocket']
					ws = new MozWebSocket(url, protocols)
				else if window['WebSocket']
					ws = new WebSocket(url, protocols)
			else
				if window['MozWebSocket']
					ws = new MozWebSocket(url)
				else if window['WebSocket']
					ws = new WebSocket(url)

			settings = {
				open: (->
					return
				)
				close: (->
					return
				)
				message: (->
					return
				)
				options: {}
				events: {}
				callbacks: {}
			}

			$.extend(settings, $.websocketSettings, s)

			if ws
				callbacks = {}
				req_id = 0
				$(ws)
					.bind('open', settings.open)
					.bind('close', settings.close)
					.bind('message', settings.message)
					.bind('message', (e) ->
						# For simplicty we assume that every message we receive
						# is complete. We check it, though.
						pattern = /^(\d+):(.*),$/
						message = e.originalEvent.data
						match = pattern.exec(message)
						
						length = parseInt(match[1])
						jsonstr = match[2]

						if length != jsonstr.length
							console.err "Wrong length"
							return

						message = JSON.parse(jsonstr)
						
						# Error result
						if message.hasOwnProperty('error')
							console.error "Error #{message.id} received"
							cb = callbacks[message.id]
							delete callbacks[message.id]
							cb.reject(
								message.error.code,
								message.error.message,
								message.error.data)

						# Function call result
						if message.hasOwnProperty('result')
							cb = callbacks[message.id]
							delete callbacks[message.id]
							cb.resolve(message.result)

						# Function invocation
						if message.hasOwnProperty('method') and message.hasOwnProperty('id')
							console.error "Method invocations are not supported yet"

						# Notification
						if message.hasOwnProperty('method') and not message.hasOwnProperty('id')
							callback = settings.events[message.method]
							if callback?
								callback.call(this, message.params...)
					)
				ws._send = ws.send
				ws.send = (type, data) ->
					m = {
						type: type
					}
					m = $.extend(true, m, $.extend(true, {}, settings.options, m))
					if data
						m['data'] = data
					this._send(JSON.stringify(m))
				ws.call = (func, args...) ->
					m = {
						'method': func,
						'params': args,
						'id': req_id,
					}
					jsonstring = JSON.stringify(m)
					netstring = "#{jsonstring.length}:#{jsonstring},"
					cb = $.Deferred()
					callbacks[req_id] = cb
					req_id += 1
					this._send(netstring)
					return cb.promise()
				ws.callback = (func) ->
					name = '_callback_' + (func.toString().hashCode() + Math.pow(2, 31) - 1 + Math.random())
					settings.events[name] = func
					return name
				$(window).unload(->
					ws.close()
					ws = null
				)
			return ws
	})
)(jQuery)
