$(".input-field").bind({
    focus: function() {
        $(this).parent().addClass('input--filled' );
        $label = $(this).siblings(".input-label");
    },
    blur: function() {
        if ($(this).val() === '') {
            $(this).parent().removeClass('input--filled' );
            $label = $(this).siblings(".input-label");
            $label.removeClass('input--hide' );
        }
    }
});



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
            $(inputEl.parentNode).addClass('input--filled');
            $(inputEl.nextElementSibling).addClass('input--filled');
            $label = $(inputEl).siblings(".input-label");
            $label.removeClass("input--hide");
        }
    } );
})();