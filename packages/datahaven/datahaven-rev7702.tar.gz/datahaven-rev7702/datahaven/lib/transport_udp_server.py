#!/usr/bin/python
#transport_udp_server.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys
import time
import struct
import cStringIO


from twisted.internet import reactor
from twisted.internet.task import LoopingCall 
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol


import dhnio
import misc
import nameurl
import tmpfile
import settings

import automat

#------------------------------------------------------------------------------ 

CODES = {'p:':  'PING',
         'g:':  'GREETING',
         'd:':  'DATA',
         'r:':  'REPORT',
         'a:':  'ALIVE',}

COMMANDS = {'PING':         'p:',
            'GREETING':     'g:',
            'DATA':         'd:',
            'REPORT':       'r:',
            'ALIVE':        'a:',}

BLOCK_SIZE_LEVELS = {   #0: 508,
                        0: 1460,
                        1: 2048,
                        2: 3072,
                        3: 4096,
                        4: 5120,
                        5: 6144,
                        6: 7168,
                        7: 8124,
                        }
MAX_BLOCK_SIZE_LEVEL = len(BLOCK_SIZE_LEVELS) - 1

#BLOCK_SIZE = 4096
TIME_OUT = 20
BLOCK_RETRIES = 5
MAX_WINDOW_SIZE = 32
MIN_WINDOW_SIZE = 1

_Protocol = None

_ReceiveStatusCallback = None
_SendStatusCallback = None
_ReceiveControlFunc = None
_SendControlFunc = None
_RegisterTransferFunc = None
_UnRegisterTransferFunc = None

#------------------------------------------------------------------------------ 

def init(udp_client):
    global _Protocol
    dhnio.Dprint(4, 'transport_udp_server.init')
    if _Protocol is None:
        _Protocol = TransportUDPServer(udp_client)
        dhnio.Dprint(4, '  TransportUDPServer() created')
    else:
        dhnio.Dprint(4, '  TransportUDPServer() object already created')
    # udp_client.datagram_received_callback = _Protocol.datagramReceived

def shutdown():
    global _Protocol
    dhnio.Dprint(4, 'transport_udp_server.shutdown')
    _Protocol = None

def send(addr, filename, fast=False, description=''):
    global _Protocol
    if _Protocol is not None:
        _Protocol.send(filename, addr, fast, description)
        
def protocol():
    global _Protocol
    return _Protocol

#------------------------------------------------------------------------------ 

def file_received(filename, status, proto='', host=None, error=None, message=''):
    global _ReceiveStatusCallback
    if _ReceiveStatusCallback is not None:
        _ReceiveStatusCallback(filename, status, proto, host, error, message)
    
    
def file_sent(host, filename, status, proto='', error=None, message=''):
    global _SendStatusCallback
    if _SendStatusCallback is not None:
        _SendStatusCallback(host, filename, status, proto, error, message)

#------------------------------------------------------------------------------ 

def SetReceiveStatusCallback(cb):
    global _ReceiveStatusCallback
    _ReceiveStatusCallback = cb
    
    
def SetSendStatusCallback(cb):
    global _SendStatusCallback
    _SendStatusCallback = cb

def SetSendControlFunc(f):
    global _SendControlFunc
    _SendControlFunc = f
    
def SetReceiveControlFunc(f):
    global _ReceiveControlFunc
    _ReceiveControlFunc = f
    
def SetRegisterTransferFunc(f):
    global _RegisterTransferFunc
    _RegisterTransferFunc = f

def SetUnRegisterTransferFunc(f):
    global _UnRegisterTransferFunc
    _UnRegisterTransferFunc = f
    
#------------------------------------------------------------------------------ 

