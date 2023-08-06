var Froogaloop=function(){function e(a){return new e.fn.init(a)}function h(a,c,b){if(!b.contentWindow.postMessage)return!1;var f=b.getAttribute("src").split("?")[0],a=JSON.stringify({method:a,value:c});"//"===f.substr(0,2)&&(f=window.location.protocol+f);b.contentWindow.postMessage(a,f)}function j(a){var c,b;try{c=JSON.parse(a.data),b=c.event||c.method}catch(f){}"ready"==b&&!i&&(i=!0);if(a.origin!=k)return!1;var a=c.value,e=c.data,g=""===g?null:c.player_id;c=g?d[g][b]:d[b];b=[];if(!c)return!1;void 0!==
a&&b.push(a);e&&b.push(e);g&&b.push(g);return 0<b.length?c.apply(null,b):c.call()}function l(a,c,b){b?(d[b]||(d[b]={}),d[b][a]=c):d[a]=c}var d={},i=!1,k="";e.fn=e.prototype={element:null,init:function(a){"string"===typeof a&&(a=document.getElementById(a));this.element=a;a=this.element.getAttribute("src");"//"===a.substr(0,2)&&(a=window.location.protocol+a);for(var a=a.split("/"),c="",b=0,f=a.length;b<f;b++){if(3>b)c+=a[b];else break;2>b&&(c+="/")}k=c;return this},api:function(a,c){if(!this.element||
!a)return!1;var b=this.element,f=""!==b.id?b.id:null,d=!c||!c.constructor||!c.call||!c.apply?c:null,e=c&&c.constructor&&c.call&&c.apply?c:null;e&&l(a,e,f);h(a,d,b);return this},addEvent:function(a,c){if(!this.element)return!1;var b=this.element,d=""!==b.id?b.id:null;l(a,c,d);"ready"!=a?h("addEventListener",a,b):"ready"==a&&i&&c.call(null,d);return this},removeEvent:function(a){if(!this.element)return!1;var c=this.element,b;a:{if((b=""!==c.id?c.id:null)&&d[b]){if(!d[b][a]){b=!1;break a}d[b][a]=null}else{if(!d[a]){b=
!1;break a}d[a]=null}b=!0}"ready"!=a&&b&&h("removeEventListener",a,c)}};e.fn.init.prototype=e.fn;window.addEventListener?window.addEventListener("message",j,!1):window.attachEvent("onmessage",j);return window.Froogaloop=window.$f=e}();

$(document).ready(function(){
    console.log($('.playerVimeo'));
    $('.playerVimeo').each(function( index ) {
        var iframe = $(this).find('iframe')[0];
        var player = $f(iframe);

        var progress = $(this).find('.progress');
        var progressload = progress.find('.progress-bar.load');
        var progressplay = progress.find('.progress-bar.play');

        var controls = $(this).find('.controls');
        var playpause = controls.find('.playpause');
        var beginning = controls.find('.beginning');
        var forward = controls.find('.forward');
        
        /*** Events ***/
        player.addEvent('ready', function() {
            player.addEvent('play', onPlay);
            player.addEvent('pause', onPlay);
            player.addEvent('finish', onPlay);
            player.addEvent('loadProgress', onLoadProgress);
            player.addEvent('playProgress', onPlayProgress);
        });
        function onPlay(id) {
            updatePause();
        }
        function onLoadProgress(data, id) {
            console.log('onLoadProgress');
            console.log(data);
            progressload.css('width', (data.percent*100)+'%');
        }
        function onPlayProgress(data, id) {
            progressplay.css('width', (data.percent*100)+'%');
        }
        function updatePause() {
            player.api('paused', function (value) {
                if (value) {
                    controls.addClass('paused');
                } else {
                    controls.removeClass('paused');
                }
            });
        }

        /*** Controls ***/
        playpause.bind('click', function(e) {
            e.preventDefault();
            player.api('paused', function (value) {
                player.api(value ? 'play' : 'pause');
            });
        });
        beginning.bind('click', function(e) {
            e.preventDefault();
            player.api('seekTo', 0);
        });
        forward.bind('click', function(e) {
            e.preventDefault();
            player.api('getCurrentTime', function (value) {
                player.api('seekTo', value+30);
            });
        });
        progress.bind('click', function(e) {
            e.preventDefault();
            var self = $(this)[0];
            player.api('getDuration', function (value) {
                player.api('seekTo', e.offsetX * value / self.clientWidth);
            });
        });
    });

});