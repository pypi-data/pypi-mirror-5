#!/usr/bin/python
#webcontrol.py
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
import locale
import pprint
import random
import textwrap
import webbrowser
import math
import cStringIO
import calendar

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in webcontrol.py')

from twisted.internet.defer import Deferred, succeed
from twisted.web import server
from twisted.web import resource
from twisted.web import static
from twisted.web import http
from twisted.web.server import Session
from twisted.web.server import NOT_DONE_YET

#-------------------------------------------------------------------------------

import lib.misc as misc
import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.settings as settings
import lib.diskspace as diskspace
import lib.dirsize as dirsize
import lib.diskusage as diskusage
import lib.commands as commands
import lib.transport_control as transport_control
import lib.contacts as contacts
import lib.nameurl as nameurl
import lib.dhncrypto as dhncrypto
import lib.schedule as schedule
import lib.automat as automat
import lib.webtraffic as webtraffic

import initializer
import shutdowner
import installer
import network_connector
import p2p_connector
import central_connector
import fire_hire
import contact_status
import backup_rebuilder

import dhnupdate
import identitypropagate
import central_service
import p2p_service
import dobackup
import backup_db
import backups
import backup_monitor
import backupshedule
import restore_monitor
import io_throttle
import money
import message
import events
import ratings 

#-------------------------------------------------------------------------------

myweblistener = None
init_done = False
read_only_state = True
local_port = 0
current_url = ''
current_pagename = ''
labels = {}
menu_order = []
installing_process_str = ''
install_page_ready = True
global_version = ''
local_version = ''
revision_number = ''
root_page_src = ''
centered_page_src = ''
url_history = [] # ['/main']
pagename_history = [] # ['main']
_DHNViewCommandFunc = []

#------------------------------------------------------------------------------

_PAGE_ROOT = ''
_PAGE_STARTING = 'starting'
_PAGE_MAIN = 'main'
_PAGE_BACKUPS = 'main'
_PAGE_MENU = 'menu'
_PAGE_CONFIRM = 'confirm'
_PAGE_BUSY = 'busy'
_PAGE_BACKUP = 'backup'
_PAGE_BACKUP_LOCAL_FILES = 'localfiles'
_PAGE_BACKUP_REMOTE_FILES = 'remotefiles'
_PAGE_BACKUP_RUNNING = 'running'
_PAGE_BACKUP_RESTORING = 'restoring'
_PAGE_BACKUP_IMAGE = 'image'
_PAGE_BACKUP_DIAGRAM = 'diagram'
_PAGE_RESTORE = 'restore'
_PAGE_SUPPLIERS = 'suppliers'
_PAGE_SUPPLIER = 'supplier'
_PAGE_SUPPLIER_REMOTE_FILES = 'supplierremotefiles'
_PAGE_SUPPLIER_LOCAL_FILES = 'supplierlocalfiles'
_PAGE_SUPPLIER_CHANGE = 'supplierchange'
_PAGE_CUSTOMERS = 'customers'
_PAGE_CUSTOMER = 'customer'
_PAGE_CUSTOMER_FILES = 'customerfiles'
_PAGE_STORAGE = 'storage'
_PAGE_STORAGE_NEEDED = 'neededstorage'
_PAGE_STORAGE_DONATED = 'donatedstorage'
_PAGE_CONFIG = 'config'
_PAGE_CONTACTS = 'contacts'
_PAGE_CENTRAL = 'central'
_PAGE_SETTINGS = 'settings'
_PAGE_SETTINGS_LIST = 'settingslist'
_PAGE_SETTING_NODE = 'settingnode'
_PAGE_PRIVATE = 'private'
_PAGE_MONEY = 'money'
_PAGE_MONEY_ADD = 'moneyadd'
_PAGE_TRANSFER = 'transfer'
_PAGE_RECEIPTS = 'receipts'
_PAGE_RECEIPT = 'receipt'
_PAGE_DIR_SELECT = 'dirselect'
_PAGE_INSTALL = 'install'
_PAGE_INSTALL_NETWORK_SETTINGS = 'installproxy'
_PAGE_UPDATE = 'update'
_PAGE_MESSAGES = 'messages'
_PAGE_MESSAGE = 'message'
_PAGE_NEW_MESSAGE = 'newmessage'
_PAGE_CORRESPONDENTS = 'correspondents'
_PAGE_SHEDULE = 'shedule'
_PAGE_BACKUP_SHEDULE = 'backupshedule'
_PAGE_UPDATE_SHEDULE = 'updateshedule'
_PAGE_DEV_REPORT = 'devreport'
_PAGE_BACKUP_SETTINGS = 'backupsettings'
_PAGE_SECURITY = 'security'
_PAGE_NETWORK_SETTINGS = 'network'
_PAGE_DEVELOPMENT = 'development'
#_PAGE_PATHS = 'paths'
_PAGE_AUTOMATS = 'automats'
_PAGE_MEMORY = 'memory'
_PAGE_EMERGENCY = 'emergency'
_PAGE_MONITOR_TRANSPORTS = 'monitortransports'
_PAGE_TRAFFIC = 'traffic'
_PAGE_CSPACE_CONTROL = 'cspace'

#------------------------------------------------------------------------------ 

_MenuItems = {
    '0|backups'             :('/'+_PAGE_MAIN,               'icons/backup01.png'),
    '1|users'               :('/'+_PAGE_SUPPLIERS,          'icons/users01.png'),
    '2|storage'             :('/'+_PAGE_STORAGE,            'icons/storage01.png'),
    '3|settings'            :('/'+_PAGE_CONFIG,             'icons/settings01.png'),
    '4|money'               :('/'+_PAGE_MONEY,              'icons/money01.png'),
    '5|messages'            :('/'+_PAGE_MESSAGES,           'icons/messages01.png'),
    '6|friends'             :('/'+_PAGE_CORRESPONDENTS,     'icons/handshake01.png'),
    #'4|shutdown'            :('/?action=exit',              'icons/exit.png'),
    }

_SettingsItems = {
    '0|backups'             :('/'+_PAGE_BACKUP_SETTINGS,    'icons/backup-options.png'),
    '1|security'            :('/'+_PAGE_SECURITY,           'icons/private-key.png'),
    '2|network'             :('/'+_PAGE_NETWORK_SETTINGS,   'icons/network-settings.png'),
    '3|emergency'           :('/'+_PAGE_EMERGENCY,          'icons/emergency01.png'),
    '4|updates'             :('/'+_PAGE_UPDATE,             'icons/software-update.png'),
    '5|development'         :('/'+_PAGE_DEVELOPMENT,        'icons/python.png'),
    #'5|shutdown'            :('/?action=exit',              'icons/exit.png'),
    }

_MessageColors = {
    'success': 'green',
    'done': 'green',
    'failed': 'red',
    'error': 'red',
    'info': 'black',
    'warning': 'red',
    'notify': 'blue',
    }

_SettingsTreeNodesDict = {}
_SettingsTreeComboboxNodeLists = {}

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def init(port = 6001):
    global myweblistener
    dhnio.Dprint(2, 'webcontrol.init ')

    if myweblistener:
        global local_port
        dhnio.Dprint(2, 'webcontrol.init SKIP, already started on port ' + str(local_port))
        return succeed(local_port)

    events.init(DHNViewSendCommand)
    
    # links
    transport_control.SetContactAliveStateNotifierFunc(OnAliveStateChanged)
    p2p_service.SetTrafficInFunc(OnTrafficIn)
    p2p_service.SetTrafficOutFunc(OnTrafficOut)
    # io_throttle.SetPacketReportCallbackFunc(OnSupplierQueuePacketCallback)
    # list_files_orator.SetRepaintFunc(OnRepaintBackups)

    def version():
        global local_version
        global revision_number
        dhnio.Dprint(4, 'webcontrol.init.version')
        if dhnio.Windows() and dhnio.isFrozen():
            local_version = dhnio.ReadBinaryFile(settings.VersionFile())
        else:
            local_version = None
        revision_number = dhnio.ReadTextFile(settings.RevisionNumberFile()).strip()

    def html():
        global root_page_src
        global centered_page_src
        dhnio.Dprint(4, 'webcontrol.init.html')

        root_page_src = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>%(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=%(encoding)s" />
%(reload_tag)s
</head>
<body>
<table width="100%%" align=center cellspacing=0 cellpadding=0>
<tr>
<td align=left width=50 nowrap>%(back)s</td>
<td>&nbsp;</td>
<td align=center width=50 nowrap>%(home)s</td>
<td>&nbsp;</td>
<td align=right width=50 nowrap>%(next)s</td>
</tr>
</table>
%(align1)s
%(body)s
%(debug)s
%(align2)s
</body>
</html>'''

        centered_page_src = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>%(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=%(encoding)s" />
</head>
<body>
<center>
%(body)s
</center>
</body>
</html>'''

    def settings_tree():
        init_settings_tree()

    def site():
        dhnio.Dprint(4, 'webcontrol.init.site')
        root = resource.Resource()
        root.putChild(_PAGE_STARTING, StartingPage())
        root.putChild(_PAGE_ROOT, RootPage())
        root.putChild(_PAGE_MAIN, MainPage())
        root.putChild(_PAGE_MENU, MenuPage())
        # root.putChild(_PAGE_BUSY, BusyPage())
        root.putChild(_PAGE_INSTALL, InstallPage())
        root.putChild(_PAGE_INSTALL_NETWORK_SETTINGS, InstallNetworkSettingsPage())
        root.putChild(_PAGE_SUPPLIERS, SuppliersPage())
        root.putChild(_PAGE_CUSTOMERS, CustomersPage())
        root.putChild(_PAGE_STORAGE, StoragePage())
        root.putChild(_PAGE_CONFIG, ConfigPage())
        root.putChild(_PAGE_BACKUP_SETTINGS, BackupSettingsPage())
        root.putChild(_PAGE_UPDATE, UpdatePage())
        root.putChild(_PAGE_SETTINGS, SettingsPage())
        root.putChild(_PAGE_SETTINGS_LIST, SettingsListPage())
        root.putChild(_PAGE_SECURITY, SecurityPage())
        root.putChild(_PAGE_NETWORK_SETTINGS, NetworkSettingsPage())
        root.putChild(_PAGE_MONEY, MoneyPage())
        root.putChild(_PAGE_MONEY_ADD, MoneyAddPage())
        root.putChild(_PAGE_TRANSFER, TransferPage())
        root.putChild(_PAGE_RECEIPTS, ReceiptsPage())
        root.putChild(_PAGE_MESSAGES, MessagesPage())
        root.putChild(_PAGE_NEW_MESSAGE, NewMessagePage())
        root.putChild(_PAGE_CORRESPONDENTS, CorrespondentsPage())
        root.putChild(_PAGE_BACKUP_SHEDULE, BackupShedulePage())
        root.putChild(_PAGE_UPDATE_SHEDULE, UpdateShedulePage())
        root.putChild(_PAGE_DEV_REPORT, DevReportPage())
        root.putChild(_PAGE_DEVELOPMENT, DevelopmentPage())
        root.putChild(_PAGE_AUTOMATS, AutomatsPage())
        root.putChild(_PAGE_MEMORY, MemoryPage())
        root.putChild(_PAGE_EMERGENCY, EmergencyPage())
        root.putChild(_PAGE_MONITOR_TRANSPORTS, MonitorTransportsPage())
        root.putChild(_PAGE_TRAFFIC, TrafficPage())
        root.putChild(_PAGE_CONFIRM, ConfirmPage())
        root.putChild(settings.IconFilename(), static.File(settings.IconFilename()))
        root.putChild('icons', static.File(settings.IconsFolderPath()))
        # misc.StartWebTraffic(root, _PAGE_TRAFFIC)
        return LocalSite(root)

    def done(x):
        global local_port
        dhnio.Dprint(4, 'webcontrol.init.done')
        local_port = int(x)
        dhnio.WriteFile(settings.LocalPortFilename(), str(local_port))
        dhnio.Dprint(4, 'webcontrol.init.done local server started on port %d' % local_port)

    def start_listener(site):
        dhnio.Dprint(4, 'webcontrol.start_listener')
        def _try(site, result):
            global myweblistener
            port = random.randint(6001, 6999)
            dhnio.Dprint(4, 'webcontrol.init.start_listener._try port=%d' % port)
            try:
                l = reactor.listenTCP(port, site)
            except:
                dhnio.Dprint(2, 'webcontrol.init.start_listener._try it seems port %d is busy' % port)
                l = None
            if l is not None:
                myweblistener = l
                result.callback(port)
                return
            reactor.callLater(1, _try, site, result)

        result = Deferred()
        reactor.callLater(0, _try, site, result)
        return result

    def run(site):
        dhnio.Dprint(4, 'webcontrol.init.run')
        d = start_listener(site)
        d.addCallback(done)
        return d

    version()
    html()
    settings_tree()
    s = site()
    d = run(s)
    return d

def show(x=None):
    global local_port

    if dhnio.Linux() and not dhnio.X11_is_running():
        dhnio.Dprint(0, 'X11 is not running, can not start DataHaven.NET GUI')
        return
    
    if local_port == 0:
        try:
            local_port = int(dhnio.ReadBinaryFile(settings.LocalPortFilename()))
        except:
            pass

    dhnio.Dprint(2, 'webcontrol.show local port is %s' % str(local_port))

    if not local_port:
        dhnio.Dprint(4, 'webcontrol.show ERROR can not read local port number')
        return

    appList = dhnio.find_process(['dhnview.', ])
    if len(appList):
        dhnio.Dprint(2, 'webcontrol.show SKIP, we found another dhnview process running at the moment, pid=%s' % appList)
        DHNViewSendCommand('raise')
        return

    try:
        if dhnio.Windows():
            if dhnio.isFrozen():
                pypath = os.path.abspath('dhnview.exe')
                os.spawnv(os.P_DETACH, pypath, ('dhnview.exe',))
            else:
                pypath = sys.executable
                os.spawnv(os.P_DETACH, pypath, ('python', 'dhnview.py',))
        else:
            pid = os.fork()
            if pid == 0:
                os.execlp('python', 'python', 'dhnview.py',)
    except:
        dhnio.DprintException()


def ready(state=True):
    global init_done
    init_done = state
    dhnio.Dprint(4, 'webcontrol.ready is ' + str(init_done))


def kill():
    total_count = 0
    while True:
        count = 0
        dhnio.Dprint(2, 'webcontrol.kill do search for "dhnview." in the processes list')
        appList = dhnio.find_process(['dhnview.', ])
        for pid in appList:
            count += 1
            dhnio.Dprint(2, 'webcontrol.kill want to stop pid %d' % pid)
            dhnio.kill_process(pid)
        if len(appList) == 0:
            dhnio.Dprint(2, 'webcontrol.kill no more "dhnview." processes found')
            return 0
        total_count += 1
        if total_count > 10:
            dhnio.Dprint(2, 'webcontrol.kill ERROR: some "dhnview." processes found, but can not stop tham')
            dhnio.Dprint(2, 'webcontrol.kill may be we do not have permissions to stop tham?')
            return 1
        time.sleep(1)
    return 1


def shutdown():
    global myweblistener
    dhnio.Dprint(2, 'webcontrol.shutdown')
    result = Deferred()
    def _kill(x):
        res = kill()
        result.callback(res)
        return res
    if myweblistener is not None:
        d = myweblistener.stopListening()
        myweblistener = None
        if d: 
            d.addBoth(_kill)
        else:
            result.callback(1)
    else:
        result.callback(1)
    return result

#------------------------------------------------------------------------------ 

def init_settings_tree():
    global _SettingsTreeNodesDict
    dhnio.Dprint(4, 'webcontrol.init_settings_tree')
    SettingsTreeAddComboboxList('desired-suppliers', settings.getECCSuppliersNumbers())
    SettingsTreeAddComboboxList('updates-mode', settings.getUpdatesModeValues())
    SettingsTreeAddComboboxList('general-display-mode', settings.getGeneralDisplayModeValues())
    SettingsTreeAddComboboxList('emergency-first', settings.getEmergencyMethods())
    SettingsTreeAddComboboxList('emergency-second', settings.getEmergencyMethods())

    _SettingsTreeNodesDict = {
    'settings':                 SettingsTreeNode,

    'central-settings':         SettingsTreeNode,
    'desired-suppliers':        SettingsTreeComboboxNode,
    'shared-megabytes':         SettingsTreeDiskSpaceNode,
    'needed-megabytes':         SettingsTreeDiskSpaceNode,
    
    'backup-block-size':        SettingsTreeNumericNonZeroPositiveNode,

    'folder':                   SettingsTreeNode,
    'folder-customers':         SettingsTreeDirPathNode,
    'folder-backups':           SettingsTreeDirPathNode,
    'folder-restore':           SettingsTreeDirPathNode,

    'network':                  SettingsTreeNode,
    'network-send-limit':       SettingsTreeNumericPositiveNode,
    'network-receive-limit':    SettingsTreeNumericPositiveNode,

    'other':                    SettingsTreeNode,
    'upnp-enabled':             SettingsTreeYesNoNode,
    'upnp-at-startup':          SettingsTreeYesNoNode,

    'emergency':                SettingsTreeNode,
    'emergency-first':          SettingsTreeComboboxNode,
    'emergency-second':         SettingsTreeComboboxNode,
    'emergency-email':          SettingsTreeUStringNode,
    'emergency-phone':          SettingsTreeUStringNode,
    'emergency-fax':            SettingsTreeUStringNode,
    'emergency-text':           SettingsTreeTextNode,

    'updates':                  SettingsTreeNode,
    'updates-mode':             SettingsTreeComboboxNode,

    'general':                          SettingsTreeNode,
    'general-desktop-shortcut':         SettingsTreeYesNoNode,
    'general-start-menu-shortcut':      SettingsTreeYesNoNode,
    'general-backups':                  SettingsTreeNumericPositiveNode,
    'general-local-backups-enable':     SettingsTreeYesNoNode,
    'general-wait-suppliers-enable':    SettingsTreeYesNoNode,

    'logs':                     SettingsTreeNode,
    'debug-level':              SettingsTreeNumericNonZeroPositiveNode,
    'stream-enable':            SettingsTreeYesNoNode,
    'stream-port':              SettingsTreeNumericPositiveNode,
    'traffic-enable':           SettingsTreeYesNoNode,
    'traffic-port':             SettingsTreeNumericPositiveNode,
    'memdebug-enable':          SettingsTreeYesNoNode,
    'memdebug-port':            SettingsTreeNumericPositiveNode,
    'memprofile-enable':        SettingsTreeYesNoNode,

    'transport':                SettingsTreeNode,
    'transport-tcp':            SettingsTreeNode,
    'transport-tcp-enable':     SettingsTreeYesNoNode,
    'transport-tcp-port':       SettingsTreeNumericNonZeroPositiveNode,
    'transport-udp':            SettingsTreeNode,
    'transport-udp-enable':     SettingsTreeYesNoNode,
    'transport-udp-port':       SettingsTreeNumericPositiveNode,
#        'transport-ssh-port':       SettingsTreeNumericNonZeroPositiveNode,
#    'transport-http':           SettingsTreeNode,
#    'transport-http-enable':    SettingsTreeYesNoNode,
#    'transport-http-server-enable':     SettingsTreeYesNoNode,
#    'transport-http-ping-timeout':      SettingsTreeNumericNonZeroPositiveNode,
#    'transport-http-server-port':       SettingsTreeNumericNonZeroPositiveNode,
#    'transport-q2q':            SettingsTreeNode,
#    'transport-q2q-host':       SettingsTreeUStringNode,
#    'transport-q2q-username':   SettingsTreeUStringNode,
#    'transport-q2q-password':   SettingsTreePasswordNode,
#    'transport-q2q-enable':     SettingsTreeYesNoNode,
    'transport-cspace':         SettingsTreeNode,
    'transport-cspace-enable':  SettingsTreeYesNoNode,
    'transport-cspace-key-id':  SettingsTreeUStringNode,
    }
        
#------------------------------------------------------------------------------

def currentVisiblePageName():
    global current_pagename
    return current_pagename

def currentVisiblePageUrl():
    global current_url
    return current_url

#------------------------------------------------------------------------------

def arg(request, key, default = ''):
    if request.args.has_key(key):
        return request.args[key][0]
    return default

def hasArg(request, key):
    return request.args.has_key(key)

def iconurl(request, icon_path):
    # return 'memory:'+icon_name
    # path = 'icons/' + icon_name
    # if icon_name == _PAGE_BACKUP_IMAGE:
    #     path = _PAGE_BACKUP_IMAGE
    if icon_path.startswith('icons/'):
        return 'memory:'+icon_path[6:]
    else:
        return 'http://%s:%s/%s' % (request.getHost().host, str(request.getHost().port), icon_path)

def wrap_long_string(longstring, width=40):
    w = len(longstring)
    if w < width:
        return longstring
    return '<br>'.join(textwrap.wrap(longstring, width))

def help_url(page_name, base_url='http://datahaven.net/gui.html'):
    return base_url + '#' + {
        _PAGE_MAIN: 'main', 
                                }.get(page_name, '')

#------------------------------------------------------------------------------

#possible arguments are: body, back, next, home, title, align
def html(request, **kwargs):
    src = html_from_args(request, **kwargs)
    request.write(str(src))
    request.finish()
    return NOT_DONE_YET

def html_from_args(request, **kwargs):
    d = {}
    d.update(kwargs)
    return html_from_dict(request, d)

def html_from_dict(request, d):
    global root_page_src
    global local_version
    global global_version
    global url_history
    global pagename_history
    if not d.has_key('encoding'):
        d['encoding'] = locale.getpreferredencoding()
    if not d.has_key('body'):
        d['body'] = ''
    if d.has_key('back') and d['back'] == 'none':
        d['back'] = '&nbsp;'
    else:
        back = ''
        if back == '' and len(url_history) > 0:
            url = url_history[-1]
            if url != request.path:
                back = url
        if back != '':
            if back == 'none':
                d['back'] = '&nbsp;'
            else: 
                d['back'] = '<a href="%s">[back]</a>' % back
        else:
            d['back'] = '&nbsp;'
    if not d.has_key('next'):
        d['next'] = '&nbsp;'
    else:
        if d['next'] != '' and d['next'].count('href=') == 0:
            if d['next'] == request.path:
                d['next'] = '&nbsp;'
            else:
                d['next'] = '<a href="%s">[next]</a>' % d['next']
    if not d.has_key('home'):
        d['home'] = '<a href="%s">[menu]</a>' % ('/'+_PAGE_MENU)
    else:
        if d['home'] == '':
            d['home'] = '&nbsp;'
    if dhnio.Windows() and dhnio.isFrozen():
        if global_version != '' and global_version != local_version:
            if request.path != '/'+_PAGE_UPDATE: 
                d['home'] += '&nbsp;&nbsp;&nbsp;<a href="%s">[update software]</a>' % ('/'+_PAGE_UPDATE)
    d['refresh'] = '<a href="%s">refresh</a>' % request.path
    if d.has_key('reload'):
        d['reload_tag'] = '<meta http-equiv="refresh" content="%s">' % d.get('reload', '600')
    else:
        d['reload_tag'] = ''
    if not d.has_key('debug'):
        if dhnio.Debug(14):
            d['debug'] = '<br><br><br>request.args: '+str(request.args) + '\n<br>\n'
            d['debug'] += 'request.path: ' + str(request.path) + '<br>\n'
            d['debug'] += 'request.getClientIP: ' + str(request.getClientIP()) + '<br>\n'
            d['debug'] += 'request.getHost: ' + str(request.getHost()) + '<br>\n'
            d['debug'] += 'request.getRequestHostname: ' + str(request.getRequestHostname()) + '<br>\n'
            if dhnio.Debug(20):
                d['debug'] += 'sys.modules:<br><pre>%s</pre><br>\n'+pprint.pformat(sys.modules) + '<br>\n'
        else:
            d['debug'] = ''
    d['title'] = 'DataHaven.NET'
    if d.has_key('window_title'):
        d['title'] = d['window_title']
    if d.has_key('align'):
        d['align1'] = '<%s>' % d['align']
        d['align2'] = '</%s>' % d['align']
    else:
        d['align1'] = '<center>'
        d['align2'] = '</center>'
    return root_page_src % d

def html_centered_src(d, request):
    global centered_page_src
    if not d.has_key('encoding'):
        d['encoding'] = locale.getpreferredencoding()
#    if not d.has_key('iconfile'):
#        d['iconfile'] = '/' + settings.IconFilename()
#    if not d.has_key('reload') or d['reload'] == '':
#        d['reload_tag'] = ''
#    else:
#        d['reload_tag'] = '<meta http-equiv="refresh" content="%s" />' % d.get('reload', '600')
#    if d.has_key('noexit'):
#        d['exit'] = ''
#    else:
#        d['exit'] = '<div style="position: absolute; right:0px; padding: 5px;"><a href="?action=exit">Exit</a></div>'
    if not d.has_key('title'):
        d['title'] = 'DataHaven.NET'
    if not d.has_key('body'):
        d['body'] = ''
    return centered_page_src % d


#    'success': 'green',
#    'done': 'green',
#    'failed': 'red',
#    'error': 'red',
#    'info': 'black',
#    'warning': 'red',
#    'notify': 'blue',
def html_message(text, typ='info'):
    global _MessageColors
    return'<font color="%s">%s</font>\n' % (_MessageColors.get(typ, 'black'), text)

def html_comment(text):
    return '<!--[begin] %s [end]-->\n' % text

#-------------------------------------------------------------------------------

def SetReadOnlyState(state):
    global read_only_state
    global dhn_state
    dhnio.Dprint(12, 'webcontrol.SetReadOnlyState ' + str(state))
    read_only_state = not state

def ReadOnly():
    # return p2p_connector.A().state not in ['CONNECTED', 'DISCONNECTED', 'INCOMMING?']
    # return p2p_connector.A().state in ['TRANSPORTS', 'NETWORK?']
    return False

def UpdateReceipts():
    dhnio.Dprint(12, 'webcontrol.UpdateReceipts ')

def GetGlobalState():
    return 'unknown'

def check_install():
    return misc.isLocalIdentityReady() and dhncrypto.isMyLocalKeyReady()

#------------------------------------------------------------------------------

def OnGlobalStateChanged(state):
    DHNViewSendCommand('DATAHAVEN-SERVER:' + state)
    if currentVisiblePageName() == _PAGE_STARTING:
        DHNViewSendCommand('update')
#    elif currentVisiblePageUrl().count(_PAGE_SETTINGS):
#        DHNViewSendCommand('update')

def OnSingleStateChanged(index, id, name, new_state):
    DHNViewSendCommand('automat %s %s %s %s' % (str(index), id, name, new_state))

def OnGlobalVersionReceived(txt):
    dhnio.Dprint(4, 'webcontrol.OnGlobalVersionReceived ' + txt)
    global global_version
    global local_version
    if txt == 'failed':
        return
    global_version = txt
    dhnio.Dprint(6, '  global:' + str(global_version))
    dhnio.Dprint(6, '  local :' + str(local_version))
    DHNViewSendCommand('version: ' + str(global_version) + ' ' + str(local_version))

def OnAliveStateChanged(idurl):
    #dhnio.Dprint(18, 'webcontrol.OnAliveStateChanged ' + idurl)
    if contacts.IsSupplier(idurl):
        if currentVisiblePageName() in [_PAGE_SUPPLIERS, 
                                        _PAGE_SUPPLIER, 
                                        _PAGE_SUPPLIER_REMOTE_FILES, 
                                        _PAGE_MAIN, 
                                        _PAGE_BACKUP,
                                        _PAGE_BACKUP_REMOTE_FILES,
                                        _PAGE_BACKUP_RESTORING,
                                        _PAGE_BACKUP_RUNNING, ]:
            DHNViewSendCommand('update')
    if contacts.IsCustomer(idurl):
        if currentVisiblePageName() in [_PAGE_CUSTOMERS, _PAGE_CUSTOMER]:
            DHNViewSendCommand('update')
    if contacts.IsCorrespondent(idurl):
        if currentVisiblePageName() == _PAGE_CORRESPONDENTS:
            DHNViewSendCommand('update')

def OnInitFinalDone():
    if currentVisiblePageName() in [_PAGE_MAIN,]:
        DHNViewSendCommand('update')

def OnBackupStats(backupID):
    # print 'OnBackupStats', backupID, currentVisiblePageName(), '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    if currentVisiblePageUrl().count(backupID) and currentVisiblePageName() in [
            _PAGE_BACKUP,
            _PAGE_BACKUP_LOCAL_FILES,
            _PAGE_BACKUP_REMOTE_FILES,
            _PAGE_BACKUP_RESTORING,
            _PAGE_BACKUP_RUNNING, ]:
        DHNViewSendCommand('update')
    elif currentVisiblePageName() == _PAGE_MAIN:
        DHNViewSendCommand('update')

def OnBackupDataPacketResult(backupID, packet):
    #dhnio.Dprint(18, 'webcontrol.OnBackupDataPacketResult ' + backupID)
    if currentVisiblePageName() not in [_PAGE_BACKUP,
                                        _PAGE_BACKUP_LOCAL_FILES,
                                        _PAGE_BACKUP_REMOTE_FILES,
                                        _PAGE_BACKUP_RESTORING,
                                        _PAGE_BACKUP_RUNNING, ]:
        return
    if currentVisiblePageUrl().count(backupID):
        DHNViewSendCommand('update')

def OnBackupProcess(backupID, packet=None):
    #dhnio.Dprint(18, 'webcontrol.OnBackupProcess ' + backupID)
    if currentVisiblePageName() in [_PAGE_BACKUP, _PAGE_BACKUP_RUNNING, ]:
        if currentVisiblePageUrl().count(backupID):
            DHNViewSendCommand('update')
    if currentVisiblePageName() in [_PAGE_MAIN]:
        DHNViewSendCommand('update')

def OnRestoreProcess(backupID, SupplierNumber, packet):
    #dhnio.Dprint(18, 'webcontrol.OnRestorePacket %s %s' % (backupID, SupplierNumber))
    if currentVisiblePageName() in [_PAGE_BACKUP, _PAGE_BACKUP_RESTORING, ]:
        if currentVisiblePageUrl().count(backupID):
            DHNViewSendCommand('update')
#    if currentVisiblePageUrl().count(backupID):
#        DHNViewSendCommand('update')

def OnRestoreDone(backupID, result):
    #dhnio.Dprint(18, 'webcontrol.OnRestoreDone ' + backupID)
    if currentVisiblePageName() in [_PAGE_BACKUP, _PAGE_BACKUP_RESTORING, ] and currentVisiblePageUrl().count(backupID):
        DHNViewSendCommand('open %s?action=restore.done&result=%s' % ('/'+_PAGE_MAIN+'/'+backupID, result))
    elif currentVisiblePageName() in [_PAGE_MAIN,]:
        DHNViewSendCommand('update')

def OnListSuppliers():
    if currentVisiblePageName() == _PAGE_SUPPLIERS:
        DHNViewSendCommand('update')

def OnListCustomers():
    #dhnio.Dprint(18, 'webcontrol.OnListCustomers ')
    if currentVisiblePageName() == _PAGE_CUSTOMERS:
        DHNViewSendCommand('update')
        
# msg is (sender, to, subject, dt, body)
def OnIncommingMessage(packet, msg):
    dhnio.Dprint(6, 'webcontrol.OnIncommingMessage')

def OnTrafficIn(newpacket, status, proto, host, error, message):
    if newpacket is None:
        DHNViewSendCommand(
            'packet in Unknown from (%s://%s) %s 0 %s' % (
                 proto,
                 host,
                 str(message).replace(' ', '_'),
                 status,))
    else:
        packet_from = newpacket.OwnerID
        if newpacket.OwnerID == misc.getLocalID() and newpacket.Command == commands.Data():
            packet_from = newpacket.RemoteID
        DHNViewSendCommand(
            'packet in %s from %s (%s://%s) %s %d %s' % (
                newpacket.Command,
                nameurl.GetName(packet_from),
                proto,
                host,
                newpacket.PacketID,
                len(newpacket),
                status,))

