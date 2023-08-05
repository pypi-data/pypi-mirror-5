(function ($) {
    $.fn.CollectionFields = function() {
        return this.each(function () {
            var container = $(this);
            var table = container.find('table.CollectionFieldsTable');
            var add_trigger = container.find('a.CollectionFieldsAddTrigger');
            var counter = container.find('#id_fields-TOTAL_FORMS');
            var sample_tr = null;

            var getSampleRow = function() {
                var tr = table.find('tr').eq(1).clone();
                tr.find('input').each(function() { $(this).val(''); });
                tr.find('.errorlist').remove();
                return tr;
            };

            var addNewField = function() {
                new_tr = sample_tr.clone();
                var count = parseInt(counter.val());
                new_tr.find('input,select').each(function(i, item) {
                    name_array = $(item).attr('name').split('-');
                    $(item).attr('name', name_array[0] + '-' + count + '-' + name_array[2]);
                });
                table.append(new_tr);
                counter.val(count+1);
                return false;
            };

            var bindTriggers = function() {
                add_trigger.click(addNewField);
            };

            var initCollection = function() {
                sample_tr = getSampleRow();
                bindTriggers();
            };

            initCollection();
        });

    };

    $(document).ready(function () {
        $('.CollectionFields').CollectionFields();
    });

})(jQuery);
