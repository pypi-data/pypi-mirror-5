#!/usr/bin/python
#block_rebuilder.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys
import time
import random


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in block_rebuilder.py')

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
import lib.packetid as packetid
import lib.automat as automat
# from lib.automat import Automat


import fire_hire
import backup_rebuilder
import list_files_orator 
import lib.automats as automats

import backups
import raidread
import p2p_service
import io_throttle
import backup_db
import contact_status
import data_sender

_BlockRebuilder = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BlockRebuilder
    if _BlockRebuilder is None:
        _BlockRebuilder = BlockRebuilder()
    if event is not None:
        _BlockRebuilder.automat(event, arg)
    return _BlockRebuilder


class BlockRebuilder(automat.Automat):
    timers = {'timer-1min':     (60,    ['REQUEST',]),
              'timer-1sec':     (1,     ['REQUEST', 'SENDING']),}
    
    def __init__(self,  
                 eccMap, 
                 backupID, 
                 blockNum, 
                 supplierSet, 
                 remoteData, 
                 remoteParity,
                 localData, 
                 localParity, 
                 creatorId = None, 
                 ownerId = None):
        self.eccMap = eccMap
        self.backupID = backupID
        self.blockNum = blockNum
        self.supplierSet = supplierSet
        self.supplierCount = len(self.supplierSet.suppliers)
        self.remoteData = remoteData
        self.remoteParity = remoteParity
        self.localData = localData
        self.localParity = localParity
        self.creatorId = creatorId
        self.ownerId = ownerId
        # at some point we may be dealing with when we're scrubbers
        if self.creatorId == None:
            self.creatorId = misc.getLocalID()
        if self.ownerId == None:
            self.ownerId = misc.getLocalID()
        # this files we want to rebuild
        # need to identify which files to work on
        self.missingData = [0] * self.supplierCount
        self.missingParity = [0] * self.supplierCount
        # list of packets ID we requested
        self.requestedFilesList = []
        # array to remember requested files
        self.requestedData = [0] * self.supplierCount
        self.requestedParity = [0] * self.supplierCount
        
        automat.Automat.__init__(self, 'block_rebuilder', 'AT_STARTUP', 12)
        
#    def __del__(self):
#        dhnio.Dprint(6, 'block_rebuilder.BlockRebuilder died %s with index %d' % (str(self), self.index))
        
    def state_changed(self, oldstate, newstate):
        backup_rebuilder.A('block_rebuilder.state', newstate)
        backups.RepaintBackup(self.backupID)
    
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state is 'AT_STARTUP':
            if event == 'start' :
                self.state = 'MISSING'
                self.doIdentifyRemoteMissingFiles(arg)
        #---MISSING---
        elif self.state is 'MISSING':
            if event == 'missing-files-identified' and not self.isMissingFilesOnHand(arg) :
                self.state = 'REQUEST'
                self.doRequestLocalMissingFiles(arg)
            elif event == 'missing-files-identified' and self.isMissingFilesOnHand(arg) :
                self.state = 'REBUILDING'
                self.doRebuild(arg)
        #---REQUEST---
        elif self.state is 'REQUEST':
            if not self.isStopped(arg) and ( ( event == 'timer-1sec' and self.isAllFilesReceived(arg) ) or event == 'timer-1min' ) :
                self.state = 'REBUILDING'
                self.doRebuild(arg)
            elif event == 'timer-1sec' and self.isStopped(arg) :
                self.state = 'STOPPED'
                self.doDestroyMe(arg)
        #---REBUILDING---
        elif self.state is 'REBUILDING':
            if event == 'rebuilding-finished' :
                self.state = 'DONE'
                self.doWorkDoneReport(arg)
                data_sender.A('new-data')
                self.doDestroyMe(arg)
        #---STOPPED---
        elif self.state is 'STOPPED':
            pass
        #---DONE---
        elif self.state is 'DONE':
            pass

    def isStopped(self, arg):
        return backup_rebuilder.ReadStoppedFlag()
    
    def isMissingFilesOnHand(self, arg):
        for supplierNum in range(self.supplierCount):
            # if supplier do not have the Data but is on line 
            if self.missingData[supplierNum] == 1:
                # ... and we also do not have the Data 
                if self.localData[supplierNum] != 1:
                    # return False - will need request the file   
                    return False
            # same for Parity                
            if self.missingParity[supplierNum] == 1:
                if self.localParity[supplierNum] != 1:
                    return False
        #dhnio.Dprint(8, 'block_rebuilder.isMissingFilesOnHand return True')
        return True
        
    def isAllFilesReceived(self, arg):
        return len(self.requestedFilesList) == 0
    
