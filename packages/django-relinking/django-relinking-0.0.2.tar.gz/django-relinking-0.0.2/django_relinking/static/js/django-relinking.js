var _$;
if(typeof(django) != "undefined" && typeof(django.jQuery) != "undefined"){
    _$ = django.jQuery;
} else if(typeof($) != "undefind"){
    _$ = $;
}


_$(document).ready(function(e){
    _$("#id_content_type").change(function(e){
        _$.ajax({
            url: _$("#id_content_type").attr("get_objects_url"),
            data: {
                csrfmiddlewaretoken: _$("#link_form input[name='csrfmiddlewaretoken']").val(),
                content_type: _$("#id_content_type").val()
            },
            type: "POST",
            success: function(data){
                _$("#id_object_pk option").remove();
                for(var key in data){
                    _$("#id_object_pk").append(_$(
                        ["<option value='", key, "'>", data[key], "</option>"].join("")
                    ));
                }
                if(data[-1]){
                    _$("#id_object_pk").attr("disabled", "disabled");
                } else {
                    _$("#id_object_pk").removeAttr("disabled");
                }
            },
            error: function(data){
                _$("#id_object_pk option").remove();
            }
        });
    });
    _$("#id_direct_link").change(function(e){
        if(_$(this).val().length > 0){
            _$("#id_target").val(1);
        } else {
            _$("#id_target").val(0);
        }
    });
});