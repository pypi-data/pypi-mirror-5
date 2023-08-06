class ClientUI
    constructor: () ->
        @root = $('#root')
        @goDirectoryList()

    replace_view: (html) ->
        @root.html(html)

    go: (url, callback) ->
        $.get(
            '/media/ajax/' + url,
            (html) =>
                @replace_view(html)
                callback()
        )

    goDirectory: (id) ->
        @currentDirectoryId = id
        @goBrowse('/')
        return
        @go "directory/#{id}", () =>
            @root.find('#go-back').click () =>
                @goDirectoryList()
            @root.find('#go-browse').click () =>
                @goBrowse('/')

    goDirectoryList: () ->
        @go 'directory-list', () =>
            @root.find('a').each (i, e) =>
                $(e).click () =>
                    @goDirectory($(e).attr('data-id'))

    goBrowse: (path) ->
        @go "browse/#{@currentDirectoryId}/#{path}", () =>
            @root.find('#go-back').click () =>
                @goDirectoryList()
            if path == '/'
                @root.find('#go-up').hide()
                path = ''
            else
                @root.find('#go-up').click () =>
                    components = path.split('/')
                    components = components.splice(0, components.length - 1)
                    path = components.join('/')
                    @goBrowse(path)

            @root.find('a.browse-item').each (i, e) =>
                $(e).click () =>
                    path = path + '/' + $(e).attr('data-id')
                    @goBrowse(path)





$ () ->
    new ClientUI()
