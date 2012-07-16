$(function () { 
  buildItem();
  
  var shelf = decodeURI((RegExp('shelf=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]);
  if(shelf != 'null') {
    $('#shelf-select option:contains("' + shelf + '")').prop('selected', true);
    $('#customizations').show();
  }
  
  if ($(".errorlist").length > 0) {
    $('#customizations').show();
  }
    
  
  $('form p input').on('propertychange keyup input paste', function() {
    buildItem();
  });
  
  $('form p select').on('change', function() {
    buildItem();
  });
  
  $('#customize').on('click', function(e) {
    $('#customizations').slideToggle();
    e.preventDefault();
  });
      
  $( "#shelfrank-slider" ).slider({
    value: $('#id_shelfrank').val(),
    min: 0,
    max: 99,
    step: 1,
    slide: function( event, ui ) {
        $( "#id_shelfrank" ).val( ui.value );
        buildItem();
    }
  });
  
  /*$('select#valueA').selectToUISlider({
				labels: 10,
				sliderOptions: {
					stop: function(event) { 
					  var val = $('select#valueA').attr('value');
						$( "#id_shelfrank" ).val(val);
						buildItem();
					} 
				}
			});*/
      
	function buildItem() {
	  var format = $('#id_format').val();
	  $('#book-fields').show();
	  if(format != 'book')
	    $('#book-fields').hide();
    var docs = {};
    var template = format + '_tmpl';
    template = template.toLowerCase().replace("/", "").replace(" ", "");
		docs.title = $('#id_title').val();
		docs.book_thickness = get_thickness($('#id_measurement_page_numeric').val());
		docs.book_height = get_height($('#id_measurement_height_numeric').val());
		docs.heat = get_heat($('#id_shelfrank').val());
		docs.year = $('#id_pub_date').val();
		docs.link = $('#id_link').val();
		docs.author = $('#id_creator').val();
		var results = document.getElementById("preview-item");
		results.innerHTML = tmpl(template, docs);
		$('.stackview').css('height',docs.book_thickness);
	}
			
	function get_thickness (measurement_page_numeric) {
		var thickness = parseInt(measurement_page_numeric, 10),
		min = 200,
		max = 540,
		multiple = 0.20;

    if (isNaN(thickness)) {
      thickness = min;
    }
    thickness = Math.min(Math.max(thickness, min), max) * multiple;
    return thickness + 'px';
  }
      
  function get_height (measurement_height_numeric) {
    var height = parseInt(measurement_height_numeric, 10),
        min = 25,
        max = 35,
		    multiple = 13;
    
    if (isNaN(height)) {
      height = min;
    }
    height = Math.min(Math.max(height, min), max) * multiple;
    return height + 'px';
	}
	    
	function get_heat (scaled_value) {
		return scaled_value === 100 ? 10 : Math.floor(scaled_value / 10) + 1;
	}
	
			/*
		   Global

		   Static modal activations.
		*/
		$('.modal').each(function(i, el) {
			var $modal = $(el),
			    $links = $('a[href="#' + $modal.attr('id') + '"]'),
			    $closers = $modal.find('.modal-close');
			    $submit = $modal.find('.modal-submit');

			$modal.dialog({
				autoOpen:false,
				modal:true,
				resizable:false,
				draggable:false
			});

			$links.click(function(e) {
				$modal.dialog('open');
				e.preventDefault();
			});

			$closers.click(function(e) {
				$modal.dialog('close');
				e.preventDefault();
			});
			
			$submit.click(function(e) {
				
				var is_private = false;
				if($('#id_is_private:checked').val() == 'private') {
					is_private = true;
				}
				
				$.ajax({
					url: '/api/shelf/',
					type: 'POST',
					data: {
						'name': $('#new_shelf_option').val(),
						'description': $('#id_description').val(),
						'is_private': is_private,
					},
					statusCode: {
						201: function(data) {
							$('#id_shelf').append(new Option($('#new_shelf_option').val(), data.shelf_id, true, true));
							
						}
					}
				})
				
				$modal.dialog('close');
				
				/*$("#id_shelf option[value='new']").remove();
				$('#id_shelf').append(new Option($('#new_shelf_option').val(), 'new', true, true));
				$('#id_new_shelf_name').val($('#new_shelf_option').val());
				$('#id_new_shelf_description').val($('#id_description').val());
				$('#id_new_shelf_is_private').val('');*/
				
				e.preventDefault();
			});

			if ($modal.find('.errorlist').length) {
				$modal.dialog('open');
			}
		});
		
		$('input[name=name]').on('propertychange keyup input paste', function() {
		// Show the user what the url of the shelfname will be
		var shelfname = $(this).val()
		var slugged_shelfname = shelfname.replace(/\s+/g,'-').replace(/[^a-zA-Z0-9\-]/g,'').toLowerCase();
    	$(this).prev().html('http://shlv.me/' + $('.icon-user').html() + '/' + slugged_shelfname);
 	});
      
});