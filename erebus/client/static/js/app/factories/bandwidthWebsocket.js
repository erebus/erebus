'use strict';

angular
    .module('erebus')
    .factory('bandwidthWebsocket', bandwidthWebsocket);

bandwidthWebsocket.$inject = ['$websocket', 'CONFIG'];
    
function bandwidthWebsocket($websocket, CONFIG) {
    var ws = $websocket(CONFIG.server_address + CONFIG.ws.bandwidth);
    return {
        start: function(callback) {
            ws.onMessage(function(event) {
                /*console.log('bw event: ', event);*/
                callback(event);
            });

            ws.onError(function(event) {
                console.log('connection error', event);
            });

            ws.onClose(function(event) {
                console.log('connection closed', event);
            });

            ws.onOpen(function() {
                console.log('connection open');
            });
        },
        getCache: function() {
            ws.send(JSON.stringify({ request: 'BW-CACHE' }));
        },
    }
}
