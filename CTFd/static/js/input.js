(function() {
    // trim polyfill : https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/Trim
    if (!String.prototype.trim) {
        (function() {
            // Make sure we trim BOM and NBSP
            var rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
            String.prototype.trim = function() {
                return this.replace(rtrim, '');
            };
        })();
    }
    [].slice.call( document.querySelectorAll( 'input.input-field' ) ).forEach( function( inputEl ) {
        // in case the input is already filled..
        if( inputEl.value.trim() !== '' ) {
            classie.add( inputEl.parentNode, 'input--filled' );
            classie.add( inputEl.nextElementSibling, 'input--hide' );
            $label = $(inputEl).siblings(".input-label");
            $label.removeClass("input--hide");
            $label.css({
                "transform": "translate3d(0, 0, 0)"
            });
        }
    } );
})();

$(".input-field").bind({
    focus: function() {
        $(this).parent().addClass('input--filled' );
        $label = $(this).siblings(".input-label");
        //$label.addClass('input--hide' );
        $label.css({
            "transform": "translate3d(0, 10%, 0)"
        });
    },
    blur: function() {
        if ($(this).val() === '') {
            $(this).parent().removeClass('input--filled' );
            $label = $(this).siblings(".input-label");
            $label.removeClass('input--hide' );
            $label.css({
                "transform": "translate3d(0, 150%, 0)"
            });
        }
    }
});
