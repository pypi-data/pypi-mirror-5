/*
 * Copyright 2006, John Drinkwater <john@nextraweb.com>
 * Distributed under the terms of the MIT License.
 * Please note, this script isn't as DOM friendly as I would like,
 * but IE, as always, has problems with <select> and <option>s
 * Version 1j, from
 * http://ezri.nextraweb.com/examples/js/haiku/rev1j/componentselect.js
 * Thanks to wkornew & tic
 */

/*
 * Rewritten & maintained by Niels Sascha Reedijk <niels.reedijk@gmail.com>
 * Copyright 2012.
*/

/*
 * Rewritten and maintained by Michael R.
 * Copyright 2013
 */

/* ......................................................................... */
/*
 * gTicketTypeList is presorted
 * when forceEmptyLeafs we get an empty subnode, whihc is useful when
 * doing queries that deal with "begins with this parent node"
 * forceEmptyLeafs is currently disabled
 */
function getLeafsForSubTicketTypeLevel(level, prefix, forceEmptyLeafs) {

	forceEmptyLeafs = false;

	var retVal = new Array();
	var previous = null;

	// take care of the first drop down, which has no prefix and is really
	// much simpler to handle
	if ( level == 0 ) {
		for (var i = 0; i < gTicketTypeList.length; i++) {
			var current = gTicketTypeList[i][level];

			// dedup (works only since gTicketTypeList has been presorted
			// else where)
			if (current != previous) {
				retVal.push(current);
			}
			previous = current;
		}
	}

	// now let do anything that level 1 and above which has prefix and
	// where need to matching on prefix + "/" so we can avoid mismatches
	// like "taskoo" beginning with "task"
	if ( level > 0 ) {
		var full_prefix = prefix + "/";
		for (var i = 0; i < gTicketTypeList.length; i++) {
			var full_item = gTicketTypeList[i].join("/") + "/";
			var current = gTicketTypeList[i][level];

			// let see if the full item starts with full prefix
			var test_full_prefix = full_item.substring(0, full_prefix.length);
			if ( test_full_prefix === full_prefix ) {
				// if prefix matches but the current node if undefined
				// it means that we need change it an empty string
				// this covers items like "task"
				if ( current === undefined ) {
					current = "";
				}

				// dedup (works only since gTicketTypeList has been presorted
				// else where)
				if (current != previous) {
					retVal.push(current);
				}
				previous = current;
			}
		}
	}

	// There are no entries, or the only entry is an empty leaf
	// (works only since gTicketTypeList has been presorted else where)
	if (retVal.length == 0 || ( retVal.length == 1 && retVal[0] == "" )) {
		return new Array();
	}

	// if we are forcing empty nodes in the list and its not there already
	// add an empty one
	// (works only since gTicketTypeList has been presorted else where)
	if (forceEmptyLeafs && retVal[0] != "") {
	 	retVal.unshift("")
	}

	return retVal;
}


/* ......................................................................... */
/*
	Event handler for when the user has changed the selected ticket type
 */
