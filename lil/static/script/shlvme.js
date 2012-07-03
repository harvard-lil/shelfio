var BASE_URL = '/shlvme/';

(function($) {
	$(function() {
		var $b = $('body');
		/*
		   /shlvme/:user/:shelf

		   Show item information on item click in shelf.
		*/
		$b.delegate('#active-stack .stack-item a', 'click', function(e) {
			var $item = $(this).closest('.stack-item');
			populateItemDetails($item);
			e.preventDefault();
		});
		
		/*
		   /shlvme/:user/:shelf

		   Show first item in right panel upon load.
		*/
		$b.on('stackview.pageload', '.stackview', function(e) {
      var $item = $(this).find('.stack-item:first');
      populateItemDetails($item);
		});
		
		function populateItemDetails($item) {
		  var data = $item.data('stackviewItem');
			$('#active-stack .active-item').removeClass('active-item');
			$item.addClass('active-item');
			$('#active-item').html(tmpl($('#item-details').html(), data));
			bindConfirmations('#active-item');
		}
		
		/*
		   /shlvme/:user/:shelf

		   Show embed code
		*/
		$b.delegate('a.embed', 'click', function(e) {
			$('.share textarea').slideToggle().select();
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
						$('#active-item').empty();
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
			if (!$('#active-stack').length) return;
			var $si = $(this).find('.stack-items'),
			    startIndex, endIndex;

			$si.sortable({
				containment: 'parent',

				start: function(event, ui) {
					$si.css('overflow-x', 'hidden');
					startIndex = $si.children().index(ui.item);
					console.log(startIndex);
				},

				stop: function(event, ui) {
					$si.css('overflow-x', 'auto');
				},

				update: function(event, ui) {
					var $item = $(ui.item),
					    uuid = $item.data('stackviewItem').item_uuid;

					$si.sortable('disable');
					endIndex = $si.children().index(ui.item);

					if (endIndex < startIndex) {
						$item.data('stackviewItem').sort_order = $item.next().data('stackviewItem').sort_order;
						$item.nextUntil($si.children()[startIndex]).add($si.children()[startIndex]).each(function() {
							$(this).data('stackviewItem').sort_order--
						});
					}
					else {
						$item.data('stackviewItem').sort_order = $item.prev().data('stackviewItem').sort_order;
						$item.prevUntil($si.children()[startIndex]).add($si.children()[startIndex]).each(function() {
							$(this).data('stackviewItem').sort_order++
						});
					}

					$.post(BASE_URL + 'api/item/' + uuid + '/reorder/', {
						'sort_order': $item.data('stackviewItem').sort_order
					}, function() {
						$si.sortable('enable');
					});

					$('#active-stack').stackView('zIndex');
				}
			});

			$si.disableSelection();
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
		function bindConfirmations(context) {
			$(context).find('[data-confirm-message]').bind('click.confirmer', function(e) {
				var $this= $(this),
				    $confirmation = $(tmpl($('#confirm-modal').html(), {
				    	type: $this.data('confirm-type'),
				    	accept: $this.data('confirm-accept'),
				    	reject: $this.data('confirm-reject'),
				    	message: $this.data('confirm-message')
				    }));

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
		}
		bindConfirmations('body');

		/*
		   Global

		   Flash message dismissal.
		*/
		$b.delegate('.flash-messages > li', 'click', function(e) {
			var $this = $(this);
			$this.animate({ 'top': '-48px' }, 500, function() {
				$this.remove();
			});
			e.preventDefault();
		});

		// A little helper for reducing flashes during page loads with CSS.
		$('html').addClass('ready');
	});
})(jQuery);