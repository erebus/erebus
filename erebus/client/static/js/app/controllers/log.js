'use strict';

angular
    .module('erebus')
    .controller('logDisplay', logDisplay);
    
logDisplay.$inject = ['$scope', 'logWebsocket'];
    
function logDisplay($scope, logWebsocket) {
    activate();

    logWebsocket.start(function(event) {
        var i, res;
        try {
            res = JSON.parse(event.data);
        } catch(e) {
            res = {'time': 0, 'message': '', 'type': '', 'reply': 'LOG-ENTRY'};
        }

        $scope.$apply(function () {
            // Push single or several entries according to type of reply
            if(res.reply == 'LOG-CACHE') {
                for(i in res.entries) {
                    $scope.entries.unshift(res.entries[i]);
                }
            } else {
                $scope.entries.unshift(res);
            }
        });
    });

    function activate() {
        $scope.entries = [];
        // Request log cache
        logWebsocket.getCache();
    }
}
