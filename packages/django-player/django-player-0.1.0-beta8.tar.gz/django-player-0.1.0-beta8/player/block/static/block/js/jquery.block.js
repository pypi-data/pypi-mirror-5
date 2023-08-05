(function ($) {

    $.fn.blocktoolbar = function(toolbar_tpl, add_url, config_url, messages_dict) {
        return this.each(function() {
            var toolbar = $(this);
            toolbar.html(toolbar_tpl);
            var containers = '.blockContainer';

            var createNewBlockTrigger = function() {
                html = '<div class="newBlockTrigger">'
                html += '<a href="#" class="trigger">+</a>'
                html += '</div>'
                return html
            };

            var sendForm = function(form, place, container) {
                data = form.serialize();
                data += '&placed_at='+place;
                $.ajax({
                    dataType: 'json',
                    url: form.attr('action'),
                    data: data,
                    cache: false,
                    type: 'POST',
                    success: function(data) {
                        if (!data.success) {
                            $('#block_add').replaceWith(data.html);
                        } else {
                            container.find('.newBlockTrigger').before(data.html);
                            Shadowbox.close();
                        }
                    }
                });
            };

            var addNewBlock = function() {
                var trigger = $(this);
                var container = trigger.parent('.newBlockTrigger').parent('.blockContainer');
                var place = container.find('input.blockPlace').val();
                $.ajax({
                    dataType: 'json',
                    url: add_url,
                    cache: false,
                    success: function(data) {
                        Shadowbox.open({
                            content:    data.html,
                            type:       "html",
                            title:      messages_dict.form_title,
                            height:     300,
                            width:      700,
                            options: {
                                onFinish: function() {
                                    $('#block-add-form #id_block_path').trigger("change");
                                }
                            }
                        });
                        $('#block-add-form').live("submit", function(event) {
                            event.preventDefault();
                            sendForm($(this), place, container);
                            return false;
                        });
                        $('#block-add-form #id_block_path').live("change", function() {
                            $.ajax({
                                dataType: 'html',
                                url: config_url,
                                cache: false,
                                data: {'block_path': $(this).val()},
                                success: function(data) {
                                    $('label[for="id_config_0"]').parents('tr').eq(0).replaceWith(data);
                                }
                            });
                            return false;
                        });
                    }
                });
                return false;
            };

            var active_block = function() {
                $(containers).each(function() {
                    $(this).data('background-color', $(this).css('background-color'));
                    $(this).css('background-color', '#ffaaaa');
                    $(this).append(createNewBlockTrigger());
                });
                $('.newBlockTrigger a.trigger').click(addNewBlock);
            };

            var disable_block = function() {
                $(containers).each(function() {
                    $(this).css('background-color', $(this).data('background-color'));
                    $(this).find('.newBlockTrigger').remove();
                });    
            };

            $("span.hightlightBlock").click(function(){
                $(this).toggleClass("active");
                if ($(this).hasClass("active")) {
                    active_block();
                }
                else {
                    disable_block();
                }
                return false;
            });

        });
    };
})(jQuery);
