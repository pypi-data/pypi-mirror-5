class window.Controls.video extends window.Control
    createDom: () ->
        @dom = $("""
            <div class="control video">
                <video controls>
                    <source src="#{if @properties.path then "/elements/video/#{@properties.path}" else ''}" type="video/mp4">
                </video>
                <div class="timestamp">
                    00:00:00.000
                </div>
                <div>
                    <a class="control button style-normal"><i class="icon-cut"></i> Cut</a>
                </div>
            </div>
        """)

        timestamp = @dom.find('.timestamp')
        @video = @dom.find('video')[0]

        @video.addEventListener 'canplay', () =>
            if not @video
                return
            @video.pause()
            if @properties.position
                @video.currentTime = @properties.position
            if @properties.autoplay
                @video.play()

        @video.addEventListener 'timeupdate', () =>
            if not @video
                return
            ts = @video.currentTime
            @lastTimestamp = ts
            h = Math.floor(ts / 3600)
            m = Math.floor(ts / 60 % 60)
            s = Math.floor(ts % 60)
            ms = Math.floor(ts * 1000 % 1000)

            ts = h + ':' + (if m < 10 then '0' else '') + m + ':' + (if s < 10 then '0' else '') + s + '.' +
                        (if ms < 100 then '0' else '') + (if ms < 10 then '0' else '') + ms

            timestamp.text(ts)
            @lastTimestampText = ts

        @dom.find('a').click () =>
            @event('cut', time: @lastTimestamp, time_text: @lastTimestampText)

    detectUpdates: () ->
        r = {}
        if @video.paused == @properties.autoplay
            r.autoplay = not @video.paused
        if @video.currentTime != @properties.position
            r.position = @video.currentTime
        return r

    onBroadcast: (msg) ->
        if msg == 'destruct'
            @video.pause()
            delete(@video)
            $(@dom).empty()