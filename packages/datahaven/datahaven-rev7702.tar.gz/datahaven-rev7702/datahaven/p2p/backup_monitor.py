#!/usr/bin/python
#backup_monitor.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#This does a bunch of things.  
#1)  monitor the lists of file sent back from suppliers,
#    if there is a gap we need to try to fix it
#    * main class is _BackupMonitor,
#      it saves the lists of files in _BackupListFiles,
#      breaks down the lists of files into info on a single backup in _SupplierBackupInfo
#    * _BlockRebuilder takes care of a single broken block,
#      request what we have available, builds whatever we can
#      and stops either when we have fixed everything
#      or there is nothing more we can do
#    * _BlockRebuilder requests files through io_throttle and sends out the fixed files
#      also through io_throttle
#
#2)  if a backup is unfixable, not enough information, we delete it CleanupBackups in _BackupMonitor
#
#3)  every hour it requests a list of files from each supplier - _hourlyRequestListFiles
#
#4)  every hour it tests a file from each supplier,
#    seeing if they have the data they claim,
#    and that it is correct
#    * data is stored in _SuppliersSet and _SupplierRemoteTestResults,
#    was data good, bad, being rebuilt, or they weren't online 
#    and we got no data on the result
#    * if a supplier hasn't been seen in settings.FireInactiveSupplierIntervalHours()
#    we replace them
#
#
# Strategy for automatic backups
#
# 1) Full backup to alternating set of nodes every 2 weeks.
#
# 2) Full monthly, then incremental weekly and daily
#
# 3) One time full and then incremental monthly, weekly
#
# 4) Break alphabetical list of files into N parts and do full
#    backup on one of those and incrementals on the rest.
#    So we no longer need part of the incremental history
#      every time, and after N times older stuff can toss.
#      so every day is part full and part incremental.  Cool.
#
#  Want user to be able to specify what he wants, or at least
#  select from a few reasonable choices.
#
#
# May just do (1) to start with.
#
# This code also wakes up every day and fires off localtester, remotetester
#   on some reasonable random stuff.
#
# This manages the whole thing, so after GUI, this has the highest level control functions.
#
# Some competitors let people choose what days to backup on.  Not sure this
#   is really so great though, once we have incremental.
#
# Some can handle partial file changes.  So if a 500 MB mail file only has
# a little bit appended, only the little bit is backed up.
#
# Some competitors can turn the computer off after a backup, but
# we need it to stay on for P2P stuff.
#
# need to record if zip, tar, dump, etc
#
# If we do regular full backups often, then we might not bother scrubbing older stuff.
# Could reduce the bandwidth needed (since scrubbing could use alot.l


import os
import sys
import time
import random
import gc


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backup_monitor.py')

from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet import threads


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.settings as settings
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.tmpfile as tmpfile
import lib.diskspace as diskspace
import lib.automat as automat
import lib.automats as automats


import backup_rebuilder
import fire_hire
import list_files_orator 
import contact_status

import backups
import backup_db
import identitypropagate

_BackupMonitor = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BackupMonitor
    if _BackupMonitor is None:
        _BackupMonitor = BackupMonitor('backup_monitor', 'READY', 4)
    if event is not None:
        _BackupMonitor.automat(event, arg)
    return _BackupMonitor