class OutboxFile():
    def __init__(self, peer, file_id, filename, description=''):
        global _RegisterTransferFunc
        self.peer = peer
        self.file_id = file_id
        self.filename = filename
        self.description = description
        try:
            self.size = os.path.getsize(self.filename)
        except:
            self.size = -1
        self.blocks = {}
        self.failed_blocks = {}
        self.num_blocks = 0
        self.bytes_sent = 0
        self.current_block_id = -1
        self.last_bytes_sent = 0
        self.has_failed_blocks = False
        self.state = 'INIT'
        self.transfer_id = None
        self.started = time.time()
        self.timeout = max( 2*int(self.size/settings.SendingSpeedLimit()), 120)        
        if _RegisterTransferFunc is not None:
            self.transfer_id = _RegisterTransferFunc('send', self.peer.remote_address, self.get_bytes_sent, self.filename, self.size, self.description)
        # dhnio.Dprint(6, 'transport_udp_server.OutboxFile [%d] to %s' % (self.file_id, str(self.peer.remote_address)))

    def close(self):
        global _UnRegisterTransferFunc
        if _UnRegisterTransferFunc is not None and self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(8, 'transport_udp_server.OutboxFile deleted [%d] to %s' % (self.file_id, str(self.peer.remote_address)))

    def get_bytes_sent(self):
        return self.bytes_sent

    def report_block(self, block_id):
        if not self.blocks.has_key(block_id):
            # dhnio.Dprint(2, 'transport_udp_session.report_block WARNING unknown block_id in REPORT packet received from %s: [%d]' % (self.remote_address, block_id))
            return
        self.bytes_sent += len(self.blocks[block_id])
        del self.blocks[block_id]
        
    def read(self):
        fin = open(self.filename, 'rb')
        block_id = 0
        while True:
            block_data = fin.read(BLOCK_SIZE_LEVELS[self.peer.block_size_level])
            if block_data == '':
                break
            self.blocks[block_id] = block_data
            block_id += 1    
        fin.close()  
        self.num_blocks = block_id
        self.current_block_id = 0
        self.last_bytes_sent = 0
        self.state = 'READ'

    def mark_failed_block(self, block_id):
        if not self.failed_blocks.has_key(block_id):
            self.failed_blocks[block_id] = 0
        self.failed_blocks[block_id] += 1
        if self.failed_blocks[block_id] >= BLOCK_RETRIES:
            self.has_failed_blocks = True
            # dhnio.Dprint(8, 'transport_udp_server.OutboxFile.mark_failed_block (%d,%d) is failed to send' % (self.file_id, block_id))
            return True
        return False
        
    def send_block(self, block_id):
        global _SendControlFunc
        data = self.blocks[block_id]
        if _SendControlFunc is not None:
            more_bytes = _SendControlFunc(self.last_bytes_sent, len(data))
            if more_bytes < len(data):
                return False
        self.last_bytes_sent = len(data)
        datagram = COMMANDS['DATA']
        datagram += struct.pack('i', self.file_id)
        datagram += struct.pack('i', block_id)
        datagram += struct.pack('i', self.num_blocks)
        datagram += struct.pack('i', len(data))
        datagram += data
        return self.peer.transport.sendDatagram(datagram, self.peer.remote_address) 
        # dhnio.Dprint(18, 'transport_udp_server.send_block [%d,%d] to %s' % (self.file_id, block_id, self.peer.remote_address))       
        
    def send(self):
        if self.state == 'INIT':
            return False
        if self.state == 'READ':
            self.state = 'SEND'
        do_send = False
        while len(self.peer.sliding_window) < self.peer.sliding_window_size and self.current_block_id < self.num_blocks:
            if not self.send_block(self.current_block_id):
                break
            self.peer.sliding_window[(self.file_id, self.current_block_id)] = time.time()
            self.current_block_id += 1
            do_send = True
        self.peer.check_window()
        return do_send

    def is_timed_out(self):
        return time.time() - self.started > self.timeout
        

