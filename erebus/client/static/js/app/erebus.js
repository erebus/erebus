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
    .module('erebus', [
        'ngWebSocket',
        'n3-line-chart',
        'ui.bootstrap',
        'erebus.config',
    ]);
