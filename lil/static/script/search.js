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
  else {
    $('#search-results').append((tmpl(templates.results, data)));
    $.each(data.docs, function(key, value) { 
      var author = value.creator && value.creator.length ? value.creator[0] : '';
		
      if(/^([^,]*)/.test(author)) {
        author = author.match(/^[^,]*/);
      }
      value.author = author;
      if(!value.notes)
        value.notes = "";
      else
        value.notes = '"' + value.notes + '"';
      $('#search-results').append((tmpl(templates[type], value)));
    });
    $("#search-results p, h4").highlight(q);
  }
  if (data.start + data.limit < data.num_found) {
			$('.next').show();
		} else {
			$('.next').hide();
		}

		if (data.start - data.limit >= 0) {
			$('.prev').show();
		} else {
		  $('.prev').hide();
		}
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
			  <div class="result-shelf-details">\
			    <h4><a href="/<%= shelf %>"><%= shelf %></a></h4>\
			    <p class="result-shelf-data"><small><%= num_items_on_shelf %> items | Created by <a href="/<%= username %>"><%= username %></a></small></p>\
			    </div>\
			  <div class="result-item-details">\
			    <p><strong><%= title %></strong> <small>published <%= pub_date %></small></p>\
			    <p class="result-author"><small><%= author %></small></p>\
			    <p><%= notes %></p>\
			  </div>\
			</div>',
			
			user: '\
			<div class="result-shelf">\
			  <a href="/<%= username %>"><img class="result-thumb" src="http://www.gravatar.com/avatar/<%= gravatar_hash %>?s=256&d=mm" alt="<%= username %>"></a>\
			  <div class="result-shelf-details">\
			    <h4><a href="/<%= username %>"><%= username %></a></h4>\
			    <p><%= num_public_shelves %> shelves</p>\
			  </div>\
			</div>',
		
		  empty: '<p>No results found for "<%= q %>"</p>',
		  
		  results: '<h4><%= num_found %> results</h4>'
	}
})();