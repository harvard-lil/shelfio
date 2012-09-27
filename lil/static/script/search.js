var q = '',
page = 1;
type = 'item';

$(function () { 

  getParameters();

  var searchUrl = "http://hlsl7.law.harvard.edu:8000/api/search/" + type + "/?limit=10&q=";

  $('#q').val(q);
  $('#type').val(type);
  $.get(searchUrl + q + "&start=0", function(data) {
		showResults(data, q);
	});

  $('.prev, .next').live('click', function(event) {
		var start = $(this).attr('data-start');
		if(start >= 0) {
      $.get(searchUrl + q + "&start=" + start, function(data) {
        showResults(data, q);
        $('.prev').attr('data-start', start*1 - 10);
        $('.next').attr('data-start', start*1 + 10);
      });
	  }
		event.preventDefault();
	});
});

function showResults(data, q){ 
  $('#search-results').html('');
  if(data.num_found === 0)
    $('#search-results').append((tmpl(templates.empty, { q: q })));
  $.each(data.docs, function(key, value) { 
    $('#search-results').append((tmpl(templates[type], value)));
  });
  $("#search-results p, h4").highlight(q);
}

function getParameters(){
  var vars = [], hash;

  var hashes = window.location.href.slice(jQuery.inArray('?', window.location.href) + 1).split('&');

  // create array for each key
  for(var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split('=');
    vars[hash[0]] = [];
  }

  // populate newly created entries with values 
  for(var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split('=');
    if (hash[1]) {
      vars[hash[0]].push(decodeURIComponent(hash[1].replace(/\+/g, '%20')));
    }
  }

	q = vars.q;
	page = vars.page;
	type = vars.type;
}

(function(undefined) {
	templates = {
		item: '\
			<div class="result-shelf">\
			  <img class="result-thumb">\
			  <div class="result-shelf-details">\
			    <h4><a href="/<%= shelf %>"><%= shelf %></a></h4>\
			    <p>7 items | Created by annie</p>\
			    <p>contains <%= title %></p>\
			  </div>\
			</div>',
			
			user: '\
			<div class="result-shelf">\
			  <img class="result-thumb">\
			  <div class="result-shelf-details">\
			    <h4><a href="/<%= username %>"><%= username %></a></h4>\
			    <p>7 shelves</p>\
			  </div>\
			</div>',
		
		  empty: '<p class="">No results found for "<%= q %>"</p>'
	}
})();