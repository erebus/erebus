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
        console.log('relay info: ' + res);
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