def OnTrafficOut(workitem, proto, host, status, error, message):
    DHNViewSendCommand(
        'packet out %s to %s (%s://%s) %s %d %s' % (
            workitem.command,
            nameurl.GetName(workitem.remoteid),
            proto,
            host,
            workitem.packetid,
            #workitem.payloadsize,
            workitem.filesize,
            status,))

def OnSupplierQueuePacketCallback(sendORrequest, supplier_idurl, packetid, result):
    DHNViewSendCommand('queue %s %s %d %d %s %s' % (
        sendORrequest, nameurl.GetName(supplier_idurl), 
        contacts.numberForSupplier(supplier_idurl), contacts.numSuppliers(),
        packetid, result))

def OnTrayIconCommand(cmd):
    if cmd == 'exit':
        DHNViewSendCommand('exit')
        #reactor.callLater(0, dhninit.shutdown_exit)
        shutdowner.A('stop', ('exit', ''))

    elif cmd == 'restart':
        DHNViewSendCommand('exit')
        #reactor.callLater(0, dhninit.shutdown_restart, 'show')
        appList = dhnio.find_process(['dhnview.',])
        if len(appList) > 0:
            shutdowner.A('stop', ('restart', 'show'))
        else:
            shutdowner.A('stop', ('restart', ''))
        
    elif cmd == 'reconnect':
        network_connector.A('reconnect')

    elif cmd == 'show':
        show()

    elif cmd == 'hide':
        DHNViewSendCommand('exit')

    else:
        dhnio.Dprint(2, 'webcontrol.OnTrayIconCommand WARNING: ' + str(cmd))

def OnInstallMessage(txt):
    global installing_process_str
    installing_process_str += txt + '\n'
    #installing_process_str = txt
    if currentVisiblePageName() == _PAGE_INSTALL:
        DHNViewSendCommand('update')

def OnUpdateInstallPage():
    #dhnio.Dprint(6, 'webcontrol.OnUpdateInstallPage')
    if currentVisiblePageName() in [_PAGE_INSTALL,]:
        DHNViewSendCommand('open /'+_PAGE_INSTALL)

def OnUpdateStartingPage():
    dhnio.Dprint(6, 'webcontrol.OnUpdateStartingPage ' + currentVisiblePageName())
    if currentVisiblePageName() in [_PAGE_STARTING,]:
        DHNViewSendCommand('open /'+_PAGE_STARTING)

def OnReadLocalFiles():
    if currentVisiblePageName() in [
            _PAGE_MAIN,
            _PAGE_BACKUP,
            _PAGE_BACKUP_LOCAL_FILES,
            _PAGE_BACKUP_REMOTE_FILES,
            _PAGE_BACKUP_RESTORING,
            _PAGE_BACKUP_RUNNING,
            _PAGE_SUPPLIER_LOCAL_FILES, ]:
        DHNViewSendCommand('update')

#-------------------------------------------------------------------------------

def BackupDone(backupID):
    dhnio.Dprint(6, 'webcontrol.BackupDone ' + backupID)
    aborted = False
    if backupID.endswith(' abort'):
        backupID = backupID[:-6]
        aborted = True
    backupDir = backup_db.GetDirectoryFromBackupId(backupID)
    if aborted:
        backup_db.SetBackupStatus(backupDir, backupID, "stopped", "")
    else:
        backup_db.SetBackupStatus(backupDir, backupID, "done", str(time.time()))
    backup_db.Save()
    backups.RemoveBackupInProcess(backupID)
    backup_monitor.Restart()
    if currentVisiblePageName() == _PAGE_BACKUP and currentVisiblePageUrl().endswith(backupID) and not aborted:
        DHNViewSendCommand('update')
    elif currentVisiblePageName() in [_PAGE_MAIN,]:
        DHNViewSendCommand('update')


def BackupFailed(backupID):
    dhnio.Dprint(6, 'webcontrol.BackupFailed ' + backupID)
    backupDir = backup_db.GetDirectoryFromBackupId(backupID)
    backup_db.SetBackupStatus(backupDir, backupID, "failed", "")
    backup_db.Save()
    backups.RemoveBackupInProcess(backupID)
    backup_monitor.Restart()
    if currentVisiblePageName() == _PAGE_BACKUP and currentVisiblePageUrl().endswith(backupID):
        DHNViewSendCommand('update')
    elif currentVisiblePageName() in [_PAGE_MAIN,]:
        DHNViewSendCommand('update')

#-------------------------------------------------------------------------------


def DHNViewSendCommand(cmd):
    global _DHNViewCommandFunc
    if isinstance(cmd, unicode):
        dhnio.Dprint(2, 'DHNViewSendCommand WARNING cmd is unicode' + str(cmd))
    try:
        for f in _DHNViewCommandFunc:
            f(str(cmd))
    except:
        dhnio.DprintException()
        return False
    # dhnio.Dprint(4, '                                                                   DHNViewSendCommand: ' + str(cmd))
    return True

#------------------------------------------------------------------------------

class LocalHTTPChannel(http.HTTPChannel):
    controlState = False
    def connectionMade(self):
        return http.HTTPChannel.connectionMade(self)

    def lineReceived(self, line):
        global _DHNViewCommandFunc
        if line.strip().upper() == 'DATAHAVEN-VIEW-REQUEST':
            dhnio.Dprint(2, 'DHNView: view request received from ' + str(self.transport.getHost()))
            self.controlState = True
            _DHNViewCommandFunc.append(self.send)
            DHNViewSendCommand('DATAHAVEN-SERVER:' + GetGlobalState())
            for index, object in automat.objects().items():
                DHNViewSendCommand('automat %s %s %s %s' % (str(index), object.id, object.name, object.state))
        else:
            return http.HTTPChannel.lineReceived(self, line)

    def send(self, cmd):
        self.transport.write(cmd+'\r\n')

    def connectionLost(self, reason):
        global _DHNViewCommandFunc
        if self.controlState:
            try:
                _DHNViewCommandFunc.remove(self.send)
            except:
                dhnio.DprintException()
            if not check_install() or GetGlobalState().lower().startswith('install'):
                reactor.callLater(0, shutdowner.A, 'ready')
                reactor.callLater(1, shutdowner.A, 'stop', ('exit', ''))

class LocalSite(server.Site):
    protocol = LocalHTTPChannel

    def buildProtocol(self, addr):
        if addr.host != '127.0.0.1':
            dhnio.Dprint(2, 'webcontrol.LocalSite.buildProtocol WARNING NETERROR connection from ' + str(addr))
            return None
        try:
            res = server.Site.buildProtocol(self, addr)
        except:
            res = None
            dhnio.DprintException()
        return res

#------------------------------------------------------------------------------ 

# This is the base class for all HTML pages
class Page(resource.Resource):
    # each page have unique name
    pagename = ''
    # we will save the last requested url
    # we want to know where is user at the moment
    def __init__(self):
        resource.Resource.__init__(self)

    # Every HTTP request by Web Browser will go here
    # So we can check everything in one place
    def render(self, request):
        global current_url
        global current_pagename
        global init_done
        global url_history
        global pagename_history
        
        if self.pagename in [_PAGE_MONITOR_TRANSPORTS, _PAGE_TRAFFIC]:
            return self.renderPage(request)

#        if len(pagename_history) == 0:
#            pagename_history.append(self.pagename)
#            url_history.append(request.path)
        
        # check if we refresh the current page
        if self.pagename != current_pagename or request.path != current_url: 
            # check if we are going back
            if len(pagename_history) > 0 and current_pagename != self.pagename and url_history[-1] == request.path:
                pagename_history.pop()
                url_history.pop()
            # if not going back - remember this place in history
            else:
                if current_pagename != '':
                    pagename_history.append(current_pagename)
                    url_history.append(current_url)
                    
        # remove old history
        while len(pagename_history) > 20:
            pagename_history.pop(0)
            url_history.pop(0)
            
        current_url = request.path
        current_pagename = self.pagename
        # dhnio.Dprint(10, 'webcontrol.Page.render current_pagename=%s current_url=%s' % (current_pagename, current_url))

        if arg(request, 'action') == 'exit' and not dhnupdate.is_running():
            #reactor.callLater(0, dhninit.shutdown_exit)
            reactor.callLater(0, shutdowner.A, 'stop', ('exit', ''))
            d = {}
            d['body'] = ('<br>' * 10) + '\n<h1>Good Luck!<br><br>See you</h1>\n'
            print >>request, html_centered_src(d, request)
            request.finish()
            return NOT_DONE_YET

        elif arg(request, 'action') == 'restart' and not dhnupdate.is_running():
            dhnio.Dprint(2, 'webcontrol.Page.render action is [restart]')
            appList = dhnio.find_process(['dhnview.',])
            if len(appList) > 0:
                dhnio.Dprint(2, 'webcontrol.Page.render found dhnview process, add param "show"')
                reactor.callLater(0, shutdowner.A, 'stop', ('restart', 'show'))
            else:
                dhnio.Dprint(2, 'webcontrol.Page.render did not found dhnview process')
                reactor.callLater(0, shutdowner.A, 'stop', ('restart', ''))
            d = {}
            d['body'] = ('<br>' * 10) + '\n<h1>Restarting DataHaven.NET</h1>\n'
            print >>request, html_centered_src(d, request)
            request.finish()
            return NOT_DONE_YET
        
        elif arg(request, 'action') == 'reconnect':
            reactor.callLater(0, network_connector.A,  'reconnect',)
            d = {}
            d['body'] = ('<br>' * 10) + '\n<h1>Reconnecting...</h1>\n'
            print >>request, html_centered_src(d, request)
            request.finish()
            return NOT_DONE_YET

        if not init_done:
            # dhninit did not finished yet
            # we should stop here at this moment
            # need to wait till all needed modules was initialized.
            # we want to call ".init()" method for all of them
            # let's show "Please wait ..." page here
            # typically we should not fall in this situation
            # because all local initializations should be done very fast
            # we will open the web browser only AFTER dhninit was finished
            dhnio.Dprint(4, 'webcontrol.Page.render will show "Please wait" page')
            d = {}
            d['reload'] = '1'
            d['body'] = '<h1>Please wait ...</h1>'
            print >>request, html_centered_src(d, request)
            request.finish()
            return NOT_DONE_YET

        # dhn is not installed or broken somehow
        if not check_install():
            # page requested is not the install page
            # we do not need this in that moment because dhnmain is not installed
            if self.pagename not in [_PAGE_INSTALL, _PAGE_INSTALL_NETWORK_SETTINGS]:
                dhnio.Dprint(4, 'webcontrol.Page.render redirect to the page %s' % _PAGE_INSTALL)
                request.redirect('/'+_PAGE_INSTALL)
                request.finish()
                return NOT_DONE_YET

            # current page is install page - okay, show it
            return self.renderPage(request)

        # DHN is installed, show the requested page normally
        try:
            ret = self.renderPage(request)
        except:
            exc_src = '<center>\n'
            exc_src += '<h1>Exception on page "%s"!</h1>\n' % self.pagename
            exc_src += '<table width="400px"><tr><td>\n'
            exc_src += '<div align=left>\n'
            exc_src += '<code>\n'
            e = dhnio.formatExceptionInfo()
            e = e.replace(' ', '&nbsp;').replace("'", '"')
            e = e.replace('<', '[').replace('>', ']').replace('\n', '<br>\n')
            exc_src += e
            exc_src += '</code>\n</div>\n</td></tr></table>\n'
            exc_src += '</center>'
            s = html_from_args(request, body=str(exc_src), back=arg(request, 'back', '/'+_PAGE_MAIN))
            request.write(s)
            request.finish()
            ret = NOT_DONE_YET
            dhnio.DprintException()

        return ret

    def renderPage(self, request):
        dhnio.Dprint(4, 'webcontrol.Page.renderPage WARNING base page requested, but should not !')
        return html(request, body='ERROR!')


class ConfirmPage(Page):
    pagename = _PAGE_CONFIRM
    
    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_MAIN)
        confirm = arg(request, 'confirm')
        urlyes = misc.unpack_url_param(arg(request, 'urlyes'))
        urlno = misc.unpack_url_param(arg(request, 'urlno'))
        text = misc.unpack_url_param(arg(request, 'text'))
        if confirm == 'yes':
            request.redirect(urlyes)
            request.finish()
            return NOT_DONE_YET
        elif confirm == 'no':
            request.redirect(urlno)
            request.finish()
            return NOT_DONE_YET
        src = ''
        src += '<br><br><br><br>\n'
        src += '<table width=50%><tr><td align=center>\n'
        src += '<p>%s</p><br>\n' % text
        src += '</td></tr>\n<tr><td align=center>\n'
        src += '<a href="%s?confirm=yes&urlyes=%s&urlno=%s&text=%s&back=%s"><b>YES</b></a>\n' % (
            request.path, misc.pack_url_param(urlyes), misc.pack_url_param(urlno), misc.pack_url_param(text), back)
        src += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        src += '<a href="%s?confirm=no&urlyes=%s&urlno=%s&text=%s&back=%s"><b>NO</b></a>\n' % (
            request.path, misc.pack_url_param(urlyes), misc.pack_url_param(urlno), misc.pack_url_param(text), back)
        src += '</td></tr></table>\n'
        return html(request, body=src, title='', home='', back=back)
            

class StartingPage(Page):
    pagename = _PAGE_STARTING
    labels = {
        'AT_STARTUP':          'starting',
        'LOCAL':               'local settings initialization',
        'CONTACTS':            'contacts initialization',
        'CONNECTION':          'preparing connections',
        'MODULES':             'starting modules', }

    def __init__(self):
        Page.__init__(self)
        self.state2page = {
            'AT_STARTUP':   self.renderStartingPage,
            'LOCAL':        self.renderStartingPage,
            'INSTALL':      self.renderInstallPage,
            'CONTACTS':     self.renderStartingPage,
            'CONNECTION':   self.renderStartingPage,
            'MODULES':      self.renderStartingPage,
            'READY':        self.renderStartingPage,
            'STOPPING':     self.renderStoppingPage,
            'EXIT':         self.renderStoppingPage, }

    def renderPage(self, request):
        current_state = initializer.A().state
        page = self.state2page.get(current_state, None)
        if page is None:
            raise Exception('incorrect state in initializer(): %s' % current_state)
        return page(request)

    def renderStartingPage(self, request):
        src = '<br>' * 3 + '\n'
        src += '<h1>launching DataHaven.NET</h1>\n'
        src += '<table width="400px"><tr><td>\n'
        src += '<div align=left>'
        src += 'Now the program is starting transport protocols.<br><br>\n'
        src += 'You connect to a Central server, which will prepare a list of suppliers for you.<br><br>\n'
        src += 'These users will store your data, and DataHaven.NET will monitor every piece of your remote data.<br><br>\n'
        src += 'That is, first we have to wait for a response from the Central server and then connect with suppliers.<br><br>\n'
        src += 'All process may take a while.\n'
        src += '</div>'
        src += '</td></tr></table>\n'
        src += '<br><br>\n'
        disabled = ''
        button =     '      GO      '
        if initializer.A().state != 'READY':
            disabled = 'disabled'
            button = 'connecting ...'
        src += '<form action="%s" method="get">\n' % ('/'+_PAGE_MAIN)
        src += '<input type="submit" name="submit" value=" %s " %s />\n' % (button, disabled)
        src += '</form>'
        return html(request, body=src, title='launching', home='', back='', reload='1')

    def renderInstallPage(self, request):
        request.redirect('/'+_PAGE_INSTALL)
        request.finish()
        return NOT_DONE_YET

    def renderStoppingPage(self, request):
        src = ('<br>' * 8) + '\n<h1>Good Luck!<br><br>See you</h1>\n'
        return html(request, body=src, title='good luck!', home='', back='')


class InstallPage(Page):
    pagename = _PAGE_INSTALL
    def __init__(self):
        Page.__init__(self)
        self.state2page = {
            'READY':        self.renderSelectPage,
            'WHAT_TO_DO?':  self.renderSelectPage,
            'INPUT_NAME':   self.renderInputNamePage,
            'REGISTER':     self.renderRegisterNewUserPage,
            'AUTHORIZED':   self.renderRegisterNewUserPage,
            'LOAD_KEY':     self.renderLoadKeyPage,
            'RECOVER':      self.renderRestorePage,
            'CENTRAL':      self.renderCentralSettingsPage,
            'CONTACTS':     self.renderContactsPage,
            'UPDATES':      self.renderUpdatesPage,
            'DONE':         self.renderLastPage, }
        self.login = ''
        self.needed = ''
        self.donated = ''
        self.bandin = ''
        self.bandout = ''
        self.customersdir = settings.getCustomersFilesDir()
        self.showall = 'false'
        self.idurl = ''
        self.keysrc = ''
        self.name = ''
        self.surname = ''
        self.nickname = ''
        self.betatester = 'True'
        self.email = ''

    def renderPage(self, request):
        current_state = installer.A().state
        page = self.state2page.get(current_state, None)
        if page is None:
            raise Exception('incorrect state in installer(): %s' % current_state)
        # import pprint
        # pprint.pprint(installer.A().output) 
        return page(request)

    def renderSelectPage(self, request):
        src = '<br>' * 6 + '\n'
        src += '<h1>install DataHaven.NET</h1>\n'
        src += '<br>' * 1 + '\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table align=center cellspacing=10>\n'
        src += '<tr><td align=left>\n'
        src += '<input id="radio1" type="radio" name="action" value="register a new account" checked />\n'
        src += '</td></tr>\n'
        src += '<tr><td align=left>\n'
        src += '<input id="radio2" type="radio" name="action" value="recover my account settings and backups" />\n'
        src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        src += '<br><br><input type="submit" name="submit" value=" next "/>\n'
        src += '</td></tr>\n'
        src += '</table>\n'
        src += '</form>\n'
        #src += '<br><br><br><br><br><br><a href="/?action=exit">[exit]</a>\n'
        action = arg(request, 'action', None)
        result = html(request, body=src, title='install', home='', back='')
        if action is not None:
            if action not in ['register a new account', 'recover my account settings and backups']:
                action = 'register a new account'
            action = action.replace('register a new account', 'register-selected')
            action = action.replace('recover my account settings and backups', 'recover-selected')
            installer.A(action)
        return result

    def renderRegisterNewUserPage(self, request):
        data = installer.A().getOutput('REGISTER').get('data')
        src = ''
        #src += '<br>' * 2 + '\n'
        #src += '<table width=90%><tr><td align=justify>\n'
        src += '<h1 align=center>registering new user identity</h1>\n'
        src += '<table width=90%><tr><td align=justify>\n'
        src += 'In order to allow others to send a data to you - \n'
        src += 'they must know the address of your computer on the Internet. \n'
        src += 'These contacts are kept in XML file called identity.<br>\n'
        src += 'File identity - is a publicly accessible file, \n'
        src += 'which has a unique address on the Internet. \n'
        src += 'So that every user may download your identity \n'
        src += 'and find out your contact information.\n'
        src += '</td></tr></table>\n'
        src += '<table align=center width=400><tr><td align=left>\n'
        src += '<ul>\n'
        for text, color in data:
            if text.strip() == '':
                continue
            src += '<li><font color="%s">%s</font></li>\n' % (color, text)
        src += '</ul>\n'
        src += '</td></tr></table>\n'
        if installer.A().state == 'AUTHORIZED':
            idurl = 'http://' + settings.IdentityServerName() + '/' + self.login + '.xml'
            src += '<br>Here is your identity file: \n'
            src += '<a href="%s" target="_blank">%s</a><br>\n' % (idurl, idurl)
            src += '<br><form action="%s" method="get">\n' % ('/'+_PAGE_INSTALL)
            src += '<input type="submit" name="submit" value=" next " />\n'
            src += '<input type="hidden" name="action" value="next" />\n'
            src += '</form>'
        action = arg(request, 'action', None)
        result = html(request, body=src, title='register new user', home='', back='' )
        if action == 'next':
            installer.A(action, self.login)
        return result

    def renderInputNamePage(self, request):
        self.login = arg(request, 'login', self.login)
        if self.login == '':
            self.login = dhnio.ReadTextFile(settings.UserNameFilename())
        try:
            message, messageColor = installer.A().getOutput('REGISTER').get('data', [('', '')])[-1]
        except:
            dhnio.DprintException()
            message = messageColor = ''
        src = ''
        src += '<br><br>'
        src += '<h1>enter your preferred username here</h1>\n'
        src += '<table><tr><td align=left>\n'
        src += '<ul>\n'
        src += '<li>you can use <b>lower</b> case letters (a-z)\n'
        src += '<li>also digits (0-9), underscore (_) and dash (-)\n'
        src += '<li>the name must be from %s to %s characters\n' % (
            str(settings.MinimumUsernameLength()),
            str(settings.MaximumUsernameLength()))
        src += '<li>it must begin from a letter\n'
        src += '</ul>\n'
        src += '</td></tr></table>\n'
        if message != '':
            src += '<p><font color="%s">%s</font></p><br>\n' % (messageColor, message)
        else:
            src += '<p>&nbsp;</p>\n'
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="text" name="login" value="%s" size=20 /><br><br>\n' % self.login
        src += '<input type="submit" name="submit" value="register" />\n'
        src += '<input type="hidden" name="action" value="register-start" />\n'
        src += '</form><br>\n'
        src += '<br><br><a href="%s?back=%s">[network settings]</a>\n' % ('/'+_PAGE_INSTALL_NETWORK_SETTINGS, request.path)
        action = arg(request, 'action', None)
        result = html(request, body=src, title='enter user name', home='', back='%s?action=back'%request.path )
        if action:
            if action == 'register-start':
                installer.A(action, self.login)
            elif action == 'back':
                installer.A(action)
            else:
                dhnio.Dprint(2, 'webcontrol.InstallPage WARNING incorrect action: %s' % action)
        return result

    def renderRestorePage(self, request):
        data = installer.A().getOutput().get('data')
        src = ''
        src += '<br>' * 4 + '\n'
        src += '<h1>restore my identity</h1>\n'
        src += '<br>\n<p>'
        for text, color in data:
            src += '<font color="%s">%s</font><br>\n' % (color, text)
        src += '</p>'
        return html(request, body=src, title='restore my identity', home='', back='' )

    def renderLoadKeyPage(self, request):
        self.idurl = arg(request, 'idurl', installer.A().getOutput().get('idurl', self.idurl))
        self.keysrc = arg(request, 'keysrc', installer.A().getOutput().get('keysrc', self.keysrc))
        try:
            message, messageColor = installer.A().getOutput('RECOVER').get('data', [('', '')])[-1] 
        except:
            message = messageColor = ''
        src = ''
        src += '<table width=90%><tr><td colspan=3 align=center>\n'
        src += '<h1>recover existing account</h1>\n'
        src += '<p>To recover your previously backed up data we first need to restore your private key and identity.\n'
        src += 'There are 3 different ways to do this below.\n'
        src += 'Choose depending on the way you stored a copy of your key.</p>\n'
        src += '</td></tr>'
        src += '<tr><td align=center>\n'
        #TODO barcodes is not finished yet
        src += '<form action="%s" method="post" enctype="multipart/form-data">\n' % request.path
        src += '<input type="hidden" name="action" value="load-barcode" />\n'
        src += '<input type="file" name="barcodesrc" />\n'
        src += '<input type="submit" name="submit" value=" load from 2D barcode scan " disabled /> '
        src += '</form>\n'
        src += '</td><td align=center>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="submit" name="openfile" value=" load from file or flash USB " />\n'
        src += '<input type="hidden" name="action" value="load-from-file" />\n'
        src += '</form>\n'
        src += '</td><td align=center>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="paste-from-clipboard" />\n'
        src += '<input type="submit" name="submit" value=" paste from clipboard " %s />' % ('disabled' if dhnio.Linux() else '')
        src += '</form>\n'
        src += '</td></tr></table>\n'
        src += '<table align=center><tr><td align=center>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table width=100%><tr align=top><td nowrap>'
        src += 'Identity URL:</td><td align=right>\n'
        src += '<input type="text" name="idurl" size=70 value="%s" />\n' % self.idurl
        src += '</td></tr></table>\n'
        src += '<textarea name="keysrc" rows=7 cols=60 >'
        src += self.keysrc
        src += '</textarea><br>\n'
        src += '<input type="hidden" name="action" value="restore-start" />\n'
        if message != '':
            src += '<p><font color="%s">%s</font></p><br><br>\n' % (messageColor, message)
        else:
            src += '<br>\n'
        src += '<input type="submit" name="submit" value=" next " />\n'
        src += '</form>\n'
        src += '</td></tr></table>\n'
        result = html(request, body=src, title='restore identity', home='', back='%s?action=back'%request.path)
        action = arg(request, 'action', None)
        if action is not None:
            if action == 'load-from-file':
                installer.A(action, arg(request, 'openfile', ''))
            elif action == 'paste-from-clipboard':
                installer.A(action)
            elif action == 'back':
                installer.A(action)
            elif action == 'restore-start':
                installer.A(action, { 'idurl': self.idurl, 'keysrc': self.keysrc } )
            else:
                dhnio.Dprint(2, 'webcontrol.InstallPage WARNING incorrect action: %s' % action)
        return result

    def renderCentralSettingsPage(self, request):
        self.needed = arg(request, 'needed', self.needed)
        if self.needed == '':
            self.needed = str(settings.DefaultNeededMb())
        self.donated = arg(request, 'donated', self.donated)
        if self.donated == '':
            self.donated = str(settings.DefaultDonatedMb())
        self.customersdir = unicode(
            misc.unpack_url_param(
                arg(request, 'customersdir', settings.getCustomersFilesDir()),
                    settings.getCustomersFilesDir()))
        self.bandin = arg(request, 'bandin', self.bandin)
        self.bandout = arg(request, 'bandout', self.bandout)
        if self.bandin == '':
            self.bandin = str(settings.DefaultBandwidthInLimit())
        if self.bandout == '':
            self.bandout = str(settings.DefaultBandwidthOutLimit())
        opendir = unicode(misc.unpack_url_param(arg(request, 'opendir'), ''))
        if opendir != '':
            self.customersdir = opendir
        try:
            message, messageColor = installer.A().getOutput().get('data')[-1]
        except:
            message = messageColor = ''
        mounts = []
        if dhnio.Windows():
            for d in dhnio.listLocalDrivesWindows():
                free, total = diskusage.GetWinDriveSpace(d[0])
                if free is None or total is None:
                    continue
                color = '#ffffff'
                if self.customersdir[0].upper() == d[0].upper():
                    color = '#e0e0e0'
                mounts.append((d[0:2],
                               diskspace.MakeStringFromBytes(free), 
                               diskspace.MakeStringFromBytes(total),
                               color,))
        elif dhnio.Linux():
            for mnt in dhnio.listMountPointsLinux():
                free, total = diskusage.GetLinuxDriveSpace(mnt)
                if free is None or total is None:
                    continue
                color = '#ffffff'
                if dhnio.getMountPointLinux(self.customersdir) == mnt:
                    color = '#e0e0e0'
                mounts.append((mnt, 
                               diskspace.MakeStringFromBytes(free), 
                               diskspace.MakeStringFromBytes(total),
                               color,))
        src = ''
        src += '<h1>needed and donated space</h1>\n'
        src += '<form action="%s?" method="post">\n' % request.path
        src += '<table cellspacing=5><tr>\n'
        src += '<td align=center><b>needed space (MB.)</b>\n'
        src += '<br><input type="text" name="needed" size="10" value="%s" />\n' % self.needed
        src += '</td>\n'
        src += '<td align=center><b>donated space (MB.)</b>\n'
        src += '<br><input type="text" name="donated" size="10" value="%s" />\n' % self.donated
        src += '</td>\n'
        src += '</tr>\n<tr>\n'
#        src += '<td align=center valign=top nowrap><b>incoming bandwidth limit (KB./sec.)</b>\n'
#        src += '<br><input type="text" name="bandin" size="10" value="%s" />\n' % self.bandin
#        src += '</td>\n'
#        src += '<td align=center valign=top nowrap><b>outgoing bandwidth limit (KB./sec.)</b>\n'
#        src += '<br><input type="text" name="bandout" size="10" value="%s" />\n' % self.bandout
#        src += '<br><font size=-1 color=#808080>0 = unlimited</font>'
#        src += '</td>\n'
        src += '</tr>\n'
        src += '</table>\n'
        src += '<b>donated space location:</b>\n'
        if len(mounts) > 0:
            src += '<table align=center cellspacing=10><tr>\n'
            for d in mounts:
                src += '<td bgcolor=%s><font size=-2>%s<br>%s free<br>%s total</font></td>\n' % (d[3], d[0], d[1], d[2])
            src += '</tr></table>\n'
        src += '<font size=+1><u>%s</u></font><br><br>\n' % self.customersdir
        src += '<input type="submit" name="opendir" value=" change location for donated space " />\n'
        src += '<input type="hidden" name="customersdir" value="%s" />\n' % self.customersdir
        if message != '':
            src += '<br><p><font color="%s">%s</font></p>\n' % (messageColor, message)
        src += '<br><br><br><input type="submit" name="submit" value=" next " />\n'
        src += '<input type="hidden" name="action" value="central-ready" />\n'
        src += '<input type="hidden" name="label" value="Select folder for donated space" />\n'
        src += '<input type="hidden" name="showincluded" value="false" />\n'
        src += '</form><br>'
        action = arg(request, 'action', None)
        result = html(request, body=src, title='backup settings', home='', back='')
        if action:
            if action == 'central-ready':
                installer.A(action, {'needed': self.needed, 
                                     'donated': self.donated, 
                                     'customersdir': self.customersdir, 
                                     'opendir': opendir,
                                     'bandin': self.bandin,
                                     'bandout': self.bandout,})
            elif action == 'back':
                installer.A(action)
            else:
                dhnio.Dprint(2, 'webcontrol.InstallPage WARNING incorrect action: %s' % action)
        return result

    def renderContactsPage(self, request):
        action = arg(request, 'action', None)
        if action == 'contacts-ready':
            self.name = arg(request, 'name')
            self.surname = arg(request, 'surname')
            self.nickname = arg(request, 'nickname')
            self.email = arg(request, 'email')
            self.betatester = arg(request, 'betatester')
        try:
            message, messageColor = installer.A().getOutput().get('data')[-1]
        except:
            message = messageColor = ''
        src = ''
        src += '<h1>enter your personal information</h1>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table width="95%" cellspacing=5>\n'
        src += '<tr><td align=left>\n'
        src += 'Please, enter information about yourself if you wish.<br>'
        src += 'Provide email to contact with you, we do not send spam and do not publish your personal information.<br>'
        src += 'We can notify you by email if your account balance is running low, if your backups are not working, or if your machine appears to not be working.'
        src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        src += '<table align=center><tr>\n'
        src += '<td>name:<br><input type="text" name="name" size="25" value="%s" /></td>\n' % self.name
        src += '<td>surname:<br><input type="text" name="surname" size="25" value="%s" /></td>\n' % self.surname
        src += '<td>nickname:<br><input type="text" name="nickname" size="25" value="%s" /></td>\n' % self.nickname
        src += '</tr></table>\n'
        src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        src += 'email:<br><input type="text" name="email" size="25" value="%s" />\n' % self.email
        src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        src += '<table width=80%><tr><td>\n'
        src += '<br><input type="checkbox" name="betatester" value="%s" %s />\n' % (
            'True', ('checked' if self.betatester=='True' else 'False'))
        src += '</td><td>I want to be a beta tester and get '
        src += '<a href="http://datahaven.net/betatest.html" target=_blank>50 US $ or 1 oz silver coin</a> '
        src += 'for testing DataHaven.NET, email is required.\n</td></tr></table>\n'
        src += '</td></tr>\n'
        if message != '':
            src += '<tr><td align=center>\n'
            src += '<font color="%s">%s</font>\n' % (messageColor, message)
            src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        src += '<br><input type="submit" name="submit" value=" next " />\n'
        src += '<input type="hidden" name="action" value="contacts-ready" />\n'
        src += '</td></tr></table>\n'
        src += '</form><br>\n'
        result = html(request, body=src, title='my contacts', home='', back='%s?action=back'%request.path)
        if action:
            if action == 'contacts-ready':
                installer.A(action, {
                    'email': self.email,
                    'name': self.name,
                    'surname': self.surname,
                    'nickname': self.nickname,
                    'betatester': self.betatester,
                    'phone': arg(request, 'phone'),
                    'fax': arg(request, 'fax'),
                    'text': arg(request, 'text'),                
                     })
            elif action == 'back':
                installer.A(action)
            else:
                dhnio.Dprint(2, 'webcontrol.InstallPage WARNING incorrect action: %s' % action)
        return result

    def renderUpdatesPage(self, request):
        choice = arg(request, 'choice', 'hourly')
        src = ''
        src += '<table width=95%><tr><td>\n'
        src += '<center><h1>update settings</h1><center>\n'
        src += '<p align=justify>The DataHaven.NET is now being actively developed and '
        src += 'current software version can be updated several times a month.</p>'
        src += '<p align=justify>If your computer will run an old version of DataHaven.NET,'
        src += 'then sooner or later, you can lose touch with other users.'
        src += 'Since data transmission protocols may be changed - '
        src += 'users will not be able to understand each other '
        src += 'if both will have different versions.'
        src += 'Thus, your suppliers will not be able to communicate with you and all your backups will be lost.</p>'
        src += '<p align=justify>We recommend that you enable automatic updates, at least for a period of active development of the project.</p>'
        src += '</table><br>\n'
        src += '<h3>How often you\'d like to check the latest version?</h3>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table cellspacing=5><tr>\n'
        items = ['disable updates', 'hourly', 'daily', 'weekly',]
        for i in range(len(items)):
            checked = ''
            if items[i] == choice:
                checked = 'checked'
            src += '<td>'
            src += '<input id="radio%s" type="radio" name="choice" value="%s" %s />' % (
                str(i),
                items[i],
                checked,)
            #src += '<label for="radio%s">  %s</label></p>\n' % (str(i), items[i],)
            src += '</td>\n'
        src += '</tr></table><br><br>'
        src += '<input type="hidden" name="action" value="updates-ready" />\n'
        src += '<input type="submit" name="submit" value=" next " />\n'
        src += '</form>'

        if dhnio.Windows():
            src += ''
        elif dhnio.Linux():
            pass
        else:
            pass

        src += '</td></tr></table>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '</form>'
        action = arg(request, 'action', None)
        result = html(request, body=src, title='updates', home='', back='%s?action=back'%request.path)
        if action:
            if action == 'updates-ready':
                installer.A(action, choice)
            elif action == 'back':
                installer.A(action)
            else:
                dhnio.Dprint(2, 'webcontrol.InstallPage WARNING incorrect action: %s' % action)
        return result

    def renderLastPage(self, request):
        src = ''
        src += '<br>' * 6 + '\n'
        src += '<table width=80%><tr><td>\n'
        src += '<font size=+2 color=green><h1>DataHaven.NET<br>installed successfully</h1></font>\n'
        src += '<br><br>\n'
        src += '<form action="%s" method="get">\n' % ('/'+_PAGE_STARTING)
        src += '<input type="submit" name="submit" value=" launch " />\n'
        src += '</form>'
        return html(request, body=src, title='installed', home='', back='')


