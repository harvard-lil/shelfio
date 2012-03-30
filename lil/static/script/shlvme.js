(function($) {
	$(function() {
		var $b = $('body');
		/*
		   /shlvme/:user/:shelf

		   Show item information on item click in shelf.
		*/
		$b.delegate('#active-stack .stack-item a', 'click', function(e) {
			var data = $(this).closest('.stack-item').data('stackviewItem');
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
						alert('Deleted!')
					}
				}
			})
			e.preventDefault();
		});

	});
})(jQuery);