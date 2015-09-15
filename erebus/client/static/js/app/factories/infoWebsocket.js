'use strict';

angular
    .module('erebus')
    .factory('infoWebsocket', infoWebsocket);

infoWebsocket.$inject = ['$websocket', 'CONFIG'];
    
function infoWebsocket($websocket, CONFIG) {
    var ws = $websocket(CONFIG.server_address + CONFIG.ws.info);
    return {
        start: function(callback) {
            ws.onMessage(function(event) {
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
        getInfo: function() {
            ws.send(JSON.stringify({ request: 'INFO' }));
        },
    }
}