class InstallNetworkSettingsPage(Page):
    pagename = _PAGE_INSTALL_NETWORK_SETTINGS
    def renderPage(self, request):
        checked = {True: 'checked', False: ''}
        action = arg(request, 'action')
        back = arg(request, 'back', request.path)
        host = arg(request, 'host', settings.getProxyHost())
        port = arg(request, 'port', settings.getProxyPort())
        upnpenable = arg(request, 'upnpenable', '')
        dhnio.Dprint(6, 'webcontrol.InstallNetworkSettingsPage.renderPage back=[%s]' % back)
        if action == 'set':
            settings.enableUPNP(upnpenable.lower()=='true')
            d = {'host': host.strip(), 'port': port.strip()}
            dhnnet.set_proxy_settings(d)
            settings.setProxySettings(d)
            settings.enableProxy(d.get('host', '') != '')
            request.redirect(back)
            request.finish()
            return NOT_DONE_YET
        if upnpenable == '':
            upnpenable = str(settings.enableUPNP())
        src = '<br><br>'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<h3>Proxy server</h3>\n'
        src += '<table><tr>\n'
        src += '<tr><td valign=center align=left>host:</td>\n'
        src += '<td valign=center align=left>port:</td></tr>\n'
        src += '<tr><td><input type="text" name="host" value="%s" size="20" /></td>\n' % host
        src += '<td><input type="text" name="port" value="%s" size="6" />\n' % port
        src += '</td></tr></table>'
        src += '<p>Leave fields blank to not use proxy server.</p>\n'
        src += '<br><br><h3>UPnP port forwarding</h3>\n'
        src += '<table><tr><td>\n'
        src += '<br><input type="checkbox" name="upnpenable" value="%s" %s />' % ('True', checked.get(upnpenable=='True'))
        src += '</td><td valign=center align=left>'
        src += 'Use UPnP to automaticaly configure port forwarding for DataHaven.NET.<br>'
        src += 'Enable this if you are connected to the Internet with network router.'
        src += '</td></tr></table>\n'
        src += '<br><br><br><input type="submit" name="button" value="   set   " />'
        src += '<input type="hidden" name="action" value="set" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '</form><br><br>\n'
        return html(request, body=src, back=back, home = '',)


class RootPage(Page):
    pagename = _PAGE_ROOT
    def renderPage(self, request):
        request.redirect('/'+_PAGE_MAIN)
        request.finish()
        return NOT_DONE_YET


#--- Main (Backups) Page
class MainPage(Page):
    pagename = _PAGE_MAIN
    showByID = False
    total_space = 0

    def _body(self, request):
        src = ''
        src += '<h1>backups</h1>\n'

        # src += '<table border=2><tr><td nowrap bgcolor=lightgray>\n'
        # src += '<table border=1><tr bgcolor=lightgray><td nowrap bgcolor=lightgray>\n'
        src += '<font size=+1><b><a href="%s?action=dirselected&path=%s&showincluded=true&label=%s" target="_opendir">[ add backup folder ]</a></b></font>\n' % (
            request.path, misc.pack_url_param(os.path.expanduser('~')), misc.pack_url_param('Select folder to backup'))
        # src += '</td></tr></table>\n' 
        # src += '</td></tr></table>\n'
        src += '<br><br>\n' 
        
        # src += '<form action="%s?" method="post">\n' % request.path
        # src += '<input type="hidden" name="action" value="dirselected" />\n'
        # src += '<input type="hidden" name="parent" value="%s" />\n' % _PAGE_MAIN
        # src += '<input type="hidden" name="label" value="Select folder to backup" />\n'
        # src += '<input type="hidden" name="showincluded" value="true" />\n'
        # src += '<input type="submit" name="opendir" value=" add backup folder " path="%s" />\n' % misc.pack_url_param(os.path.expanduser('~'))
        # src += '</form><br><br>\n'

        if len(backup_db.GetBackupDirectories()) == 0:
            src += '<p>Click "add backup folder" to add a new backup.</p>\n'
            src += html_comment('run "datahaven add <folder path>" to add backup folder')
            return src

        self.total_space = 0
        if self.showByID or arg(request, 'byid') == 'show':
            src += self._idlist(request)
        else:
            src += self._list(request)
        return src

    def _idlist(self, request):
        src = ''
        src += '<br><table cellspacing=10 cellpadding=0 border=0>\n'
        for backupID, backupDir, dirSizeBytes, backupStatus in backup_db.GetBackupsByDateTime(True):
            dirSizeString = diskspace.MakeStringFromBytes(dirSizeBytes)
            self.total_space += dirSizeBytes * 2
            percent = 0.0
            state = ''
            condition = ''
            is_running = backup_db.IsBackupRunning(backupDir)
            if is_running:
                backupObj = backup_db.GetRunningBackupObject(backupID)
                if backupObj is not None:
                    if backupObj.state != 'SENDING':
                        state = 'started'
                        if dirSizeBytes > 0:
                            percent = 100.0 * backupObj.dataSent / dirSizeBytes
                            if percent > 100.0:
                                percent = 100.0
                        else:
                            percent = 0.0
                    else:
                        state = 'sending'
                        percent = 100.0 * backupObj.blocksSent / (backupObj.blockNumber + 1) 
                    condition = '%s' % misc.percent2string(percent)
                else:
#                    state = 'started'
#                    blocks, percent = backups.GetBackupBlocksAndPercent(backupID)
                    state = 'ready'
                    blocks, percent, weakBlock, weakPercent = backups.GetBackupRemoteStats(backupID)
                    localPercent, localFiles, totalSize, maxBlockNum, localStats  = backups.GetBackupLocalStats(backupID)
                    # condition = '%s/%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(percent), misc.percent2string(localPercent))
                    condition = '%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(localPercent))
            else:
                state = 'ready'
                blocks, percent, weakBlock, weakPercent = backups.GetBackupRemoteStats(backupID)
                localPercent, localFiles, totalSize, maxBlockNum, localStats  = backups.GetBackupLocalStats(backupID)
                # condition = '%s/%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(percent), misc.percent2string(localPercent))
                condition = '%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(localPercent))
            is_working = restore_monitor.IsWorking(backupID)
            if is_working:
                state = 'restoring' 

            src += '<tr>\n'
           
            # backupID
            src += '<td valign=center>'
            src += '<a href="%s?back=%s">%s</a>' % (
                '/'+_PAGE_MAIN+'/'+backupID, request.path, backupID)
            src += '</td>\n'
            
            # size
            src += '<td nowrap valign=center>'
            src += dirSizeString
            src += '</td>\n' 
            
            # state 
            src += '<td valign=center>'
            src += state
            src += '</td>\n'

            # condition
            src += '<td valign=center>'
            src += '[%s]' % condition
            src += '</td>\n'
            
            # backup dir 
            src += '<td valign=center>'
            src += '<font size=+0><b>%s</b></font>' % str(backupDir)
            src += '</td>\n'
            
            # restore button
            src += '<td align=right valign=top>\n'
            dhnio.Dprint(6, '    %s   is_running=%s   is_working=%s' % (backupID, str(is_running), str(is_working)))
            if is_running or is_working:
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, 'icons/norestore04.png'), 24, 24 )
            else:
                src += '<a href="%s?action=restore&back=%s">' % (
                    '/'+_PAGE_MAIN+'/'+backupID, request.path)
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, 'icons/startrestore04.png'), 24, 24 )
                src += '</a>'
            src += '</td>\n'

            # delete button
            src += '<td align=right valign=top>\n'
            src += '<a href="%s?action=deleteid&backupid=%s&back=%s">' % (
                request.path, backupID, request.path)
            src += '<img src="%s" width=%d height=%d>' % (
                iconurl(request, 'icons/delete02.png'), 24, 24 )
            src += '</a>'
            src += '</td>\n'

            src += html_comment('  %s %s %s%% %s %s' % (
                backupID, dirSizeString.rjust(12), str(int(percent)).rjust(3), 
                state.rjust(9), str(backupDir)))
              
            src += '</tr>\n'
        src += '</table><br><br>\n'
        return src

    def _list(self, request):
        src = ''
        backupIdsRemote = backups.GetBackupIds()
        backupDirsLocal = backup_db.GetBackupDirectories()

        src += '<table width=90% cellspacing=0 cellpadding=5 border=0>\n'
        
        for backupDir, backupRuns, totalBackupsSizeForDir, is_running, recentBackupID in backup_db.GetBackupsByFolder():
            is_run2 = backup_db.IsBackupRunning(backupDir) 
            dhnio.Dprint(10, '    %s (%d backups) %s %s %s ' % (backupDir, 
                                                     len(backupRuns),
                                                     recentBackupID,
                                                     str(is_running),
                                                     str(is_run2),))
            totalBackupSizeString = diskspace.MakeStringFromBytes(totalBackupsSizeForDir)
            self.total_space += totalBackupsSizeForDir * 2
            dirSizeBytes = dirsize.getInBytes(backupDir)
            dirSizeString = dirsize.getLabel(backupDir)

            src += '<tr valign=top>\n'

            #--- folder name
            src += '<td align=left valign=center width=95%>'
            src += '<font size=+1><b>%s</b></font>' % str(backupDir) #wrap_long_string(str(backupDir), 80)
            src += '</td>\n'

            #--- folder size
            src += '<td nowrap align=right valign=center>%s</td>\n' % dirSizeString

            src += '<td align=right valign=top nowrap>\n'
            src += '<div>&nbsp;\n'
            #--- start backup button or hourglass button
            if dirsize.isjob(backupDir):
                # if we calculating size of this folder at the moment
                # we do not want user to press this button
                src += '<img src="%s" width=%d height=%d />' % (
                    iconurl(request, 'icons/read-folder.png'), 24, 24 )
            else:
                if is_running:
                    src += '<a href="%s?back=%s">' % (
                        '/'+_PAGE_MAIN+'/'+recentBackupID, request.path)
                    src += '<img src="%s" width=%d height=%d />' % (
                        iconurl(request, 'icons/hourglass.png'), 24, 24 )
                    src += '</a>'
                else:
                    src += '<a href="%s?action=start&backupdir=%s&back=%s">' % (
                        request.path, misc.pack_url_param(backupDir), request.path)
                    src += '<img src="%s" width=%d height=%d />' % (
                        iconurl(request, 'icons/start.png'), 24, 24 )
                    src += '</a>'

            #--- restore button
            if is_running:
                src += '<img src="%s" width=%d height=%d />' % (
                    iconurl(request, 'icons/norestore04.png'), 24, 24 )
            else:
                if recentBackupID != '' and not restore_monitor.IsWorking(recentBackupID):
                    src += '<a href="%s?action=restore&back=%s">' % (
                        '/'+_PAGE_MAIN+'/'+recentBackupID, request.path)
                    src += '<img src="%s" width=%d height=%d />' % (
                        iconurl(request, 'icons/startrestore04.png'), 24, 24 )
                    src += '</a>'
                else:
                    src += '<img src="%s" width=%d height=%d />' % (
                        iconurl(request, 'icons/norestore04.png'), 24, 24 )

            #--- shedule button
            src += '<a href="%s?&backupdir=%s&back=%s">' % (
                '/'+_PAGE_BACKUP_SHEDULE, misc.pack_url_param(backupDir), request.path)
            src += '<img src="%s" width=%d height=%d />' % (
                iconurl(request, 'icons/schedule.png'), 24, 24 )
            src += '</a>'

            #--- delete folder button
            src += '<a href="%s?action=delete&backupdir=%s&back=%s">' % (
                request.path, misc.pack_url_param(backupDir), request.path)
            src += '<img src="%s" width=%d height=%d />' % (
                iconurl(request, 'icons/delete02.png'), 24, 24 )
            src += '</a>'
            src += '</div>'
            src += '</td>\n'
            src += '</tr>\n'

            src += html_comment('%s [%s]' % (str(backupDir), dirSizeString,))

            if len(backupRuns) > 0:
                # src += '<table width=90% align=left cellspacing=0 cellpadding=5 border=0>\n'
                for backupRun in backupRuns:
                    backupID = backupRun.backupID
                    #--- calculate percent, state and condition
                    percent = 0.0
                    percents = []
                    state = ''
                    condition = ''
                    if is_running:
                        backupObj = backup_db.GetRunningBackupObject(backupID)
                        if backupObj is not None:
                            if backupObj.state != 'SENDING':
                                state = 'started'
                                if dirSizeBytes > 0:
                                    percent = 100.0 * backupObj.dataSent / dirSizeBytes
                                    if percent > 100.0:
                                        percent = 100.0
                                else:
                                    percent = 0.0
                            else:
                                state = 'sending'
                                percent = 100.0 * backupObj.blocksSent / (backupObj.blockNumber + 1) 
                            condition = '%s' % misc.percent2string(percent)
                            percents = [percent,]
                        else:
                            state = 'ready'
                            blocks, percent, weakBlock, weakPercent = backups.GetBackupRemoteStats(backupID)
                            localPercent, localFiles, totalSize, maxBlockNum, localStats  = backups.GetBackupLocalStats(backupID)
                            condition = '%s/%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(percent), misc.percent2string(localPercent))
                            # condition = '%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(localPercent))
                            percents = [weakPercent, percent, localPercent]
                    else:
                        state = 'ready'
                        if backup_rebuilder.A().state in [ 'NEXT_BLOCK', 'REBUILDING' ] and backup_rebuilder.A().currentBackupID == backupID:
                            state = 'rebuilding'
                        blocks, percent, weakBlock, weakPercent = backups.GetBackupRemoteStats(backupID)
                        localPercent, localFiles, totalSize, maxBlockNum, localStats  = backups.GetBackupLocalStats(backupID)
                        condition = '%s/%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(percent), misc.percent2string(localPercent))
                        # condition = '%s/%s' % (misc.percent2string(weakPercent), misc.percent2string(localPercent))
                        percents = [weakPercent, percent, localPercent]
                    is_working = restore_monitor.IsWorking(backupID)
                    if is_working:
                        state = 'restoring' 

                    #--- comment
                    src += html_comment('    %s %s [%s]' % (backupID, condition, state))

                    src += '<tr>'

                    #--- label and link
                    src += '<td nowrap width=95%>\n'
                    
                    src += '<table cellspacing=0 cellpadding=0 width=100%><tr><td align=left>'
                    src += '&nbsp;' * 8
                    
                    src += '<a href="%s?back=%s">%s</a>\n' % (
                        '/'+_PAGE_MAIN+'/'+backupID, request.path, backupID)
                    
                    src += '</td>\n<td align=right>\n'

                    #--- condition 
                    src += '<font size=-1>%s</font>' % condition
                    src += '</td>\n<td align=right>\n'
                    
                    #--- state
                    src += '<b>[%s]</b>' % state
                    
                    src += '</td></tr>\n</table>\n' 
                    
                    src += '</td>\n'
                    
                    #--- image
                    src += '<td nowrap align=left>\n'
                    src += '<a href="%s?back=%s">' % ('/'+_PAGE_MAIN+'/'+backupID+'/'+_PAGE_BACKUP_DIAGRAM, request.path,)
                    src += '<img src="%s?type=bar&width=100&height=16" />' % (
                        iconurl(request, _PAGE_MAIN+'/'+backupID+'/'+_PAGE_BACKUP_IMAGE))
                    src += '</a>\n'
                    src += '</td>\n'

                    #--- delete single backupID button
                    src += '<td nowrap align=left>&nbsp;\n'
                    src += '<a href="%s?action=deleteid&backupid=%s&back=%s">' % (
                        request.path, backupID, request.path)
                    src += '<img src="%s" width=%d height=%d />' % (
                        iconurl(request, 'icons/delete01.png'), 16, 16 )
                    src += '</a>'
                    src += '</td>\n'
                    src += '</tr>'

                src += '</tr>\n'
                    
                src += '<tr><td colspan=3>&nbsp;</td></tr>\n'
                
                src += html_comment(' ')
            else:
                src += html_comment(' ')


        src += '</table>\n'
        return src

    def renderPage(self, request):
        dhnio.Dprint(12, 'webcontrol.MainPage.renderPage')
        if not backup_db.InitDone:
            return html(request, title='backups', reload='1',
                        body='<h1>connecting ...</h1>\n'+html_comment('connecting ...'),)

        if arg(request, 'byid') == '1':
            self.showByID = True
        elif arg(request, 'byid') == '0':
            self.showByID = False

        action = arg(request, 'action').strip()
        backupdir = unicode(misc.unpack_url_param(arg(request, 'backupdir'), ''))
        backupid = arg(request, 'backupid')
        opendir = unicode(misc.unpack_url_param(arg(request, 'opendir'), ''))

        ready2backup = False

        #---dirselected---
        if action == 'dirselected':
            if opendir != '':
                backup_db.AddDirectory(opendir, True)
                backup_db.Save()
            dirsize.ask(opendir, self._dir_size_dirselected, 'open '+request.path)

        #---start---
        elif action == 'start':
            if backupdir != '' and not backup_db.CheckDirectory(backupdir):
                backup_db.AddDirectory(backupdir, True)
                backup_db.Save()
            #dirSZ = dirsize.ask(backupdir, self._dir_size_start)
            dirSZ = dirsize.ask(backupdir, self._dir_size_start, 'open '+request.path)

        #---deleteid---
        elif action == 'deleteid':
            if backupid != '':
                backup_db.AbortRunningBackup(backupid)
                backupDir = backup_db.GetDirectoryFromBackupId(backupid)
                if backupDir != '':
                    backup_db.AbortDirectoryBackup(backupDir)
                backups.DeleteBackup(backupid)
                backup_monitor.Restart()

        #---delete---
        elif action == 'delete':
            dhnio.Dprint(4, 'webcontrol.MainPage.renderPage action=delete backupdir='+backupdir)
            if backupdir != '':
                #recentBackupID, totalBackupsSize, lastBackupStatus = backup_db.GetDirectoryInfo(backupdir)
                for backupID in backup_db.GetDirBackupIds(backupdir):
                    #if backup_db.IsBackupRunning(backupdir):
                    backup_db.AbortRunningBackup(backupID)
                    backups.DeleteBackup(backupID)
                backup_db.AbortDirectoryBackup(backupdir)
                backup_db.DeleteDirectory(backupdir)
                backup_db.Save()
                backup_monitor.Restart()
        
        #---deleteall---
        elif action == 'deleteall':
            dhnio.Dprint(4, 'webcontrol.MainPage.renderPage action=deleteall !!!!!')
            backups.DeleteAllBackups()
            backups.ClearRemoteInfo()
            backups.ClearLocalInfo()
            backup_monitor.Restart()
            request.redirect(request.path)
            request.finish()
            return NOT_DONE_YET

        #---update---
        elif action == 'update':
            backup_monitor.Restart()
            request.redirect(request.path)
            request.finish()
            return NOT_DONE_YET
        
        #---restore---
        elif action == 'restore':
            if backupid != '':
                restorePath = os.path.abspath(arg(request, 'destination', 
                    os.path.join(settings.getRestoreDir(), backupid+'.tar')))
                restore_monitor.Start(backupid, restorePath)

        src = self._body(request)
        
        # src += '<table><tr><td><div align=left><ul>\n'

        src += '<br><br><table><tr><td><div align=left>\n'
        availibleSpace = diskspace.MakeStringFromString(settings.getCentralMegabytesNeeded())
        totalSpace = diskspace.MakeStringFromBytes(self.total_space)
        src += 'total space used: %s<br>\n' % totalSpace
        src += 'availible space: <a href="%s">%s</a><br>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'central-settings.needed-megabytes?back='+request.path, availibleSpace,)
        src += '</div></td></tr></table>\n'

        src += html_comment('total space used: %s' % totalSpace)
        src += html_comment('availible space:  %s' % availibleSpace)

        reload = ''
        src += '<p><a href="%s?action=update">Request my suppliers to check my backups now</a></p>\n' % request.path
        if len(backup_db.GetBackupDirectories()) > 0:
            msg = 'Do you really want to delete the whole saved data?'
            delete_all_backups_link = '%s?urlyes=%s&urlno=%s&text=%s&back=%s' % (
                '/'+_PAGE_CONFIRM, 
                misc.pack_url_param('%s?action=deleteall&back=%s' % (request.path, request.path)),
                misc.pack_url_param(request.path),
                misc.pack_url_param(msg),
                request.path)
            src += '<p><a href="%s">Delete all my backed up data - local and remote.</a></p>\n' % delete_all_backups_link
            reload = ''
        if self.showByID:
            src += '<p><a href="%s?byid=0">Show backups for every folder</a></p>\n' % request.path
        else:
            src += '<p><a href="%s?byid=1">Show backups sorted by date and time</a></p>\n' % request.path
        src += '<p><a href="%s">Check the backup settings</a></p>\n' % ('/'+_PAGE_BACKUP_SETTINGS+'?back='+request.path,)
        src += '<p><a href="%s" target=_blank>Get help on this page</a></p>\n' % help_url(self.pagename)

        # src += '</ul></div></td></tr></table>\n'

        return html(request, body=str(src), title='my backups', back='', reload=reload )

    def getChild(self, path, request):
        # dhnio.Dprint(12, 'webcontrol.MainPage.getChild path='+path)
        if path == '':
            return self
        return BackupPage(path)

    def _dir_size_dirselected(self, dirpath, size, cmd):
        dhnio.Dprint(6, 'webcontrol.MainPage._dir_size_dirselected %d %s' % (size, dirpath))
        DHNViewSendCommand(cmd)

    def _dir_size_start(self, backupdir, size, cmd=None):
        dhnio.Dprint(6, 'webcontrol.MainPage.renderPage._dir_size_start %d %s' % (size, backupdir))
        BackupID = misc.NewBackupID()
        backups.AddBackupInProcess(BackupID)
        recursive_subfolders = backup_db.GetDirectorySubfoldersInclude(backupdir)
        dir_size = size
        result = Deferred()
        result.addCallback(BackupDone)
        result.addErrback(BackupFailed)
        dobackup.dobackup(BackupID, backupdir, dir_size, recursive_subfolders, OnBackupProcess, result)
        if cmd is None:
            DHNViewSendCommand('open '+'/'+_PAGE_MAIN+'/'+BackupID)
        else:
            DHNViewSendCommand(cmd)


class CentralPage(Page):
    pagename = _PAGE_CENTRAL
    def renderPage(self, request):
        src = ''
        return src
    
    
class AutomatsPage(Page):
    pagename = _PAGE_AUTOMATS
    def renderPage(self, request):
        src = ''
        # for index, object in automats.get_automats_by_index().items():
        for index, object in automat.objects().items():
            src += html_comment('  %s %s %s' % (
                str(index).ljust(4), 
                str(object.id).ljust(50), 
                object.state))
        return src
    

class MenuPage(Page):
    pagename = _PAGE_MENU
    
    def renderPage(self, request):
        global _MenuItems
        menuLabels = _MenuItems.keys()
        menuLabels.sort()
        w, h = misc.calculate_best_dimension(len(menuLabels))
        imgW = 128
        imgH = 128
        if w >= 4:
            imgW = 4 * imgW / w
            imgH = 4 * imgH / w
        padding = 64/w - 8
        back = arg(request, 'back', request.path)
        src = ''
        src += '<tr><td align=center>\n'
        src += '<table cellpadding=%d cellspacing=2>\n' % padding
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                n = y * w + x
                src += '<td align=center valign=top>\n'
                if n >= len(menuLabels):
                    src += '&nbsp;\n'
                    continue
                label = menuLabels[n]
                link_url, icon_url = _MenuItems[label]
                if link_url.find('?') < 0:
                    link_url += '?back=' + back
                label = label.split('|')[1]
                src += '<a href="%s">' % link_url
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon_url),
                    imgW, imgH,)
                src += '<br>[%s]' % label
                src += '</a>\n'
                src += '</td>\n'
                src += html_comment('    [%s] %s' % (label, link_url))
            src += '</tr>\n'
        src += '</table>\n'
        src += '</td></tr></table>\n'
        src += '<br><br>\n'
        shutdown_link = '%s?urlyes=%s&urlno=%s&text=%s&back=%s' % (
            '/'+_PAGE_CONFIRM, 
            misc.pack_url_param(request.path+'?action=exit'),
            misc.pack_url_param(request.path),
            misc.pack_url_param('Do you want to stop DataHaven.NET?'),
            back)
        return html(request, body=src, home='', title='menu', back=back, next='<a href="%s">[shutdown]</a>' % shutdown_link)


class BackupLocalFilesPage(Page):
    pagename = _PAGE_BACKUP_LOCAL_FILES
    isLeaf = True

    def __init__(self, backupID, backupDir):
        Page.__init__(self)
        self.backupID = backupID
        self.backupDir = backupDir

    def renderPage(self, request):
        localPercent, numberOfFiles, totalSize, maxBlockNum, bstats = backups.GetBackupLocalStats(self.backupID)
        w, h = misc.calculate_best_dimension(contacts.numSuppliers())
        imgW, imgH, padding = misc.calculate_padding(w, h)
        src = '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p>%s</p>\n' % self.backupID
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir)) 
        src += '<table width=95%><tr><td align=center><p>'
        src += 'Here is a list of local files stored on your hard drive for this backup.<br>\n'
        src += 'This local copy of your backup folder will allow instantaneous data recovery in case of it loss.<br>\n'
        src += 'If you wish these files can be deleted to save space on your disk.<br>\n'
        src += 'At the moment, saved <b>%d</b> files with total size of <b>%s</b>, this is <b>%s</b> of the whole data.\n' % (
            numberOfFiles, diskspace.MakeStringFromBytes(totalSize), misc.percent2string(localPercent))
        src += '</p></td></tr></table>\n'
        src += html_comment('  saved %d files with total size of %s' % (numberOfFiles, diskspace.MakeStringFromBytes(totalSize)))
        src += '<table cellpadding=%d cellspacing=2>\n' % padding #width="90%%"
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                src += '<td align=center valign=top>\n'
                supplierNum = y * w + x
                link = '/' + _PAGE_SUPPLIERS + '/' + str(supplierNum) + '?back=%s' % request.path
                if supplierNum >= contacts.numSuppliers():
                    src += '&nbsp;\n'
                    continue
                idurl = contacts.getSupplierID(supplierNum)
                name = nameurl.GetName(idurl)
                if not name:
                    src += '&nbsp;\n'
                    continue
                if idurl:
                    icon = 'icons/offline-user01.png'
                else:
                    icon = 'icons/unknown-user01.png'
                state = 'offline'
                if contact_status.isOnline(idurl):
                    icon = 'icons/online-user01.png'
                    state = 'online '
                if w >= 5 and len(name) > 10:
                    name = name[0:9] + '<br>' + name[9:]
                src += '<a href="%s">' % link
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon),
                    imgW, imgH,)
                src += '</a><br>\n'
                if supplierNum < len(bstats):
                    percent, localFiles = bstats[supplierNum]
                    src += misc.percent2string(percent)
                    src += ' in %d/%d files<br>for ' % (localFiles, 2 * (maxBlockNum + 1))
                    src += '<a href="%s">%s</a>\n' % (link, name)
                src += '</td>\n'
                src += html_comment('    %s in %d/%d files for %s [%s]' % (
                    misc.percent2string(percent), localFiles, 2 * (maxBlockNum + 1), name, state))
            src += '</tr>\n'
        src += '</table>\n'
        if not backup_db.IsBackupRunning(self.backupDir) and not restore_monitor.IsWorking(self.backupID):
            src += '<br><br><a href="%s?action=deletelocal">Remove all local files for this backup now</a><br>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID)
        src += '<br>\n'
        return html(request, body=src, back='/'+_PAGE_MAIN+'/'+self.backupID)


