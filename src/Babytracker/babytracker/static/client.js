!function( $ ){

    /* Client */

    var Alert = function ( content, options ) {
        if (options == 'close') return this.close.call(content)
        this.settings = $.extend({}, $.fn.alert.defaults, options)
        this.$element = $(content)
            .delegate(this.settings.selector, 'click', this.close)
    }

    Alert.prototype = {

        close: function (e) {
            var $element = $(this)
                , className = 'alert-message'

            $element = $element.hasClass(className) ? $element : $element.parent()

            e && e.preventDefault()
            $element.removeClass('in')

            function removeElement () {
                $element.remove()
            }

            $.support.transition && $element.hasClass('fade') ?
                $element.bind(transitionEnd, removeElement) :
                removeElement()
        }

    }


    /* ALERT PLUGIN DEFINITION
    * ======================= */

    $.fn.alert = function ( options ) {

        if ( options === true ) {
            return this.data('alert')
        }

        return this.each(function () {
            var $this = $(this)
                , data

            if ( typeof options == 'string' ) {

                data = $this.data('alert')

                if (typeof data == 'object') {
                    return data[options].call( $this )
                }

            }

            $(this).data('alert', new Alert( this, options ))

        })
    }

    $.fn.alert.defaults = {
        selector: '.close'
    }

}(window.jQuery);