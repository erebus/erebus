/*
* This file is part of Erebus, a web dashboard for tor relays.
*
* :copyright:   (c) 2015, The Tor Project, Inc.
*               (c) 2015, Damian Johnson
*               (c) 2015, Cristobal Leiva
*
* :license: See LICENSE for licensing information.
*/

'use strict';

angular
    .module('erebus')
    .controller('relayInfo', relayInfo);
    
relayInfo.$inject = ['$scope', 'infoWebsocket'];
    
function relayInfo($scope, infoWebsocket) {
    activate();

    infoWebsocket.start(function(event) {
        var res;
        try {
            res = JSON.parse(event.data);
        } catch(e) {
            // Default values
            res = {'version': 'Unknown', 'nickname': 'Unnamed', 'fingerprint': '-'};
        }
        $scope.$apply(function () {
            $scope.info = res;
        });
    });

    function activate() {
        $scope.info = [];
        // Request relay info
        infoWebsocket.getInfo();
    }
}
