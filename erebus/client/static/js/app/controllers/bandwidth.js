'use strict';

angular
    .module('erebus')
    .controller('bandwidthGraph', bandwidthGraph);
    
bandwidthGraph.$inject = ['$scope', '$modal', 'bandwidthWebsocket'];
    
function bandwidthGraph($scope, $modal, bandwidthWebsocket) {
    var max_value, graph_width = 60;
    var read_bytes = [], written_bytes = [], data = [];
    var stats = {}

    activate();
    
    bandwidthWebsocket.start(function(event) {
        var i, res;
        try {
            res = JSON.parse(event.data);
        } catch(e) {
            /* Default values */
            res = {'reply': 'BW-EVENT', 'read': 0, 'written': 0};
        }

        // Push single or several entries according to type of reply
        if(res.reply == 'BW-CACHE') {
            for(i in res.entries) {
                read_bytes.unshift(res.entries[i].read);
                written_bytes.unshift(res.entries[i].written);
            }
        } else {
            read_bytes.unshift(res.read);
            written_bytes.unshift(res.written);
        }

        // Truncate to graph_width size
        if(read_bytes.length > graph_width)
            read_bytes.splice(graph_width, read_bytes.length - graph_width);
        if(written_bytes.length > graph_width)
            written_bytes.splice(graph_width, written_bytes.length - graph_width);

        // Format for charting: { x: index, y1: value, y2: value }
        max_value = 1024; // default value
        for(i = 0; i < graph_width; i++) {
            data[i] = {
                x: i,
                read: read_bytes[i],
                written: written_bytes[i]
            };
            max_value = Math.max(max_value, Math.max(read_bytes[i], written_bytes[i]))
        }
        
        // Bandwidth stats
        stats['read'] = formatBytesPerSec(res.read, 2);
        stats['written'] = formatBytesPerSec(res.written, 2);
        if(res.read_total) stats['read_total'] = formatBytes(res.read_total, 2);
        if(res.write_total) stats['write_total'] = formatBytes(res.write_total, 2);
        if(res.read_avg) stats['read_avg'] = formatBytesPerSec(res.read_avg, 2);
        if(res.write_avg) stats['write_avg'] = formatBytesPerSec(res.write_avg, 2);
        if(res.limit) stats['limit'] = formatBytes(res.limit, 2);
        if(res.burst) stats['burst'] = formatBytesPerSec(res.burst, 2);
        if(res.measured) stats['measured'] = formatBytesPerSec(res.measured, 2);
        if(res.observed) stats['observed'] = formatBytesPerSec(res.observed, 2);
        
        $scope.$apply(function () {
            $scope.data = data;
            $scope.stats = stats;
            if($scope.maxValue['autoAdjust']) {
                $scope.options['axes']['y']['max'] = max_value;
                $scope.options['axes']['y2']['max'] = max_value;
            }
        });
    });
    
    $scope.changeMaxValue = function(max = 0) {
        $scope.maxValue = {
            'autoAdjust': false,
            'custom': false,
        }
        if(max == 0) {
            $scope.maxValue['autoAdjust'] = true;
        } else {
            $scope.maxValue['custom'] = true;
            // Update the graph
            $scope.options['axes']['y']['max'] = max;
            $scope.options['axes']['y2']['max'] = max;
            // Save this custom value
            $scope.customMaxValue = max;
        }
    }
    
    // Open modal box to choose max
    $scope.maxValueModalBox = function() {
        // Angular UI modal (for bootstrap)
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'chooseMax.html',
            controller: 'customMaxCtrl', // At the bottom of this file
            size: 'sm',
            resolve: { // Pass the current saved max value
                customMaxValue: function() {
                    return $scope.customMaxValue;
                }
            }
        });

        modalInstance.result.then(function (customValue) {
            // Get the value and update 
            $scope.changeMaxValue(customValue);
        });
    }

    function activate() {
        $scope.options = {
            axes: {
                x: {key: 'x', type: 'linear', min: 0, max: 60, ticks: 10, grid: true},
                y: {min: 0, max: 1024, ticks: 5, innerTicks: true, grid: true},
                y2: {min: 0, max: 1024, ticks: 5, innerTicks: true, grid: true}
            },
            margin: {
                left: 35
            },
            series: [
                {y: 'read', color: '#3498db', thickness: '3px', type: 'area', striped: false},
                {y: 'written', color: '#e74c3c', thickness: '3px', type: 'area', striped: false, axis: 'y2'}
            ],
            tooltip: {mode: 'scrubber', formatter: function(x, y, series) {return formatBytes(y, 2);}},
            drawLegend: false,
            drawDots: true,
            hideOverflow: false,
            columnsHGap: 4
        }
        $scope.data = []
        // Request bandwidth cache
        bandwidthWebsocket.getCache();
        // Auto-adjust max value by default
        $scope.maxValue = {
            'autoAdjust': true,
            'custom': false,
        }
        $scope.customMaxValue = 0;
    }
}

function formatBytes(bytes, decimals) {
    if(bytes == 0) return '0 Byte';
    var k = 1000;
    var dm = decimals + 1 || 3;
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toPrecision(dm) + ' ' + sizes[i];
}

function formatBytesPerSec(bytes, decimals) {
    return formatBytes(bytes, decimals) + '/sec';
}


// Small controller to handle the chooseMax modal box
angular
    .module('erebus')
    .controller('customMaxCtrl', customMaxCtrl);
    
customMaxCtrl.$inject = ['$scope', '$modalInstance', 'customMaxValue'];
    
function customMaxCtrl($scope, $modalInstance, customMaxValue) {
    // The current max value
    $scope.value = customMaxValue;
    $scope.update = function () {
        // Return the choosen max value
        $modalInstance.close($scope.value);
    };
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}
