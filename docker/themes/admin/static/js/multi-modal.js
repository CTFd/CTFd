(function($, window) {
    'use strict';

    var MultiModal = function(element) {
        this.$element = $(element);
    };

    MultiModal.BASE_ZINDEX = 1040;

    MultiModal.prototype.show = function(target) {
        var that = this;
        var $target = $(target);
        var modalCount = $('.modal:visible').length;

        $target.css('z-index', MultiModal.BASE_ZINDEX + (modalCount * 20) + 10);

        window.setTimeout(function() {
            var modalCount = $('.modal:visible').length;
            if(modalCount > 0)
                $('.modal-backdrop').not(':first').addClass('hidden');

            that.adjustBackdrop(modalCount);
        });
    };

    MultiModal.prototype.hidden = function(target) {
        var modalCount = $('.modal:visible').length;

        var $target = $(target);

        if(modalCount) {
           this.adjustBackdrop(modalCount - 1);
            $('body').addClass('modal-open');
        }
    };

    MultiModal.prototype.adjustBackdrop = function(modalCount) {
        $('.modal-backdrop:first').css('z-index', MultiModal.BASE_ZINDEX + ((modalCount)* 20));
    };

    function Plugin(method, target) {
        return this.each(function() {
            var $this = $(this);
            var data = $this.data('multi-modal-plugin');

            if(!data)
                $this.data('multi-modal-plugin', (data = new MultiModal(this)));

            if(method)
                data[method](target);
        });
    }

    $.fn.multiModal = Plugin;
    $.fn.multiModal.Constructor = MultiModal;

    $(document).on('show.bs.modal', function(e) {
        $(document).multiModal('show', e.target);
    });

    $(document).on('hidden.bs.modal', function(e) {
        $(document).multiModal('hidden', e.target);
    });
}(jQuery, window));
