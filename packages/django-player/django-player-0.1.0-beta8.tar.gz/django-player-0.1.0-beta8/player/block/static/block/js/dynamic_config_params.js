(function ($) {
    var config_content = '';
    var update_block_config = function() {
        var selected_block = $("#id_block_path").val()
        if (selected_block != "") {
            var container = $(".configField");
            $.ajax({
                url: '/manage/block/ajax/config_by_path/' + selected_block,
                success: function(data) {
                    if (data != "") {
                        container.html(data);
                    } else {
                        container.html(config_content);
                    }
                }
            });
        } else {
            container.html(config_content);
        }
    }

    $(document).ready(function () {
        $("#id_block_path").change(function(){
            update_block_config();
        });
    });
}(jQuery));