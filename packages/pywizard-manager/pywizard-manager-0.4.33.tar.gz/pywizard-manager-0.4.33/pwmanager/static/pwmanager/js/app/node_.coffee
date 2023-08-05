

define ['jquery', 'knockout', 'app/message'], ($, ko, Message) ->

    class Node
        constructor: (@ws, @name) ->
            @is_online = ko.observable()
            @last_seen = 0
            @highlighted = ko.observable()
            @messages = ko.observableArray([])
            @follow_uptime()

        write_line: (data) ->
            len = @messages().length;
            maxLen = 1000
            if len > maxLen
                @messages().splice(0, len - maxLen)
            @messages.push(new Message(data))

            $('.messages').each ->
                $(this).scrollTop($(this).find('ul').height())

            @blink()

        blink: ->
            @highlighted(true)
            setTimeout (=> @highlighted(false)), 70

        on_ws_message: (data) ->
            cmd = data['cmd'];
            data = data['data'];

            if cmd == 'up'
                self.last_seen = new Date().getTime();

            else if cmd == 'log'
                @write_line(data)

            else if cmd == 'continue'
                if @messages.length > 0
                  @messages[@messages.length - 1].text += data
                 else
                    @write_line(data)
            else
                @write_line('Unknown command from server: ' + cmd)

            @last_seen = new Date().getTime()

            @is_online(true)

        send_msg: (data) ->
            @ws.send(JSON.stringify({
              host: @name,
              msg: data
            }))

        execCmd: (formElement) =>
            input = $(formElement).find('[name=text]')
            cmd = input.val();
            input.val('');

            if cmd == 'cls'
                @messages.removeAll()
            else
                @send_msg({
                    'cmd': cmd
                })

            return false

        provision: =>
            @messages.removeAll()
            @send_msg({
                'cmd': 'date'
            })

        follow_uptime: =>
            if @ws.readyState != WebSocket.OPEN
                $('#server-down-msg').show();
                @is_online(false);
                @last_seen = 0

            time = new Date().getTime()

            if @last_seen < (time - 3000)
                @is_online(false)
            else
                @last_seen = time
                @is_online(true)

            setTimeout(@follow_uptime, 2000)