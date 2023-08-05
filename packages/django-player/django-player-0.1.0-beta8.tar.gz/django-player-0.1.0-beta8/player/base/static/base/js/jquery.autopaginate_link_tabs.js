(function ($) {
   $(document).ready(function() {
     var tab = "#" + $("#paginate-tab").text();
     $.map($("div.pagelements a"), function(elem) {
        var elem_href = $(elem).attr("href");
        $(elem).attr("href", elem_href + tab);
     });
   });
})(jQuery);