# Keep this in sync with the SASS variable
DIALOGS_ANIMATION_DURATION = 700

(($) ->
    $.fn.flipBoxFlip = ->
        this.toggleClass('flipped')
    $.fn.flipBoxOpen = ->
        this.addClass('flipped')
    $.fn.flipBoxClose = ->
        this.removeClass('flipped')
)(jQuery)
