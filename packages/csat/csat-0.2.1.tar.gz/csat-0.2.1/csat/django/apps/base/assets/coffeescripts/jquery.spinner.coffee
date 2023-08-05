(($) ->
    $.spinner = (ticks=50, class_='') ->
        spinner = $('<span/>').addClass("spinner #{class_}")
        for i in [0...ticks]
            $('<span/>').appendTo(spinner)
        return spinner
)(jQuery)
