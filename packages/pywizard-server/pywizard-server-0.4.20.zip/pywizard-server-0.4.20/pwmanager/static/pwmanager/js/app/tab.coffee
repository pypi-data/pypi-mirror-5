
define ['knockout'], (ko) ->

    class Tab
        constructor: (@id, @title, @node) ->
            @is_selected = ko.observable()
