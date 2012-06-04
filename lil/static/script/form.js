$(function () { 
  buildItem();
      
  $('form p input').on('change', function() {
    buildItem();
  });
  
  $('#customize').on('click', function(e) {
    $('#customizations').slideToggle();
    e.preventDefault();
  });
      
  $( "#shelfrank-slider" ).slider({
    value: $('#id_shelfrank').val(),
    min: 0,
    max: 100,
    step: 1,
    slide: function( event, ui ) {
        //Its setting the slider value to the element with id "amount"
        $( "#id_shelfrank" ).val( ui.value );
        buildItem();
    }
  });
      
	function buildItem() {
    var docs = {};
		docs.title = $('#id_title').val();
		docs.book_thickness = get_thickness($('#id_measurement_page_numeric').val());
		docs.book_height = get_height($('#id_measurement_height_numeric').val());
		docs.heat = get_heat($('#id_shelfrank').val());
		docs.year = $('#id_pub_date').val();
		docs.link = $('#id_link').val();
		docs.author = $('#id_creator').val();
		var results = document.getElementById("preview-item");
		results.innerHTML = tmpl("item_tmpl", docs);
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
        min = 20,
        max = 39,
		    multiple = 12;
    
    if (isNaN(height)) {
      height = min;
    }
    height = Math.min(Math.max(height, min), max) * multiple;
    return height + 'px';
	}
	    
	function get_heat (scaled_value) {
		return scaled_value === 100 ? 10 : Math.floor(scaled_value / 10) + 1;
	}
      
});