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
    .factory('logGroup', logGroup);

logGroup.$inject = ['CONFIG'];
    
function logGroup(CONFIG) {

    var logGroup = function() {
        this.groupDuplicates = true;
        this.maxSize = 10; // CONFIG.max_log_size
        this.entries = []
        this.groupSize = 0;
    };

    logGroup.prototype.add = function(entry) {
        var i, duplicate = -1;

        if(this.groupDuplicates) {
            // Look for duplicates in existing entries
            for(i in this.entries) {
                if(entry.isDuplicateOf(this.entries[i])) {
                    duplicate = i;
                    break;
                }
            }
            if(duplicate != -1) {
                // Found duplicate
                this.entries[duplicate].addDuplicate(entry);
            } else {
                this.entries.unshift(entry);
                this.groupSize += 1;
            }
        } else {
            this.entries.unshift(entry);
            this.groupSize += 1;
        }
            
        while(this.groupSize > this.maxSize) {
            this.pop();
        }
    };
        
    logGroup.prototype.pop = function() {
        var lastEntry = this.entries[this.groupSize-1];
        if(lastEntry.numDuplicates() == 0) {
            this.entries.pop();
            this.groupSize -= 1;
        } else {
            lastEntry.removeDuplicate();
        }
    };

    // Get all entries in a readable format
    // {message, type, time, count}
    logGroup.prototype.getAll = function() {
        var i, entry, entries = [];
        for(i in this.entries) {
            entry = this.entries[i].getEntry();
            entry.count = this.entries[i].numDuplicates();
            entries.push(entry);
        }
        return entries;
    };
    
    logGroup.prototype.emptyLog = function() {
        this.entries = [];
        this.groupSize = 0;
    };
    
    logGroup.prototype.showDuplicates = function() {
        var i, j, entry, dedup_entries = [], dup_entries = [];
        
        this.groupDuplicates = false;
        // Get all entries and their duplicates
        for(i in this.entries) {
            entry = this.entries[i];
            // Push duplicates
            if(entry.numDuplicates() > 0) {
                dedup_entries = entry.popDuplicates();
                for(j in dedup_entries) {
                    dup_entries.push(dedup_entries[j]);
                }
            }
            // Push original entry to deduplicated list
            dup_entries.push(entry);
        }
        // Drop all log entries
        this.emptyLog();
        // Refill
        for(i in dup_entries) {
            this.add(dup_entries[i]);
        }
    };
    
    // Hide duplicates
    logGroup.prototype.hideDuplicates = function() {
        var i, dup_entries = [];
        
        this.groupDuplicates = true;
        
        for(i in this.entries) {
            dup_entries.push(this.entries[i]);
        }
        // Drop all log entries
        this.emptyLog();
        // Refill
        for(i in dup_entries) {
            this.add(dup_entries[i]);
        }
    };
    
    return logGroup;
}
