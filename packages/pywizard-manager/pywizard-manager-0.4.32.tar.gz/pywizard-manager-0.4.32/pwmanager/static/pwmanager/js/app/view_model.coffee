
define ['app/tab', 'app/node_', 'sammy', 'knockout'], (Tab, Node, Sammy, ko) ->

    class MessagesViewModel
        constructor: (@ws, initial_nodes) ->
            @nodes = ko.observableArray([])
            @tabs = ko.observableArray([])

            @node_index = {}

            tab = new Tab('overview', 'Overview', null)
            tab.is_selected(true)
            @tabs.push(tab)

            for node_name in initial_nodes
                @register_node(node_name)

            view = this

            Sammy ->
                this.get('#:tab_id', ->
                    view.switch_tab(this.params.tab_id)
                )

                this.get('', -> this.app.runRoute  'get', '#overview')
            .run()

        switch_tab: (tab_id) ->
            for tab in @tabs()
                tab.is_selected(tab.id == tab_id)

        select_tab: (selected_tab) =>
            location.hash = '#' + selected_tab.id

        register_node: (node_name) ->
            if node_name of @node_index
                return @node_index[node_name]

            new_node = new Node(@ws, node_name)
            @node_index[node_name] = new_node
            @nodes.push(new_node)

            @tabs.push(new Tab(new_node.name, new_node.name, new_node))

            return new_node

        provision_all: =>
            for node in @nodes()
                node.provision()

        get_node: (node_name) ->
            if not (node_name of @node_index)
                return @register_node(node_name)

            @node_index[node_name]