#    def isAllFilesSent(self):
#        return ( 1 not in self.dataSent ) and ( 1 not in self.paritySent )
    
#    def isOutstandingFiles(self):
#        return len(self.outstandingFilesList) > 0
    
#    def isTimeoutSending(self):
#        result = time.time() - self.sendingStartedTime > self.timeoutSending
#        if result:
#            dhnio.Dprint(6, 'block_rebuilder.isTimeoutSending return True, timeout=%d' % self.timeoutSending)
#        return result
    
    def doIdentifyRemoteMissingFiles(self, arg):
        def do_identify():
            self.availableSuppliers = self.supplierSet.GetActiveArray()
            for supplierNum in range(self.supplierCount):
                if self.availableSuppliers[supplierNum] == 0:
                    continue
                # if remote Data file not exist and supplier is online
                # we mark it as missing and will try to rebuild this file and send to him
                if self.remoteData[supplierNum] != 1:
                    # mark file as missing  
                    self.missingData[supplierNum] = 1
                # same for Parity file
                if self.remoteParity[supplierNum] != 1:
                    self.missingParity[supplierNum] = 1
            return True
        maybeDeferred(do_identify).addCallback(
            lambda x: self.automat('missing-files-identified'))
        
    def doRequestLocalMissingFiles(self, arg):
        self.availableSuppliers = self.supplierSet.GetActiveArray()
        # at the moment I'm download
        # everything I have available and needed
        for supplierNum in range(self.supplierCount):
            # if supplier is not alive - we can't request from him           
            if self.availableSuppliers[supplierNum] == 0:
                continue
            supplierID = self.supplierSet.suppliers[supplierNum]      
            # if the remote Data exist and is available because supplier is on line,
            # but we do not have it on hand - do request  
            if self.remoteData[supplierNum] == 1 and self.localData[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Data')
                io_throttle.QueueRequestFile(
                    self.FileReceived, 
                    self.creatorId, 
                    PacketID, 
                    self.ownerId, 
                    supplierID)
                self.requestedFilesList.append(PacketID)
                self.requestedData[supplierNum] = 1
            # same for Parity
            if self.remoteParity[supplierNum] == 1 and self.localParity[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Parity')
                io_throttle.QueueRequestFile(
                    self.FileReceived, 
                    self.creatorId, 
                    PacketID, 
                    self.ownerId, 
                    supplierID)
                self.requestedFilesList.append(PacketID)
                self.requestedParity[supplierNum] = 1
        
    def doRebuild(self, arg):
#        threads.deferToThread(self.AttemptRepair).addCallback(
#            lambda x: self.automat('rebuilding-thread-finished'))
        maybeDeferred(self.AttemptRebuild).addCallback(
            lambda someNewData: self.automat('rebuilding-finished', someNewData))
        
    def doDestroyMe(self, arg):
        # automats.get_automats_by_index().pop(self.index)
        # reactor.callLater(0, backup_rebuilder.RemoveBlockRebuilder, self)
        backup_rebuilder.RemoveBlockRebuilder(self)
        automat.objects().pop(self.index)
    
#    def doRemoveBlockFiles(self):
#        # we want to remove files for this block 
#        # because we only need them during rebuilding
#        if settings.getGeneralLocalBackups() is True:
#            # if user set this in settings - he want to keep the local files
#            return
#        # ... user do not want to keep local backups
#        if settings.getGeneralWaitSuppliers() is True:
#            # but he want to be sure - all suppliers are green for long time
#            if contact_status.hasOfflineSuppliers() or time.time() - fire_hire.GetLastFireTime() < 24*60*60:
#                # some people are not there or we do not have stable team yet.
#                # do not remove the files because we need it to rebuild
#                return
#        dhnio.Dprint(2, 'block_rebuilder.doRemoveBlockFiles [%s] [%s]' % (self.remoteData, self.remoteParity))
#        for supplierNum in range(self.supplierCount):
#            # data_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Data'))
#            # parity_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Parity'))
#            data_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Data'))
#            parity_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Parity'))
#            if os.path.isfile(data_filename) and self.remoteData[supplierNum] == 1:
#                try:
#                    os.remove(data_filename)
#                    #dhnio.Dprint(6, '    ' + os.path.basename(data_filename))
#                except:
#                    dhnio.DprintException()
#            if os.path.isfile(parity_filename) and self.remoteParity[supplierNum] == 1:
#                try:
#                    os.remove(parity_filename)
#                    #dhnio.Dprint(6, '    ' + os.path.basename(parity_filename))
#                except:
#                    dhnio.DprintException()
        
    def doWorkDoneReport(self, arg):
        if backup_rebuilder.ReadStoppedFlag() is False:
            for supplierNum in range(self.supplierCount):
                # if local file exist and we know we did the request - this mean it is a new file 
                if self.localData[supplierNum] == 1 and self.requestedData[supplierNum] == 1:
                    backups.LocalFileReport(None, self.backupID, self.blockNum, supplierNum, 'Data')
                if self.localParity[supplierNum] == 1 and self.requestedParity[supplierNum] == 1:
                    backups.LocalFileReport(None, self.backupID, self.blockNum, supplierNum, 'Parity')

    #------------------------------------------------------------------------------ 


    def HaveAllData(self, parityMap):
        for segment in parityMap:
            if self.localData[segment] == 0:
                return False
        return True


    def AttemptRebuild(self):
        #dhnio.Dprint(6, 'block_rebuilder.AttemptRepair BEGIN')
        newData = False
        madeProgress = True
        while madeProgress:
            madeProgress = False
            # will check all data packets we have 
            for supplierNum in range(self.supplierCount):
                dataFileName = self.BuildRaidFileName(supplierNum, 'Data')
                # if we do not have this item on hands - we will reconstruct it from other items 
                if self.localData[supplierNum] == 0:
                    parityNum, parityMap = self.eccMap.GetDataFixPath(self.localData, self.localParity, supplierNum)
                    if parityNum != -1:
                        rebuildFileList = []
                        rebuildFileList.append(self.BuildRaidFileName(parityNum, 'Parity'))
                        for supplierParity in parityMap:
                            if supplierParity != supplierNum:
                                rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                        raidread.RebuildOne(rebuildFileList, len(rebuildFileList), dataFileName)
                    if os.path.exists(dataFileName):
                        self.localData[supplierNum] = 1
                        madeProgress = True
                        dhnio.Dprint(12, 'block_rebuilder.AttemptRebuild made progress with supplier %d' % supplierNum)
                # now we check again if we have the data on hand after rebuild at it is missing - send it
                # but also check to not duplicate sending to this man   
                # now sending is separated, see the file data_sender.py          
                if self.localData[supplierNum] == 1 and self.missingData[supplierNum] == 1: # and self.dataSent[supplierNum] == 0:
                    dhnio.Dprint(12, "block_rebuilder.AttemptRebuild new Data for supplier %d" % supplierNum)
                    newData = True
                    # self.outstandingFilesList.append((dataFileName, self.BuildFileName(supplierNum, 'Data'), supplierNum))
                    # self.dataSent[supplierNum] = 1
        # now with parities ...            
        for supplierNum in range(self.supplierCount):
            parityFileName = self.BuildRaidFileName(supplierNum, 'Parity')
            if self.localParity[supplierNum] == 0:
                parityMap = self.eccMap.ParityToData[supplierNum]
                if self.HaveAllData(parityMap):
                    rebuildFileList = []
                    for supplierParity in parityMap:
                        rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                    raidread.RebuildOne(rebuildFileList, len(rebuildFileList), parityFileName)
                    if os.path.exists(parityFileName):
                        dhnio.Dprint(12, 'block_rebuilder.AttemptRebuild parity file found after rebuilding for supplier %d' % supplierNum)
                        self.localParity[supplierNum] = 1
            # so we have the parity on hand and it is missing - send it
            if self.localParity[supplierNum] == 1 and self.missingParity[supplierNum] == 1: # and self.paritySent[supplierNum] == 0:
                dhnio.Dprint(12, 'block_rebuilder.AttemptRebuild new Parity for supplier %d' % supplierNum)
                newData = True
                # self.outstandingFilesList.append((parityFileName, self.BuildFileName(supplierNum, 'Parity'), supplierNum))
                # self.paritySent[supplierNum] = 1
        return newData


#    def SendFileAcked(self, packet, remoteID, packetID):
#        dhnio.Dprint(8, 'block_rebuilder.SendFileAcked to %s with %s' % (nameurl.GetName(remoteID), packetID))
#        try:
#            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
#            blockNum = int(blockNum)
#            supplierNum = int(supplierNum)
#            if dataORparity == 'Data':
#                self.missingData[supplierNum] = 0
#                self.remoteData[supplierNum] = 1
#                self.dataSent[supplierNum] = 2
#            elif dataORparity == 'Parity':
#                self.missingParity[supplierNum] = 0
#                self.remoteParity[supplierNum] = 1
#                self.paritySent[supplierNum] = 2
#            else:
#                dhnio.Dprint(8, "block_rebuilder.SendFileAcked WARNING odd PacketID? -" + str(packetID))
#            if self.sentReports.has_key(packetID):
#                dhnio.Dprint(2, 'block_rebuilder.SendFileAcked WARNING already got sending report for %s' % packetID)
#            self.sentReports[packetID] = 'acked'
#        except:
#            dhnio.DprintException()
#        self.automat('file-sent-report')


#    def SendFileFailed(self, creatorID, packetID, reason):
#        dhnio.Dprint(8, 'block_rebuilder.SendFileFailed to %s with %s (%s)' % (nameurl.GetName(creatorID), packetID, reason))
#        try:
#            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
#            blockNum = int(blockNum)
#            supplierNum = int(supplierNum)
#            if dataORparity == 'Data':
#                self.missingData[supplierNum] = 1
#                self.remoteData[supplierNum] = 0
#                self.dataSent[supplierNum] = 3
#            elif dataORparity == 'Parity':
#                self.missingParity[supplierNum] = 1
#                self.remoteParity[supplierNum] = 0
#                self.paritySent[supplierNum] = 3
#            else:
#                dhnio.Dprint(8, "block_rebuilder.SendFileFailed WARNING odd PacketID? -" + str(packetID))
#            if self.sentReports.has_key(packetID):
#                dhnio.Dprint(2, 'block_rebuilder.SendFileFailed WARNING already got sending report for %s' % packetID)
#            self.sentReports[packetID] = reason
#        except:
#            dhnio.DprintException()
#        self.automat('file-sent-report')


    def FileReceived(self, packet, state):
        if state in ['in queue', 'shutdown']:
            return
        
        if state == 'exist':
            packetID = packet
            filename = os.path.join(settings.getLocalBackupsDir(), packetID)
            try:
                self.requestedFilesList.remove(packetID)
            except:
                dhnio.DprintException()
                return
            try: 
                supplierNum = int((packetID.split("-"))[2])
                if packetID.endswith("-Data"):
                    self.localData[supplierNum] = 1
                elif packetID.endswith("-Parity"):
                    self.localParity[supplierNum] = 1
            except:
                dhnio.DprintException()
            return              

        if state != 'received':
            dhnio.Dprint(4, "block_rebuilder.FileReceived WARNING incorrect state [%s] for packet %s" % (str(state), str(packet)))
            return
            
        packetID = packet.PacketID
        try:
            self.requestedFilesList.remove(packetID)
        except:
            dhnio.DprintException()
            return
        filename = os.path.join(settings.getLocalBackupsDir(), packetID)
        if packet.Valid():
            dhnio.Dprint(8, "block_rebuilder.FileReceived %s, requestedFilesList length is %d" % (packetID, len(self.requestedFilesList)))
            # if we managed to rebuild a file 
            # before a request came in don't overwrite it
            if os.path.exists(filename):
                dhnio.Dprint(4, "block_rebuilder.FileReceived WARNING rewriting existed file" + filename)
                try: 
                    os.remove(filename)
                except:
                    dhnio.DprintException()
            dhnio.WriteFile(filename, packet.Payload)
            try: 
                supplierNum = int((packetID.split("-"))[2])
                if packetID.endswith("-Data"):
                    self.localData[supplierNum] = 1
                elif packetID.endswith("-Parity"):
                    self.localParity[supplierNum] = 1
            except:
                dhnio.DprintException()              
        else:
            # TODO 
            # if we didn't get a valid packet ... re-request it or delete it?
            dhnio.Dprint(8, "block_rebuilder.FileReceived WARNING " + filename + " is not a valid packet")
            try: 
                os.remove(filename)
            except:
                dhnio.DprintException()


    def BuildRaidFileName(self, supplierNumber, dataOrParity):
        # return os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNumber, dataOrParity))
        return os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNumber, dataOrParity))


    def BuildFileName(self, supplierNumber, dataOrParity):
        return packetid.MakePacketID(self.backupID, self.blockNum, supplierNumber, dataOrParity)
        # return self.backupID + "-" + str(self.blockNum) + "-" + str(supplierNumber) + "-" + dataOrParity

#------------------------------------------------------------------------------ 
