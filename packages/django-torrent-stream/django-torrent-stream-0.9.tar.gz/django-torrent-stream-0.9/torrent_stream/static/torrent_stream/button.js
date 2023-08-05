var torrent_stream = {
    'video_box_id': 'torrent_stream_video_box',
    'get_browser_size': function () {
        // Output window width and height
        var browserWidth, browserHeight;
        if (typeof(window.innerWidth) == 'number') {
            browserWidth = window.innerWidth;
            browserHeight = window.innerHeight;
        } else if (document.documentElement && (document.documentElement.clientWidth || document.documentElement.clientHeight)) {
            // IE 6+ in 'standards compliant mode'
            browserWidth = document.documentElement.clientWidth;
            browserHeight = document.documentElement.clientHeight;
        }
        return {'w': parseInt(browserWidth), 'h': parseInt(browserHeight)}
    },
    'create_video_box': function () {
        // Create a video-box for output online video
        var video_box = document.createElement('div');
        video_box.id = torrent_stream['video_box_id'];
        var browser_size = torrent_stream['get_browser_size']();
        var box_top = (browser_size['h'] / 2) - (torrent_stream_config['box_height'] / 2);
        var box_left = (browser_size['w'] / 2) - (torrent_stream_config['box_width'] / 2);
        video_box.style.cssText =
            'display: none;' +
            'text-align: center;' +
            'position: fixed;' +
            'top:' + box_top + 'px;' +
            'left:' + box_left + 'px;' +
            'width:' + torrent_stream_config['box_width'] + 'px;' +
            'height:' + torrent_stream_config['box_height'] + 'px';
        document.body.appendChild(video_box);
    },
    'attach_video_player_to_video_box': function () {
        // Click to "Watch online" and setup video-player to video-box
        var video_box = document.getElementById(torrent_stream['video_box_id']);
        video_box.style.display = 'block';
        video_box.innerHTML = '<img src="' + torrent_stream_config['ajax_loader'] + '" alt="Loading..." />';

        var script = document.createElement('script');
        script.type = "text/javascript";
        script.src = torrent_stream_config['torrent_stream_js'];
        script.async = true;
        document.documentElement.appendChild(script);
        script.onload = function() {
            tsplayer(
                torrent_stream['video_box_id'],
                {width: torrent_stream_config['box_width'], height: torrent_stream_config['box_height']}
            );
            document.getElementsByClassName('ts-power')[0].onclick = torrent_stream['dettach_video_player_from_video_box'];
        };
        return false;
    },
    'dettach_video_player_from_video_box': function () {
        // When we click to "Close", then to hide a video-box
        var video_box = document.getElementById(torrent_stream['video_box_id']);
        video_box.style.display = 'none';
        video_box.innerHTML = "";
        return false;
    }
}

if (!document.getElementById(torrent_stream['video_box_id'])) {
    // Once create a video-box
    torrent_stream['create_video_box']();
}

document.getElementById(torrent_stream_config['transport_id']).onclick =
    torrent_stream['attach_video_player_to_video_box'];

document.addEventListener('keypress', function(e) {
    if (e.keyCode == 27) {  // ESC
        torrent_stream['dettach_video_player_from_video_box']();
    }
});

document.getElementById('torrent_stream_video_box').onclick = function() {
    window.CLICK_TO_TS_PLAYER = true;
}

document.onclick = function() {
    if (document.getElementsByClassName('ts-power').length && !window.CLICK_TO_TS_PLAYER) {
        if (confirm(torrent_stream_config['close_player_confirm'])) {
            torrent_stream['dettach_video_player_from_video_box']();
        }
    }
}