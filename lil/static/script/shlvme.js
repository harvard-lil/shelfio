var BASE_URL = '/shlvme/';

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

		   Delete an item. Requires confirmation first.
		*/
		$b.delegate('a.delete-item.confirmed', 'click', function(e) {
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

		/*
		   /shlvme/:user

		   Show/hide edit profile form
		*/
		var $editProfileLinks = $('a[href="#edit-profile"]'),
		    $editProfile = $('#edit-profile');

		$editProfileLinks.click(function(e) {
			$editProfileLinks.addClass('hidden');
			$editProfile.removeClass('form-hidden');
			e.preventDefault();
		});

		/*
		   /shlvme/:user

		   Edit shelf modal
		*/
		$b.delegate('.edit-shelf', 'click', function(e) {
			var $this = $(this),
			    uuid = $this.closest('.shelf-overview').data('uuid'),
			    template = $('#edit-shelf').html();

			$this.addClass('loading');

			$.getJSON(BASE_URL + 'api/shelf/' + uuid + '/', function(data) {
				$(tmpl(template, data)).appendTo('body').dialog({
					modal:true,
					resizable:false,
					draggable:false
				});

				$('#cancel-edit').click(function(event) {
					$(this).closest('form').dialog('destroy').remove();
					event.preventDefault();
				});
			});

			e.preventDefault();
		});

		/*
		   Global

		   Static modal activations.
		*/
		$('.modal').each(function(i, el) {
			var $modal = $(el),
			    $links = $('a[href="#' + $modal.attr('id') + '"]'),
			    $closers = $modal.find('.modal-close');

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

			if ($modal.find('.errorlist').length) {
				$modal.dialog('open');
			}
		});

		/*
		   Global

		   Declarative confirmation modal.
		*/
		$('[data-confirm-message]').bind('click.confirmer', function(e) {
			var $this= $(this),
			    $confirmation = $(tmpl($('#confirm-modal').html(), {
			    	type: $this.data('confirm-type'),
			    	accept: $this.data('confirm-accept'),
			    	reject: $this.data('confirm-reject'),
			    	message: $this.data('confirm-message')
			    }));

			console.log('clicked');
			$confirmation.delegate('.confirm-reject', 'click', function(e) {
				$confirmation.dialog('destroy').remove();
				e.preventDefault();
			}).delegate('.confirm-accept', 'click', function(e) {
				$this.unbind('click.confirmer').addClass('confirmed');
				$confirmation.dialog('close');
				$this.click();
				e.preventDefault();
			});

			$confirmation.dialog({
				modal:true,
				resizable:false,
				draggable:false
			});

			e.preventDefault();
		});

		// A little helper for reducing flashes during page loads with CSS.
		$('html').addClass('ready');
	});
})(jQuery);