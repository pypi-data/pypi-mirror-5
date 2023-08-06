(function($) {

	if (typeof($.ZBlog) == 'undefined') {
		$.ZBlog = {};
	}

	/**
	 * ZBlog tree view management
	 */
	$.ZBlog.treeview = {

		init: function(parent) {
			$('TABLE.treeview TR.section TD.title, TABLE.treeview TR.topic TD.title', parent).draggable({
				helper: 'clone',
				opacity: .75,
				revert: 'invalid',
				revertDuration: 300,
				scroll: true,
				containment: 'TABLE.treeview'
			});
			$('TABLE.treeview TR.site', parent).droppable({
				accept: 'TR.section TD.title',
				hoverClass: 'accept',
				over: function(event,ui) {
					if(this.id != $(ui.draggable.parents("TR")[0]).id && !$(this).is(".expanded")) {
						$(this).expand();
					}
				},
				drop: $.ZTFY.treeview.changeParent
			});
			$('TABLE.treeview TR.section', parent).droppable({
				accept: 'TR.section TD.title, TR.topic TD.title',
				hoverClass: 'accept',
				over: function(event,ui) {
					if(this.id != $(ui.draggable.parents("TR")[0]).id && !$(this).is(".expanded")) {
						$(this).expand();
					}
				},
				drop: $.ZTFY.treeview.changeParent
			});
		}

	}  /** $.ZBlog.treeview */

	/**
	 * Topics management
	 */
	$.ZBlog.topic = {

		remove: function(form) {
			$.ZTFY.ajax.post($(form).attr('action') + '/@@ajax/ajaxDelete', {}, $.ZBlog.topic.removeCallback, null, 'json');
			return false;
		},

		removeCallback: function(result, status) {
			if (status == 'success') {
				window.location = result.url;
			}
		}

	}  /** $.ZBlog.topic */

})(jQuery);