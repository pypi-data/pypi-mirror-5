
AJAX_LIST_DEFAULT_VALUES = {
    beforeLoad: function(){},
    successLoad: function(data, textStatus, jqXHR){},
    errorLoad: function(jqXHR, textStatus, errorThrow){},
    completeLoad: function(jqXHR, textStatus){},
    filter_form_id: '',
    filter_button_id: ''
};


init_ajax_list = function(container, list_url, opts){
    container = '#' + container;
    
    var config = $.extend({}, AJAX_LIST_DEFAULT_VALUES, opts);
    
    var load_list = function(page){
        config.beforeLoad();
        
        var ajax_data = {
            page: page || $(container).find('table.ajax_list>tfoot .current_page').val() // if no page was passed, reloads the current page
        };
        
        // sorting
        var selected_order = $(container).find('table.ajax_list>thead span.sort_list.active').data('order-field');
        if (selected_order)
            ajax_data['order_by'] = selected_order;
            
        ajax_data = $.param(ajax_data);
        
        if (config.filter_form_id)
            ajax_data += '&' + $('#' + config.filter_form_id).serialize();
        
        $.ajax({
            url: list_url,
            method: 'get',
            cache: false,
            data: ajax_data,
            dataType: 'html',
            success: function(data, textStatus, jqXHR){
                $(container).html(data);
                config.successLoad(data, textStatus, jqXHR);
            },
            error: function(jqXHR, textStatus, errorThrow){
                $(container).html('<b>Error loading list.</b>');
                $(container).append('<br/><b>Error type:&nbsp;</b><span>' + textStatus + '</span>');
                if (errorThrow)
                    $(container).append('<br/><b>Error:&nbsp;</b><span>' + errorThrow + '</span>');
                config.errorLoad(jqXHR, textStatus, errorThrow);
            },
            complete: function(jqXHR, textStatus){
                config.completeLoad(jqXHR, textStatus);
            }
        });
    };
    load_list();
    
    $(container).on('click', 'table.ajax_list>thead span.sort_list:not(.active)', function(event){
        $(container).find('table.ajax_list>thead span.sort_list').removeClass('active');
        $(this).addClass('active');
        load_list();
    });
    
    $(container).on('click', 'table.ajax_list>tfoot span.ajax_list_page', function(event){
        var page = $(this).data('page-number');
        load_list(page);
    });
    
    if (config.filter_form_id && config.filter_button_id){
        $(document).on('click', '#' + config.filter_button_id, function(event){
            load_list(1);
        });
    }
};