class BackupRemoteFilesPage(Page):
    pagename = _PAGE_BACKUP_REMOTE_FILES
    isLeaf = True

    def __init__(self, backupID, backupDir):
        Page.__init__(self)
        self.backupID = backupID
        self.backupDir = backupDir

    def renderPage(self, request):
        totalNumberOfFiles, maxBlockNumber, bstats = backups.GetBackupStats(self.backupID)
        blocks, percent = backups.GetBackupBlocksAndPercent(self.backupID)
        w, h = misc.calculate_best_dimension(contacts.numSuppliers())
        imgW, imgH, padding =  misc.calculate_padding(w, h)
        src = '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p>%s</p>\n' % self.backupID
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir)) 
        src += '<table width=70%><tr><td align=center><p>'
        src += 'Each supplier keeps a piece of that backup.<br>\n'
        src += 'Here you see the overall condition and availability of data at the moment.<br>\n'
        src += 'This backup contains <b>%d</b> blocks in <b>%d</b> files and ' % (blocks, totalNumberOfFiles)
        src += 'ready by <b>%s</b>. ' % misc.percent2string(percent)
        src += '</p></td></tr></table>\n'
        src += html_comment('  this backup contains %d blocks in %d files and ready by %s' % (
            blocks, totalNumberOfFiles, misc.percent2string(percent)))
        src += '<table cellpadding=%d cellspacing=2>\n' % padding
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                src += '<td align=center valign=top>\n'
                supplierNum = y * w + x
                link = '/' + _PAGE_SUPPLIERS + '/' + str(supplierNum) + '?back=%s' % request.path
                if supplierNum >= contacts.numSuppliers():
                    src += '&nbsp;\n'
                    continue
                idurl = contacts.getSupplierID(supplierNum)
                name = nameurl.GetName(idurl)
                if not name:
                    src += '&nbsp;\n'
                    continue
                if idurl:
                    icon = 'icons/offline-user01.png'
                else:
                    icon = 'icons/unknown-user01.png'
                state = 'offline'
                if contact_status.isOnline(idurl):
                    icon = 'icons/online-user01.png'
                    state = 'online '
                if w >= 5 and len(name) > 10:
                    name = name[0:9] + '<br>' + name[9:]
                src += '<a href="%s">' % link
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon),
                    imgW, imgH,)
                src += '</a><br>\n'
                percent, remoteFiles = (bstats[supplierNum] if supplierNum < len(bstats) else (0, 0))
                if remoteFiles > 0:
                    src += misc.percent2string(percent)
                    src += ' in %d/%d files<br>on ' % (remoteFiles, 2 * (maxBlockNumber + 1))
                src += '<a href="%s">%s</a>\n' % (link, name)
                src += '</td>\n'
                src += html_comment('    %s in %d/%d files on %s [%s]' % (
                    misc.percent2string(percent), remoteFiles, 2 * (maxBlockNumber + 1), name, state))
            src += '</tr>\n'
        src += '</table>\n'
        src += '<br>\n'
        return html(request, body=src, back='/'+_PAGE_MAIN+'/'+self.backupID)


class BackupRunningPage(Page):
    pagename = _PAGE_BACKUP_RUNNING
    isLeaf = True

    def __init__(self, backupID, backupDir):
        Page.__init__(self)
        self.backupID = backupID
        self.backupDir = backupDir

    def renderPage(self, request):
        backupObj = backup_db.GetRunningBackupObject(self.backupID)
        if backupObj is None:
            dhnio.Dprint(6, 'webcontrol.BackupRunningPage.renderPage %s is not running at the moment, possible is finished?. Redirect now.' % self.backupID)
            request.redirect('/'+_PAGE_MAIN+'/'+self.backupID)
            request.finish()
            return NOT_DONE_YET
        bstats = {} # TODO backupObj.GetStats()
        blockNumber = backupObj.blockNumber + 1
        dirSizeBytes = dirsize.getInBytes(self.backupDir)
        dataSent = backupObj.dataSent
        blocksSent = backupObj.blocksSent
        percent = 0.0
        if dirSizeBytes: # non zero and not None
            if dataSent > dirSizeBytes:
                dataSent = dirSizeBytes
            percent = 100.0 * dataSent / dirSizeBytes
        else:
            dirSizeBytes = 0
        percentSupplier = 100.0 / contacts.numSuppliers()
        sizePerSupplier = dirSizeBytes / contacts.numSuppliers()
        w, h = misc.calculate_best_dimension(contacts.numSuppliers())
        imgW, imgH, padding =  misc.calculate_padding(w, h)
        src = ''
        src += '<table width=95%><tr><td align=center>'
        src += '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p><b>%s</b></p>\n' % self.backupID
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir)) 

        src += '<div align=left><font size="-1"><p>'
        src += 'This backup is currently running.\n'
        src += 'Contents of the folder will be compressed, encrypted and divided into blocks. \n'
        src += 'Below you can see how data is sent to your suppliers. \n'
        src += 'The process will be completed as soon as all blocks will be transferred to suppliers. \n'
        src += 'After this DataHaven.NET will monitor your data and restore the missing blocks. \n'
        src += '</p></font></div>\n'
        src += html_comment('  this backup is currently running')

        src += '<div align=left><p>'
        if dataSent < dirSizeBytes:
            src += 'Currently <b>%s</b> read from total <b>%s</b> folder size, ' % (
                diskspace.MakeStringFromBytes(dataSent),
                diskspace.MakeStringFromBytes(dirSizeBytes))
            src += 'this is <b>%s</b>.\n' % misc.percent2string(percent)
            src += 'Preparing block number <b>%d</b>.\n' % blockNumber
            src += html_comment('  currently %s read from total %s folder size, this is %s' % (
                diskspace.MakeStringFromBytes(dataSent), diskspace.MakeStringFromBytes(dirSizeBytes), misc.percent2string(percent)))
            src += html_comment('  preparing block number %d' % blockNumber)
        else:
            src += 'Folder size is <b>%s</b>, all the files have been processed ' % diskspace.MakeStringFromBytes(dirSizeBytes)
            src += 'and divided into <b>%s</b> blocks.\n' % blockNumber
            src += html_comment('  folder size is %s, all the files have been processed and divided into %s blocks' % (
                diskspace.MakeStringFromBytes(dirSizeBytes), blockNumber))
        src += 'Delivered <b>%d</b> blocks of data at this point.\n' % blocksSent
        src += html_comment('  delivered %d blocks of data at this point' % blocksSent)
        if dataSent >= dirSizeBytes and blockNumber > 0:
            percent_complete = 100.0 * blocksSent / (blockNumber + 1) 
            src += '<br>Backup completed on <b>%s</b>.\n' % misc.percent2string(percent_complete)
            src += html_comment('  backup completed on %s' % misc.percent2string(percent_complete))
        src += '</p></div>\n'
        src += '</td></tr></table>\n'
        src += '<table cellpadding=%d cellspacing=2>\n' % padding
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                src += '<td align=center valign=top>\n'
                supplierNum = y * w + x
                link = '/' + _PAGE_SUPPLIERS + '/' + str(supplierNum) + '?back=%s' % request.path
                if supplierNum >= contacts.numSuppliers():
                    src += '&nbsp;\n'
                    continue
                idurl = contacts.getSupplierID(supplierNum)
                name = nameurl.GetName(idurl)
                if not name:
                    src += '&nbsp;\n'
                    continue
                if idurl:
                    icon = 'icons/offline-user01.png'
                else:
                    icon = 'icons/unknown-user01.png'
                state = 'offline'
                if contact_status.isOnline(idurl):
                    icon = 'icons/online-user01.png'
                    state = 'online '
                if w >= 5 and len(name) > 10:
                    name = name[0:9] + '<br>' + name[9:]
                src += '<a href="%s">' % link
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon),
                    imgW, imgH,)
                src += '</a><br>\n'
                sentBytes, sentDuration = bstats.get(supplierNum, [0, 0])
                if sentBytes > 0:
                    speed = ( sentBytes / 1024.0 ) / sentDuration if sentDuration != 0 else 0
                    perc = percentSupplier * sentBytes / sizePerSupplier
#                    if perc > percentSupplier:
#                        perc = percentSupplier
                    src += '%s in %s <br>\n' % (misc.percent2string(perc), diskspace.MakeStringFromBytes(sentBytes))
                    src += 'to <a href="%s">%s</a><br>\n' % (link, name)
                    src += 'at %s KB/s\n' % round(speed, 1)
                    src += html_comment('    %s in %s at %s KB/s to %s [%s]' % (
                        misc.percent2string(perc), diskspace.MakeStringFromBytes(sentBytes), round(speed, 1), name, state))
                else:
                    src += '<a href="%s">%s</a>\n' % (link, name)
                    src += html_comment('    %s [%s]' % (name, state))
                src += '</td>\n'
            src += '</tr>\n'
        src += '</table>\n'
        src += '<br><br><a href="%s">Show me only local files stored on my HDD</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_LOCAL_FILES)
        src += '<br><br><a href="%s">Let me see the big picture!</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_DIAGRAM)
        src += '<br><br><a href="%s?action=delete">Stop this backup and delete all files associated with it.</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID)
        src += '<br>\n'
        return html(request, body=src, back='/'+_PAGE_MAIN)


class BackupRestoringPage(Page):
    pagename = _PAGE_BACKUP_RESTORING
    isLeaf = True

    def __init__(self, backupID, backupDir):
        Page.__init__(self)
        self.backupID = backupID
        self.backupDir = backupDir

    def renderPage(self, request):
        if not restore_monitor.IsWorking(self.backupID):
            dhnio.Dprint(6, 'webcontrol.BackupRestoringPage.renderPage %s is not restoring at the moment, or finished. redirect!.' % self.backupID)
            request.redirect('/'+_PAGE_MAIN + '/' + self.backupID)
            request.finish()
            return NOT_DONE_YET
        bstats = restore_monitor.GetProgress(self.backupID)
        w, h = misc.calculate_best_dimension(contacts.numSuppliers())
        imgW, imgH, padding =  misc.calculate_padding(w, h)

        src = '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p>%s</p>\n' % self.backupID
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir)) 

        src += '<table width=70%><tr><td align=center>\n'
        src += '<p>This backup is currently restoring,\n'
        src += 'your data is downloaded from remote computers and will be decrypted.</p>\n'
        src += '<p>It should be noted that if too much from your remote suppliers are offline - ' 
        src += 'you need to wait until they become available to restore your data.</p>'
        src += '</td></tr></table>\n'
        src += html_comment('  this backup is currently restoring')

        src += '<table cellpadding=%d cellspacing=2>\n' % padding
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                src += '<td align=center valign=top>\n'
                supplierNum = y * w + x
                link = '/' + _PAGE_SUPPLIERS + '/' + str(supplierNum) + '?back=%s' % request.path
                if supplierNum >= contacts.numSuppliers():
                    src += '&nbsp;\n'
                    continue
                idurl = contacts.getSupplierID(supplierNum)
                name = nameurl.GetName(idurl)
                if not name:
                    src += '&nbsp;\n'
                    continue
                if idurl:
                    icon = 'icons/offline-user01.png'
                else:
                    icon = 'icons/unknown-user01.png'
                state = 'offline'
                if contact_status.isOnline(idurl):
                    icon = 'icons/online-user01.png'
                    state = 'online '
                if w >= 5 and len(name) > 10:
                    name = name[0:9] + '<br>' + name[9:]
                src += '<a href="%s">' % link
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon),
                    imgW, imgH,)
                src += '</a><br>\n'
                received = bstats.get(supplierNum, 0) 
                src += '%s from<br>\n' % diskspace.MakeStringFromBytes(received)
                src += '<a href="%s">%s</a>\n' % (link, name)
                src += '</td>\n'
                src += html_comment('    %s from %s [%s]' % (
                    diskspace.MakeStringFromBytes(received), name, state))
            src += '</tr>\n'
        src += '</table>\n'
        src += '<br><br><a href="%s">Show me only local files stored on my HDD</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_LOCAL_FILES)
        src += '<br><br><a href="%s">Let me see the big picture!</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_DIAGRAM)
        src += '<br><br><a href="%s?action=abort">Abort restoring of my data.</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID)
        src += '<br>\n'
        return html(request, body=src, back='/'+_PAGE_MAIN)


class BackupPage(Page):
    pagename = _PAGE_BACKUP

    def __init__(self, path):
        Page.__init__(self)
        self.backupID = path
        self.backupDir = backup_db.GetDirectoryFromBackupId(self.backupID)
        self.exist = self.backupDir != ''
        self.restorePath = os.path.abspath(os.path.join(
            settings.getRestoreDir(), self.backupID+'.tar'))
        self.fullPath = '/' + _PAGE_MAIN + '/' + self.backupID + '/' + _PAGE_BACKUP_LOCAL_FILES

    def getChild(self, path, request):
        if path == '':
            return self
        elif path == _PAGE_BACKUP_RUNNING:
            return BackupRunningPage(self.backupID, self.backupDir)
        elif path == _PAGE_BACKUP_RESTORING:
            return BackupRestoringPage(self.backupID, self.backupDir)
        elif path == _PAGE_BACKUP_REMOTE_FILES:
            return BackupRemoteFilesPage(self.backupID, self.backupDir)
        elif path == _PAGE_BACKUP_LOCAL_FILES:
            return BackupLocalFilesPage(self.backupID, self.backupDir)
        elif path == _PAGE_BACKUP_DIAGRAM:
            return BackupDiagramPage(self.backupID, self.backupDir)
        elif path == _PAGE_BACKUP_IMAGE:
            return BackupDiagramImage(self.backupID, self.backupDir)
        return BackupPage(path)

    def renderPage(self, request):
        src = ''
        if not self.exist:
            request.redirect('/'+_PAGE_MAIN)
            request.finish()
            return NOT_DONE_YET

        if not backup_db.InitDone:
            request.redirect('/'+_PAGE_MAIN)
            request.finish()
            return NOT_DONE_YET

        action = arg(request, 'action')

        src = '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p>%s</p>\n' % self.backupID
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir)) 

        if action == 'delete':
            backup_db.AbortRunningBackup(self.backupID)
            backup_db.AbortDirectoryBackup(self.backupDir)
            backups.DeleteBackup(self.backupID)
            backup_monitor.Restart()
            request.redirect('/'+_PAGE_MAIN)
            request.finish()
            return NOT_DONE_YET

        elif action == 'deletelocal':
            num, sz = backups.DeleteLocalBackupFiles(self.backupID)
            backups.ReadLocalFiles()
            backup_monitor.Restart()
            src += '<br>\n'
            if num > 0:
                src += '%d files were removed with a total size of %s' % (num, diskspace.MakeStringFromBytes(sz))
                src += html_comment('  %d files were removed with a total size of %s' % (num, diskspace.MakeStringFromBytes(sz)))
            else:
                src += 'This backup does not contain any files stored on your hard disk.'
                src += html_comment('  this backup does not contain any files stored on your hard disk.')
            src += '<br>\n'
            return html(request, body=src, back=request.path)

        elif action == 'restore':
            if not backup_db.IsBackupRunning(self.backupDir):
                restorePath = os.path.abspath(arg(request, 'destination', self.restorePath))
                restore_monitor.Start(self.backupID, restorePath)
                request.redirect('/'+_PAGE_MAIN+'/'+self.backupID+'/'+_PAGE_BACKUP_RESTORING)
                request.finish()
                return NOT_DONE_YET

        elif action == 'restore.open':
            if os.path.isfile(self.restorePath):
                misc.OpenFileInOS(self.restorePath)

        elif action == 'abort':
            restore_monitor.Abort(self.backupID)
        
        backupObj = backup_db.GetRunningBackupObject(self.backupID)
        if backupObj is not None:
            request.redirect('/'+_PAGE_MAIN+'/'+self.backupID+'/'+_PAGE_BACKUP_RUNNING)
            request.finish()
            return NOT_DONE_YET

        if restore_monitor.IsWorking(self.backupID):
            request.redirect('/'+_PAGE_MAIN+'/'+self.backupID+'/'+_PAGE_BACKUP_RESTORING)
            request.finish()
            return NOT_DONE_YET
                
        blocks, percent, weakBlock, weakPercent = backups.GetBackupRemoteStats(self.backupID)
        localPercent, localFiles, totalSize, maxBlockNum, localStats  = backups.GetBackupLocalStats(self.backupID)

#        blocks, percent = backups.GetBackupBlocksAndPercent(self.backupID)
        start_tm = misc.TimeFromBackupID(self.backupID)
        start_dt, start_suf = misc.getDeltaTime(start_tm)

        src += '<table width=70%><tr><td align=center><p>\n'
        if maxBlockNum >= 0:
            src += 'This backup contains <b>%d</b> blocks and ready at <b>%s</b>.<br>' % (maxBlockNum + 1, misc.percent2string(weakPercent))
            src += 'Delivered <b>%s</b> and <b>%s</b> is stored on local HDD.' % (misc.percent2string(percent), misc.percent2string(localPercent))  
            src += html_comment('  contains %d blocks and ready by %s' % (maxBlockNum + 1, misc.percent2string(weakPercent)))
            src += html_comment('  %s delivered, %s stored' % (misc.percent2string(percent), misc.percent2string(localPercent)))
        else:
            src += 'No information about this backup yet.'
            src += html_comment('  no information about this backup yet')
#        backupId_, backupSize, backupStatus, backupStart, backupFinish = backup_db.GetBackupIdRunInfo(self.backupID)
#        if backupFinish != '':
#            try:
#                finish_tm = float(backupFinish)
#                finish_dt, finish_suf = misc.getDeltaTime(finish_tm)
#            except:
#                finish_dt = None
#            if finish_dt is not None:
#                delta_tm = finish_tm - start_tm
#                delta_dt, delta_suf = misc.getDeltaTime(time.time() - delta_tm)
#                if delta_dt is not None:
#                    src += 'Total backup duration is '
#                    if delta_suf != 'seconds':
#                        src += 'about '
#                    src += '<b>%s %s</b>.\n' % (str(int(delta_dt)), delta_suf)
        src += '</p></td></tr></table><br>\n'

        restoreLabel = ' restore my data now '

        if os.path.isfile(self.restorePath) and time.time() - os.path.getmtime(self.restorePath) < 60 and os.path.getsize(self.restorePath) > 0: # made in last minute and is not empty
            src += '<font color=green><h3>There is a new file on your HDD,<br>it seems like your data were restored!</h3></font>\n'
            src += '<p>The data is stored in the file:</p>\n'
            src += '<h3>%s</h3>\n' % wrap_long_string(self.restorePath, 60)
            src += '<br><form action="%s" method="post">\n' % request.path
            src += '<input type="submit" name="submit" value=" open the file " />\n'
            src += '<input type="hidden" name="action" value="restore.open" />\n'
            src += '</form>\n<br>\n'
            restoreLabel = ' I like it! Restore same backup again, please! '

        src += '<br><br><form action="%s" method="post">\n' % request.path
        src += '<input type="submit" name="submit" value="%s" />\n' % restoreLabel
        src += '<input type="hidden" name="action" value="restore" />\n'
        src += '</form>\n<br>\n'

        src += '<br><br><a href="%s">Show me remote files stored on suppliers computers</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_REMOTE_FILES)
        src += '<br><br><a href="%s">Show me only local files stored on my HDD</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_LOCAL_FILES)
        src += '<br><br><a href="%s">Let me see the big picture!</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID + '/' + _PAGE_BACKUP_DIAGRAM)
        src += '<br><br><a href="%s?action=delete">Delete this backup forever!</a>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID)
        src += '<br>\n'

        return html(request, body=src, back='/'+_PAGE_MAIN)


class BackupDiagramPage(Page):
    pagename = _PAGE_BACKUP_DIAGRAM
    isLeaf = True

    def __init__(self, backupID, backupDir):
        Page.__init__(self)
        self.backupID = backupID
        self.backupDir = backupDir
    
    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_MAIN+'/'+self.backupID)
        src = '<h3>%s</h3>\n' % wrap_long_string(str(self.backupDir), 60)
        src += '<p><a href="%s?back=%s">%s</a></p>\n' % ('/'+_PAGE_MAIN+'/'+self.backupID, back, self.backupID) 
        src += html_comment('  [%s] %s' % (self.backupID, self.backupDir))
        src += '<br><br>\n'
        src += '<img width=400 height=400 src="%s?type=circle&width=400&height=400" />\n' % (
           iconurl(request, _PAGE_MAIN+'/'+self.backupID+'/'+_PAGE_BACKUP_IMAGE))
        src += '<br><br><table>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#20f220">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td>local and remote copy is available</td></tr>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#20b220">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td>no local data but remote copy is available</td></tr>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#a2a2f2">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td>remote data exist but not available, local copy is here</td></tr>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#d2d2d2">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td>only local block exist</td></tr>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#e2e282">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td>only remote copy exist but not available</td></tr>\n'
        src += '</table>\n'
        src += '<br>\n'
        return html(request, body=src, back=back, reload='3')
        

class BackupDiagramImage(resource.Resource):
    pagename = _PAGE_BACKUP_IMAGE
    isLeaf = True
    colors = {'D': {'000': '#ffffff', # white | nor local, nor remote
                    '100': '#d2d2d2', # gray  | only local                       
                    '010': '#e2e242', # yellow| only remote, user is not here - data is not available
                    '110': '#7272f2', # blue  | local and remote, but user is out 
                    '001': '#ffffff', # white | nor local, nor remote, but supplier is here
                    '101': '#d2d2d2', # gray  | only local and user is here
                    '011': '#20b220', # green | only remote and user is here - this should be GREEN!
                    '111': '#20f220', # lgreen| all is here - absolutely GREEN! 
                    }, 
              'P': {'000': '#ffffff', # make small difference for Parity packets
                    '100': '#dddddd', 
                    '010': '#eded4d',
                    '110': '#7d7dfd', 
                    '001': '#ffffff', 
                    '101': '#dddddd', 
                    '011': '#20bd20', 
                    '111': '#20ff20',  
                    }}

    def __init__(self, backupID, backupDir):
        self.backupID = backupID
        self.backupDir = backupDir
    
    def toInt(self, f):
        return int(round(f))
    
    def render_GET(self, request):
        request.responseHeaders.setRawHeaders("content-type", ['image/png'])
        try:
            import Image
            import ImageDraw
            import ImageFont
            import cStringIO
        except:
            # 1x1 png picture 
            src = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAABp0RVh0\nU29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAADElEQVQYV2P4//8/AAX+Av6nNYGEAAAA\nAElFTkSuQmCC\n'
            bin = misc.AsciiToBinary(src)
            request.write(bin)
            request.finish()
            return NOT_DONE_YET
        backupID = self.backupID
        type = arg(request, 'type')
        width = misc.ToInt(arg(request, 'width'), 64)
        height = misc.ToInt(arg(request, 'height'), 64)
        img = Image.new("RGB", (width, height), "#fff")
        draw = ImageDraw.Draw(img)
        f = cStringIO.StringIO()
        try:
            font = ImageFont.truetype(settings.FontImageFile(), 12)
        except:
            font = None
        if not backupID:
            img.save(f, "PNG")
            f.seek(0)
            request.write(f.read())
            request.finish()
            return NOT_DONE_YET
        arrayLocal = backups.GetBackupLocalArray(backupID)
        arrayRemote = backups.GetBackupRemoteArray(backupID)
        suppliersActive = backups.suppliers_set().GetActiveArray()
        w = backups.suppliers_set().supplierCount
        h = backups.GetKnownMaxBlockNum(backupID) + 1
        backupObj = backup_db.GetRunningBackupObject(backupID)
        if backupObj is not None:
            dirSizeBytes = dirsize.getInBytes(backup_db.GetDirectoryFromBackupId(backupID), 0)
            h = ( dirSizeBytes / backupObj.blockSize ) + 1 
        if h == 0 or w == 0:
            img.save(f, "PNG")
            f.seek(0)
            request.write(f.read())
            request.finish()
            return NOT_DONE_YET
        if type == 'bar':
            dx = float(width-2) / float(h)
            dy = float(height-2) / float(w)
            for x in range(h): # blocks
                for y in range(w): # suppliers
                    for DP in ['D', 'P']:
                        remote = (0 if (arrayRemote is None or not arrayRemote.has_key(x)) else (0 if arrayRemote[x][DP][y] != 1 else 1))
                        active = suppliersActive[y]
                        local = (0 if (arrayLocal is None or not arrayLocal.has_key(x)) else arrayLocal[x][DP][y])
                        color = self.colors[DP]['%d%d%d' % (local, remote, active)]
                        x0 = 1 + x * dx
                        y0 = 1 + y * dy
                        if DP == 'P':
                            draw.polygon([
                                (self.toInt(x0),                self.toInt(y0)),
                                (self.toInt(x0),                self.toInt(y0 + dy)), 
                                (self.toInt(x0 + dx / 2.0 - 1), self.toInt(y0 + dy)), 
                                (self.toInt(x0 + dx / 2.0 - 1), self.toInt(y0)),], 
                                fill=color, outline=None)
                        else: 
                            draw.polygon([
                                (self.toInt(x0 + dx / 2.0),     self.toInt(y0)),
                                (self.toInt(x0 + dx / 2.0),     self.toInt(y0 + dy)), 
                                (self.toInt(x0 + dx - 1),       self.toInt(y0 + dy)), 
                                (self.toInt(x0 + dx - 1),       self.toInt(y0)),], 
                                fill=color, outline=None) 
            draw.polygon([(0,0), (0, height-1), (width-1, height-1), (width-1, 0)], fill=None, outline="#555555")
        elif type == 'circle':
            x0 = (width - 2) / 2.0
            y0 = (height - 2) / 2.0
            R = float(min(width, height)) / 2.0 - 1
            dR = R / float(h) 
            dA = 360.0 / float(w)
            for x in range(h): # blocks
                for y in range(w): # suppliers
                    for DP in ['D', 'P']:
                        remote = (0 if (arrayRemote is None or not arrayRemote.has_key(x)) else (0 if arrayRemote[x][DP][y] != 1 else 1))
                        active = suppliersActive[y]
                        local = (0 if (arrayLocal is None or not arrayLocal.has_key(x)) else arrayLocal[x][DP][y])
                        color = self.colors[DP]['%d%d%d' % (local, remote, active)]
                        r1 = R - dR * x
                        r12 = R - dR * x - dR/2.0
                        r2 = R - dR * x - dR
                        if DP == 'D':
                            box = (self.toInt(x0 - r1), self.toInt(y0 - r1),
                                   self.toInt(x0 + r1), self.toInt(y0 + r1))
                        else:
                            box = (self.toInt(x0 - r12), self.toInt(y0 - r12),
                                   self.toInt(x0 + r12), self.toInt(y0 + r12))
                        start = float(y) * dA
                        end = start + dA
                        draw.pieslice(box, self.toInt(start), self.toInt(end), fill=color, outline=None)
            for y in range(w):
                start = float(y) * dA
                end = start + dA
                draw.pieslice(( self.toInt(x0 - R), self.toInt(y0 - R), 
                                self.toInt(x0 + R), self.toInt(y0 + R)),
                                self.toInt(start), self.toInt(end), outline='#555555', fill=None)
            if width > 256 and height > 256:
                for supplierNum in range(w):
                    a = float(supplierNum) * dA + dA / 2.0 
                    x1 = math.cos(a * math.pi / 180.0) * R * 0.7 + x0
                    y1 = math.sin(a * math.pi / 180.0) * R * 0.7 + y0
                    draw.text((x1-20, y1-5), 
                              '%s' % nameurl.GetName(contacts.getSupplierID(supplierNum)), 
                              fill="#000000", font=font)
        img.save(f, "PNG")
        f.seek(0)
        request.write(f.read())
        request.finish()
        return NOT_DONE_YET


class SupplierPage(Page):
    pagename = _PAGE_SUPPLIER
    #isLeaf = True
    def __init__(self, path):
        Page.__init__(self)
        self.path = path
        try:
            self.index = int(self.path)
        except:
            self.index = -1
            self.idurl = ''
            self.name = ''
            return
        self.idurl = contacts.getSupplierID(self.index)
        protocol, host, port, self.name = nameurl.UrlParse(self.idurl)
        self.name = self.name.strip()[0:-4]

    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_SUPPLIERS)
        src = ''
        if self.idurl == '':
            src = '<h1>Unknown supplier</h1>\n'
            return html(request, body=src)

        action = arg(request, 'action')

        if action == 'replace':
            msg = ''
            msg += '<font color=red><b>WARNING!</b></font><br>\n'
            msg += 'After changing one of your suppliers DataHaven.NET start the rebuilding process to distribute your data.\n' 
            msg += 'This takes some time depending on data size and network speed.<br>\n'
            msg += 'If you change your suppliers too often you can loose your backed up data!<br>' 
            msg += 'Do you want to replace user <b>%s</b> with someone else?' % nameurl.GetName(self.idurl)
            replace_link = '%s?urlyes=%s&urlno=%s&text=%s&back=%s' % (
                '/'+_PAGE_CONFIRM, 
                misc.pack_url_param('%s?action=yes.replace&back=%s' % (request.path, back)),
                misc.pack_url_param(request.path),
                misc.pack_url_param(msg),
                back)
            request.redirect(replace_link)
            request.finish()
            return NOT_DONE_YET
        elif action == 'yes.replace':
            # fire_hire.A('fire-him-now', self.idurl)
            # request.redirect('/'+_PAGE_SUPPLIERS)
            url = '%s?action=replace&idurl=%s&back=%s' % ('/'+_PAGE_SUPPLIERS, misc.pack_url_param(self.idurl), request.path)
            request.redirect(url)
            request.finish()
            return NOT_DONE_YET

        src += '<h1>%s</h1>\n' % nameurl.GetName(self.idurl)
        if contact_status.isOnline(self.idurl):
            src += '<br><font color="green">is online</font>\n'
        else:
            src += '<br><font color="red">is offline</font>\n'
        src += '<br><br>\n'
        src += '<p><a href="%s" target="_blank">%s</a></p>\n' % (self.idurl, self.idurl)
        src += '<p><a href="%s?action=replace&back=%s">Fire %s and find another person to store My Files</a></p>\n' % (
            request.path, back, self.name)
        src += '<p><a href="%s/change?back=%s">I want to swap %s with another person, whom I will choose</a></p>\n' % (
            request.path, back, self.name)
        src += '<p><a href="%s/remotefiles?back=%s">Show me a list of My Files stored on %s\'s machine</a></p>\n' % (
            request.path, back, self.name)
        src += '<p><a href="%s/localfiles?back=%s">Print a list of My Files stored on my machine but intended for %s</a></p>\n' % (
            request.path, back, self.name)
        src += '<br><br>\n'
        return html(request, body=src, back=back, title=self.name)

    def getChild(self, path, request):
        if self.idurl == '':
            return self
        if path == 'remotefiles':
            return SupplierRemoteFilesPage(self.idurl)
        elif path == 'localfiles':
            return SupplierLocalFilesPage(self.idurl)
        elif path == 'change':
            return SupplierChangePage(self.idurl)
        return self
    
class SupplierRemoteFilesPage(Page):
    pagename = _PAGE_SUPPLIER_REMOTE_FILES
    def __init__(self, idurl):
        Page.__init__(self)
        self.idurl = idurl
        self.supplierNum = contacts.numberForSupplier(self.idurl)
        self.name = nameurl.GetName(self.idurl)
        
    def renderPage(self, request):
        back = arg(request,'back','/'+_PAGE_SUPPLIERS+'/'+str(self.supplierNum))
        title = 'remote files on %s' % self.name
        action = arg(request, 'action')
        src = '<h1>%s</h1>\n' % title
        
        if action == 'files':
            packetID = p2p_service.RequestListFiles(self.supplierNum)
            src += html_message('list of your files were requested', 'notify')

        list_files_src = dhnio.ReadTextFile(settings.SupplierListFilesFilename(self.idurl))
        if list_files_src:
            src += '<table width=70%><tr><td align=center>\n'
            src += '<div><code>\n'
            src += list_files_src[list_files_src.find('\n'):].replace('\n', '<br>\n').replace(' ', '&nbsp;')
            src += '</code></div>\n</td></tr></table>\n'
        else:
            src += '<p>no information about your files received yet</p>\n'
        src += '<p><a href="%s?action=files&back=%s">Request a list of My Files from %s</a></p>\n' % (request.path, back, self.name)
        return html(request, body=src, back=back, title=title)