function selectedTicketTypeChanged (evt, forceEmptyLeafs) {

	var elem = jQuery(evt.target);
	// Get the level of select element that triggered the event
	var level = elem.prevAll('[class=subtickettype]').length + 1;

	// Hide the deeper subtickettypes (if applicable)
	elem.nextAll('[class=subtickettype]').hide();

	// Check if the current selected value is an empty leaf
	if (elem.val().length == 0) {
		var prefix = "";
		elem.prevAll('[class=subtickettype]').reverse()
			.each(
				function (index, select_elem) {
					if (prefix.length != 0) {
						prefix += "/"
					}
					prefix += jQuery(select_elem).val();
				});
		// Store the path of the previous leafs and end
		elem.parent().find("input[type=hidden]").val(prefix);
		return;
	}

	// Just store the new path if this is the 'highest' level
	if (level == gTicketTypeMaxBranches) {
		var prefix = "";
		elem.parent().find('[class=subtickettype]')
			.each(
				function (index, select_elem) {
					if (prefix.length != 0) {
						prefix += "/";
					}
					prefix += jQuery(select_elem).val();
				});

		elem.parent().find("input[type=hidden]").val(prefix);
		return;
	}

	// Empty the next selects
	elem.nextAll('[class=subtickettype]').empty();

	// Fill the next selects with the right options. Sometimes that only means
	// that the next select is filled, at other times, we have to go deeper,
	// for example when there are no empty leaves for a subtickettype.
	var prefix = "";
	elem.prevAll('[class=subtickettype]').reverse()
		.each(
			function (index, select_elem) {
				prefix += jQuery(select_elem).val();
				prefix += "/";
			});
	prefix += elem.val();

	var currentSelector = elem;
	for (var i = level; i < gTicketTypeMaxBranches; i++) {
		var items = getLeafsForSubTicketTypeLevel(i, prefix,
			evt.data.forceEmptyLeafs);

		for (var j = 0; j < items.length; j++) {
			currentSelector.next()
				.append(
					jQuery("<option/>", {value: items[j], text: items[j]}));
		}

		// If there are any entries in the select to the right, show it
		// otherwise break out of the loop as we are done
		if (items.length) {
			currentSelector.next().show();
		}
		else {
			break;
		}

		// If the next selector has an empty leaf, then we are done. Otherwise
		// go deeper
		if (items[0] == "") {
			break;
		}

		prefix += "/"
		prefix += items[0]
		currentSelector = currentSelector.next()
	}

	// Update the current selected value. The prefix string has the complete
	// path of the current selection
	elem.parent().find("input[type=hidden]").val(prefix);
}


/* ......................................................................... */
/*
	This function deletes the <select> box, replaces it with a hidden input
	box, and as many <select>s as the first/selected ticket types had parts:
	this new element has an  event that triggers on change, to add or remove
	<select> boxes
	original: the <select> field that is to be replaced
	set: support multiple ticket type fields, can leave null for autoincrement
	forceEmptyLeafs: add leafs that contain '', so users can pick super
	ticket types used in the Query
*/
function convertTicketTypeSelect(element, forceEmptyLeafs)
{
	var elem = jQuery(element);
	var parent = jQuery(element).parent();

	gTicketTypeCount++;

	// Populate the global ticket type list if it has not been populated before
	if ( gTicketTypeList.length == 0 ) {
		var i = 0;
		elem.find('option')
			.each(
				function (index, option_elem) {
					gTicketTypeList[i] = jQuery(option_elem).text().split("/");
					gTicketTypeMaxBranches =
						(gTicketTypeMaxBranches < gTicketTypeList[i].length ?
	    				gTicketTypeList[i].length : gTicketTypeMaxBranches);
					i++;
				});

		gTicketTypeList.sort(); // so Trac can be lazy
	}

	// create some replacement dropdowns
	for (var i = 1; i <= gTicketTypeMaxBranches; i++) {
		parent.append(jQuery(document.createElement('select'))
			.attr('id', 'subtickettype-selector' + gTicketTypeCount + '-' + i)
			.attr('class', 'subtickettype')
            .change(
	             // this is to accomodate jQuery 1.4.2 in trac 0.12
	             // since the .change event there does not support
	             // passing additional data
	             function (evt) {
	             	 evt.data = {forceEmptyLeafs: forceEmptyLeafs};
	                 selectedTicketTypeChanged(evt, forceEmptyLeafs)
	             }
             ));
	}

	// Store the current selected item
	var currentItems = elem.val().split("/");
	var currentSelectors = parent.find('[class=subtickettype]');
	var prefix = "";

	// Populate choice(s)
	// Note: always use currentItems.length + 1 because we want to check
	// whether there are more subselections possible

	for (var i = 0; i < currentItems.length + 1; i++) {
		var items = getLeafsForSubTicketTypeLevel(i, prefix, forceEmptyLeafs);

		for (j = 0; j < items.length; j++) {
			jQuery(currentSelectors[i]).append(jQuery("<option/>", {
				value: items[j],
				text: items[j]
			}));
		}

		if (items.length == 0) {
			break;
		}

		jQuery(currentSelectors[i]).val(currentItems[i]);

		// Add the current selected item to the prefix to prepare for the next
		// level
		if (prefix.length != 0) {
			prefix += "/";
		}

		if (currentItems[i] == "") {
			// In case we have an 'empty' value, we only need to go once to get
			// the toplevel
			break;
		}
		prefix += currentItems[i];
	}

	// Hide the unused inputs
	jQuery(currentSelectors[currentItems.length]).nextAll().hide();

	// Hide the highest input if there are no options
	var foo = jQuery(currentSelectors[currentItems.length]).children();
	if (jQuery(currentSelectors[currentItems.length]).children().length == 0)
		jQuery(currentSelectors[currentItems.length]).hide();

	// Replace the current selector with a hidden input field
	elem.replaceWith(
		jQuery(document.createElement('input'))
			.attr('id', elem.attr('id'))
			.attr('name', elem.attr('name'))
			.attr('value', elem.val())
			.attr('type', "hidden")
	);
}


