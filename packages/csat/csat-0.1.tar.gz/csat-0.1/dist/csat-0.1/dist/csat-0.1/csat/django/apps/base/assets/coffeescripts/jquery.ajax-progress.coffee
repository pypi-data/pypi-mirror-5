(($) ->
    oldXHR = $.ajaxSettings.xhr
    $.ajaxSettings.xhr = ->
        xhr = oldXHR()
        if (xhr instanceof window.XMLHttpRequest)
            xhr.addEventListener('progress', this.progress, false)
        if (xhr.upload)
            xhr.upload.addEventListener('progress', this.progress, false)
        return xhr
)(jQuery)