class BackupMonitor(automat.Automat):
    timers = {'timer-1sec':   (1,       ['RESTART', 'PING']), 
              'timer-10sec':  (20,      ['PING']),
              # 'timer-10min':  (10*60,   ['READY']), 
              }
    ackCounter = 0

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('MONITOR ' + newstate)

    def A(self, event, arg):
        #---READY---
        if self.state is 'READY':
            if event == 'init' :
                backup_rebuilder.A('init')
            elif event == 'restart' :
                self.state = 'RESTART'
        #---RESTART---
        elif self.state is 'RESTART':
            if event == 'timer-1sec' and backup_rebuilder.A().state in [ 'STOPPED', 'DONE', ] :
                self.state = 'PING'
                self.doPingAllSuppliers(arg)
        #---PING---
        elif self.state is 'PING':
            if event == 'timer-10sec' or ( event == 'timer-1sec' and self.isAllSuppliersResponded(arg) ) :
                self.state = 'LIST_FILES'
                list_files_orator.A('need-files')
            elif event == 'restart' :
                self.state = 'RESTART'
        #---LIST_FILES---
        elif self.state is 'LIST_FILES':
            if event == 'restart' :
                self.state = 'RESTART'
            elif ( event == 'list_files_orator.state' and arg is 'NO_FILES' ) :
                self.state = 'READY'
            elif ( event == 'list_files_orator.state' and arg is 'SAW_FILES' ) :
                self.state = 'LIST_BACKUPS'
                self.doPrepareListBackups(arg)
        #---LIST_BACKUPS---
        elif self.state is 'LIST_BACKUPS':
            if event == 'list-backups-done' :
                self.state = 'REBUILDING'
                backup_rebuilder.A('start')
            elif event == 'restart' :
                self.state = 'RESTART'
        #---REBUILDING---
        elif self.state is 'REBUILDING':
            if event == 'restart' :
                self.state = 'RESTART'
                backup_rebuilder.SetStoppedFlag()
            elif ( event == 'backup_rebuilder.state' and arg is 'STOPPED' ) :
                self.state = 'READY'
            elif ( event == 'backup_rebuilder.state' and arg is 'DONE' ) :
                self.state = 'FIRE_HIRE'
                fire_hire.A('start')
        #---FIRE_HIRE---
        elif self.state is 'FIRE_HIRE':
            if event == 'fire-hire-finished' :
                self.state = 'READY'
                self.doCleanUpBackups(arg)
            elif event == 'restart' or event == 'hire-new-supplier' :
                self.state = 'RESTART'

    def isAllSuppliersResponded(self, arg):
        onlines = contact_status.countOnlineAmong(contacts.getSupplierIDs())
        dhnio.Dprint(6, 'backup_monitor.isAllSuppliersResponded ackCounter=%d onlines=%d' % (self.ackCounter, onlines))
        if self.ackCounter == contacts.numSuppliers():
            return True
        if self.ackCounter >= onlines - 1:
            return True
        return False

    def doPingAllSuppliers(self, arg):
        self.ackCounter = 0
        def increaseAckCounter(packet):
            self.ackCounter += 1
        identitypropagate.suppliers(increaseAckCounter)

    def doPrepareListBackups(self, arg):
        # take remote and local backups and get union from it 
        allBackupIDs = set(backups.local_files().keys() + backups.remote_files().keys())
        # take only backups from data base
        allBackupIDs.intersection_update(backup_db.GetBackupIds())
        # remove running backups
        allBackupIDs.difference_update(backups.backups_in_process())
        # sort it in reverse order - newer backups should be repaired first
        allBackupIDs = misc.sorted_backup_ids(list(allBackupIDs), True)
        # add backups to the queue
        backup_rebuilder.AddBackupsToWork(allBackupIDs)
        # update suppliers, clear stats for all 
        backups.suppliers_set().UpdateSuppliers(contacts.getSupplierIDs()) 
        dhnio.Dprint(6, 'backup_monitor.doPrepareListBackups %s' % str(allBackupIDs))
        self.automat('list-backups-done')

    def doCleanUpBackups(self, arg):
        backupsToKeep = settings.getGeneralBackupsToKeep()
        bytesUsed = backup_db.GetTotalBackupsSize()
        bytesNeeded = diskspace.GetBytesFromString(settings.getCentralMegabytesNeeded(), 0) 
        dhnio.Dprint(6, 'backup_monitor.doCleanUpBackups backupsToKeep=%d used=%d needed=%d' % (
            backupsToKeep, bytesUsed, bytesNeeded))
        if backupsToKeep > 0:
            for backupDir in backup_db.GetBackupDirectories():
                backupIDsForDirectory = backup_db.GetDirBackupIds(backupDir)
                # backupIDsForDirectory.reverse()
                while len(backupIDsForDirectory) > backupsToKeep:
                    backupID = backupIDsForDirectory.pop(0)
                    dhnio.Dprint(6, 'backup_monitor.doCleanUpBackups %d of %d backups for %s, so remove older %s' % (
                        len(backupIDsForDirectory), backupsToKeep, backupDir, backupID))
                    backup_db.AbortRunningBackup(backupID)
                    backups.DeleteBackup(backupID)
        # we need to fit used space into needed space (given from other users)
        # they trust us - do not need to take extra space from our friends
        # so remove oldest backups, but keep at least one for every folder - at least locally!
        # still our suppliers will remove our "extra" files by their "local_tester" 
        if bytesNeeded <= bytesUsed:
            all_backups = backup_db.GetBackupIds(full_info_please=True)
            all_backups.reverse()
            for i in range(len(all_backups)-1, -1, -1):
                backupID = all_backups[i][0]
                backupDir = all_backups[i][1]
                backupSize = all_backups[i][2]
                if len(backup_db.GetDirBackupIds(backupDir)) <= 1:
                    continue
                dhnio.Dprint(6, 'backup_monitor.doCleanUpBackups over use %d of %d, so remove %s of %s' % (
                    bytesUsed, bytesNeeded, backupID, backupDir))
                backup_db.AbortRunningBackup(backupID)
                backups.DeleteBackup(backupID)
                bytesUsed -= backupSize
                if bytesNeeded > bytesUsed:
                    break 
        collected = gc.collect()
        dhnio.Dprint(6, 'backup_monitor.doCleanUpBackups collected %d objects' % collected)



def Restart():
    dhnio.Dprint(4, 'backup_monitor.Restart')
    A('restart')


def shutdown():
    dhnio.Dprint(4, 'backup_monitor.shutdown')
    automat.clear_object(A().index)

        


