(function($) {
	
	$.fn.initialStars = function(inputType, handler_path, disabled, starWidth, extra_success) {
		$(this).each(function(){
		    var options = {
		    	inputType: inputType, //"select",
			    split: 2,
			    cancelShow: false,
			    callback: function(ui, type, value) {
			        $.get(handler_path, {'score': value}, function(data)
			          {	
			        	if (extra_success) extra_success(data);
			          });
			    }
            };
		    if (starWidth) options['starWidth'] = starWidth;
		    if (disabled) options['disabled'] = true;
	    
		    $(this).stars(options);
		    //$(this).stars("selectID", avarage-1);
		    
		});
	};

})(jQuery);
