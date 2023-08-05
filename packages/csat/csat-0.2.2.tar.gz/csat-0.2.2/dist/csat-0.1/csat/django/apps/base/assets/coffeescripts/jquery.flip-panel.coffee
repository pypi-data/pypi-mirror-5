# Keep this in sync with the SASS variable
DIALOGS_ANIMATION_DURATION = 700

(($) ->
    $.fn.twostepsShow = (cb) ->
        this.addClass('active')
        show = =>
            this.addClass('visible')
        setTimeout(show, 0)
        if cb?
            invoke = =>
                cb.apply(this)
            setTimeout(invoke, DIALOGS_ANIMATION_DURATION)
        return this

    $.fn.twostepsHide = (cb) ->
        this.removeClass('visible')
        hide = =>
            this.removeClass('active')
            if cb?
                cb.apply(this)
        setTimeout(hide, DIALOGS_ANIMATION_DURATION)
        return this

    $.fn.modalGet = ->
        modal = $('body > .modal-background')
        if not modal.size()
            modal = $('<div/>').addClass('modal-background').appendTo($('body'))
        return modal

    $.fn.modalShow = ->
        modal = this.modalGet()
        return modal.twostepsShow()

    $.fn.modalHide = (cb)->
        return this.modalGet().twostepsHide(cb)

    $.fn.scrollingLock = ->
        [scrollTop, scrollLeft] = [this.scrollTop(), this.scrollLeft()]
        this
            .data({
                'scroll-position-top': scrollTop,
                'scroll-position-left': scrollLeft,
                'previous-overflow': this.css('overflow'),
            })
            .css('overflow', 'hidden')
            .scrollTop(scrollTop)
            .scrollLeft(scrollLeft)

    $.fn.scrollingUnlock = ->
        this
            .css('overflow', this.data('previous-overflow'))
            .scrollTop(this.data('scroll-position-top'))
            .scrollLeft(this.data('scroll-position-left'))

    $.fn.flipPanelOpen = ->
        $('html').scrollingLock()

        # Current size and position
        cw = this.outerWidth()
        ch = this.outerHeight()
        ct = this.offset().top
        cl = this.offset().left

        # Flipped panel size and position
        ow = Math.min(
            this.data('width')
            $(window).width() - 40
        )
        oh = Math.min(
            this.data('height'),
            $(window).height() - 40
        )
        ot = ($(window).height() - oh) / 2 + $('body').scrollTop()
        ol = ($(window).width() - ow) / 2 + $('body').scrollLeft()

        # Make a placeholder to put in place of the
        # flipped panel. Use the same element type
        # as the flipped panel.
        $("<#{this.get(0).tagName}/>")
            .addClass('flip-panel-placeholder')
            .width(cw).height(ch)
            .css({
                'display': 'block',
            })
                .insertAfter(this)

        # Create the style rules dynamically in order
        # to exploit CSS transitions
        style = $("""
            <style>
                .flip-panel.closed {
                    width: #{cw}px;
                    height: #{ch}px;
                    top: #{ct}px;
                    left: #{cl}px;
                }
                    .flip-panel.open {
                        width: #{ow}px;
                    height: #{oh}px;
                    top: #{ot}px;
                    left: #{ol}px;
                }
            </style>
                """).appendTo(this)

        this.modalShow()
        this.addClass('closed')

        # Set the other styles asynchronously in
        # order to display the transition animation
        open = =>
            this.addClass('open visible').removeClass('closed')
        setTimeout(open, 0)

        return this

    $.fn.flipPanelClose = ->
        $('html').scrollingUnlock()
        this.removeClass('open').addClass('closed')
        this.modalHide(=>
            this.removeClass('visible closed')
            this.find('style').remove()
            this.next('.flip-panel-placeholder').remove()
        )

        return this

    $.fn.flipPanel = (settings = {}) ->
        # TODO: Accept/fire open/close callbacks
        this.data(settings)
)(jQuery)
