
define ['jquery', 'reconnecting-websocket', 'app/view_model', 'knockout'], ($, ReconnectingWebSocket, MessagesViewModel, ko) ->

    class PywizardUI
        constructor: (@group_nodes) ->

        run: ->
            @url = "ws://" + location.hostname + ":8888/io";
            @ws = new ReconnectingWebSocket(@url);

            @ws.onopen = @on_ws_connect
            @ws.onmessage = @on_ws_message

            @viewModel = new MessagesViewModel(@ws, @group_nodes);
            ko.applyBindings(@viewModel);

            @start_resize_listeners()

        on_ws_connect: =>
            $('#server-down-msg').hide()

        on_ws_message: (evt) =>
            data = JSON.parse(evt.data)
            if 'host' of data
                @viewModel.get_node(data['host']).on_ws_message(data['msg'])


        start_resize_listeners: ->
            resizeIt = ->
                height = $(window).height() - $('#header').height() - 160
                $('.messages').css('height', height)

            resizeIt()
            $(window).resize(resizeIt)