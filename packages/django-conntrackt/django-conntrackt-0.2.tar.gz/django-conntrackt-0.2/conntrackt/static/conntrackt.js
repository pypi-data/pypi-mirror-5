/**
 * Copyright (C) 2013 Branko Majic
 *
 * This file is part of Django Conntrackt.
 *
 * Django Conntrackt is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option) any
 * later version.
 *
 * Django Conntrackt is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
 */

$(document).ready(function(){

    /**
     * BEGIN (search suggestions)
     */

    // Search input field in navigation bar.
    var searchField = $("#search");

    // Set-up the search suggestions as the user types-in the search query.
    searchField.keyup(function(){
        // Fetch the needed elements. The search suggestions element is kept
        // invisble by default via CSS.
        var searchField = $("#search");
        var searchSuggestions = $("#search-suggestions");
        var searchSuggestionsList = searchSuggestions.find("ul");

        // Show the search suggestions only if the user has provided 2 or more
        // characters.
        if (searchField.val().length >= 2) {
            request = $.getJSON(conntrackt_api_url + "/search/" + searchField.val(), {"limit": 4})
                .done(function(data) {

                    // Process the retrieved JSON response, setting-up list of
                    // items that will be offered as suggestion.
                    var items = [];
                    $.each(data, function(index, item) {
                        if (item.type == "project") {
                            items.push('<li><a class="search-option" href="' + item.url + '">' + item.name + '<br/><small>Project</small></a></li>');
                        } else if (item.type == "entity") {
                            items.push('<li><a class="search-option" href="' + item.url + '">' + item.name + '<br/><small>from ' + item.project + '<small></a></li>');
                        }
                    });

                    // Add the suggestions (if any) to correct HTML element.
                    if (items.length) {
                        searchSuggestions.find("ul").empty().append(items);
                        searchSuggestions.fadeIn(200);

                        // Set-up up/down arrow navigation through suggested
                        // elements.  Since we empty and add new elements on
                        // each change of list, this has to be done here (and
                        // not globally).
                        $(".search-option").keydown(function(e){
                            // Down arrow was pressed.
                            if(e.which == 40) {
                                $(this).parent().next().find(".search-option").focus();
                                // Stops the page from scrolling.
                                return false;
                            }
                            if(e.which == 38) {
                                // Up arrow was pressed. Focus the search box if
                                // there's no more search items up in the list.
                                var prev = $(this).parent().prev().find(".search-option");
                                if (prev.length) {
                                    prev.focus();
                                } else {
                                    $("#search").focus();
                                }
                                // Stops the page from scrolling
                                return false;
                            }
                        });

                        // Hide the suggestions if search options lose focus,
                        // and search field doesn't have the focus
                        // either. Timeout has to be used since focus change
                        // takes some time.
                        //
                        // @TODO: Figure out if this can be done without timeout, since it feels
                        // like race condition issue.
                        $(".search-option").blur(function(){
                            setTimeout(function() {
                                var focusedElement = $(document.activeElement);

                                if ( focusedElement.attr('id') != "search" && focusedElement.attr('class') != "search-option") {
                                    $("#search-suggestions").fadeOut(200);
                                }
                            }, 10);
                        });
                    } else {
                        // No search results were returned (nothing matched).
                        searchSuggestions.find("ul").empty().append("<li class='disabled'><a href='#'>No matches</a></li>");
                        searchSuggestions.fadeIn(200);
                    }

                })
                .fail(function() {
                    // Show error message if search query failed.
                    searchSuggestions.find("ul").append("<li class='disabled'><a href='#'>Search error.</a></li>");
                });
        } else {
            // Hide the search suggestions if less than two characters were provided.
            searchSuggestions.fadeOut(200);
        }
    });

    // Focus the first search suggestion if arrow done is pressed while within
    // the search field.
    searchField.keydown(function(event){
        if (event.which == 40) {
            $(".search-option:first").focus();
            return false;
        }
    });

    // Hide the suggestions if search box loses focus, and no search suggestions
    // have the focus either. Timeout has to be used since focus change takes
    // some time.
    //
    // @TODO: Figure out if this can be done without timeout, since it feels
    // like race condition issue.
    searchField.blur(function(){
        setTimeout(function() {
            if ($(document.activeElement).attr('class') != "search-option") {
                $("#search-suggestions").fadeOut(200);
            }
        }, 10);
    });

    // Show the suggestions if search box gains focus, and more than two
    // characters were entered as search term previously.
    searchField.focus(function(){
        if ($("#search").val().length >= 2) {
            $("#search-suggestions").fadeIn(200);
        }
    });

    /**
     * END (search suggestions)
     */

});