class InboxFile():
    def __init__(self, peer, file_id, num_blocks):
        global _RegisterTransferFunc
        self.fd, self.filename = tmpfile.make("udp-in")
        self.peer = peer
        self.file_id = file_id
        self.num_blocks = num_blocks
        self.blocks = {}
        self.bytes_received = 0
        self.transfer_id = None
        if _RegisterTransferFunc is not None:
            self.transfer_id = _RegisterTransferFunc('receive', self.peer.remote_address, self.get_bytes_received, self.filename, -1, '')
        # dhnio.Dprint(6, 'transport_udp_server.InboxFile [%d] from %s' % (self.file_id, str(self.peer.remote_address)))

    def close(self):
        global _UnRegisterTransferFunc
        if _UnRegisterTransferFunc is not None and self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(6, 'transport_udp_server.InboxFile deleted [%d] from %s' % (self.file_id, str(self.peer.remote_address)))

    def get_bytes_received(self):
        return self.bytes_received
        
    def input_block(self, block_id, block_data):
        self.blocks[block_id] = block_data
        self.bytes_received += len(block_data) 
    
    def build(self):
        for block_id in range(len(self.blocks)):
            os.write(self.fd, self.blocks[block_id])
        os.close(self.fd)
        # dhnio.Dprint(10, 'transport_udp_server.InboxFile.build [%s] file_id=%d, blocks=%d' % (
        #     os.path.basename(filename), file_id, len(self.incommingFiles[file_id])))
    


class UDPPeer():
    def __init__(self, transport, addr):
        self.transport = transport
        self.remote_address = addr
        self.incommingFiles = {}
        self.receivedFiles = {}
        self.outgoingFiles = {}
        self.outboxQueue = []
        self.sliding_window = {}
        self.sliding_window_size = MIN_WINDOW_SIZE
        self.last_alive_packet_time = time.time()
        self.block_size_level = 0
        dhnio.Dprint(8, 'UDPPeer %s created' % str(self.remote_address))
    
    def read_outbox_file(self, filename, description=''):
        file_id = self.transport.make_file_ID()
        outFile = OutboxFile(self, file_id, filename, description)
        outFile.read()
        self.outgoingFiles[file_id] = outFile
        # dhnio.Dprint(10, 'transport_udp_server.UDPPeer.read_outbox_file [%s] file_id=%d, blocks=%d' % (os.path.basename(filename), file_id, outFile.num_blocks))
        return file_id
   
    def add_outbox_file(self, filename, description=''):
        self.outboxQueue.append((filename, description))
#        dhnio.Dprint(10, 'UDPPeer.add_outbox_file [%s] to %s' % (os.path.basename(filename), str(self.remote_address)))        

    def put_outbox_file(self, filename, description=''):
        self.outboxQueue.insert(0, (filename, description))