class SupplierLocalFilesPage(Page):
    pagename = _PAGE_SUPPLIER_LOCAL_FILES

    def __init__(self, idurl):
        Page.__init__(self)
        self.idurl = idurl
        self.supplierNum = contacts.numberForSupplier(self.idurl)
        self.name = nameurl.GetName(self.idurl)
        
    def renderPage(self, request):
        back = arg(request,'back','/'+_PAGE_SUPPLIERS+'/'+str(self.supplierNum))
        title = 'local files for %s' % self.name
        src = '<h1>%s</h1>\n' % title
        list_files = []
        for filename in os.listdir(settings.getLocalBackupsDir()):
            if filename.startswith('newblock-'):
                continue
            try:
                backupID, blockNum, supplierNum, dataORparity  = filename.split('-')
                blockNum = int(blockNum)
                supplierNum = int(supplierNum)
            except:
                continue
            if dataORparity not in ['Data', 'Parity']:
                continue
            if supplierNum != self.supplierNum:
                continue
            list_files.append(filename)
        if len(list_files) > 0:
            src += '<table width=70%><tr><td align=center>\n'
            src += '<div><code>\n'
            for filename in list_files:
                src += filename + '<br>\n' 
            src += '</code></div>\n</td></tr></table>\n'
        else:
            src += '<p>no files found</p>\n' 
        return html(request, body=src, back=back, title=title)

class SupplierChangePage(Page):
    pagename = _PAGE_SUPPLIER_CHANGE

    def __init__(self, idurl):
        Page.__init__(self)
        self.idurl = idurl
        self.supplierNum = contacts.numberForSupplier(self.idurl)
        self.name = nameurl.GetName(self.idurl)
        
    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_SUPPLIERS)
        action = arg(request, 'action')
        if action == 'do.change':
            newidurl = arg(request, 'newidurl')
            url = '%s?action=change&idurl=%s&newidurl=%s&back=%s' % (
                '/'+_PAGE_SUPPLIERS, misc.pack_url_param(self.idurl), 
                misc.pack_url_param(newidurl), request.path)
            request.redirect(url)
            request.finish()
            return NOT_DONE_YET
        src = ''
        src += '<br><br><br><br>\n'
        src += '<table width=50%><tr><td align=center>\n'
        src += '<p>'
        src += '<font color=red><b>WARNING!</b></font><br>\n'
        src += 'After changing one of your suppliers DataHaven.NET start the rebuilding process to distribute your data.\n' 
        src += 'This takes some time depending on data size and network speed.<br>\n'
        src += 'If you change your suppliers too often you can loose your backed up data!'
        src += '</p><br><br>\n'
        src += '<p>Type a username or IDURL here:</p>\n' 
        src += '<form action="%s">\n' % request.path
        src += '<input type="text" name="newidurl" value="" size=60 /><br><br>\n'
        src += '<input type="submit" name="submit" value=" swap supplier " />\n'
        src += '<input type="hidden" name="action" value="do.change" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % request.path
        src += '</form>\n'
        src += '</td></tr></table>\n'
        return html(request, body=src, back=back, title=self.name)
        

class SuppliersPage(Page):
    pagename = _PAGE_SUPPLIERS
    def __init__(self):
        Page.__init__(self)
        self.show_ratings = False

    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_MENU)
        #---show_ratings---
        if arg(request, 'ratings') == '1':
            self.show_ratings = True
        elif arg(request, 'ratings') == '0':
            self.show_ratings = False
            
        action = arg(request, 'action')
        if action == 'call':
            #---action call---
            transport_control.ClearAliveTimeSuppliers()
            contact_status.check_contacts(contacts.getSupplierIDs())
            identitypropagate.SlowSendSuppliers(0.2)
            request.redirect(request.path)
            request.finish()
            return NOT_DONE_YET
            #DHNViewSendCommand('open %s' % request.path)
            
        elif action == 'replace':
            #---action replace---
            idurl = arg(request, 'idurl')
            if idurl != '':
                if not idurl.startswith('http://'):
                    try:
                        idurl = contacts.getSupplierID(int(idurl))
                    except:
                        idurl = 'http://'+settings.IdentityServerName()+'/'+idurl+'.xml'
                if contacts.IsSupplier(idurl):
                    fire_hire.A('fire-him-now', idurl)
        
        elif action == 'change':
            #---action change---
            idurl = arg(request, 'idurl')
            newidurl = arg(request, 'newidurl')
            if idurl != '' and newidurl != '':
                if not idurl.startswith('http://'):
                    try:
                        idurl = contacts.getSupplierID(int(idurl))
                    except:
                        idurl = 'http://'+settings.IdentityServerName()+'/'+idurl+'.xml'
                if not newidurl.startswith('http://'):
                    newidurl = 'http://'+settings.IdentityServerName()+'/'+newidurl+'.xml'
                if contacts.IsSupplier(idurl):
                    fire_hire.A('fire-him-now', (idurl, newidurl))
                

        #---draw page---
        src = ''
        src += '<h1>suppliers</h1>\n'

        if contacts.numSuppliers() > 0:
            w, h = misc.calculate_best_dimension(contacts.numSuppliers())
            #DEBUG
            #w = 8; h = 8
#            paddingX = str(40/w)
#            paddingY = str(160/h)
#            fontsize = str(60 + 200/(w*w))
#            fontsize = str(10-w)
            imgW = 64
            imgH = 64
            if w >= 4:
                imgW = 4 * imgW / w
                imgH = 4 * imgH / w
            padding = 64 / w - 8 
            src += html_comment('  index status    user                 month rating         total rating' ) 
            src += '<table cellpadding=%d cellspacing=2>\n' % padding #width="90%%"
            for y in range(h):
                src += '<tr valign=top>\n'
                for x in range(w):
                    src += '<td align=center valign=top>\n'
                    n = y * w + x
                    link = _PAGE_SUPPLIERS+'/'+str(n)+'?back='+back
                    if n >= contacts.numSuppliers():
                        src += '&nbsp;\n'
                        continue

                    idurl = contacts.getSupplierID(n)
                    name = nameurl.GetName(idurl)
                    if not name:
                        src += '&nbsp;\n'
                        continue
                    
                    #---icon---
                    if idurl:
                        icon = 'icons/offline-user01.png'
                    else:
                        icon = 'icons/unknown-user01.png'
                    state = 'offline'
                    if contact_status.isOnline(idurl):
                        icon = 'icons/online-user01.png'
                        state = 'online '

                    if w >= 5 and len(name) > 10:
                        name = name[0:9] + '<br>' + name[9:]
                    src += '<a href="%s">' % link
                    src += '<img src="%s" width=%d height=%d>' % (
                        iconurl(request, icon),
                        imgW, imgH,)
                    src += '</a><br>\n'
                    central_status = central_service._CentralStatusDict.get(idurl, '')
                    central_status_color = {'!':'green', 'x':'red'}.get(central_status, 'gray')
                    #src += '<img src="%s" width=15 height=15>' % iconurl(request, central_status_icon)
                    src += '<font color="%s">' % central_status_color
                    src += '%s' % name
                    src += '</font>\n'

                    #---show_ratings---
                    if self.show_ratings:
                        src += '<font size=1>\n'
                        src += '<table cellpadding=0 cellspacing=0 border=0>\n'
                        src += '<tr><td>%s%% - %s/%s</td></tr></table>\n' % (
                            ratings.month_percent(idurl),
                            ratings.month(idurl)['alive'],
                            ratings.month(idurl)['all'])

                    #---show_contacts---
                    if dhnio.Debug(8):
                        idobj = contacts.getSupplier(idurl)
                        idcontacts = []
                        if idobj:
                            idcontacts = idobj.getContacts()
                        if len(idcontacts) > 0:
                            src += '<font size=1>\n'
                            src += '<table cellpadding=0 cellspacing=0 border=0>\n'
                            for c in idcontacts:
                                src += '<tr><td>'
                                src += c[0:26]
                                src += '</td></tr>\n'
                            src += '</table>\n'
                            src += '</font>\n'

                    src += '</td>\n'

                    #---html_comment---
                    month_str = '%d%% %s/%s' % (
                        ratings.month_percent(idurl),
                        ratings.month(idurl)['alive'],
                        ratings.month(idurl)['all'],)
                    total_str = '%d%% %s/%s' % (
                        ratings.total_percent(idurl),
                        ratings.total(idurl)['alive'],
                        ratings.total(idurl)['all'],)
                    src += html_comment('  %s [%s] %s %s %s' % (
                        str(n).rjust(5),
                        state, 
                        nameurl.GetName(idurl).ljust(20),
                        month_str.ljust(20),
                        total_str.ljust(20),))
                        
                src += '</tr>\n'

            src += '</table>\n'

            if dhnio.Debug(8):
                idcontacts = misc.getLocalIdentity().getContacts()
                if len(idcontacts) > 0:
                    src += '<font size=1>\n'
                    src += 'my contacts is:\n'
                    src += '<table cellpadding=0 cellspacing=0 border=0>\n'
                    for c in idcontacts:
                        src += '<tr><td>'
                        src += c[0:26]
                        src += '</td></tr>\n'
                    src += '</table>\n'
                    src += '</font>\n'

            src += '<br><br><p><a href="?action=call&back=%s">Call all suppliers to find out who is alive</a></p><br>\n' % back

        else:
            src += '<table width="80%"><tr><td>\n'
            src += '<p>List of your suppliers is empty.</p>\n'
            src += '<p>This may be due to the fact that the connection to the Central server is not finished yet\n'
            src += 'or the Central server can not find the number of users that meet your requirements.</p>\n'
            src += '<p>Wait a bit and or check your Central options in the Settings.</p>\n'
            src += '<p>If you request too much needed space, you may not find the right number of suppliers.</p><br>\n'
            src += '</td></tr></table>\n'
            src += html_comment(
                'List of your suppliers is empty.\n'+
                'This may be due to the fact that the connection to the Central server is not finished yet\n'+
                'or the Central server can not find the number of users that meet your requirements.')

        src += '<p><a href="%s?back=%s">Switch to Customers</a></p>\n' % ('/'+_PAGE_CUSTOMERS, back)
        if self.show_ratings:
            src += '<p><a href="%s?ratings=0&back=%s">Hide monthly ratings</a></p>\n' % (request.path, back)
        else:
            src += '<p><a href="%s?ratings=1&back=%s">Show monthly ratings</a></p>\n' % (request.path, back)
        return html(request, body=src, title='suppliers', back=back, reload='5',)

    def getChild(self, path, request):
        if path == '':
            return self
        return SupplierPage(path)

class CustomerPage(Page):
    pagename = _PAGE_CUSTOMER
    
    def __init__(self, path):
        Page.__init__(self)
        self.path = path
        try:
            self.index = int(self.path)
        except:
            self.index = -1
            self.idurl = ''
            self.name = ''
            return
        self.idurl = contacts.getCustomerID(self.index)
        protocol, host, port, self.name = nameurl.UrlParse(self.idurl)
        self.name = self.name.strip()[0:-4]

    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_CUSTOMERS)

        if self.idurl == '':
            src = '<p>Wrong customer number.</p>\n'
            return html(request, body=src, back=back)

        action = arg(request, 'action')
        
        if action == 'remove':
            if contacts.IsCustomer(self.idurl):
                central_service.SendReplaceCustomer(self.idurl)
                request.redirect('/'+_PAGE_CUSTOMERS)
                request.finish()
                return NOT_DONE_YET

        src = ''
        src += '<br><h1>%s</h1>\n' % nameurl.GetName(self.idurl)
        if contact_status.isOnline(self.idurl):
            src += '<font color="green">is online</font>\n'
        else:
            src += '<font color="red">is offline</font>\n'
        src += '<br>\n'
        src += '<p><a href="%s" target="_blank">%s</a></p>\n' % (self.idurl, self.idurl)
        src += '<p><a href="%s?action=remove&back=%s">Dismis customer %s and throw out His/Her Files from my HDD</a></p>\n' % (
            request.path, back, self.name)
        src += '<p><a href="%s/files?back=%s">Show me %s\'s Files</a></p>\n' % (
            request.path, back, self.name)
        return html(request, body=src, title=self.name, back=back)

    def getChild(self, path, request):
        if path == 'files':
            return CustomerFilesPage(self.idurl)
        return self

class CustomerFilesPage(Page):
    pagename = _PAGE_CUSTOMER_FILES

    def __init__(self, idurl):
        Page.__init__(self)
        self.idurl = idurl
        self.customerNum = contacts.numberForCustomer(self.idurl)
        self.name = nameurl.GetName(self.idurl)
        
    def renderPage(self, request):
        back = arg(request,'back','/'+_PAGE_CUSTOMERS+'/'+str(self.customerNum))
        title = '%s\'s files' % self.name
        src = '<h1>%s</h1>\n' % title
        list_files = []
        customer_dir = settings.getCustomerFilesDir(self.idurl)
        if os.path.isdir(customer_dir):
            for filename in os.listdir(customer_dir):
                list_files.append(filename)
        if len(list_files) > 0:
            src += '<table width=70%><tr><td align=center>\n'
            src += '<div><code>\n'
            for filename in list_files:
                src += filename + '<br>\n' 
            src += '</code></div>\n</td></tr></table>\n'
        else:
            src += '<p>no files found</p>\n' 
        return html(request, body=src, back=back, title=title)
    
class CustomersPage(Page):
    pagename = _PAGE_CUSTOMERS
    def __init__(self):
        Page.__init__(self)
        self.show_ratings = False

    def renderPage(self, request):
        back = arg(request, 'back', '/'+_PAGE_MENU)
        #---show_ratings---
        if arg(request, 'ratings') == '1':
            self.show_ratings = True
        elif arg(request, 'ratings') == '0':
            self.show_ratings = False
        
        action = arg(request, 'action')

        if action == 'call':
            #---action call---
            transport_control.ClearAliveTimeCustomers()
            contact_status.check_contacts(contacts.getCustomerIDs())
            identitypropagate.SlowSendCustomers(0.2)
            request.redirect(request.path)
            request.finish()
            return NOT_DONE_YET

        elif action == 'remove':
            #---action remove---
            idurl = arg(request, 'idurl')
            if idurl != '':
                if not idurl.startswith('http://'):
                    try:
                        idurl = contacts.getCustomerID(int(idurl))
                    except:
                        idurl = 'http://'+settings.IdentityServerName()+'/'+idurl+'.xml'
                if contacts.IsCustomer(idurl):
                    central_service.SendReplaceCustomer(idurl)

        src = ''
        src += '<h1>customers</h1>\n'

        if contacts.numCustomers() > 0:
            w, h = misc.calculate_best_dimension(contacts.numCustomers())
            imgW = 64
            imgH = 64
            if w > 4:
                imgW = 4 * imgW / w
                imgH = 4 * imgH / w
            padding = 64/w - 8
            src += html_comment('  index status    user                 month rating         total rating' ) 
            src += '<table cellpadding=%d cellspacing=2>\n' % padding
            for y in range(h):
                src += '<tr valign=top>\n'
                for x in range(w):
                    src += '<td align=center valign=top>\n'
                    n = y * w + x
                    link = _PAGE_CUSTOMERS+'/'+str(n)+'?back='+back
                    if n >= contacts.numCustomers():
                        src += '&nbsp;\n'
                        continue

                    idurl = contacts.getCustomerID(n)
                    name = nameurl.GetName(idurl)
                    if not name:
                        src += '&nbsp;\n'
                        continue

                    #---icon---
                    icon = 'icons/offline-user01.png'
                    state = 'offline'
                    if contact_status.isOnline(idurl):
                        icon = 'icons/online-user01.png'
                        state = 'online '

                    if w >= 5 and len(name) > 10:
                        name = name[0:9] + '<br>' + name[9:]
                    src += '<a href="%s">' % link
                    src += '<img src="%s" width=%d height=%d>' % (
                        iconurl(request, icon),
                        imgW, imgH,)
                    src += '</a><br>\n'
                    central_status = central_service._CentralStatusDict.get(idurl, '')
                    central_status_color = {'!':'green', 'x':'red'}.get(central_status, 'gray')
                    src += '<font color="%s">' % central_status_color
                    src += '%s' % name
                    src += '</font>\n'

                    #---show_ratings---
                    if self.show_ratings:
                        src += '<font size=1>\n'
                        src += '<table cellpadding=0 cellspacing=0 border=0>\n'
                        src += '<tr><td>%s%% - %s/%s</td></tr></table>\n' % (
                            ratings.month_percent(idurl),
                            ratings.month(idurl)['alive'],
                            ratings.month(idurl)['all'])

                    #--show_contacts---
                    if dhnio.Debug(8):
                        idobj = contacts.getCustomer(idurl)
                        idcontacts = []
                        if idobj:
                            idcontacts = idobj.getContacts()
                        if len(idcontacts) > 0:
                            src += '<font size=1>\n'
                            src += '<table cellpadding=0 cellspacing=0 border=0>\n'
                            for c in idcontacts:
                                src += '<tr><td>'
                                src += c[0:26]
                                src += '</td></tr>\n'
                            src += '</table>\n'
                            src += '</font>\n'

                    src += '</td>\n'
                    
                    #---html_comment---
                    month_str = '%d%% %s/%s' % (
                        ratings.month_percent(idurl),
                        ratings.month(idurl)['alive'],
                        ratings.month(idurl)['all'],)
                    total_str = '%d%% %s/%s' % (
                        ratings.total_percent(idurl),
                        ratings.total(idurl)['alive'],
                        ratings.total(idurl)['all'],)
                    src += html_comment('  %s [%s] %s %s %s' % (
                        str(n).rjust(5),
                        state, 
                        nameurl.GetName(idurl).ljust(20),
                        month_str.ljust(20),
                        total_str.ljust(20),))

                src += '</tr>\n'

            src += '</table>\n'
            src += '<br><br><p><a href="?action=call&back=%s">Call all customers to find out who is alive</a></p><br>\n' % back

        else:
            src += '<p>List of your customers is empty.<br></p>\n'
            src += html_comment('List of your customers is empty.\n')

        src += '<p><a href="%s?back=%s">Switch to Suppliers</a></p>\n' % ('/'+_PAGE_SUPPLIERS, back)
        if self.show_ratings:
            src += '<p><a href="%s?ratings=0&back=%s">Hide monthly ratings</a></p>\n' % (request.path, back)
        else:
            src += '<p><a href="%s?ratings=1&back=%s">Show monthly ratings</a></p>\n' % (request.path, back)
        return html(request, body=src, title='customers', back=back, reload='5',)

    def getChild(self, path, request):
        if path == '': 
            return self
        return CustomerPage(path)


class StoragePage(Page):
    pagename = _PAGE_STORAGE
    def renderPage(self, request):
        bytesNeeded = diskspace.GetBytesFromString(settings.getCentralMegabytesNeeded(), 0)
        bytesDonated = diskspace.GetBytesFromString(settings.getCentralMegabytesDonated(), 0)
        bytesUsed = backup_db.GetTotalBackupsSize()
        suppliers_count = contacts.numSuppliers() 
        bytesNeededPerSupplier = bytesNeeded / suppliers_count 
        bytesUsedPerSupplier = bytesUsed / suppliers_count
        dataDir = settings.getCustomersFilesDir()
        dataDriveFreeSpace, dataDriveTotalSpace = diskusage.GetDriveSpace(dataDir)
        if dataDriveFreeSpace is None:
            dataDriveFreeSpace = 0
        customers_count = contacts.numCustomers()
        spaceDict = dhnio._read_dict(settings.CustomersSpaceFile(), {})
        totalCustomersMB = 0.0
        try:
            freeDonatedMB = float(spaceDict.get('free', bytesDonated/(1024*1024)))
        except:
            dhnio.DprintException()
            freeDonatedMB = 0.0
        if freeDonatedMB < 0:
            freeDonatedMB = 0.0
        try:
            for idurl in contacts.getCustomerIDs():
                totalCustomersMB += float(spaceDict.get(idurl, '0.0'))
        except:
            dhnio.DprintException()
            totalCustomersMB = 0.0
        if totalCustomersMB < 0:
            totalCustomersMB = 0.0
        currentlyUsedDonatedBytes = dhnio.getDirectorySize(dataDir)
        StringNeeded = diskspace.MakeStringFromBytes(bytesNeeded)
        StringDonated = diskspace.MakeStringFromBytes(bytesDonated)
        StringUsed = diskspace.MakeStringFromBytes(bytesUsed)
        StringNeededPerSupplier = diskspace.MakeStringFromBytes(bytesNeededPerSupplier)
        StringUsedPerSupplier = diskspace.MakeStringFromBytes(bytesUsedPerSupplier)
        StringDiskFreeSpace = diskspace.MakeStringFromBytes(dataDriveFreeSpace)
        StringTotalCustomers = diskspace.MakeStringFromBytes(totalCustomersMB*1024.0*1024.0)
        StringFreeDonated = diskspace.MakeStringFromBytes(freeDonatedMB*1024.0*1024.0)
        StringUsedDonated = diskspace.MakeStringFromBytes(currentlyUsedDonatedBytes)
        try:
            PercNeed = 100.0 * bytesUsed / bytesNeeded
        except:
            PercNeed = 0.0
        try:
            PercAllocated = (100.0*totalCustomersMB/(totalCustomersMB+freeDonatedMB))
        except:
            PercAllocated = 0.0
        try:
            PercDonated = (100.0*currentlyUsedDonatedBytes/bytesDonated)
        except:
            PercDonated = 0.0
        src = ''
        src += '<h1>storage</h1>\n'
        src += '<table><tr>\n'
        src += '<td valign=top align=center>\n'
        src += '<h3>needed</h3>\n'
        src += '<img src="%s?width=300&height=300" /><br>\n' % (iconurl(request, _PAGE_STORAGE+'/needed'))
        src += '<table>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>\n'
        src += '<td bgcolor="#82f282">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td nowrap>needed</td>\n'
        src += '<td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#22b222">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td nowrap>used</td></tr>\n'
        src += '</table>\n'
        src += '<table>\n'
        src += html_comment('needed space:')
        src += '<tr><td nowrap>number of <a href="%s">suppliers</a>:</td><td nowrap><b>%d</b></td></tr>\n' % ('/'+_PAGE_SUPPLIERS, suppliers_count)
        src += html_comment('  number of suppliers: %d' % suppliers_count)
        src += '<tr><td nowrap>space given to you:</td><td nowrap><b>%s</b></td></tr>\n' % StringNeeded 
        src += html_comment('  space given to you: %s' % StringNeeded)
        src += '<tr><td nowrap>space used at the moment:</td><td nowrap><b>%s</b></td></tr>\n' % StringUsed
        src += html_comment('  space used at the moment: %s' % StringUsed) 
        src += '<tr><td nowrap>percentage used:</td><td nowrap><b>%3.2f%%</b></td></tr>\n' % PercNeed
        src += html_comment('  percentage used: %3.2f%%' % PercNeed)
        src += '<tr><td nowrap>each supplier gives you:</td><td nowrap><b>%s</b></td></tr>\n' % StringNeededPerSupplier 
        src += html_comment('  each supplier gives you: %s' % StringNeededPerSupplier)
        src += '<tr><td nowrap>space used per supplier:</td><td nowrap><b>%s</b></td></tr>\n' % StringUsedPerSupplier
        src += html_comment('  space used per supplier: %s' % StringUsedPerSupplier)   
        src += '</table>\n'
        src += '</td>\n'
        src += '<td valign=top align=center>\n'
        src += '<h3 align=center>donated</h3>\n'
        src += '<img src="%s?width=300&height=300" /><br>\n' % (iconurl(request, _PAGE_STORAGE+'/donated'))
        src += '<table>\n'
        src += '<tr><td><table border=1 cellspacing=0 cellpadding=0><tr>\n'
        src += '<td bgcolor="#e2e242">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td nowrap>donated</td>\n'
        src += '<td><table border=1 cellspacing=0 cellpadding=0><tr>'
        src += '<td bgcolor="#a2a202">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td nowrap>used</td>\n'
        src += '<td align=center><table border=1 cellspacing=0 cellpadding=0><tr>\n'
        src += '<td bgcolor="#ffffff">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr></table></td>\n'
        src += '<td nowrap>free</td><td>&nbsp;</td></tr>\n'
        src += '</table>\n'
        src += '<table>\n'
        src += html_comment('donated space:')
        src += '<tr><td nowrap>number of <a href="%s">customers</a>:</td><td nowrap><b>%d</b></td></tr>\n' % ('/'+_PAGE_CUSTOMERS, customers_count)
        src += html_comment('  number of customers: %d' % customers_count)
        if bytesDonated > dataDriveFreeSpace:
            src += '<tr><td nowrap>your donated space:</td><td nowrap><b><font color="red">%s</font></b></td></tr>\n' % StringDonated
        else:
            src += '<tr><td nowrap>your donated space:</td><td nowrap><b>%s</b></td></tr>\n' % StringDonated
        src += html_comment('  your donated space: %s' % StringDonated) 
        src += '<tr><td nowrap>free space on the disk:</td><td nowrap><b>%s</b></td></tr>\n' % StringDiskFreeSpace 
        src += html_comment('  free space on the disk: %s' % StringDiskFreeSpace)
        src += '<tr><td nowrap>space taken by customers:</td><td nowrap><b>%s</b></td></tr>\n' % StringTotalCustomers
        src += html_comment('  space taken by customers: %s' % StringTotalCustomers) 
        src += '<tr><td nowrap>free donated space:</td><td nowrap><b>%s</b></td></tr>\n' % StringFreeDonated 
        src += html_comment('  free donated space: %s' % StringFreeDonated) 
        src += '<tr><td nowrap>percentage allocated:</td><td nowrap><b>%3.2f%%</b></td></tr>\n' % PercAllocated 
        src += html_comment('  percentage allocated: %3.2f%%' % PercAllocated) 
        src += '<tr><td nowrap>space used by customers:</td><td nowrap><b>%s</b></td></tr>\n' % StringUsedDonated   
        src += html_comment('  space used by customers: %s' % StringUsedDonated) 
        src += '<tr><td nowrap>percentage used:</td><td nowrap><b>%3.2f%%</b></td></tr>\n' % PercDonated 
        src += html_comment('  percentage used: %3.2f%%' % PercDonated) 
        src += '</table>\n'
        src += '</td>\n'
        src += '</tr></table>\n'
        return html(request, body=src, title='storage',)

    def getChild(self, path, request):
        if path == 'needed':
            return StorageNeededImage() 
        elif path == 'donated':
            return StorageDonatedImage()
        return self
        

class StorageNeededImage(resource.Resource):
    pagename = _PAGE_STORAGE_NEEDED
    isLeaf = True

    def toInt(self, f):
        return int(round(f))
    
    def render_GET(self, request):
        request.responseHeaders.setRawHeaders("content-type", ['image/png'])
        try:
            import Image
            import ImageDraw
            import ImageFont 
        except:
            dhnio.DprintException()
            # 1x1 png picture 
            src = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAABp0RVh0\nU29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAADElEQVQYV2P4//8/AAX+Av6nNYGEAAAA\nAElFTkSuQmCC\n'
            bin = misc.AsciiToBinary(src)
            request.write(bin)
            request.finish()
            return NOT_DONE_YET
        width = misc.ToInt(arg(request, 'width'), 256)
        height = misc.ToInt(arg(request, 'height'), 256)
        img = Image.new("RGB", (width, height), "#fff")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(settings.FontImageFile(), 12)
        except:
            font = None
        f = cStringIO.StringIO()
        bytesNeeded = diskspace.GetBytesFromString(settings.getCentralMegabytesNeeded(), None)
        if bytesNeeded is None:
            img.save(f, "PNG")
            f.seek(0)
            request.write(f.read())
            request.finish()
            return NOT_DONE_YET
        bytesUsed = backup_db.GetTotalBackupsSize()
        w = backups.suppliers_set().supplierCount
        if w == 0:
            img.save(f, "PNG")
            f.seek(0)
            request.write(f.read())
            request.finish()
            return NOT_DONE_YET
        x0 = (width - 2) / 2.0
        y0 = (height - 2) / 2.0
        R = float(min(width, height)) / 2.0 - 1
        dR = ( R / float(bytesNeeded) ) * float(bytesUsed) 
        dA = 360.0 / float(w)
        for y in range(w): # needed
            start = float(y) * dA
            end = start + dA
            draw.pieslice((self.toInt(x0 - R), self.toInt(y0 - R),
                           self.toInt(x0 + R), self.toInt(y0 + R)), 
                           self.toInt(start), self.toInt(end), fill='#82f282', outline='#777777')
        for y in range(w): # used
            start = float(y) * dA
            end = start + dA
            draw.pieslice((self.toInt(x0 - dR), self.toInt(y0 - dR), 
                           self.toInt(x0 + dR), self.toInt(y0 + dR)),
                           self.toInt(start), self.toInt(end), fill='#22b222', outline='#777777')
        if width >= 256 and height >= 256:
            for supplierNum in range(w):
                a = float(supplierNum) * dA + dA / 2.0 
                x1 = math.cos(a * math.pi / 180.0) * R * 0.7 + x0
                y1 = math.sin(a * math.pi / 180.0) * R * 0.7 + y0
                s = nameurl.GetName(contacts.getSupplierID(supplierNum))
                sw, sh = draw.textsize(s, font=font)
                draw.text((self.toInt(x1-sw/2.0), self.toInt(y1-sh/2.0)), s, fill="#000000", font=font)
        img.save(f, "PNG")
        f.seek(0)
        request.write(f.read())
        request.finish()
        return NOT_DONE_YET
    
    