/* ......................................................................... */
window.gTicketTypeList = new Array();
window.gTicketTypeMaxBranches = 0;
window.gTicketTypeCount = 0;


/* ......................................................................... */
/*
  We hook into the query page with this attached to the filter <select>
  We should be called after the ticket type has been created if the browser
  follows the DOM way of thinking
 */
function convertQueryTicketType () {
	jQuery('tr.type td.filter select')
		.each(
			function (index, select_elem) {
				if (select_elem.name.match(/[0-9]+_type/g) ) {
					convertTicketTypeSelect(select_elem, true)
				}
	});
}


/* ......................................................................... */
function convertBatchModifyTicketType () {
	jQuery('#batchmod_type td.batchmod_property select')
		.each(
			function (index, select_elem) {
				if (select_elem.name == "batchmod_value_type") {
					convertTicketTypeSelect(select_elem, false);
				}
			});
}


/* ......................................................................... */
/*
 * Enable support for TracTicketTemplate plugin if it exists
 * This creates a "Apply Template" button
 */
function enableTracTicketTemplateSupport () {

    if ( typeof jQuery('body').tt_newticket === "function" ) {
        var button_css = {
            "background": "none repeat scroll 0 0 #FFFFFF",
            "border": "1px solid #DDDDDD",
            "border-radius" : "1em 1em 1em",
            "color": "#000000",
            "cursor": "pointer",
            "font-size": "82%",
            "height": "1.9em",
            "padding": "0 1.0em 0 1.0em",
            "margin": "0 0.9em 0 1.0em"
            };

        var template_button_elem = jQuery("<input>")
            .css(button_css)
            .attr("type", "button")
            .attr("title", "Apply template to the ticket")
            .attr("value", "Apply Template");

        template_button_elem.click(
            function () {
                jQuery("#field-type").trigger('change');
            });
        jQuery(jQuery("#field-type")[0]).parent().append(template_button_elem);
    }

}

/* ......................................................................... */
function initializeTicketTypes() {
	// Query page: add filters
	if (jQuery('[id^=add_filter_]').length) {
		jQuery('[id^=add_filter_]').change(convertQueryTicketType);
	}

	// Query page: batch modify
	if (jQuery('#add_batchmod_field').length) {
		jQuery('#add_batchmod_field').change(convertBatchModifyTicketType);
	}

	// Query page: existing filters
	jQuery('tr.type td.filter select')
		.each(
			function (index, select_elem) {
				convertTicketTypeSelect(select_elem, true)
			});

	// Ticket/Newticket page: tickettype field
	// Original comment: Opera picks up .names in getElementById(), hence it
	// being at the end now
	if ( jQuery( '#field-type' ).length ) {
		// For the new ticket page
		convertTicketTypeSelect( jQuery( '#field-type' )[0], false );
		// if TracTicketTemplateSupport is installed enable "Load Template"
		// button
		enableTracTicketTemplateSupport();
	}

	// Add the reverse function to jQuery, used by convertTicketTypeSelect()
	jQuery.fn.reverse = [].reverse;
}


/* ......................................................................... */
jQuery(document).ready(initializeTicketTypes);