#        dhnio.Dprint(10, 'UDPPeer.put_outbox_file [%s] to %s' % (os.path.basename(filename), str(self.remote_address)))        

    def check_queue(self):
        if len(self.outgoingFiles) > 2:
            return False
        if len(self.outboxQueue) == 0:
            return False
        filename, description = self.outboxQueue.pop(0)
        self.read_outbox_file(filename, description)
        return True
    
    def is_alive(self):
        return time.time() - self.last_alive_packet_time < 60 * 3.0
    
    def shutdown(self):
        dhnio.Dprint(8, 'UDPPeer %s shutdown' % str(self.remote_address))
        for file_id in self.outgoingFiles.keys():
            file_sent(self.remote_address, self.outgoingFiles[file_id].filename, 'failed', 'udp', None, 'session has been closed')

    def keep_alive(self):
        self.transport.sendDatagram(COMMANDS['ALIVE'], self.remote_address)

    def erase_old_file_ids(self):
        if len(self.receivedFiles) > 10:
            file_ids = self.receivedFiles.keys()
            cur_tm = time.time()
            for file_id in file_ids:
                if cur_tm - self.receivedFiles[file_id] > 60 * 20:
                    del self.receivedFiles[file_id]
            del file_ids 
    
    def check_window(self):
        if len(self.sliding_window) == 0:
            return
        # dhnio.Dprint(8, 'transport_udp_server.check_window has %d items' % len(self.sliding_window))
        to_remove = [] 
        to_update = {}
        cur_tm = time.time()
        for block_info, tm in self.sliding_window.items():
            if cur_tm - tm < TIME_OUT: # give some time to get an Ack. 
                continue
            to_remove.append(block_info)
            file_id = block_info[0]
            block_id = block_info[1]
            if not self.outgoingFiles.has_key(file_id):
                # dhnio.Dprint(2, 'transport_udp_server.check_window WARNING unknown file_id: %d' % file_id)
                continue
            if not self.outgoingFiles[file_id].blocks.has_key(block_id):
                dhnio.Dprint(2, 'transport_udp_server.check_window WARNING unknown block_id: %d' % block_id)
                continue
            self.outgoingFiles[file_id].send_block(block_id)
            isFailed = self.outgoingFiles[file_id].mark_failed_block(block_id)
            if not isFailed:
                to_update[block_info] = cur_tm
        for block_info in to_remove:
            del self.sliding_window[block_info]
            # dhnio.Dprint(8, 'transport_udp_server.check_window (%d,%d) removed, window=%d' % (file_id, block_id, len(self.sliding_window)))
        for block_info, tm in to_update.items():
            self.sliding_window[block_info] = tm
            # dhnio.Dprint(8, 'transport_udp_server.check_window %s resending to %s, window=%d' % (block_info, self.remote_address, len(self.sliding_window)))
        if len(to_remove) > 0:
            self.sliding_window_size = int( self.sliding_window_size / 2.0 )
            if self.sliding_window_size < MIN_WINDOW_SIZE:
                self.sliding_window_size = MIN_WINDOW_SIZE
            # dhnio.Dprint(8, 'transport_udp_server.check_window decreased, window=%d' % self.sliding_window_size)
        del to_remove
        del to_update

    def datagram_received(self, cmd, io):
        self.last_alive_packet_time = time.time()
        #---DATA---
        if cmd == 'DATA':
            try:
                file_id = struct.unpack('i', io.read(4))[0]
                block_id = struct.unpack('i', io.read(4))[0]
                num_blocks = struct.unpack('i', io.read(4))[0]
                data_size = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            if not self.incommingFiles.has_key(file_id):
                if self.receivedFiles.has_key(file_id):
                    self.transport.sendDatagram(COMMANDS['REPORT'] + struct.pack('i', file_id) + struct.pack('i', block_id), self.remote_address)
                    return
                # self.incommingFiles[file_id] = {}
                self.incommingFiles[file_id] = InboxFile(self, file_id, num_blocks)
            inp_data = io.read()
            if len(inp_data) < data_size:
                # dhnio.Dprint(2, 'transport_udp_server.UDPPeer.datagram_received WARNING not full data from [%s]' % (str(self.remote_address)))
                return
            self.incommingFiles[file_id].input_block(block_id, inp_data) 
            self.transport.sendDatagram(COMMANDS['REPORT'] + struct.pack('i', file_id) + struct.pack('i', block_id), self.remote_address)            # dhnio.Dprint(10, 'transport_udp_server.UDPPeer.datagram_received DATA [%d,%d/%d] from %s' % (file_id, block_id, num_blocks, self.remote_address))
            if len(self.incommingFiles[file_id].blocks) == num_blocks:
                self.incommingFiles[file_id].build()
                file_received(self.incommingFiles[file_id].filename, 'finished', 'udp', self.remote_address)              
                self.incommingFiles[file_id].close()
                del self.incommingFiles[file_id]
                self.receivedFiles[file_id] = time.time()
                self.erase_old_file_ids()
        #---REPORT---        
        elif cmd == 'REPORT':
            try:
                file_id = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            if not self.outgoingFiles.has_key(file_id):
                return
            try:
                block_id = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            if not self.outgoingFiles[file_id].blocks.has_key(block_id):
                # dhnio.Dprint(2, 'transport_udp_server.UDPPeer.datagram_received WARNING unknown block_id in REPORT packet received: [%d]' % block_id)
                return
            # dhnio.Dprint(8, 'transport_udp_server.UDPPeer.datagram_received REPORT for [%d,%d] from %s, window=%d' % (file_id, block_id, self.remote_address, len(self.sliding_window)))
            self.outgoingFiles[file_id].report_block(block_id)
            self.sliding_window.pop((file_id, block_id), None)
            self.sliding_window_size += 1
            if self.sliding_window_size > MAX_WINDOW_SIZE:
                self.sliding_window_size = MAX_WINDOW_SIZE
            if len(self.outgoingFiles[file_id].blocks) == 0:
                file_sent(self.remote_address, self.outgoingFiles[file_id].filename, 'finished', 'udp')
                self.outgoingFiles[file_id].close()
                del self.outgoingFiles[file_id]
                self.block_size_level += 1
                if self.block_size_level > MAX_BLOCK_SIZE_LEVEL:
                    self.block_size_level = MAX_BLOCK_SIZE_LEVEL
                # dhnio.Dprint(8, 'transport_udp_server.UDPPeer.datagram_received [%s] sending finished to %s' % (os.path.basename(filename), self.remote_address))
        #---PING---    
        elif cmd == 'PING':
            self.transport.sendDatagram(COMMANDS['GREETING']+misc.getLocalID(), self.remote_address)
        #---GREETING---
        elif cmd == 'GREETING':
            self.transport.sendDatagram(COMMANDS['ALIVE'], self.remote_address)
        #---ALIVE---
        elif cmd == 'ALIVE':
            pass
            #self.transport.sendDatagram(COMMANDS['ALIVE'], self.remote_address)
        