class StorageDonatedImage(resource.Resource):
    pagename = _PAGE_STORAGE_NEEDED
    isLeaf = True

    def toInt(self, f):
        return int(round(f))
    
    def render_GET(self, request):
        request.responseHeaders.setRawHeaders("content-type", ['image/png'])
        try:
            import Image
            import ImageDraw
            import ImageFont 
        except:
            dhnio.DprintException()
            # 1x1 png picture 
            src = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAABp0RVh0\nU29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAADElEQVQYV2P4//8/AAX+Av6nNYGEAAAA\nAElFTkSuQmCC\n'
            bin = misc.AsciiToBinary(src)
            request.write(bin)
            request.finish()
            return NOT_DONE_YET
        width = misc.ToInt(arg(request, 'width'), 256)
        height = misc.ToInt(arg(request, 'height'), 256)
        img = Image.new("RGB", (width, height), "#fff")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(settings.FontImageFile(), 12)
        except:
            font = None
        f = cStringIO.StringIO()
        dataDir = settings.getCustomersFilesDir()
        dataDriveFreeSpace, dataDriveTotalSpace = diskusage.GetDriveSpace(dataDir)
        if dataDriveFreeSpace is None:
            dataDriveFreeSpace = 0
        customers_ids = contacts.getCustomerIDs()
        customers_count = contacts.numCustomers()
        spaceDict = dhnio._read_dict(settings.CustomersSpaceFile(), {})
        usedSpaceDict = {}
        totalCustomersBytes = 0
        bytesDonated = diskspace.GetBytesFromString(settings.getCentralMegabytesDonated(), 0)
        try:
            freeDonatedBytes = int(float(spaceDict['free'])*1024.0*1024.0)
        except:
            freeDonatedBytes = bytesDonated
            spaceDict['free'] = freeDonatedBytes/(1024.0*1024.0)
        for idurl in customers_ids:
            try:
                totalCustomersBytes += int(float(spaceDict.get(idurl, 0.0))*1024.0*1024.0)
            except:
                dhnio.DprintException()
            customerDir = os.path.join(dataDir, nameurl.UrlFilename(idurl))
            if os.path.isdir(customerDir):
                sz = dhnio.getDirectorySize(customerDir)
            else:
                sz = 0
            usedSpaceDict[idurl] = sz
        x0 = (width - 2) / 2.0
        y0 = (height - 2) / 2.0
        R = float(min(width, height)) / 2.0 - 1
        A = 0.0
        # idurls = spaceDict.keys()
        # idurls.append('free')
        try:
            if customers_count == 0:
                colorGiven = '#ffffff'
                draw.ellipse((self.toInt(x0 - R), self.toInt(y0 - R),
                              self.toInt(x0 + R), self.toInt(y0 + R)), 
                              fill=colorGiven, outline='#777777')
            else:
                for idurl in customers_ids + ['free',]:
                    usedBytes = usedSpaceDict.get(idurl, 0)
                    givenBytes = int(float(spaceDict[idurl])*1024*1024)
                    dA = 360.0 * givenBytes / ( totalCustomersBytes + freeDonatedBytes )
                    if dA < 1.0:
                        A += dA
                        continue
                    try:
                        dR = R * float(usedBytes) / float(givenBytes)
                    except:
                        dR = 0 
                    start = A
                    end = start + dA
                    colorGiven = '#ffffff' if idurl == 'free' else '#e2e242'
                    colorUsed = '#a2a202'
                    draw.pieslice((self.toInt(x0 - R), self.toInt(y0 - R),
                                   self.toInt(x0 + R), self.toInt(y0 + R)), 
                                   self.toInt(start), self.toInt(end), fill=colorGiven, outline='#777777')
                    draw.pieslice((self.toInt(x0 - dR), self.toInt(y0 - dR), 
                                   self.toInt(x0 + dR), self.toInt(y0 + dR)),
                                   self.toInt(start), self.toInt(end), fill=colorUsed, outline='#777777')
                    A += dA
            A = 0.0
            if width >= 256 and height >= 256:
                if customers_count == 0:
                    s = 'free ' + diskspace.MakeStringFromBytes(freeDonatedBytes)
                    sw, sh = draw.textsize(s, font=font)
                    draw.text((self.toInt(x0-sw/2.0), self.toInt(y0-sh/2.0)), s, fill="#000000", font=font)
                else:
                    for idurl in customers_ids:
                        usedBytes = usedSpaceDict.get(idurl, 0)
                        givenBytes = int(float(spaceDict[idurl])*1024*1024)
                        dA = 360.0 * givenBytes / bytesDonated
                        if dA < 1.0:
                            A += dA
                            continue
                        a = A + dA / 2.0 
                        x1 = math.cos(a * math.pi / 180.0) * R * 0.7 + x0
                        y1 = math.sin(a * math.pi / 180.0) * R * 0.7 + y0
                        if idurl == 'free':
                            s = 'free ' + diskspace.MakeStringFromBytes(givenBytes)
                            sw, sh = draw.textsize(s, font=font)
                            draw.text((self.toInt(x1-sw/2.0), self.toInt(y1-sh/2.0)), s, fill="#000000", font=font)
                        else:
                            s1 = nameurl.GetName(idurl) 
                            s2 = '%s/%s' % (diskspace.MakeStringFromBytes(usedBytes),
                                            diskspace.MakeStringFromBytes(givenBytes))
                            sw1, sh1 = draw.textsize(s1, font=font)
                            sw2, sh2 = draw.textsize(s2, font=font)
                            draw.text((self.toInt(x1-sw1/2.0), self.toInt(y1-sh1)), s1, fill="#000000", font=font)
                            draw.text((self.toInt(x1-sw2/2.0), self.toInt(y1)), s2, fill="#000000", font=font)
                        A += dA
        except:
            dhnio.DprintException()
            img.save(f, "PNG")
            f.seek(0)
            request.write(f.read())
            request.finish()
            return NOT_DONE_YET
        img.save(f, "PNG")
        f.seek(0)
        request.write(f.read())
        request.finish()
        return NOT_DONE_YET

    
class ConfigPage(Page):
    pagename = _PAGE_CONFIG
    def renderPage(self, request):
        global _SettingsItems
        menuLabels = _SettingsItems.keys()
        menuLabels.sort()
        w, h = misc.calculate_best_dimension(len(menuLabels))
        imgW = 128
        imgH = 128
        if w >= 4:
            imgW = 4 * imgW / w
            imgH = 4 * imgH / w
        padding = 64/w - 8
        src = '<h1>settings</h1>\n'
        src += '<table width="90%%" cellpadding=%d cellspacing=2>\n' % padding
        for y in range(h):
            src += '<tr valign=top>\n'
            for x in range(w):
                n = y * w + x
                src += '<td align=center valign=top>\n'
                if n >= len(menuLabels):
                    src += '&nbsp;\n'
                    continue
                label = menuLabels[n]
                link_url, icon_url = _SettingsItems[label]
                if link_url.find('?') < 0:
                    link_url += '?back='+request.path
                label = label.split('|')[1]
                src += '<a href="%s">' % link_url
                src += '<img src="%s" width=%d height=%d>' % (
                    iconurl(request, icon_url),
                    imgW, imgH,)
                src += '<br>[%s]' % label
                src += '</a>\n'
                src += '</td>\n'
                # src += html_comment('  [%s] %s' % (label, link_url))
            src += '</tr>\n'
        src += '</table>\n'
        return html(request, body=str(src), title='settings', back='', )


class BackupSettingsPage(Page):
    pagename = _PAGE_BACKUP_SETTINGS
    def renderPage(self, request):
        dhnio.Dprint(14, 'webcontrol.BackupSettingsPage.renderPage')
        donatedStr = diskspace.MakeStringFromString(settings.getCentralMegabytesDonated())
        neededStr = diskspace.MakeStringFromString(settings.getCentralMegabytesNeeded())

        src = '<h1>backup settings</h1>\n'
        src += '<br><h3>needed space: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'central-settings.needed-megabytes',
            request.path,
            neededStr)
#        src += '<p>This will cost %s$ per day.</p>\n' % 'XX.XX'

        src += '<br><h3>donated space: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'central-settings.shared-megabytes',
            request.path,
            donatedStr)
#        src += '<p>This will earn up to %s$ per day, depending on space used.</p>\n' % 'XX.XX'

        numSuppliers = settings.getCentralNumSuppliers()
        src += '<br><h3>number of suppliers: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'central-settings.desired-suppliers',
            request.path, str(numSuppliers))

        blockSize = settings.getBackupBlockSize()
        src += '<br><h3>maximum block size: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'backup.backup-block-size',
            request.path, str(blockSize))

        backupCount = settings.getGeneralBackupsToKeep()
        if backupCount == '0':
            backupCount = 'unlimited'
        src += '<br><h3>backup copies: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'general.general-backups',
            request.path, backupCount)
        
        keepLocalFiles = settings.getGeneralLocalBackups()
        src += '<br><h3>local backups: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'general.general-local-backups-enable', request.path,
            'yes' if keepLocalFiles else 'no')
        if not keepLocalFiles:
            src += '<br><h3>remove the local data, but wait 24 hours,<br>to check suppliers: <a href="%s?back=%s">%s</a></h3>\n' % (
                '/'+_PAGE_SETTINGS+'/'+'general.general-wait-suppliers-enable', request.path,
                'yes' if settings.getGeneralWaitSuppliers() else 'no')

        src += '<br><h3>directory for donated space:</h3>\n'
        src += '<a href="%s?back=%s">%s</a></p>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'folder.folder-customers',
            request.path, settings.getCustomersFilesDir())

        src += '<br><br><h3>directory for local backups:</h3>\n'
        src += '<a href="%s?back=%s">%s</a></p>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'folder.folder-backups',
            request.path, settings.getLocalBackupsDir())
        
        src += '<br><br><h3>directory for restored files:</h3>\n'
        src += '<a href="%s?back=%s">%s</a></p>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'folder.folder-restore',
            request.path, settings.getRestoreDir())

        src += '<br><br>\n'

        back = arg(request, 'back', '/'+_PAGE_BACKUP_SETTINGS)
        return html(request, body=src, title='backup settings', back=back)


class SecurityPage(Page):
    pagename = _PAGE_SECURITY
    def renderPage(self, request):
        message = ''
        comment = ''
        action = arg(request, 'action')
        back = arg(request, 'back', '/'+_PAGE_CONFIG)

        if action == 'copy':
            TextToSave = misc.getLocalID() + "\n" + dhncrypto.MyPrivateKey()
            misc.setClipboardText(TextToSave)
            message = '<font color="green">Now you can "paste" with Ctr+V your Private Key where you want.</font>'
            comment = 'now you can "paste" with Ctr+V your private key where you want.'
            del TextToSave

        elif action == 'view':
            TextToSave = misc.getLocalID() + "\n" + dhncrypto.MyPrivateKey()
            TextToSave = TextToSave.replace('\n', '<br>\n').replace(' ', '&nbsp;')
            src = '<h1>private key</h1>\n'
            src += '<table align=center><tr><td align=center>\n'
            src += '<div align=left><code>\n'
            src += TextToSave
            src += '</code></div>\n'
            src += '</td></tr></table>\n'
            src += html_comment('\n'+TextToSave+'\n')
            del TextToSave
            return html(request, body=src, back=back, title='private key')

        elif action == 'write':
            TextToSave = misc.getLocalID() + "\n" + dhncrypto.MyPrivateKey()
            savefile = unicode(misc.unpack_url_param(arg(request, 'savefile'), ''))
            dhnio.AtomicWriteFile(savefile, TextToSave)
            message = '<font color="green">Your Private Key were copied to the file %s</font>' % savefile
            comment = 'your private key were copied to the file %s' % savefile
            del TextToSave
            
        elif action == 'move':
            TextToSave = dhncrypto.MyPrivateKey()
            savefile = unicode(misc.unpack_url_param(arg(request, 'savefile'), ''))
            if dhnio.AtomicWriteFile(savefile, TextToSave):
                keyfilename = settings.KeyFileName()
                if dhnio.AtomicWriteFile(keyfilename+'_location', savefile):
                    try:
                        os.remove(keyfilename)
                    except:
                        dhnio.DprintException()
                        message = '<font color="red">Failed to remove your Private Key from %s</font>' % keyfilename
                        comment = 'failed to remove your Private Key from %s' % keyfilename
                    message = '<font color="green">Your Private Key were moved to %s,<br>be sure to have the file in same place during next program start</font>' % savefile
                    comment = 'your private key were moved to %s,\nbe sure to have the file in same place during next program start' % savefile
                else:
                    message = '<font color="red">Failed to write to the file %s</font>' % (keyfilename+'_location')
                    comment = 'failed to write to the file %s' % (keyfilename+'_location')
            else:
                message = '<font color="red">Failed to write your Private Key to the file %s</font>' % savefile
                comment = 'failed to write your Private Key to the file %s' % savefile
            del TextToSave

        src = '<h1>public and private key</h1>\n'
        src += '<table width="80%"><tr><td>\n'
        
        src += '<p><b>Saving the key to your backups</b> someplace other than this machine <b>is vitally important!</b></p>\n'
        src += '<p>If this machine is lost due to a broken disk, theft, fire, flood, earthquake, tornado, hurricane, etc. you must have a copy of your key someplace else to recover your data.</p>\n'
        src += '<p>We recommend at least 3 copies in different locations. For example one in your safe deposit box at the bank, one in your fireproof safe, and one at work.'
        src += 'You only need to do this at the beginning, then the keys can stay put till you need one.<\p>\n'
        src += '<p><b>Without a copy of your key nobody can recover your data!</b><br>Not even DataHaven.NET LTD ...</p>\n'
        src += '<p>You can do the following with your Private Key:</p>\n'

        src += '<table><tr>\n'
        
        src += '<td>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="submit" name="submit" value=" view the whole key " />\n'
        src += '<input type="hidden" name="action" value="view" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % request.path
        src += '</form>\n'
        src += '</td>\n'
        
        src += '<td>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="submit" name="submit" value=" copy to clipboard " />\n'
        src += '<input type="hidden" name="action" value="copy" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '</form>\n'
        src += '</td>\n'

        src += '<td>\n'
        src += '<form action="%s?" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="write" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '<input type="hidden" name="parent" value="%s" />\n' % _PAGE_SECURITY
        src += '<input type="hidden" name="label" value="Select filename to save" />\n'
        src += '<input type="hidden" name="showincluded" value="true" />\n'
        src += '<input type="submit" name="savefile" value=" write to file " path="%s" />\n' % (
            misc.pack_url_param(os.path.join(os.path.expanduser('~'), '%s-DataHaven.NET.key' % misc.getIDName())))
        src += '</form>\n'
        src += '</td>\n'

        src += '</tr></table>\n'

        src += '<p>You can create <b>a completely inaccessible for anybody but you</b>, keeping your data, if after creating a distributed remote backup - delete the original data from your computer. '
        src += 'Private key can be stored on a USB flash drive and <b>local copy of the Key can be removed from your HDD</b>.</p>\n'
        src += '<p>Than, DataHaven.NET will only run with this USB stick and read the Private Key at startup, it will only be stored in RAM. '
        src += 'After starting the program, disconnect the USB stick, and hide it in a safe place.</p>\n'
        src += '<p>If control of the computer was lost - just <b>be sure that the power is turned off</b>, it is easy to provide. '
        src += 'In this case the memory is reset and working key will be erased, so that copy of your Key will remain only on USB flash drive, hidden by you.</p>\n'
        src += '<p>This way, <b>only you will have access to the data</b> after a loss of the computer, where DataHaven.NET were launched.</p>\n'
        
        src += '<table><tr>\n'
        src += '<td>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="move" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '<input type="hidden" name="parent" value="%s" />\n' % _PAGE_SECURITY
        src += '<input type="hidden" name="label" value="Select filename to save" />\n'
        src += '<input type="hidden" name="showincluded" value="true" />\n'
        removable_drives = dhnio.listRemovableDrives()
        if len(removable_drives) > 0:
            start_path = os.path.join(removable_drives[0], misc.getIDName()+'-DataHaven.NET.key')
        else:
            start_path = ''
        src += '<input type="submit" name="savefile" value=" move my key to removable media " path="%s" />\n' % start_path 
        src += '</form>\n'
        src += '</td>\n'
        src += '</tr></table>\n'

        src += message
        
        src += '<br><p>The public part of your key is stored in the <b>Identity File</b>.' 
        src += 'This is a publicly accessible file wich keeps information needed to connect to you.\n'
        src += 'Identity file has a <b>unique address on the Internet</b>,' 
        src += 'so that every user may download it and find out your contact information.</p>\n'
        src += '<p>Your Identity is <b>digitally signed</b> and that would change it is '
        src += 'necessary to know the Private Key.</p>\n'
        src += '<br><br>\n'
        src += '<a href="%s" target="_blank">open my public identity file</a>\n' % misc.getLocalID()
        src += '<br>\n'
        
        src += '</td></tr></table>\n'
        
        src += html_comment(comment)

        return html(request, body=src, title='security', back=back)


class NetworkSettingsPage(Page):
    pagename = _PAGE_NETWORK_SETTINGS
    def renderPage(self, request):
        src = '<h1>network settings</h1>\n'
        src += '<br><h3>enable transport_tcp: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'transport.transport-tcp.transport-tcp-enable', request.path,
            'yes' if settings.enableTCP() else 'no')
        if settings.enableTCP():
            src += '<br><h3>transport_tcp port: <a href="%s?back=%s">%s</a></h3>\n' % (
                '/'+_PAGE_SETTINGS+'/'+'transport.transport-tcp.transport-tcp-port', request.path,
                settings.getTCPPort())
            src += '<br><h3>enable UPnP: <a href="%s?back=%s">%s</a></h3>\n' % (
                '/'+_PAGE_SETTINGS+'/'+'other.upnp-enabled', request.path,
                'yes' if settings.enableUPNP() else 'no')
        src += '<br><h3>enable transport_cspace: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'transport.transport-cspace.transport-cspace-enable', request.path,
            'yes' if settings.enableCSpace() else 'no')
        src += '<br><h3>enable transport_udp: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'transport.transport-udp.transport-udp-enable', request.path,
            'yes' if settings.enableUDP() else 'no')
        if settings.enableUDP():
            src += '<br><h3>transport_udp port: <a href="%s?back=%s">%s</a></h3>\n' % (
                '/'+_PAGE_SETTINGS+'/'+'transport.transport-udp.transport-udp-port', request.path,
                settings.getUDPPort())
        
#        src += '<br><h3>outgoing bandwidth limit: <a href="%s?back=%s">%s</a></h3>\n' % (
#            '/'+_PAGE_SETTINGS+'/'+'network.network-send-limit', request.path,
#            str(settings.getBandOutLimit()))
#        src += '<br><h3>incoming bandwidth limit: <a href="%s?back=%s">%s</a></h3>\n' % (
#            '/'+_PAGE_SETTINGS+'/'+'network.network-receive-limit', request.path,
#            str(settings.getBandInLimit()))
        return html(request, body=src,  back=arg(request, 'back', '/'+_PAGE_CONFIG), title='network settings')


#class PathsPage(Page):
#    pagename = _PAGE_PATHS
#    
#    def renderPage(self, request):
#        src = '<h1>program paths</h1>\n'
#        src += '<table width="90%"><tr><td align=center>\n'
#        
#        src += '<br><h3>directory for donated space:</h3>\n'
#        src += '<a href="%s?back=%s">%s</a></p>\n' % (
#            '/'+_PAGE_SETTINGS+'/'+'folder.folder-customers',
#            request.path, settings.getCustomersFilesDir())
#
#        src += '<br><br><h3>directory for local backups:</h3>\n'
#        src += '<a href="%s?back=%s">%s</a></p>\n' % (
#            '/'+_PAGE_SETTINGS+'/'+'folder.folder-backups',
#            request.path, settings.getLocalBackupsDir())
#        
#        src += '<br><br><h3>directory for restored files:</h3>\n'
#        src += '<a href="%s?back=%s">%s</a></p>\n' % (
#            '/'+_PAGE_SETTINGS+'/'+'folder.folder-restore',
#            request.path, settings.getRestoreDir())
#        
#        src += '</td></tr></table>\n'
#        back = arg(request, 'back', '/'+_PAGE_CONFIG)
#        return html(request, body=src, title='security', back=back)        


class UpdatePage(Page):
    pagename = _PAGE_UPDATE
    debug = False
    def _check_callback(self, x, request):
        global local_version
        global revision_number
        local_version = dhnio.ReadBinaryFile(settings.VersionFile())
        src = '<h1>update software</h1>\n'
        src += '<p>your software revision number is <b>%s</b></p>\n' % revision_number
        src += self._body_windows_frozen(request)
        back = '/'+_PAGE_CONFIG
        request.write(html_from_args(request, body=str(src), title='update software', back=back))
        request.finish()

    def _body_windows_frozen(self, request, repo_msg=None):
        global local_version
        global global_version
        try:
            repo, update_url = dhnio.ReadTextFile(settings.RepoFile()).split('\n')
        except:
            repo = settings.DefaultRepo()
            update_url = settings.UpdateLocationURL()
        if repo == '':
            repo = 'test' 
        button = None
        if global_version == '':
            button = (' check latest version ', True, 'check')
        else:
            if local_version == '':
                button = (' update DataHaven.NET now ', True, 'update')
            else:
                if local_version != global_version:
                    button = (' update DataHaven.NET now ', True, 'update')
                else:
                    button = (' DataHaven.NET updated! ', False, 'check')
        src = ''
        src += '<h3>Update repository</h3>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table align=center>\n'
        src += '<tr><td align=left>\n'
        src += '<input id="test" type="radio" name="repo" value="testing" %s />\n' % ('checked' if repo=='test' else '')
        src += '</td></tr>\n'
        src += '<tr><td align=left>\n'
        src += '<input id="devel" type="radio" name="repo" value="development" %s />\n' % ('checked' if repo=='devel' else '') 
        src += '</td></tr>\n'
        src += '<tr><td align=left>\n'
        src += '<input id="stable" type="radio" name="repo" value="stable" %s />\n' % ('checked' if repo=='stable' else '')
        src += '</td></tr>\n'
        src += '<tr><td align=center>\n'
        if repo_msg is not None:
            src += '<p><font color=%s>%s</font></p>\n' % (repo_msg[1], repo_msg[0])
        src += '<input type="hidden" name="action" value="repo" />\n'
        src += '<br><input type="submit" name="submit" value=" set "/>\n'
        src += '</td></tr>\n'
        src += '</table>\n'
        src += '</form>\n'
        src += '<h3>Update schedule</h3>\n'
        shed = schedule.Schedule(from_dict=dhnupdate.read_shedule_dict())
        next = shed.next_time()
        src += '<p>'
        if next is None:
            src += 'icorrect schedule<br>\n'
        elif next < 0:
            src += 'not scheduled<br>\n'
        else:
            src += shed.html_description() + ',<br>\n'
            src += shed.html_next_start() + ',<br>\n'
        src += '<a href="%s?back=%s">change schedule</a>\n' % ('/'+_PAGE_UPDATE_SHEDULE, request.path)
        src += '</p>\n' 
        if button is not None:
            src += '<br><br><form action="%s" method="post">\n' % request.path
            src += '<table align=center>\n'
            src += '<tr><td>\n'
            src += '<input type="hidden" name="action" value="%s" />\n' % button[2]
            src += '<input type="submit" name="submit" value="%s" %s />\n' % (button[0], ('disabled' if not button[1] else '')) 
            src += '</td></tr>\n'
            src += '</table>\n'
            src += '</form>\n'
        src += '<br>\n'
        return src 
        
    def _body_windows_soures(self, request):
        src = '<p>Running from python sources.</p>\n'
        return src

    def _body_linux_deb(self, request):
        src = ''
        src += '<table align=center><tr><td><div align=left>\n'
        src += '<p>You can manually update DataHaven.NET<br>\n'
        src += 'from command line using apt-get:</p>\n'
        src += '<code><br>\n'
        src += 'sudo apt-get update<br>\n'
        src += 'sudo apt-get install datahaven\n'
        src += '</code></div></td></tr></table>\n'
        return src
           
    def _body_linux_sources(self, request):
        src = '<p>Running from python sources.</p>\n'
        return src
    
    def renderPage(self, request):
        global local_version
        global global_version
        global revision_number
        action = arg(request, 'action')
        repo_msg = None
        update_msg = None

        if action == 'update':
            if self.debug or (dhnio.Windows() and dhnio.isFrozen()):
                if not dhnupdate.is_running():
                    dhnupdate.run()
                    update_msg = 'preparing update process ...'

        elif action == 'check':
            if self.debug or (dhnio.Windows() and dhnio.isFrozen()):
                d = dhnupdate.check()
                d.addCallback(self._check_callback, request)
                d.addErrback(self._check_callback, request)
                request.notifyFinish().addErrback(self._check_callback, request)
                return NOT_DONE_YET
            
        elif action == 'repo':
            repo = arg(request, 'repo')
            repo = {'development': 'devel', 'testing': 'test', 'stable': 'stable'}.get(repo, 'test')
            repo_file_src = '%s\n%s' % (repo, settings.UpdateLocationURL(repo))
            dhnio.WriteFile(settings.RepoFile(), repo_file_src)
            global_version = ''
            repo_msg = ('repository changed', 'green')
            
        src = '<h1>update software</h1>\n'
        src += '<p>Current revision number is <b>%s</b></p>\n' % revision_number
        if update_msg is not None:
            src += '<h3><font color=green>%s</font></h3>\n' % update_msg
            back = '/'+_PAGE_CONFIG
            return html(request, body=src, title='update software', back=back)
        
        if dhnio.Windows():
            if dhnio.isFrozen():
                src += self._body_windows_frozen(request, repo_msg)
            else:
                if self.debug:
                    src += self._body_windows_frozen(request, repo_msg)
                else:
                    src += self._body_windows_soures(request)
        else:
            if dhnio.getExecutableDir().count('/usr/share/datahaven'):
                src += self._body_linux_deb(request)
            else:
                src += self._body_linux_sources(request)
                
        back = '/'+_PAGE_CONFIG
        return html(request, body=src, title='update software', back=back)


class DevelopmentPage(Page):
    pagename = _PAGE_DEVELOPMENT
    def renderPage(self, request):
        src = '<h1>for developers</h1>\n'
        src += '<br><h3>debug level: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'logs.debug-level', request.path,
            settings.getDebugLevelStr())
        src += '<br><h3>use http server for logs: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'logs.stream-enable', request.path,
            'yes' if settings.enableWebStream() else 'no')
        src += '<br><h3>http server port number: <a href="%s?back=%s">%s</a></h3>\n' % (
            '/'+_PAGE_SETTINGS+'/'+'logs.stream-port', request.path,
            str(settings.getWebStreamPort()))
        if settings.enableWebStream():
            src += '<p>You can browse logs by clicking on icon "Logs" in top right of the main window, '
            src += 'or <a href="http://127.0.0.1:%d" target="_blank">here</a>.<br>\n' % settings.getWebStreamPort()
            src += 'It is needed to restart DataHaven.NET to be able to see the logs.</p>\n'
        # src += '<br><br><h3>To see current packets transfers go to the <a href="%s">Packet Transfers page</a>.</h3>\n' % ('/'+_PAGE_MONITOR_TRANSPORTS)
        src += '<p>You can watch current memory usage on the <a href="%s">Memory page</a>.</p>\n' % ('/'+_PAGE_MEMORY)
        src += '<h3>If you want to give a feedback or you found a bug or other cause,<br>you can <a href="%s?back=%s">send a developer report</a> now.</h3>' % (
            '/'+_PAGE_DEV_REPORT, request.path)
        src += '<br><br>\n'
        return html(request, body=src, back=arg(request, 'back', '/'+_PAGE_CONFIG), title='developers')


class MoneyPage(Page):
    pagename = _PAGE_MONEY
    
    def renderPage(self, request):
        bal, balnt, rcptnum = money.LoadBalance()
        src = '<h1>money</h1>\n'
        src += '<table align=center><tr><td align=left>\n'
        src += 'Total balance: <b>%6.6f$</b>\n' % (bal + balnt) # (<b>%d</b> days remaining)
        src += html_comment('total balance: %6.6f$' % (bal + balnt))
        src += '<br><br>Transferable balance: <b>%6.6f$</b>\n' % bal
        src += html_comment('transferable balance: %6.6f$' % bal)
        src += '<br><br>Not transferable balance: <b>%6.6f$</b>\n' % balnt
        src += html_comment('not transferable balance: %6.6f$' % balnt)
        src += '</td></tr></table>\n'
        src += '<br><br><br>\n'
        src += '<a href="%s">I want to add money to my account</a>\n' % _PAGE_MONEY_ADD
        src += '<br><br><a href="%s">Let\'s send some funds to one of my friends</a>\n' % _PAGE_TRANSFER
        src += '<br><br><a href="%s">Show me the full receipts history</a>\n' % _PAGE_RECEIPTS
        src += '<br><br>\n'
        return html(request, body=src, back=arg(request, 'back', '/'+_PAGE_MENU), title='money')


class MoneyAddPage(Page):
    pagename = _PAGE_MONEY_ADD
    def renderPage(self, request):
        action = arg(request, 'action')
        back = arg(request, 'back', '/'+_PAGE_MONEY)
        src = '<h1>add money</h1>\n'
        
        if action == 'pay':
            url = 'http://%s:%s?id=%s' % (
                settings.MoneyServerName(), str(settings.MoneyServerPort()),
                misc.encode64(misc.getLocalID()))
            webbrowser.open(url, new=1, autoraise=1)
            request.redirect('/'+_PAGE_MONEY)
            request.finish()
            return NOT_DONE_YET
            
        src += '<table width=55%><tr><td>\n'
        src += '<p align=justify>At the moment, that would increase your balance you can use credit card: Visa or MasterCard.</p>\n'
        src += '<p align=justify>The money will be transferred without commission.</p>\n'
        src += '<p align=justify>In the opened browser window, fill in your credit card info and payment will be accomplished immediately,\n'
        src += 'check receipts history to monitor money transfer.</p>\n'
        src += '</td></tr></table>\n'
        src += '<br><br><br>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="pay" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '<input type="submit" name="submit" value=" pay ON-LINE with your Credit Card " />\n'
        src += '</form>\n'
        return html(request, body=src, back=back, title='add money')
        

class TransferPage(Page):
    pagename = _PAGE_TRANSFER
    def _checkInput(self, amount, bal, recipient):
        if recipient.strip() == '':
            return 3
        try:
            float(amount)
        except:
            return 1
        if float(amount) > float(bal):
            return 2
        return 0

    def renderPage(self, request):
        bal, balnt, rcptnum = money.LoadBalance()
        idurls = contacts.getContactsAndCorrespondents()
        idurls.sort()
        recipient = arg(request, 'recipient')
        if recipient.strip() and not recipient.startswith('http://'):
            recipient = 'http://'+settings.IdentityServerName()+'/'+recipient+'.xml'
        amount = arg(request, 'amount', '0.0')
        action = arg(request, 'action')
        dhnio.Dprint(6, 'webcontrol.TransferPage.renderPage [%s] [%s] [%s]' % (action, amount, recipient))
        msg = ''
        typ = 'info'
        button = 'Send money'
        modify = True

        if action == '':
            action = 'send'

        elif action == 'send':
            res = self._checkInput(amount, bal, recipient)
            if res == 0:
                action = 'commit'
                button = 'Yes! Send the money!'
                modify = False
                msg = '<table width="60%"><tr><td align=center>'
                msg += 'Do you want to transfer <font color=blue><b>%6.6f$</b></font>' % float(amount)
                msg += ' of your total <font color=blue><b>%6.6f$</b></font> transferable funds ' % bal
                msg += ' to user <font color=blue><b>%s</b></font> ?<br>\n' % nameurl.GetName(recipient)
                msg += '<br>Your transferable balance will become <font color=blue><b>%6.6f$</b></font>.' % (float(bal) - float(amount))
                msg += '</td></tr></table>'
                typ = 'info'
            elif res == 1:
                msg = 'Wrong amount! Please enter a number!'
                typ = 'error'
            elif res == 2:
                msg = 'Sorry! But you do not have enough transferable funds.'
                typ = 'error'
            else:
                msg = 'Unknown error! Please try again.'
                typ = 'error'

        elif action == 'commit':
            res = self._checkInput(amount, bal, recipient)
            if res == 0:
                central_service.SendTransfer(recipient, amount)
                msg = 'Money was transferred successfully to the user <b>%s</b>.' % nameurl.GetName(recipient)
                typ = 'success'
                button = 'Return'
                modify = False
                action = 'return'
            elif res == 1:
                action = 'send'
                button = 'Send money'
                modify = True
                msg = 'Wrong amount! Please enter a number!'
                typ = 'error'
            elif res == 2:
                action = 'send'
                button = 'Send money'
                modify = True
                msg = 'Sorry! But you do not have enough transferable funds.'
                typ = 'error'
            else:
                action = 'send'
                button = 'Send money'
                modify = True
                msg = 'Unknown error! Please try again.'
                typ = 'error'

        elif action == 'return':
            request.redirect('/'+_PAGE_MONEY)
            request.finish()
            return NOT_DONE_YET
        
        else:
            action = 'send'
            button = 'Send money'
            modify = True
            msg = 'Unknown action! Please try again.'
            typ = 'error'

        src = '<h1>money</h1>\n'
        src += '<table align=center><tr><td align=left>\n'
        src += 'Total balance: <b>%6.6f$</b>\n' % (bal + balnt)
        src += '<br><br>Transferable balance: <b>%6.6f$</b>\n' % bal
        src += '<br><br>Not transferable balance: <b>%6.6f$</b>\n' % balnt
        src += '</td></tr></table>\n'
        src += '<br><br><br>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="%s" />\n' % action
        if modify:
            src += '<table><tr>\n'
            src += '<td align=right><input type="text" name="amount" value="%s" size=12 /></td>\n' % amount
            src += '<td align=left>$</td>\n'
            src += '</tr></table><br>\n'
            src += '<select name="recipient">\n'
            for idurl in idurls:
                name = nameurl.GetName(idurl)
                src += '<option value="%s"' % idurl
                if idurl == recipient:
                    src += ' selected '
                src += '>%s</option>\n' % name
            src += '</select><br><br>\n'
        else:
            src += '<input type="hidden" name="amount" value="%s" />\n' % amount
            src += '<input type="hidden" name="recipient" value="%s" />\n' % recipient
        src += html_message(msg, typ)
        src += '<br><br>\n'
        src += '<input type="submit" name="submit" value="%s" />\n' % button
        src += '</form><br><br>\n'
        src += html_comment(msg.lower().replace('<b>', '').replace('</b>', ''))
        return html(request, body=src, back='/'+_PAGE_MONEY, title='money transfer')


