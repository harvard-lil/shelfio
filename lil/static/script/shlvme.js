(function($) {
	$(function() {
		var $b = $('body');
		/*
		   /shlvme/:user/:shelf

		   Show item information on item click in shelf.
		*/
		$b.delegate('#active-stack .stack-item a', 'click', function(e) {
			var $item = $(this).closest('.stack-item'),
			    data = $item.data('stackviewItem');

			$('#active-stack .active-item').removeClass('active-item');
			$item.addClass('active-item');
			$('#active-item').html(tmpl($('#item-details').html(), data));
			e.preventDefault();
		});

		/*
		   /shlvme/:user/:shelf

		   Delete an item.
		*/
		$b.delegate('a.delete-item', 'click', function(e) {
			var $this = $(this);

			$.ajax({
				url: $this.attr('href'),
				type: 'POST',
				data: {
					'_method': 'delete'
				},
				statusCode: {
					204: function() {
						var $num = $('#active-stack .num-found span'),
						    num = parseInt($num.html(), 10);

						$num.html(num-1);
						$('#active-stack .active-item').remove();
					}
				}
			})
			e.preventDefault();
		});

		/*
		   /shlvme/:user/:shelf

		   Sort shelf items.
		*/
		$b.delegate('.stackview', 'stackview.init', function(e) {
			$(this).find('.stack-items').sortable({
				update: function(event, ui) {
					$('#active-stack').stackView('zIndex');
				}
			});
			$(this).find('.stack-items').disableSelection();
		});
	});
})(jQuery);