(function ($) {
    $.fn.GenericDelete = function() {
        return this.each(function () {
            var container = $(this).parent();
            var form = container.find('.remove-form');
            var confirm_message = form.find('.confirm-message');
            var delete_ok = form.find('.delete-ok').html();
            var delete_cancel = form.find('.delete-cancel').html();
            var trigger = $(this);

            var askDelete = function() {
                var deleteFunction = function() {
                    form.submit();
                    $(this).dialog("close");
                };
                var cancelFunction = function() {
                    $(this).dialog("close");
                };
                eval("var buttons ={'" + delete_ok +"': deleteFunction, '" + delete_cancel + "': cancelFunction}");
                confirm_message.dialog({
                    width: 460,
                    modal: true,
                    buttons: buttons
                });
                return false;
            };

            var bindTriggers = function() {
                trigger.click(askDelete);
            };

            var initGenericDelete = function() {
                bindTriggers();
            };

            initGenericDelete();
        });

    };

    $(document).ready(function () {
        $('.remove-trigger').GenericDelete();
    });

})(jQuery);
