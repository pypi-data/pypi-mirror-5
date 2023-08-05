
define ['knockout'], (ko) ->

    class Message
        constructor: (@text, @level, @date) ->
            @message = ko.computed =>
                @text