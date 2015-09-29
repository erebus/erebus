'use strict';

angular
    .module('erebus')
    .controller('logConsole', logConsole);
    
logConsole.$inject = ['$scope', '$modal', 'logWebsocket', 'logEntry', 'logGroup'];
    
function logConsole($scope, $modal, logWebsocket, logEntry, logGroup) {
    var entries = new logGroup();

    activate();

    logWebsocket.start(function(event) {
        var i, entry, local_entries;
        
        entry = new logEntry(event.data);
        
        if(entry.isValid()) {
            $scope.$apply(function () {
                // Push single or several entries according to entry header
                if(entry.getHeader() == 'LOG-CACHE') {
                    local_entries = entry.getEntries();
                    for(i in local_entries) {
                        entries.add(local_entries[i]);
                    }
                } else {
                    entries.add(entry);
                }
                $scope.entries = entries.getAll();
            });
        }
    });
    
    $scope.duplicates = function() {
        $scope.hideDuplicates = !$scope.hideDuplicates; // Switch boolean value
        if($scope.hideDuplicates) {
            entries.hideDuplicates();
        } else {
            entries.showDuplicates();
        }
        $scope.entries = entries.getAll();
    }
    
    // Open modal box to change event filters
    $scope.eventFiltering = function() {
        // Angular UI modal (for bootstrap)
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'eventFiltering.html',
            controller: 'eventFilteringCtrl', // At the bottom of this file
            resolve: { // Pass the current saved max value
                filters: function() {
                    //return $scope.filters;
                    return {};
                }
            }
        });

        modalInstance.result.then(function (filters) {
            // Get the new filters and update 
            //$scope.changeF(filters);
            console.log("filters: " + filters);
        });
    }

    function activate() {
        $scope.entries = [];
        $scope.hideDuplicates = true;
        // Request log cache
        logWebsocket.getCache();
    }
}


// Small controller to handle the eventFiltering modal box
angular
    .module('erebus')
    .controller('eventFilteringCtrl', eventFilteringCtrl);
    
eventFilteringCtrl.$inject = ['$scope', '$modalInstance', 'filters'];
    
function eventFilteringCtrl($scope, $modalInstance, filters) {
    // Current filters
    $scope.value = filters;
    
    //$scope.eventTypes = {};
    
    $scope.update = function () {
        // Return the choosen filters
        //$modalInstance.close($scope.value);
    };
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}
