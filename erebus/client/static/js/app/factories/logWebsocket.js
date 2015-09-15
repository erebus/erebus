'use strict';

angular
    .module('erebus')
    .factory('logWebsocket', logWebsocket);

logWebsocket.$inject = ['$websocket', 'CONFIG'];
    
function logWebsocket($websocket, CONFIG) {
    var ws = $websocket(CONFIG.server_address + CONFIG.ws.log);
    return {
        start: function(callback) {
            ws.onMessage(function(event) {
                /*console.log('log entry: ', event);*/
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
            ws.send(JSON.stringify({ request: 'LOG-CACHE' }));
        },
    }
}
