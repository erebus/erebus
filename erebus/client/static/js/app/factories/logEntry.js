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
    .factory('logEntry', logEntry);

logEntry.$inject = ['CONFIG'];
    
function logEntry(CONFIG) {

    var logEntry = function(data) {
        this.entry = {};
        this.count = 0;
        this.validEntry = false;
        this.duplicates = [];

        try {
            this.entry = JSON.parse(data);
            if(("header" in this.entry) && ("time" in this.entry) && ("message" in this.entry) && ("type" in this.entry)) {
                this.validEntry = true;
            }
        } catch(e) {
            console.log('Received bad log entry');
        }
    };

    logEntry.prototype.isValid = function() {
        return this.validEntry;
    };

    logEntry.prototype.getHeader = function() {
        return this.entry.header;
    };
        
    logEntry.prototype.getType = function() {
        return this.entry.type;
    };
        
    logEntry.prototype.getMessage = function() {
        return this.entry.message;
    };
        
    logEntry.prototype.getDate = function() {
        return this.entry.readable_time;
    };
        
    logEntry.prototype.addDuplicate = function(entry) {
        this.duplicates.push(entry);
        // Check if it's the first duplicate
        if(this.count == 0) {
            this.count = 2;
        } else {
            this.count += 1;
        }
    };
        
    logEntry.prototype.numDuplicates = function() {
        return this.count;
    };
    
    logEntry.prototype.getDuplicates = function() {
        return this.duplicates;
    };
    
    logEntry.prototype.popDuplicates = function() {
        var entries;
        if(this.count > 0) {
            entries = this.duplicates;
            this.count = 0;
            this.duplicates = [];
        }
        return entries;
    };
        
    logEntry.prototype.removeDuplicate = function() {
        if(this.count > 0) {
            this.duplicates.pop();
            this.count -= 1;
        }
    };
        
    logEntry.prototype.getEntry = function() {
        return this.entry;
    };
        
    logEntry.prototype.getEntries = function() {
        if("entries" in this.entry) {
            return this.entry.entries;
        } else {
            return {};
        }
    };
        
    logEntry.prototype.isDuplicateOf = function(entry) {
        var i, entryMsg, selfMsg, commonMsgs;
        if(this.getType() != entry.getType()) {
            return false;
        } else if(this.getMessage() == entry.getMessage()) {
            return true;
        }
        
        entryMsg = entry.getMessage();
        selfMsg = this.getMessage();
        commonMsgs = commonLogMessages(this.getType());
        for(i in commonMsgs) {
            if(selfMsg.indexOf(commonMsgs[i]) > -1 && entryMsg.indexOf(commonMsgs[i]) > -1) {
                return true;
            }
        }
        return false;
    };
    
    return logEntry;
}

function commonLogMessages(type) {
    var messages = {
        'debug': [
            "connection_handle_write(): After TLS write of",
            "flush_chunk_tls(): flushed",
            "conn_read_callback(): socket",
            "conn_write_callback(): socket",
            "connection_remove(): removing socket",
            "connection_or_process_cells_from_inbuf():",
            "pending in tls object). at_most", //*
            "connection_read_to_buf(): TLS connection closed on read. Closing.",
        ],
        'info': [
            "run_connection_housekeeping(): Expiring",
            "rep_hist_downrate_old_runs(): Discounting all old stability info by a factor of",
            "build time we have ever observed. Capping it to", //*
        ],
        'notice': [
            "build time we have ever observed. Capping it to", //*
            "We will now assume a circuit is too slow to use after waiting", //*
            "We stalled too much while trying to write",
            "I learned some more directory information, but not enough to build a circuit",
            "Attempt by",
            "Loading relay descriptors.", //*
            "Average packaged cell fullness:",
            "Heartbeat: Tor's uptime is",
        ],
        'warn': [
            "You specified a server",
            "I have no descriptor for the router named",
            "Controller gave us config lines that didn't validate",
            "Problem bootstrapping. Stuck at",
            "missing key,", //*
        ]
    }
    if(type in messages) {
        return messages[type];
    } else {
        return [];
    }
}