class TransportUDPServer():
    def __init__(self, client):
        self.client = client
        self.peers = {}
        self.sending_worker = None
        self.queue_worker = None
        self.max_sending_delay = settings.MaximumSendingDelay()
        self.min_sending_delay = settings.MinimumSendingDelay()
        self.sending_delay = self.min_sending_delay
        self.max_queue_delay = settings.MaximumSendingDelay()
        self.min_queue_delay = settings.MinimumSendingDelay()
        self.queue_delay = self.min_queue_delay
        self.last_file_id = 0
        reactor.callLater(0, self.process_outbox_queue)
        reactor.callLater(1, self.process_sending)
        LoopingCall(self.process_close_sessions).start(60, False)
        LoopingCall(self.process_keep_alive).start(60, False)
    
    def sendDatagram(self, datagram, addr):
        try:
            self.client.transport.write(datagram, addr)
            # dhnio.Dprint(10, '    [UDP] %d bytes to %s' % (len(datagram), addr))
            return True
        except:
            # dhnio.Dprint(2, '     [UDP] WARNING cant write to %s' % (addr))
            return False    
    
    def datagramReceived(self, datagram, addr):
        global _ReceiveControlFunc
        try:
            from transport_control import black_IPs_dict
            if addr[0] in black_IPs_dict().keys() or '.'.join(addr[0].split('.')[:-1]) in black_IPs_dict().keys():
                # dhnio.Dprint(12, 'transport_udp_server.datagramReceived %d bytes from BLACK IP: %s, %s' % (len(datagram), str(addr[0]), str(black_IPs_dict()[addr[0]])) )
                return
        except:
            pass
        if len(datagram) < 2:
            return
        io = cStringIO.StringIO(datagram)
        code = io.read(2)
        if code.strip() == '':
            return
        cmd = CODES.get(code, None)
        if cmd is None:
            # dhnio.Dprint(8, '                [UDP] WARNING wrong code from %s' % (addr,))
            return
        # dhnio.Dprint(10, '                   [UDP] %d bytes from %s (%s)' % (len(datagram), addr, cmd))
        if _ReceiveControlFunc is not None:
            seconds_pause = _ReceiveControlFunc(len(datagram))
            if seconds_pause > 0:
                # print 'paused for', seconds_pause, 'seconds'
                self.client.transport.pauseProducing()
                reactor.callLater(seconds_pause, self.client.transport.resumeProducing)
        if not self.peers.has_key(addr):
            self.peers[addr] = UDPPeer(self, addr)
        self.peers[addr].datagram_received(cmd, io)
        io.close()
        del io
        
    def make_file_ID(self):
        file_id = int(str(int(time.time() * 100.0))[4:])
        if self.last_file_id == file_id:
            file_id += 1
        self.last_file_id = file_id 
        return self.last_file_id
        
    def process_sending(self):
        do_sends = False
        for addr in self.peers.keys():
            failed_ids = []
            for file_id in self.peers[addr].outgoingFiles.keys():
                if self.peers[addr].outgoingFiles[file_id].send():
                    do_sends = True
                if self.peers[addr].outgoingFiles[file_id].has_failed_blocks:
                    failed_ids.append((file_id, 'has failed blocks'))
                elif self.peers[addr].outgoingFiles[file_id].is_timed_out():
                    failed_ids.append((file_id, 'timeout'))
                    # dhnio.Dprint(8, 'transport_udp_server.process_sending [%d] has failed blocks' % file_id)
            for file_id, why in failed_ids:
                self.peers[addr].block_size_level -= 2
                if self.peers[addr].block_size_level < 0:
                    self.peers[addr].block_size_level = 0
                file_sent(addr, self.peers[addr].outgoingFiles[file_id].filename, 'failed', 'udp', None, why)
                self.peers[addr].outgoingFiles[file_id].close()
                del self.peers[addr].outgoingFiles[file_id]
            del failed_ids

        self.sending_delay = misc.LoopAttenuation(
            self.sending_delay, 
            do_sends, 
            self.min_sending_delay, 
            self.max_sending_delay)
        # attenuation
        self.sending_worker = reactor.callLater(self.sending_delay, self.process_sending)

    def check_outbox_queues(self):
        has_files = False
        for addr in self.peers.keys():
            if self.peers[addr].check_queue():
                has_files = True
        return has_files

    def process_outbox_queue(self):
        has_files = self.check_outbox_queues()

        self.queue_delay = misc.LoopAttenuation(
            self.queue_delay, 
            has_files, 
            self.min_queue_delay, 
            self.max_queue_delay)
        # attenuation
        self.queue_worker = reactor.callLater(self.queue_delay, self.process_outbox_queue)

    def send(self, filename, addr, fast=False, description=''):
        if not self.peers.has_key(addr):
            self.peers[addr] = UDPPeer(self, addr)
        if fast:
            self.peers[addr].put_outbox_file(filename, description)
        else:
            self.peers[addr].add_outbox_file(filename, description)
        self.check_outbox_queues()
    
    def process_close_sessions(self):
        dead_peers = []
        peers_count = 0
        outbox_files_count = 0
        inbox_files_count = 0
        for addr in self.peers.keys():
            peers_count += 1
            outbox_files_count += len(self.peers[addr].outgoingFiles)
            inbox_files_count += len(self.peers[addr].incommingFiles)
            if not self.peers[addr].is_alive():
                dead_peers.append(addr)
        for addr in dead_peers:
            self.peers[addr].shutdown()
            del self.peers[addr]
        del dead_peers
        dhnio.Dprint(10, 'transport_udp_server.process_close_sessions peers=%d, outbox_files=%d, inbox_files=%d' % (peers_count, outbox_files_count, inbox_files_count))

    def process_keep_alive(self):
        for addr in self.peers.keys():
            self.peers[addr].keep_alive()

#------------------------------------------------------------------------------ 
    
def main():
    start(int(sys.argv[1]))
    reactor.run()
    
if __name__ == '__main__':
    main()

    
    
    




