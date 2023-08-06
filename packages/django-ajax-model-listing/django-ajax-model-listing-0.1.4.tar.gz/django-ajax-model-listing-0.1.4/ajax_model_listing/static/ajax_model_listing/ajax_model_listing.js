(function($) {
    
    reload_django_ajax_model_listing = function(container, page){
        container = $(container);
        var settings = container.data('django_ajax_model_listing_settings');
        
        settings.beforeLoad();
            
        var ajax_data = {
            page: page || $(container).find('table.ajax_list>tfoot .current_page').val() || 1 // if no page was passed, reloads the current page
        };
        
        // sorting
        var selected_order = $(container).find('table.ajax_list>thead>tr>th.active_sort');
        if (selected_order.length){
            var order = selected_order.data('order-field');
            if (selected_order.hasClass('ajax_list_sorter_desc'))
                order = '-' + order;
            ajax_data['order_by'] = order;
        }
            
        ajax_data = $.param(ajax_data);
        
        if (settings.filter_form)
            ajax_data += '&' + $(settings.filter_form).serialize();
        
        $.ajax({
            url: settings.list_url,
            method: 'get',
            cache: false,
            data: ajax_data,
            dataType: 'html',
            success: function(data, textStatus, jqXHR){
                $(container).html(data);
                settings.successLoad(data, textStatus, jqXHR);
            },
            error: function(jqXHR, textStatus, errorThrow){
                $(container).html('<b>Error loading list.</b>');
                $(container).append('<br/><b>Error type:&nbsp;</b><span>' + textStatus + '</span>');
                if (errorThrow)
                    $(container).append('<br/><b>Error:&nbsp;</b><span>' + errorThrow + '</span>');
                settings.errorLoad(jqXHR, textStatus, errorThrow);
            },
            complete: function(jqXHR, textStatus){
                settings.completeLoad(jqXHR, textStatus);
            }
        });
    };
    
    $.fn.django_ajax_model_listing = function(options) {
        var settings = $.extend({
            list_url: null,
            beforeLoad: function(){},
            successLoad: function(data, textStatus, jqXHR){},
            errorLoad: function(jqXHR, textStatus, errorThrow){},
            completeLoad: function(jqXHR, textStatus){},
            filter_form: '',
            filter_button: ''
        }, options );
        
        var container = this;
        container.data('django_ajax_model_listing_settings', settings);
        
        // FILTER BUTTON
        if (settings.filter_button){
            $(document).on('click', settings.filter_button, function(event){
                reload_django_ajax_model_listing(container);
            });
        }
        
        // SORTING
        $(container).on('click', 'table.ajax_list>thead>tr>th.ajax_list_sorter', function(event){
            var th = $(this);
            var cls_asc = 'ajax_list_sorter_asc', cls_desc = 'ajax_list_sorter_desc', cls_active = 'active_sort';
            
            $('table.ajax_list>thead>tr>th.ajax_list_sorter').not(th).removeClass(cls_asc+' '+cls_desc+' '+cls_active);
            
            if ( !(th.hasClass(cls_asc) || th.hasClass(cls_desc)) ){ // no sort -> asc
                th.addClass(cls_asc+' '+cls_active);
            }
            else if (th.hasClass(cls_asc)){ // asc -> desc
                th.removeClass(cls_asc);
                th.addClass(cls_desc+' '+cls_active);
            }
            else if (th.hasClass(cls_desc)){ // desc -> asc
                th.removeClass(cls_desc);
                th.addClass(cls_asc+' '+cls_active);
            }
            reload_django_ajax_model_listing(container, 1);
        });
        
        // PAGINATION
        $(container).on('click', 'table.ajax_list>tfoot .ajax_list_page', function(event){
            event.preventDefault();
            var page = $(this).data('page-number');
            reload_django_ajax_model_listing(container, page);
        });
        
        reload_django_ajax_model_listing(container);
        
        return this;
    };

}(jQuery));