class ReceiptPage(Page):
    pagename = _PAGE_RECEIPT
    isLeaf = True
    def __init__(self, path):
        Page.__init__(self)
        self.path = path

    def renderPage(self, request):
        dhnio.Dprint(6, 'webcontrol.ReceiptPage.renderPage ' + self.path)
        receipt = money.ReadReceipt(self.path)
        src = '<h1>receipt %s</h1>\n' % self.path
        if receipt is None:
            src += html_message('Can not read receipt with number ' + self.path , 'error')
            return html(request, body=src, back='/'+_PAGE_RECEIPTS)
        src += '<table cellspacing=5 width=80% align=center>\n'
        src += '<tr><td align=right width=20%><b>ID:</b></td><td width=80% align=left>' + str(receipt[0]) + '</td></tr>\n'
        src += html_comment('  ID:     %s' % str(receipt[0]))
        src += '<tr><td align=right><b>Type:</b></td><td align=left>' + str(receipt[2]) + '</td></tr>\n'
        src += html_comment('  Type:   %s' % str(receipt[2]))
        src += '<tr><td align=right><b>From:</b></td><td align=left>' + str(receipt[3]) + '</td></tr>\n'
        src += html_comment('  From:   %s' % str(receipt[3]))
        src += '<tr><td align=right><b>To:</b></td><td align=left>' + str(receipt[4]) + '</td></tr>\n'
        src += html_comment('  To:     %s' % str(receipt[4]))
        src += '<tr><td align=right><b>Amount:</b></td><td align=left>' + misc.FloatToString(money.GetTrueAmount(receipt)) + '$</td></tr>\n'
        src += html_comment('  Amount: %s $' % misc.FloatToString(money.GetTrueAmount(receipt)))
        src += '<tr><td align=right><b>Date:</b></td><td align=left>' + str(receipt[1]) + '</td></tr>\n'
        src += html_comment('  Date:   %s' % str(receipt[1]))
        d = money.UnpackReport(receipt[-1])
        if str(receipt[2]) == 'space':
            src += '<tr><td colspan=2>\n'
            src += '<br><br><table width=100%><tr><td valign=top align=right>\n'
            src += '<table>\n'
            src += '<tr><td colspan=2 align=left><b>Suppliers:</b></td></tr>\n'
            src += '<tr><td>user</td><td>taken Mb</td></tr>\n'
            src += html_comment('    suppliers, taken Mb')
            for idurl, mb in d['suppliers'].items():
                if idurl == 'space' or idurl == 'costs':
                    continue
                src += '<tr><td>%s</td>' % nameurl.GetName(idurl)
                src += '<td nowrap>%s Mb</td>\n' % str(mb)
                src += '</tr>\n'
                src += html_comment('      %s  %s' % (nameurl.GetName(idurl).ljust(20), str(mb)))
            src += '<tr><td>&nbsp;</td></tr>\n'
            # src += '<tr><td nowrap>total taken space</td><td nowrap>%s Mb</td></tr>\n' % str(d['suppliers']['space'])
            # src += '<tr><td nowrap>suppliers costs</td><td nowrap>%s$</td></tr>\n' % str(d['suppliers']['costs'])
            src += '</table>\n'
            src += '</td><td valign=top align=left>\n'
            src += '<table>'
            src += '<tr><td colspan=2 align=left><b>Customers:</b></td></tr>\n'
            src += html_comment('    customers, given Mb')
            src += '<tr><td>user</td><td>given Mb</td></tr>\n'
            for idurl, mb in d['customers'].items():
                if idurl == 'space' or idurl == 'income':
                    continue
                src += '<tr><td>%s</td>' % nameurl.GetName(idurl)
                src += '<td nowrap>%s Mb</td>\n' % str(mb)
                src += '</tr>\n'
                src += html_comment('      %s  %s' % (nameurl.GetName(idurl).ljust(20), str(mb)))
            src += '<tr><td>&nbsp;</td></tr>\n'
            # src += '<tr><td nowrap>total given space</td><td nowrap>%s Mb</td></tr>\n' %  str(d['customers']['space'])
            # src += '<tr><td>customers income</td><td nowrap>%s$</td></tr>\n' % str(d['customers']['income'])
            src += '</table>\n'
            src += '</td></tr>\n'
            src += '<tr><td align=right>\n'
            src += '<table><tr><td nowrap>total taken space</td><td nowrap>%s Mb</td></tr>\n' % str(d['suppliers']['space'])
            src += html_comment('    total taken space: %s Mb' % str(d['suppliers']['space']))
            src += '<tr><td nowrap>suppliers costs</td><td nowrap>%s $</td></tr></table>\n' % str(d['suppliers']['costs'])
            src += html_comment('    suppliers costs:   %s $' % str(d['suppliers']['costs']))
            src += '</td><td>\n'
            src += '<table><tr><td nowrap>total given space</td><td nowrap>%s Mb</td></tr>\n' %  str(d['customers']['space'])
            src += html_comment('    total given space: %s Mb' % str(d['customers']['space']))
            src += '<tr><td>customers income</td><td nowrap>%s $</td></tr></table>\n' % str(d['customers']['income'])
            src += html_comment('    customers income:  %s $' % str(d['customers']['income']))
            src += '</td></tr>'
            src += '</table>\n'
            src += '</td></tr>\n'
            src += '<tr><td colspan=2 align=center>\n'
            src += '<br><b>Total profits:</b> %s $\n' % str(d['total']).strip()
            src += html_comment('    total profits:     %s $' % str(d['total']).strip())
            src += '</td></tr>\n'
            src += '<tr><td colspan=2>\n'
            src += d['text']
            src += '</td></tr>\n'
            src += html_comment('    ' + d['text'])
        else:
            src += '<tr><td align=right><b>Details:</b></td><td align=left>' + str(d['text']).replace('\n', '') + '</td></tr>\n'
            src += html_comment('  Details: %s' % str(d['text']).replace('\n', ''))
        src += '</table>\n'
        return html(request, body=src, back='/'+_PAGE_RECEIPTS)

class ReceiptsPage(Page):
    pagename = _PAGE_RECEIPTS
    def renderPage(self, request):
        receipts_list = money.ReadAllReceipts()
        page = arg(request, 'page', time.strftime('%Y%m'))
        pageYear = nextYear = prevYear = misc.ToInt(page[:4], int(time.strftime('%Y')))
        pageMonth =  nextMonth = prevMonth = misc.ToInt(page[4:], int(time.strftime('%m')))
        nextMonth = pageMonth + 1
        if nextMonth == 13:
            nextMonth = 1
            nextYear += 1
        prevMonth = pageMonth -1
        if prevMonth == 0:
            prevMonth = 12
            prevYear -= 1
        next = '%d%02d' % (nextYear, nextMonth)
        prev = '%d%02d' % (prevYear, prevMonth)
        nextLabel = '%d %s' % (nextYear, calendar.month_name[nextMonth])
        prevLabel = '%d %s' % (prevYear, calendar.month_name[prevMonth])
        src = '<h1>receipts</h1>\n'
        src += '<br><br>\n'
        src += '<a href="%s?page=%s">[%s]</a>\n' % (request.path, prev, prevLabel)
        src += '<a href="%s?page=%s">[%s]</a>\n' % (request.path, next, nextLabel)
        src += '<table cellpadding=5>\n'
        src += '<tr align=left>\n'
        src += '<th>ID</th>\n'
        src += '<th>Type</th>\n'
        src += '<th>Amount</th>\n'
        src += '<th>From</th>\n'
        src += '<th>To</th>\n'
        src += '<th>Date</th>\n'
        src += '</tr>\n'
        src += html_comment('  ID          Type      Amount        From            To              Date')
        for receipt in receipts_list:
            src += html_comment('  %s  %s  %s  %s  %s  %s' % (
                receipt[0].ljust(10), receipt[1].ljust(8), misc.FloatToString(receipt[2]).ljust(12), 
                receipt[3].ljust(14), receipt[4].ljust(14), receipt[5]))
            try:
                d = time.strptime(receipt[5], "%a, %d %b %Y %H:%M:%S")
                if d[0] != pageYear or d[1] != pageMonth:
                    continue
            except:
                dhnio.DprintException()
                continue
            src += '<tr><td>'
            src += '<a href="%s/%s">' % (request.path, receipt[0])
            src += '%s</a></td>\n' % receipt[0]
            src += '<td>%s</td>\n' % receipt[1]
            src += '<td>%s</td>\n' % misc.FloatToString(receipt[2])
            src += '<td>%s</td>\n' % receipt[3]
            src += '<td>%s</td>\n' % receipt[4]
            src += '<td>%s</td>\n' % receipt[5]
            src += '</tr>\n'
        src += '\n</table>\n'
        return html(request, body=src, back='/'+_PAGE_MONEY, title='receipts')

    def getChild(self, path, request):
        if path == '':
            return self
        return ReceiptPage(path)

class MessagePage(Page):
    pagename = _PAGE_MESSAGE
    isLeaf = True
    def __init__(self, path):
        Page.__init__(self)
        self.path = path

    def renderPage(self, request):
        msg = message.ReadMessage(self.path)
        src = ''
        if msg[0] == misc.getLocalID():
            src += '<h1>message to %s</h1>\n' % nameurl.GetName(msg[1])
        else:
            src += '<h1>message from %s</h1>\n' % nameurl.GetName(msg[0])
        src += '<table width=70%><tr><td align=center>'
        src += '<table>\n'
        src += '<tr><td align=right><b>From:</b></td><td>%s</td></tr>\n' % nameurl.GetName(msg[0])
        src += '<tr><td align=right><b>To:</b></td><td>%s</td></tr>\n' % nameurl.GetName(msg[1])
        src += '<tr><td align=right><b>Date:</b></td><td>%s</td></tr>\n' % msg[3]
        src += '<tr><td align=right><b>Subject:</b></td><td>%s</td></tr>\n' % msg[2]
        src += '</table>\n'
        src += '</td></tr>\n'
        src += '<tr><td align=left>\n'
        src += '<table border=1><tr><td>\n'
        src += msg[4].replace('\n', '<br>\n')
        src += '</td></tr></table>\n'
        src += '</td></tr></table>\n'
        src += '<br><br>\n'
        return html(request, body=src, back=_PAGE_MESSAGES)

class MessagesPage(Page):
    pagename = _PAGE_MESSAGES
    sortby = 0
    sortreverse = False
    
    def renderPage(self, request):
        action = arg(request, 'action')
        mid = arg(request, 'mid')
        if action == 'delete' and mid:
            message.DeleteMessage(mid)
        myname = misc.getIDName()
        mlist = message.ListAllMessages()
        _sortby = arg(request, 'sortby', '')
        if _sortby != '':
            _sortby = misc.ToInt(arg(request, 'sortby'), 0)
            if self.sortby == _sortby:
                self.sortreverse = not self.sortreverse
            self.sortby = _sortby
        _reverse = self.sortreverse
        if self.sortby == 0:
            _reverse = not _reverse
        mlist.sort(key=lambda item: item[self.sortby], reverse=_reverse)
        src = ''
        src += '<h1>messages</h1>\n'
        src += '<a href="%s?back=%s">Create a new message</a><br><br>\n' % (
            _PAGE_NEW_MESSAGE, request.path)
        src += '<a href="%s?back=%s">Edit my correspondents list</a><br><br><br>\n' % (
            _PAGE_CORRESPONDENTS, request.path)
        if len(mlist) == 0:
            src += '<p>you have no messages</p>\n'
        else:
            src += '<table width=80% cellpadding=5 cellspacing=0>\n'
            src += '<tr align=left>\n'
            src += '<th><a href="%s?sortby=1">From</a></th>\n' % request.path
            src += '<th><a href="%s?sortby=2">To</a></th>\n' % request.path
            src += '<th><a href="%s?sortby=3">Received/Created</a></th>\n' % request.path
            src += '<th><a href="%s?sortby=4">Subject</a></th>\n' % request.path
            src += '</tr>\n'
            for i in range(len(mlist)):
                msg = mlist[i]
                mid = msg[0]
                bgcolor = '#DDDDFF'
                if myname != msg[1]:
                    bgcolor = '#DDFFDD'
                src += '<tr bgcolor="%s">\n' % bgcolor
                src += '<a href="%s/%s">\n' % (request.path, mid)
                for m in msg[1:]:
                    src += '<td>'
                    src += str(m)
                    src += '</td>\n'
                src += '</a>\n'
                src += '<a href="%s?action=delete&mid=%s"><td>' % (request.path, mid)
                src += '<img src="%s" /></td></a>\n' % iconurl(request, 'icons/delete02.png')
                src += '</tr>\n'
            src += '</table><br><br>\n'
        return html(request, body=src, title='messages', back=arg(request, 'back', '/'+_PAGE_MENU))

    def getChild(self, path, request):
        if path == '':
            return self
        return MessagePage(path)


class NewMessagePage(Page):
    pagename = _PAGE_NEW_MESSAGE
    
    def renderPage(self, request):
        idurls = contacts.getContactsAndCorrespondents()
        idurls.sort()
        recipient = arg(request, 'recipient')
        subject = arg(request, 'subject')
        body = arg(request, 'body')
        action = arg(request, 'action').lower().strip()

        if action == 'send':
            msgbody = message.MakeMessage(recipient, subject, body)
            message.SendMessage(recipient, msgbody)
            message.SaveMessage(msgbody)
            request.redirect('/'+_PAGE_MESSAGES)
            request.finish()
            return NOT_DONE_YET

        src = ''
        src += '<h1>new message</h1>\n'
        src += '<form action="%s", method="post">\n' % request.path
        src += '<table>\n'
        src += '<tr><td align=right><b>To:</b></td>\n'
        src += '<td><select name="recipient">\n'
        for idurl in idurls:
            name = nameurl.GetName(idurl)
            src += '<option value="%s"' % idurl
            if idurl == recipient:
                src += ' selected '
            src += '>%s</option>\n' % name
        src += '</select></td>\n'
        src += '<td align=right><a href="%s?back=%s">Add new correspondent</a></td></tr>\n' % (
            '/'+_PAGE_CORRESPONDENTS, request.path)
        src += '<tr><td align=right><b>Subject:</b></td>\n'
        src += '<td colspan=2><input type="text" name="subject" value="%s" size="51" /></td></tr>\n' % subject
        src += '</table>\n'
        src += '<textarea name="body" rows="10" cols="60">%s</textarea><br><br>\n' % body
        src += '<input type="submit" name="action" value=" Send " /><br>\n'
        src += '</form>'
        return html(request, body=src, back=_PAGE_MESSAGES)

class CorrespondentsPage(Page):
    pagename = _PAGE_CORRESPONDENTS

    def _check_name_cb(self, x, request, name):
        idurl = 'http://' + settings.IdentityServerName() + '/' + name + '.xml'
        contacts.addCorrespondent(idurl)
        contacts.saveCorrespondentIDs()
        identitypropagate.SendToID(idurl) #, lambda packet: self._ack_handler(packet, request, idurl))
        src = self._body(request, '', '%s was found' % name, 'success')
        request.write(html_from_args(request, body=src, back=arg(request, 'back', '/'+_PAGE_MENU)))
        request.finish()

    def _check_name_eb(self, x, request, name):
        src = self._body(request, name, '%s was not found' % name, 'failed')
        request.write(html_from_args(request, body=src, back=arg(request, 'back', '/'+_PAGE_MENU)))
        request.finish()

    def _body(self, request, name, msg, typ):
        #idurls = contacts.getContactsAndCorrespondents()
        idurls = contacts.getCorrespondentIDs()
        idurls.sort()
        src = ''
        src += '<h1>friends</h1>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += 'enter user name:<br>\n'
        src += '<input type="text" name="name" value="%s" size="20" />\n' % name
        src += '<input type="submit" name="button" value=" add " />'
        src += '<input type="hidden" name="action" value="add" />\n'
        src += '</form><br><br>\n'
        src += html_message(msg, typ)
        src += '<br><br>\n'
        if len(idurls) == 0:
            src += '<p>you have no friends</p>\n'
        else:
            w, h = misc.calculate_best_dimension(len(idurls))
            imgW = 64
            imgH = 64
            if w >= 4:
                imgW = 4 * imgW / w
                imgH = 4 * imgH / w
            padding = 64 / w - 8 
            src += '<table cellpadding=%d cellspacing=2>\n' % padding
            for y in range(h):
                src += '<tr valign=center>\n'
                for x in range(w):
                    src += '<td align=center width="%s%%">\n' % ((str(int(100.0/float(w)))))
                    n = y * w + x
                    if n >= len(idurls):
                        src += '&nbsp;\n'
                        continue
                    idurl = idurls[n]
                    name = nameurl.GetName(idurl)
                    if not name:
                        src += '&nbsp;\n'
                        continue
                    
                    central_status = central_service._CentralStatusDict.get(idurl, '')
                    icon = 'icons/offline-user01.png'
                    state = 'offline'
                    #if contact_status.isOnline(idurl):
                    if central_status == '!':
                        icon = 'icons/online-user01.png'
                        state = 'online '
    
                    if w >= 5 and len(name) > 10:
                        name = name[0:9] + '<br>' + name[9:]
                    src += '<img src="%s" width=%d height=%d>' % (
                        iconurl(request, icon), imgW, imgH,)
                    src += '<br>\n'
                    src += '%s' % name
                    src += '&nbsp;[<a href="%s?action=remove&idurl=%s&back=%s">x</a>]\n' % (
                        request.path, nameurl.Quote(idurl), arg(request, 'back', '/'+_PAGE_MENU))

                    src += '</td>\n'
                src += '</tr>\n'
            src += '</table>\n'
        src += '<br><br>\n'
        return src

    def renderPage(self, request):
        idurls = contacts.getCorrespondentIDs()
        idurls.sort()
        action = arg(request, 'action')
        idurl = nameurl.UnQuote(arg(request, 'idurl'))
        name = arg(request, 'name', nameurl.GetName(idurl))
        msg = ''
        typ = 'info'

        if action == 'add':
            idurl = 'http://' + settings.IdentityServerName() + '/' + name + '.xml'
            if not misc.ValidUserName(name):
                msg = 'incorrect user name'
                typ = 'error'
            elif idurl in idurls:
                msg = '%s is your friend already' % name
                typ = 'error' 
            else:
                dhnio.Dprint(6, 'webcontrol.CorrespondentsPage.renderPage (add) will request ' + idurl)
                res = dhnnet.getPageTwisted(idurl)
                res.addCallback(self._check_name_cb, request, name)
                res.addErrback(self._check_name_eb, request, name)
                request.notifyFinish().addErrback(self._check_name_eb, request, name)
                return NOT_DONE_YET
            
        elif action == 'remove':
            if idurl in contacts.getCorrespondentIDs():
                contacts.removeCorrespondent(idurl)
                contacts.saveCorrespondentIDs()
                msg = '%s were removed from friends list' % name
                typ = 'success'
                name = ''
            else:
                msg = '%s is not your friend' % name
                typ = 'error'

        src = self._body(request, name, msg, typ)
        return html(request, body=src, back=arg(request, 'back', _PAGE_CORRESPONDENTS))


class ShedulePage(Page):
    pagename = _PAGE_SHEDULE
    set_change = False
    available_types = {  '0': 'none',
                         '1': 'hourly',
                         '2': 'daily',
                         '3': 'weekly',
                         '4': 'monthly',
                         '5': 'continuously'}

    def load_from_data(self, request):
        return schedule.default()

    def read_from_html(self, request, default=schedule.default_dict()):
        shedule_type = arg(request, 'type', default['type'])
        shedule_time = arg(request, 'daytime', default['daytime'])
        shedule_interval = arg(request, 'interval', default['interval'])
        shedule_details = arg(request, 'details',  '')
        if shedule_details.strip() == '':
            shedule_details = default['details']
        shedule_details_str = ''
        for i in range(32):
            if request.args.has_key('detail'+str(i)):
                shedule_details_str += request.args['detail'+str(i)][0] + ' '
        if shedule_details_str != '':
            shedule_details = shedule_details_str.strip()
        return schedule.Schedule(from_dict={
            'type':     shedule_type,
            'daytime':  shedule_time,
            'interval': shedule_interval,
            'details':  shedule_details,
            'lasttime': ''})

    def store_params(self, request):
        return ''

    def save(self, request):
        pass

    def print_shedule(self, request):
        stored = self.load_from_data(request)
        src = '<p>'
        src += stored.html_description()
        src += '<br>\n'
        src += stored.html_next_start()
        src += '</p>\n'
        return src
    
    def renderPage(self, request):
        action = arg(request, 'action')
        submit = arg(request, 'submit').strip()
        back = arg(request, 'back', '/'+_PAGE_MAIN)
        
        stored = self.load_from_data(request)
        dhnio.Dprint(6, 'webcontrol.ShedulePage.renderPage stored=%s args=%s' % (str(stored), str(request.args)))

        src = ''

        #---form                    
        src += '<form action="%s" method="post">\n' % request.path

        if action == '':
            src += '<input type="hidden" name="action" value="type" />\n'
            src += '<input type="hidden" name="back" value="%s" />\n' % back
            src += self.store_params(request)
            src += '<br><br>\n<input type="submit" name="submit" value=" change "/>\n'
            
        elif action == 'type' or ( action == 'save' and submit == 'back'):
            #---type
            current_type = stored.type #arg(request, 'type', 'none')
            src += '<input type="hidden" name="action" value="details" />\n'
            src += '<input type="hidden" name="back" value="%s" />\n' % back
            src += self.store_params(request)
            src += '<br><br>\n'
            for i in range(len(self.available_types)):
                src += '<input id="radio%s" type="radio" name="type" value="%s" %s />&nbsp;&nbsp;&nbsp;\n' % (
                    str(i), self.available_types[str(i)],
                    ( 'checked' if current_type == self.available_types[str(i)] else '' ), )
            src += '<br><br>\n<input type="submit" name="submit" value=" select "/>\n'
        
        elif action == 'details':
            #---details
            current_type = arg(request, 'type', 'none')
            if current_type != stored.type:
                current = schedule.Schedule(typ=current_type)
            else:
                current = stored
            src += '<input type="hidden" name="action" value="save" />\n'
            src += '<input type="hidden" name="back" value="%s" />\n' % back
            src += '<input type="hidden" name="type" value="%s" />\n' % current.type
            src += self.store_params(request)
            src += '<br><br>\n'
            #---none
            if current.type == 'none':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start only one time, after you press a button<br>\n'
                src += '<input type="hidden" name="daytime" value="%s" />\n' % current.daytime
                src += '<input type="hidden" name="interval" value="%s" />\n' % current.interval
            #---continuously
            elif current.type == 'continuously':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start every '
                src += '<input type="text" name="interval" value="%s" size=4 />' % current.interval
                src += '&nbsp;seconds<br>\n'
                src += '<input type="hidden" name="daytime" value="%s" />\n' % current.daytime
            #---hourly
            elif current.type == 'hourly':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start every '
                src += '<input type="text" name="interval" value="%s" size=2 />' % current.interval
                src += '&nbsp;hour(s)<br>\n'
                src += '<input type="hidden" name="daytime" value="%s" size=10 />\n' % current.daytime
            #---daily
            elif current.type == 'daily':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start at&nbsp;&nbsp;'
                src += '<input type="text" name="daytime" value="%s" size=10 />' % current.daytime
                src += '&nbsp;&nbsp;every&nbsp;&nbsp;'
                src += '<input type="text" name="interval" value="%s" size=1 />' % current.interval
                src += '&nbsp;&nbsp;day(s)<br>\n'
            #---weekly
            elif current.type == 'weekly':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start at '
                src += '<input type="text" name="daytime" value="%s" size=10 />' % current.daytime
                src += '&nbsp;every&nbsp;'
                src += '<input type="text" name="interval" value="%s" size=1 />' % current.interval
                src += '&nbsp;week(s) in:<br><br>\n'
                src += '<table><tr>\n'
                labels = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                days = current.details.split(' ')
                for i in range(len(labels)):
                    day = labels[i]
                    src += '<td>'
                    src += '<input type="checkbox" name="detail%d" value="%s" %s /> &nbsp;&nbsp;%s\n' % (
                        i, day, ('checked' if day in days else ''), day)
                    src += '</td>\n'
                    if i == 3:
                        src += '</tr>\n<tr>\n'
                src += '<td>&nbsp;</td>\n'
                src += '</tr></table><br>\n'
            #---monthly
            elif current.type == 'monthly':
                src += '<input type="hidden" name="details" value="%s" />\n' % current.details
                src += 'start at '
                src += '<input type="text" name="daytime" value="%s" size=10 />' % current.daytime
                src += '&nbsp;every&nbsp;'
                src += '<input type="text" name="interval" value="%s" size=1 />' % current.interval
                src += '&nbsp;month(s) at dates:<br><br>\n'
                src += '<table><tr>\n'
                labels = current.details.split(' ')
                for i in range(0,4):
                    for j in range(0, 8):
                        label = str(i*8 + j + 1)
                        if int(label) > 31:
                            src += '<td>&nbsp;</td>\n'
                        else:
                            src += '<td><input type="checkbox" name="detail%s" value="%s" %s />&nbsp;&nbsp;%s</td>\n' % (
                                label, label, ('checked' if label in labels else ''), label)
                    src += '</tr>\n<tr>\n'
                src += '</tr></table><br>\n'
            src += '<br>\n'
            src += '<input type="submit" name="submit" value=" back "/>&nbsp;&nbsp;&nbsp;&nbsp;\n'
            src += '<input type="submit" name="submit" value=" save "/>\n'
            
        elif action == 'save':
            #---save
            if submit == 'save':
                self.save(request)
                src += '<br><br>\n'
                src += html_message('saved!', 'done')
            else:
                dhnio.Dprint(2, 'webcontrol.ShedulePage.renderPage ERROR incorrect "submit" parameter value: ' + submit)
                src += '<input type="hidden" name="action" value="type" />\n'
                src += '<input type="hidden" name="back" value="%s" />\n' % back
                src += self.store_params(request)
                src += '<br><br>\n<input type="submit" name="submit" value=" change "/>\n'
                
        src += '</form><br><br>\n'

        #---print schedule
        src = '<br><br>\n' + self.print_shedule(request) + '<br>\n' + src
        src += '\n<a href="%s">[return]</a><br>\n' % back


        return html(request, body=src, back=back)
        

class BackupShedulePage(ShedulePage):
    pagename = _PAGE_BACKUP_SHEDULE

    def load_from_data(self, request):
        backupdir = unicode(misc.unpack_url_param(arg(request, 'backupdir'), None))
        if backupdir is None:
            dhnio.Dprint(1, 'webcontrol.BackupShedulePage.load WARNING backupdir=%s' % str(backupdir))
            return schedule.empty()
        current = backup_db.GetSchedule(backupdir)
        if current is None:
            return schedule.empty()
        return current

    def save(self, request):
        backupdir = unicode(misc.unpack_url_param(arg(request, 'backupdir'), None))
        if backupdir is None:
            dhnio.Dprint(1, 'webcontrol.BackupShedulePage.save ERROR backupdir=None')
            return
        if backupdir != '' and not backup_db.CheckDirectory(backupdir):
            backup_db.AddDirectory(backupdir, True)
        dirsize.ask(backupdir)
        current = self.read_from_html(request)
        backup_db.SetSchedule(backupdir, current)
        backup_db.Save()
        reactor.callLater(0, backupshedule.run)
        dhnio.Dprint(6, 'webcontrol.BackupShedulePage.save success %s %s' % (backupdir, current))

    def list_params(self):
        return ('backupdir',)

    def store_params(self, request):
        src = ''
        backupdir = unicode(misc.unpack_url_param(arg(request, 'backupdir'), None))
        if backupdir is not None:
            src += '<input type="hidden" name="backupdir" value="%s" />\n' % str(misc.pack_url_param(backupdir))
        return src

    def print_shedule(self, request):
        backupdir = unicode(misc.unpack_url_param(arg(request, 'backupdir'), None))
        src = ''
        if backupdir is None:
            src += '<p>icorrect backup directory</p>\n'
            src += html_comment('icorrect backup directory\n')
            return src
        src += '<h3>%s</h3>\n' % backupdir
        src += html_comment(str(backupdir))
        stored = self.load_from_data(request)
        description = stored.html_description()
        next_start = stored.html_next_start()
        src += '<p>'
        src += description+'<br>\n'
        src += html_comment(description.replace('<b>', '').replace('</b>', ''))+'\n'
        src += next_start+'\n'
        src += html_comment(next_start.replace('<b>', '').replace('</b>', ''))+'\n'
        src += '</p>\n'
        return src


class UpdateShedulePage(ShedulePage):
    pagename = _PAGE_UPDATE_SHEDULE
    available_types = {  '0': 'none',
                         '1': 'hourly',
                         '2': 'daily',
                         '3': 'weekly',
                         '4': 'monthly',}

    def load_from_data(self, request):
        return schedule.Schedule(from_dict=dhnupdate.read_shedule_dict())

    def save(self, request):
        current = self.read_from_html(request)
        settings.setUpdatesSheduleData(current.to_string())
        dhnupdate.update_shedule_file(settings.getUpdatesSheduleData())
        dhnupdate.update_sheduler()
        dhnio.Dprint(6, 'webcontrol.UpdateShedulePage.save success')

    def print_shedule(self, request):
        src = '<h3>update schedule</h3>\n'
        stored = self.load_from_data(request)
        src += '<p>'
        description = stored.html_description()
        next_start = stored.html_next_start()
        src += description + ',<br>\n'
        src += next_start
        src += '</p>\n'
        return src


class DevReportPage(Page):
    pagename = _PAGE_DEV_REPORT

    def renderPage(self, request):
        global local_version

        subject = arg(request, 'subject')
        body = arg(request, 'body')
        action = arg(request, 'action').lower().strip()
        includelogs = arg(request, 'includelogs', 'True')

        src = ''
        if action == 'send':
            # d = threads.deferToThread(misc.SendDevReport, subject, body, includelogs=='True')
            misc.SendDevReport(subject, body, includelogs=='True')
            src += '<br><br><br><h3>Thank you for your help!</h3>'
            return html(request, body=src, back=_PAGE_CONFIG)

        src += '<h3>send Message</h3>'
        src += '<form action="%s", method="post">\n' % request.path
        src += '<table>\n'
        src += '<tr><td align=right><b>To:</b></td>\n'
        src += '<td>DataHaven.NET LTD'
        src += '</td>\n'
        src += '<td align=right>\n'
        src += '<input type="checkbox" name="includelogs" value="True" %s /> include logs\n' % (
            'checked' if includelogs=='True' else '')
        src += '</td></tr>\n'
        src += '<tr><td align=right><b>Subject:</b></td>\n'
        src += '<td colspan=2><input type="text" name="subject" value="%s" size="51" /></td></tr>\n' % subject
        src += '</table>\n'
        src += '<textarea name="body" rows="10" cols="40">%s</textarea><br><br>\n' % body
        src += '<input type="submit" name="action" value=" Send " /><br>\n'
        src += '</form>'
        return html(request, body=src, back='/'+_PAGE_CONFIG)


class MemoryPage(Page):
    pagename = _PAGE_MEMORY

    def renderPage(self, request):
        src = '<h1>memory usage</h1>\n'
        if not settings.enableMemoryProfile():
            src = '<p>You need to switch on <a href="%s">memory profiler</a> in the settings and restart DataHaven.NET.</p>\n' % (
                '/'+_PAGE_SETTINGS+'/'+'logs.memprofile-enable')
            src += html_comment('You need to switch on memory profiler in the settings.')
            return html(request, back=arg(request, 'back', '/'+_PAGE_CONFIG), body=src)
        try:
            from guppy import hpy
        except:
            src = 'guppy package is not installed in your system.'
            src += html_comment('guppy package is not installed in your system.')
            return html(request, back=arg(request, 'back', '/'+_PAGE_CONFIG), body=src)
        # dhnio.Dprint(6, 'webcontrol.MemoryPage')
        h = hpy()
        out = str(h.heap())
        dhnio.Dprint(6, '\n'+out)
        src = ''
        src += '<table width="600px"><tr><td>\n'
        src += '<div align=left>\n'
        src += '<code>\n'
        wwwout = out.replace(' ', '&nbsp;').replace("'", '"').replace('<', '[').replace('>', ']').replace('\n', '<br>\n')
        src += wwwout
        src += '</code>\n</div>\n</td></tr></table>\n'
        for line in out.splitlines():
            src += html_comment(line)
        return html(request, back=arg(request, 'back', '/'+_PAGE_CONFIG), body=src)

                   
class EmergencyPage(Page):
    pagename = _PAGE_EMERGENCY
    
    def renderPage(self, request):
        back = arg(request, 'back') 
        message = ''
        src = ''
        src += '<h1>emergency contacts</h1>\n'
        src += '<form action="%s" method="post">\n' % request.path
        src += '<table width="70%"><tr><td align=center>\n'
        src += '<p>We can contact you if your account balance is running low,' 
        src += 'if your backups are not working, or if your machine appears to not be working.</p>\n'
        src += '<br><br><b>What email address should we contact you at? Email contact is free.</b>\n'
        src += '<br><br><input type="text" name="email" size="25" value="%s" />\n' % arg(request, 'email')
        src += '<br><br><b>%s</b>\n' % settings.uconfig().get('emergency.emergency-phone', 'info')
        src += '<br><br><input type="text" name="phone" size="25" value="%s" />\n' % arg(request, 'phone')
        src += '<br><br><b>%s</b>\n' % settings.uconfig().get('emergency.emergency-fax', 'info')
        src += '<br><br><input type="text" name="fax" size="25" value="%s" />\n' % arg(request, 'fax')
        src += '<br><br><b>%s</b>\n' % settings.uconfig().get('emergency.emergency-text', 'info')
        src += '<br><br><textarea name="text" rows="5" cols="40">%s</textarea><br>\n' % arg(request, 'text')
        if message != '':
            src += '<br><br><font color="%s">%s</font>\n' % (messageColor, message)
        src += '<br><center><input type="submit" name="submit" value=" save " /></center>\n'
        src += '<input type="hidden" name="action" value="contacts-ready" />\n'
        src += '<input type="hidden" name="showall" value="true" />\n'
        src += '</td></tr></table>\n'
        src += '</form>\n'
        return html(request, body=src, back=back)     
   

class MonitorTransportsPage(Page):
    pagename = _PAGE_MONITOR_TRANSPORTS
    
    def renderPage(self, request):
        # back = arg(request, 'back', '/'+_PAGE_DEVELOPMENT) 
        transfers = transport_control.current_transfers()
        bytes_stats = transport_control.current_bytes_transferred()
        # print 'MonitorTransportsPage', len(bytes_stats)
        counters = transport_control.counters()
        index = {}
        for info in transfers:
            idurl = info.remote_idurl 
            if not idurl:
                idurl = info.proto_address
            if not index.has_key(idurl):
                index[idurl] = {'send': [], 'receive':[]}
            index[idurl][info.send_or_receive].append((info.transfer_id, info.proto, info.size, info.description))
        src = ''
        src += '<table width=100% cellspacing=0 cellpadding=2 border=0>\n'
        src += '<tr>\n'
        src += '<td align=left><h3>received</h3></td>\n'
        src += '<td align=right width=45%>&nbsp;</td>\n'
        src += '<td align=center width=100>&nbsp;</td>\n'
        src += '<td align=left width=45%>&nbsp;</td>\n'
        src += '<td align=right><h3>sent</h3></td>\n'
        src += '</tr>\n'
        i = 0
        # all = contacts.getContactsAndCorrespondents()+[settings.CentralID()]
        for idurl in sorted(index.keys()):
#             label = idurl
#             if not idurl.startswith('http://identity.datahaven.net/'):
#                 label = ''
            i += 1
            bytes_in = counters.get(idurl, {'receive': 0})['receive']
            bytes_in = '&nbsp;' if bytes_in == 0 else diskspace.MakeStringFromBytes(bytes_in) 
            bytes_out = counters.get(idurl, {'send': 0})['send']
            bytes_out = '&nbsp;' if bytes_out == 0 else diskspace.MakeStringFromBytes(bytes_out)
            if i % 2: 
                src += '<tr>\n'
            else:
                src += '<tr bgcolor="#f0f0f0">\n'
            src += '<td nowrap align=left>%s</td>\n' % bytes_in
            src += '<td align=right>\n'
            if len(index.get(idurl, {'receive': []})['receive']) > 0:
                src += '<table border=0 cellspacing=0 cellpadding=0><tr><td align=right>\n'
                counter = 0
                for tranfer_id, proto, size, description in index[idurl]['receive']:
                    b = bytes_stats[tranfer_id]
                    if str(size) not in ['', '0', '-1']:
                        progress = '%s/%s' % (diskspace.MakeStringFromBytes(b).replace(' ',''), diskspace.MakeStringFromBytes(size).replace(' ',''))
                    else:
                        progress = '%s' %  diskspace.MakeStringFromBytes(b).replace(' ','')
                    src += '<table bgcolor="#a0a0f0"><tr><td nowrap><font size=-1>%s:%s[%s]</font></td></tr></table>\n' % (proto, description, progress)
                    counter += 1
                src += '</td></tr></table>\n'
            else:
                src += '&nbsp;'
            src += '</td>\n'
            if contact_status.isOnline(idurl):
                color = 'green'
            else:
                color = 'gray'
            udp_out = 0
            udp_in = 0
            for a in automat.objects().values():
                if a.name.startswith('udp_') and a.remote_idurl == idurl:
                    udp_out = len(a.outgoingFiles)
                    udp_in = len(a.incommingFiles)
            src += '<td align=center nowrap><b><font color=%s>%d,%d,%d | %s | %d,%d,%d</font></b></td>\n' % (
                color, 
                io_throttle.GetRequestQueueLength(idurl), 
                len(index[idurl]['receive']),
                udp_in,
                nameurl.GetName(idurl), 
                io_throttle.GetSendQueueLength(idurl),
                len(index[idurl]['send']),
                udp_out)
            src += '<td align=left>'
            if len(index.get(idurl, {'send': []})['send']) > 0:
                src += '<table border=0 cellspacing=0 cellpadding=0><tr><td align=left>\n'
                for tranfer_id, proto, size, description in index[idurl]['send']:
                    b = bytes_stats[tranfer_id]
                    if b:
                        progress = '%s/%s' % (diskspace.MakeStringFromBytes(b).replace(' ',''), diskspace.MakeStringFromBytes(size).replace(' ',''))
                    else:
                        progress = '%s' %  diskspace.MakeStringFromBytes(size).replace(' ','')
                    src += '<table bgcolor="#a0f0a0"><tr><td nowrap><font size=-1>%s:%s[%s]</font></td></tr></table>\n' % (proto, description, progress)
                src += '</td></tr></table>\n'
            else:
                src += '&nbsp;'
            src += '</td>\n'
            src += '<td nowrap align=right>%s</td>\n' % bytes_out
            src += '</tr>\n'
        src += '<tr bgcolor="#d0d0d0">\n'
        src += '<td nowrap>%s</td>\n' % diskspace.MakeStringFromBytes(counters.get('total_bytes', {'receive': 0})['receive'])
        src += '<td>&nbsp;</td>\n'
        src += '<td>&nbsp;</td>\n'
        src += '<td>&nbsp;</td>\n'
        src += '<td nowrap>%s</td>\n' % diskspace.MakeStringFromBytes(counters.get('total_bytes', {'send': 0})['send'])
        src += '</tr>\n'
        src += '</table><br>\n'
        src += '<p>send queue length: <b>%d</b>\n</p>\n' % transport_control.SendQueueLength()
        src += '<p>current transfers: <b>%d</b>\n</p>\n' % len(transport_control.current_transfers())
        src += '<br><br><br>\n'
        
        # html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n'
        # html += '<html><head>'
        # html += '<title>%(title)s</title>'
        # html += '<meta http-equiv="refresh" content="1">'
        # html += '</head>\n'
        # html += '<body><center>%(body)s</center></body></html>'        
        # return html % {'body': src, 'title': 'Traffic'}
        return html(request, body=src, back='none', home='', reload='1', window_title='Traffic')


class TrafficPage(Page):
    pagename = _PAGE_TRAFFIC
    def renderPage(self, request):
        src = ''
        src += '<a href="%(baseurl)s?type=%(type)s&dir=in">[incoming]</a>|\n'
        src += '<a href="%(baseurl)s?type=%(type)s&dir=out">[outgoing]</a>\n'
        src += '&nbsp;&nbsp;&nbsp;\n'
        src += '<a href="%(baseurl)s?type=idurl&dir=%(dir)s">[by idurl]</a>|\n'
        src += '<a href="%(baseurl)s?type=host&dir=%(dir)s">[by host]</a>|\n'
        src += '<a href="%(baseurl)s?type=proto&dir=%(dir)s">[by proto]</a>\n'
        src += '<a href="%(baseurl)s?type=type&dir=%(dir)s">[by type]</a>\n'
        direction = request.args.get('dir', [''])[0]
        if direction not in ('in', 'out'):
            direction = 'in'
        typ = request.args.get('type', [''])[0]
        if typ not in ('idurl', 'host', 'proto', 'type'):
            typ = 'idurl'
        if direction == 'in' and webtraffic.inbox_packets_count() > 0:
            src += '<hr>\n'
            src += '<table width=100%%><tr>\n'
            src += '<td align=left>%(type)s</td>\n'
            src += '<td nowrap>total bytes</td>\n'
            src += '<td nowrap>total packets</td>\n'
            src += '<td nowrap>finished packets</td>\n'
            src += '<td nowrap>failed packets</td></tr>\n'
            if typ == 'idurl':
                for i, v in webtraffic.inbox_by_idurl().items():
                    src += '<tr><td><a href="%s">%s</a></td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, i, v[0], v[3], v[1], v[2])
            elif typ == 'host':
                for i, v in webtraffic.inbox_by_host().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'proto':
                for i, v in webtraffic.inbox_by_proto().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'type':
                for i, v in webtraffic.inbox_by_type().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            src += '</table>'
        if direction == 'out' and webtraffic.outbox_packets_count() > 0:
            src += '<hr>\n'
            src += '<table width=100%%><tr>\n'
            src += '<td align=left>%(type)s</td>\n'
            src += '<td nowrap>total bytes</td>\n'
            src += '<td nowrap>total packets</td>\n'
            src += '<td nowrap>finished packets</td>\n'
            src += '<td nowrap>failed packets</td></tr>\n'
            if typ == 'idurl':
                for i, v in webtraffic.outbox_by_idurl().items():
                    src += '<tr><td><a href="%s">%s</a></td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, i, v[0], v[3], v[1], v[2])
            elif typ == 'host':
                for i, v in webtraffic.outbox_by_host().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'proto':
                for i, v in webtraffic.outbox_by_proto().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'type':
                for i, v in webtraffic.outbox_by_type().items():
                    src += '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (
                        i, v[0], v[3], v[1], v[2])
            src += '</table>'
        src += '<hr>\n'
        if direction == 'in':
            src += '<p>total income packets: %d</p>' % webtraffic.inbox_packets_count()
        if direction == 'out':
            src += '<p>total outgoing packets: %d</p>' % webtraffic.outbox_packets_count()
        src += '</body></html>'
        d = {'type': typ, 'dir': direction, 'baseurl': 'http://127.0.0.1:%d%s' % (local_port, request.path)}
        src = src % d
        return html(request, body=src, back='none', home='', reload=1, window_title='Counters')

#------------------------------------------------------------------------------

class SettingsTreeNode(Page):
    pagename = _PAGE_SETTING_NODE
    isLeaf = True
    def __init__(self, path):
        Page.__init__(self)
        self.path = path
        self.modifyList = []
        self.modifyTask = None
        self.update()

    def renderPage(self, request):
        dhnio.Dprint(6, 'webcontrol.SettingsTreeNode.renderPage [%s] args=%s' % (self.path, str(request.args)))
        src = ''
        if self.exist:
            src += '<h3>%s</h3>\n' % self.label 
            if self.info != '':
                src += '<table width=80%><tr><td>\n'
                src += '<p>%s</p>\n' % self.info
                src += '</td></tr></table>\n'
            old_value = self.value
            #dhnio.Dprint(6, 'webcontrol.SettingsTreeNode.renderPage before %s: %s' % (self.path, self.value))
            ret = self.body(request)
            #src += self.body(request)
            #dhnio.Dprint(6, 'webcontrol.SettingsTreeNode.renderPage after %s: %s' % (self.path, self.value))
            src += html_comment('  path:     %s' % self.path)
            src += html_comment('  label:    %s' % self.label)
            src += html_comment('  info:     %s' % self.info)
            src += html_comment('  value:    %s' % self.value)
            if old_value != self.value:
                src += html_comment('  modified: [%s]->[%s]' % (old_value, self.value))
            if ret.startswith('redirect'):
                ret = ret.split(' ', 1)[1]
                request.redirect(ret)
                request.finish()
                return NOT_DONE_YET
            src += ret
        else:
            src += '<p>This setting is not exist.</p><br>'
            src += html_comment('  incorrect name, this option is not exist')
        d = {}
        header = ''
        if self.exist and len(self.leafs) >= 1:
            header = 'settings'
            try:
                dhnio.Dprint(14, 'webcontrol.SettingsTreeNode.renderPage leafs=%s' % (self.leafs))
                for i in range(0, len(self.leafs)):
                    fullname = '.'.join(self.leafs[0:i+1])
                    label = settings.uconfig().get(fullname, 'label')
                    if label is None:
                        label = self.leafs[i]
                    header += ' > ' + label
                    dhnio.Dprint(14, 'webcontrol.SettingsTreeNode.renderPage fullname=%s label=%s' % (fullname, label))
            except:
                dhnio.DprintException()
        else:
            header = str(self.label)
        back = ''
        if arg(request, 'back', None) is not None:
            back = arg(request, 'back')
        else:
            back = '/' + _PAGE_CONFIG
        return html(request, body=src, back=back, title=header)

    def requestModify(self, path, value):
        if p2p_connector.A().state in ['TRANSPORTS', 'NETWORK?']:
            self.modifyList.append((path, value))
            if self.modifyTask is None:
                self.modifyTask = reactor.callLater(1, self.modifyWorker)
                dhnio.Dprint(4, 'webcontrol.SettingsTreeNode.requestModify(%s) task for %s' % (self.path, path))
        else:
            oldvalue = settings.uconfig(path)
            settings.uconfig().set(path, value)
            settings.uconfig().update()
            self.update()
            self.modified(oldvalue)
            
    def modifyWorker(self):
        #dhnio.Dprint(4, 'webcontrol.SettingsTreeNode.modifyWorker(%s)' % self.path)
        if len(self.modifyList) == 0:
            return
        if p2p_connector.A().state in ['TRANSPORTS', 'NETWORK?']:
            self.modifyTask = reactor.callLater(1, self.modifyWorker)
            return
        oldvalue = settings.uconfig(self.path)
        for path, value in self.modifyList:
            settings.uconfig().set(path, value)
        settings.uconfig().update()
        self.update()
        self.modified(oldvalue)
        self.modifyList = []
        self.modifyTask = None

    def update(self):
        self.exist = settings.uconfig().has(self.path)
        self.value = settings.uconfig().data.get(self.path, '')
        self.label = settings.uconfig().labels.get(self.path, '')
        self.info = settings.uconfig().infos.get(self.path, '')
        self.leafs = self.path.split('.')
        self.has_childs = len(settings.uconfig().get_childs(self.path)) > 0

    def modified(self, old_value=None):
        dhnio.Dprint(8, 'webcontrol.SettingsTreeNode.modified %s %s' % (self.path, self.value))

        if self.path in (
                'transport.transport-tcp.transport-tcp-port',
                'transport.transport-tcp.transport-tcp-enable',
                'transport.transport-udp.transport-udp-port',
                'transport.transport-udp.transport-udp-enable',
                'transport.transport-ssh.transport-ssh-port',
                'transport.transport-ssh.transport-ssh-enable',
                'transport.transport-q2q.transport-q2q-host',
                'transport.transport-q2q.transport-q2q-username',
                'transport.transport-q2q.transport-q2q-password',
                'transport.transport-q2q.transport-q2q-enable',
                'transport.transport-email.transport-email-address',
                'transport.transport-email.transport-email-pop-host',
                'transport.transport-email.transport-email-pop-username',
                'transport.transport-email.transport-email-pop-password',
                'transport.transport-email.transport-email-pop-ssl',
                'transport.transport-email.transport-email-smtp-host',
                'transport.transport-email.transport-email-smtp-port',
                'transport.transport-email.transport-email-smtp-username',
                'transport.transport-email.transport-email-smtp-password',
                'transport.transport-email.transport-email-smtp-need-login',
                'transport.transport-email.transport-email-smtp-ssl',
                'transport.transport-email.transport-email-enable',
                'transport.transport-http.transport-http-server-port',
                'transport.transport-http.transport-http-ping-timeout',
                'transport.transport-http.transport-http-server-enable',
                'transport.transport-http.transport-http-enable',
                'transport.transport-skype.transport-skype-enable',
                'transport.transport-cspace.transport-cspace-enable',
                'transport.transport-cspace.transport-cspace-key-id',
                ):
            p2p_connector.A('settings', [self.path,])

        if self.path in (
                'central-settings.desired-suppliers',
                'central-settings.needed-megabytes',
                'central-settings.shared-megabytes',
                'emergency.emergency-first',
                'emergency.emergency-second',
                'emergency.emergency-email',
                'emergency.emergency-phone',
                'emergency.emergency-fax',
                'emergency.emergency-text',):
            #centralservice.SendSettings(True)
            central_connector.A('settings', [self.path,])

        if self.path in (
                'updates.updates-mode',
                'updates.updates-shedule'):
            dhnupdate.update_shedule_file(settings.getUpdatesSheduleData())
            dhnupdate.update_sheduler()

        if self.path == 'logs.stream-enable':
            if settings.enableWebStream():
                misc.StartWebStream()
            else:
                misc.StopWebStream()

        # if self.path == 'logs.traffic-enable':
        #     if settings.enableWebTraffic():
        #         misc.StartWebTraffic()
        #     else:
        #         misc.StopWebTraffic()

        if self.path == 'logs.stream-port':
            misc.StopWebStream()
            if settings.enableWebStream():
                reactor.callLater(5, misc.StartWebStream)

        if self.path == 'logs.traffic-port':
            misc.StopWebTraffic()
            if settings.enableWebTraffic():
                reactor.callLater(5, misc.StartWebTraffic)

        if self.path == 'logs.debug-level':
            try:
                dhnio.SetDebug(int(self.value))
            except:
                dhnio.Dprint(1, 'webcontrol.SettingsTreeNode.modified ERROR wrong value!')

        if self.path == 'general.general-autorun':
            if dhnio.isFrozen() and dhnio.Windows():
                if settings.getGeneralAutorun():
                    misc.SetAutorunWindows()
                else:
                    misc.ClearAutorunWindows()
                    
        if self.path == 'folder.folder-customers':
            if old_value is not None:
                result = misc.MoveFolderWithFiles(old_value, settings.getCustomersFilesDir(), True)
                dhnio.Dprint(2, 'misc.MoveFolderWithFiles returned ' + result)
            
        if self.path == 'folder.folder-backups':
            if old_value is not None:
                result = misc.MoveFolderWithFiles(old_value, settings.getLocalBackupsDir(), True)
                dhnio.Dprint(2, 'misc.MoveFolderWithFiles returned ' + result)
                
        if self.path == 'backup.backup-block-size':
            settings.setBackupBlockSize(self.value)

    def body(self, request):
        global SettingsTreeNodesDict
        dhnio.Dprint(12, 'webcontrol.SettingsTreeNode.body path='+self.path)
        if not self.has_childs:
            return ''
        src = '<br>'
        back = arg(request, 'back')
        childs = settings.uconfig().get_childs(self.path).keys()
        dhnio.Dprint(12, 'webcontrol.SettingsTreeNode.body childs='+str(childs))
        for path in settings.uconfig().default_order:
            if path.strip() == '':
                continue
            if path not in childs:
                continue
            leafs = path.split('.')
            name = leafs[-1]
            typ = _SettingsTreeNodesDict.get(name, None)
            if typ is None:
                continue
            if len(leafs) == len(self.leafs)+1:
                label = settings.uconfig().labels.get(path, '')
                args = ''
                if back:
                    args += '?back=' + back
                src += '<br><a href="%s%s">%s</a>\n' % ('/' + _PAGE_SETTINGS + '/' + path, args , label)
        return src

class SettingsTreeYesNoNode(SettingsTreeNode):
    def body(self, request):
        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        choice = arg(request, 'choice', None)
        if choice is not None and not ReadOnly() and choice.lower() != self.value.lower():
            self.requestModify(self.path, choice)
#            settings.uconfig().set(self.path, choice)
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        yes = no = ''
        if self.value.lower() == 'true':
            yes = 'checked'
        else:
            no = 'checked'

        if back:
            back = '&back=' + back

        src = ''
        src += '<br><font size=+2>\n'
        if not ReadOnly():
            src += '<a href="%s?choice=True%s">' % (request.path, back)
        if yes:
            src += '<b>[Yes]</b>'
        else:
            src += ' Yes '
        if not ReadOnly():
            src += '</a>'
        src += '\n&nbsp;&nbsp;&nbsp;\n'
        if not ReadOnly():
            src += '<a href="%s?choice=False%s">' % (request.path, back)
        if no:
            src += '<b>[No]</b>'
        else:
            src += ' No '
        if not ReadOnly():
            src += '</a>'
        src += '\n</font>'
        src += '<br>\n'
        src += html_message(message[0], message[1])
        return src


def SettingsTreeAddComboboxList(name, l):
    global _SettingsTreeComboboxNodeLists
    _SettingsTreeComboboxNodeLists[name] = l

class SettingsTreeComboboxNode(SettingsTreeNode):
    def listitems(self):
        global _SettingsTreeComboboxNodeLists
        combo_list = _SettingsTreeComboboxNodeLists.get(self.leafs[-1], list())
        return map(str, combo_list)
    def body(self, request):
        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        items = self.listitems()
        message = ('', 'info')
        
        choice = arg(request, 'choice', None)
        if choice is not None and not ReadOnly():
            self.requestModify(self.path, choice)
#            settings.uconfig().set(self.path, choice)
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<table>\n'
        for i in range(len(items)):
            checked = ''
            if items[i] == self.value or items[i] == self.leafs[-1]:
                checked = 'checked'
            src += '<tr><td><input id="radio%s" type="radio" name="choice" value="%s" %s />' % (
                str(i),
                items[i],
                checked,)
            #src += '<label for="radio%s">  %s</label></p>\n' % (str(i), items[i],)
            src += '</td></tr>\n'
        src += '</table><br>\n'
        src += '<br>'
        src += '<input class="buttonsave" type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input class="buttonreset" type="reset" name="reset" value=" Reset " /><br>\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreeUStringNode(SettingsTreeNode):
    def body(self, request):
        dhnio.Dprint(12, 'webcontrol.SettingsTreeUStringNode.body path='+self.path)

        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        text = arg(request, 'text', None)
        if text is not None and not ReadOnly():
            self.requestModify(self.path, unicode(text))
#            settings.uconfig().set(self.path, unicode(text))
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="text" name="text" value="%s" /><br>\n' % self.value
        src += '<br>'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " /><br>\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreePasswordNode(SettingsTreeNode):
    def body(self, request):
        dhnio.Dprint(12, 'webcontrol.SettingsTreePasswordNode.body path='+self.path)

        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        text = arg(request, 'text', None)
        if text is not None and not ReadOnly():
            self.requestModify(self.path, unicode(text))
#            settings.uconfig().set(self.path, unicode(text))
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="password" name="text" value="%s" /><br>\n' % self.value
        src += '<br>'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n'  % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " /><br>\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreeNumericNonZeroPositiveNode(SettingsTreeNode):
    def body(self, request):
        dhnio.Dprint(12, 'webcontrol.SettingsTreeNumericNonZeroPositiveNode.body path='+self.path)

        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        text = arg(request, 'text', None)
        if text is not None:
            try:
                text = int(text)
            except:
                message = ('wrong value. enter positive non zero number.', 'failed')
                text = None
            if text <= 0:
                message = ('wrong value. enter positive non zero number.', 'failed')
                text = None
        if text is not None and not ReadOnly():
            self.requestModify(self.path, unicode(text))
#            settings.uconfig().set(self.path, unicode(text))
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="text" name="text" value="%s" />\n' % self.value
        src += '<br><br>\n'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreeNumericPositiveNode(SettingsTreeNode):
    def body(self, request):
        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        text = arg(request, 'text', None)
        if text is not None and not ReadOnly():
            try:
                text = int(text)
            except:
                message = ('wrong value. enter positive number.', 'failed')
                text = None
            if text < 0:
                message = ('wrong value. enter positive number.', 'failed')
                text = None
        if text is not None:
            self.requestModify(self.path, unicode(text))
#            settings.uconfig().set(self.path, unicode(text))
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="text" name="text" value="%s" />\n' % self.value
        src += '<br><br>\n'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % back
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreeDirPathNode(SettingsTreeNode):
    def body(self, request):
        src = ''
        msg = None
        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        action = arg(request, 'action')
        opendir = unicode(misc.unpack_url_param(arg(request, 'opendir'), ''))
        if action == 'dirselected' and not ReadOnly():
            if opendir:
#                oldValue = settings.uconfig(self.path)
                self.requestModify(self.path, str(opendir))
#                settings.uconfig().set(self.path, str(opendir))
#                settings.uconfig().update()
#                self.update()
#                self.modified(oldValue)
                #msg = ('saved', 'success')
                return 'redirect ' + back

        src += '<p>%s</p><br>' % self.value
        
        if msg is not None:
            src += '<br>\n'
            src += html_message(msg[0], msg[1])

        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="hidden" name="action" value="dirselected" />\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '<input type="hidden" name="parent" value="%s" />\n' % request.path
        src += '<input type="hidden" name="label" value="Select folder" />\n'
        src += '<input type="hidden" name="showincluded" value="true" />\n'
        src += '<input type="submit" name="opendir" value=" browse " path="%s" %s />\n' % (self.value, ('disabled' if ReadOnly() else ''))
        src += '</form>\n'
        return src

class SettingsTreeTextNode(SettingsTreeNode):
    def body(self, request):
        dhnio.Dprint(12, 'webcontrol.SettingsTreeTextNode.body path='+self.path)

        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')
        text = arg(request, 'text', None)
        if text is not None and not ReadOnly():
            self.requestModify(self.path, unicode(text))
#            settings.uconfig().set(self.path, unicode(text))
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<textarea name="text" rows="5" cols="40">%s</textarea><br>\n' % self.value
        src += '<br>'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " /><br>\n'
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        return src

class SettingsTreeDiskSpaceNode(SettingsTreeNode):
    def body(self, request):
        dhnio.Dprint(6, 'webcontrol.SettingsTreeDiskSpaceNode.body args=%s' % str(request.args))

        number = arg(request, 'number', None)
        suffix = arg(request, 'suffix', None)
        back = arg(request, 'back', '/'+_PAGE_CONFIG)
        message = ('', 'info')

        if number is not None and suffix is not None:
            try:
                float(number)
            except:
                message = ('wrong value. enter number.', 'failed')
                number = None
            if float(number) < 0:
                message = ('wrong value. enter positive value.', 'failed')
                number = None
            if not diskspace.SuffixIsCorrect(suffix):
                message = ('wrong suffix. use values from the drop down list only.', 'failed')
                suffix = None

        dhnio.Dprint(6, 'webcontrol.SettingsTreeDiskSpaceNode.body path=%s number=%s suffix=%s' % (self.path, str(number), str(suffix)))

        if number is not None and suffix is not None and not ReadOnly():
            newvalue = number + ' ' + suffix
            newvalue = diskspace.MakeString(number, suffix)
            self.requestModify(self.path, newvalue)
#            settings.uconfig().set(self.path, newvalue)
#            settings.uconfig().update()
#            self.update()
#            self.modified()
            #message = ('saved', 'success')
            return 'redirect ' + back

        number_current, suffix_current = diskspace.SplitString(self.value)

        src = ''
        src += '<br><form action="%s" method="post">\n' % request.path
        src += '<input type="text" name="number" value="%s" />\n' % number_current
        src += '<input type="hidden" name="back" value="%s" />\n' % arg(request, 'back', '/'+_PAGE_CONFIG)
        src += '<select name="suffix">\n'
        for suf in diskspace.SuffixLabels():
            if diskspace.SameSuffix(suf, suffix_current):
                src += '<option value="%s" selected >%s</option>\n' % (suf, suf)
            else:
                src += '<option value="%s">%s</option>\n' % (suf, suf)
        src += '</select><br><br>\n'
        src += '<input type="submit" name="submit" value=" Save " %s />&nbsp;\n' % ('disabled' if ReadOnly() else '')
        # src += '<input type="reset" name="reset" value=" Reset " /><br>\n'
        src += '</form><br>\n'
        src += html_message(message[0], message[1])
        #src += html_comment(message[0])
        return src


class SettingsPage(Page):
    pagename = _PAGE_SETTINGS
    def renderPage(self, request):
        global _SettingsTreeNodesDict
        dhnio.Dprint(6, 'webcontrol.SettingsPage.renderPage args=%s' % str(request.args))

        src = ''

        for path in settings.uconfig().default_order:
            if path.strip() == '':
                continue
#            if path not in settings.uconfig().public_options:
#                continue
            value = settings.uconfig().data.get(path, '')
            label = settings.uconfig().labels.get(path, '')
            info = settings.uconfig().infos.get(path, '')
            leafs = path.split('.')
            name = leafs[-1]
            typ = _SettingsTreeNodesDict.get(name, None)

            if len(leafs) == 1 and typ is not None:
                src += '<h3><a href="%s">%s</a></h3>\n' % (
                    _PAGE_SETTINGS+'/'+path,
                    label.capitalize())
                
        return html(request, body=src, back='/'+_PAGE_CONFIG, title='settings')

    def getChild(self, path, request):
        global _SettingsTreeNodesDict
        if path == '':
            return self
        leafs = path.split('.')
        name = leafs[-1]
        cls = _SettingsTreeNodesDict.get(name, SettingsTreeNode)
        #TODO
        if isinstance(cls, str):
            return SettingsTreeNode(path)

        return cls(path)


class SettingsListPage(Page):
    pagename = _PAGE_SETTINGS_LIST
    def renderPage(self, request):
        src = ''
        src += '<table>\n'
        for path in settings.uconfig().default_order:
            if path.strip() == '':
                continue
            if path not in settings.uconfig().public_options:
                continue
            value = settings.uconfig().data.get(path, '').replace('\n', ' ')
            label = settings.uconfig().labels.get(path, '')
            info = settings.uconfig().infos.get(path, '')
            src += '<tr>\n'
            src += '<td><a href="%s">%s</a></td>\n' % (_PAGE_SETTINGS+'/'+path, path)
            src += '<td>%s</td>\n' % label
            src += '<td>%s</td>\n' % value
            src += '</tr>\n'
            #src += html_comment('  %s    %s    %s' % (label.ljust(30), value.ljust(20)[:20], path))
            src += html_comment('  %s    %s' % (path.ljust(50), value.ljust(20)))
        src += '</table>\n'
        return html(request, body=src, back='/'+_PAGE_CONFIG, title='settings')
    
#------------------------------------------------------------------------------

