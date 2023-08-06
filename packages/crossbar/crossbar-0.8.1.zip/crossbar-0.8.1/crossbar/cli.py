###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License, version 3,
##  as published by the Free Software Foundation.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################


import sys, json
from pprint import pprint

import twisted
import autobahn

from twisted.python import log, usage
from twisted.internet import reactor
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol


class CrossbarCLIOptions(usage.Options):

   COMMANDS = ['connect',
               'config',
               'restart',
               'log',
               'status',
               'watch',
               'scratchdb',
               'scratchweb',
               'wiretap']

   optParameters = [
      ['command', 'c', None, 'Command, one of: %s [required]' % ', '.join(COMMANDS)],
      ['wsuri', 'w', None, 'Crossbar Admin WebSocket URI, i.e. "ws://192.168.1.128:9000".'],
      ['password', 'p', None, 'Crossbar Admin password.'],
      ['limit', 'l', 0, 'Limit number of log lines or records returned.'],
      ['spec', 's', None, 'Command/config spec file.'],
      ['ident', 'i', None, 'WAMP session ID, i.e. for wiretap mode.'],
   ]

   optFlags = [
      ['json', 'j', 'Output everything in JSON.'],
      ['debug', 'd', 'Enable debug output.']
   ]

   def postOptions(self):

      if not self['command']:
         raise usage.UsageError, "A command must be specified to run!"

      if not self['wsuri']:
         raise usage.UsageError, "Crossbar Admin WebSocket URI required!"
      if not self['password']:
         raise usage.UsageError, "Crossbar Admin password required!"

      if self['command'] in ['wiretap']:
         if not self['ident']:
            raise usage.UsageError, "WAMP session ID required for command '%s'." % self['command']

      if self['command'] in ['config']:
         if not self['spec']:
            raise usage.UsageError, "Command/config spec file required for command '%s'." % self['command']



class CrossbarCLIProtocol(WampCraClientProtocol):

   def connectionMade(self):
      if not self.factory.options['json']:
         print "connected."

      WampCraClientProtocol.connectionMade(self)


   def onSessionOpen(self):
      if not self.factory.options['json']:
         print "session opened."

      d = self.authenticate(authKey = self.factory.user,
                            authSecret = self.factory.password)
      d.addCallbacks(self.onAuthSuccess, self.onAuthError)


   def onClose(self, wasClean, code, reason):
      try:
         reactor.stop()
      except:
         pass


   def onAuthSuccess(self, permissions):
      if not self.factory.options['json']:
         print "authenticated."
         print

      self.prefix("api", "http://crossbar.io/api#");
      self.prefix("error", "http://crossbar.io/error#");
      self.prefix("event", "http://crossbar.io/event#");
      self.prefix("wiretap", "http://crossbar.io/event/wiretap#");

      CMDS = {'restart': self.cmd_restart,
              'log': self.cmd_log,
              'status': self.cmd_status,
              'watch': self.cmd_watch,
              'config': self.cmd_config,
              'scratchdb': self.cmd_scratchdb,
              'scratchweb': self.cmd_scratchweb,
              'connect': self.cmd_connect,
              'wiretap': self.cmd_wiretap}

      if CMDS.has_key(self.factory.command):
         CMDS[self.factory.command]()
      else:
         raise Exception("unknown command '%s'" % self.factory.command)


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      if not self.factory.options['json']:
         print "Authentication Error!", uri, desc, details
      self.sendClose()


   ## WATCH Command
   ##

   BRIDGENAME = {'ora': 'Oracle',
                 'pg': 'PostgreSQL',
                 'hana': 'SAP HANA',
                 'rest': 'REST',
                 'extdirect': 'Ext.Direct'}

   REMOTERSTATMAP = {'oraremoterstat': 'ora',
                     'pgremoterstat': 'pg',
                     'hanaremoterstat': 'hana',
                     'restremoterstat': 'rest',
                     'extdirectremoterstat': 'extdirect'}

   PUSHERSTATMAP = {'orapusherstat': 'ora',
                    'pgpusherstat': 'pg',
                    'hanapusherstat': 'hana',
                    'restpusherstat': 'rest'}

   def _onremoterstat(self, topic, event):
      z = topic.split('-')[-1]
      for e in event:
         if e['uri'] is None:
            m = CrossbarCLIProtocol.BRIDGENAME[CrossbarCLIProtocol.REMOTERSTATMAP[z]] + " Remoter"
            print m.ljust(20), e

   def _onpusherstat(self, topic, event):
      z = topic.split('-')[-1]
      for e in event:
         if e['uri'] is None:
            m = CrossbarCLIProtocol.BRIDGENAME[CrossbarCLIProtocol.PUSHERSTATMAP[z]] + " Pusher"
            print m.ljust(20), e

   def cmd_watch(self):
      for k in CrossbarCLIProtocol.REMOTERSTATMAP:
         self.subscribe("event:on-%s" % k, self._onremoterstat)
      for k in CrossbarCLIProtocol.PUSHERSTATMAP:
         self.subscribe("event:on-%s" % k, self._onpusherstat)


   ## STATUS Command
   ##

   @inlineCallbacks
   def cmd_status(self):
      res = {}
      for t in ['remoter', 'pusher']:
         res[t] = {}
         for s in ['ora', 'pg', 'hana', 'rest']:
            res[t][s] = {}
            try:
               rr = yield self.call("api:get-%s%sstats" % (s, t))
               for r in rr:
                  if r['uri'] is None:
                     for k in r:
                        if k != 'uri':
                           res[t][s][k] = r[k]
            except Exception, e:
               pass
      if self.factory.options['json']:
         print json.dumps(res)
      else:
         print "Crossbar Pusher and Remoter Statistics"
         print "-" * 80
         print
         pprint(res)
      self.sendClose()


   ## CONNECT Command
   ##

   def cmd_connect(self):
      print "Crossbar is alive!"
      self.factory.reconnect = False
      self.sendClose()


   ## RESTART Command
   ##

   @inlineCallbacks
   def cmd_restart(self):
      if not self.factory.options['json']:
         print "restarting Crossbar .."

      res = yield self.call("api:restart")


   ## SCRATCHDB Command
   ##

   @inlineCallbacks
   def cmd_scratchdb(self, dorestart = False):
      if not self.factory.options['json']:
         if dorestart:
            print "scratching Crossbar service database and immediate restart .."
         else:
            print "scratching Crossbar service database .."

      res = yield self.call("api:scratch-database", dorestart)

      print "scratched service database"
      if not dorestart:
         self.sendClose()


   ## SCRATCHWEB Command
   ##

   @inlineCallbacks
   def cmd_scratchweb(self, doinit = True):
      if not self.factory.options['json']:
         print "scratching Crossbar Web directory .."

      res = yield self.call("api:scratch-webdir", doinit)
      if doinit:
         print "scratched Web directory and copied %d files (%d bytes)" % (res[0], res[1])
      else:
         print "scratched Web directory"

      self.sendClose()


   ## LOG Command
   ##

   def _printlog(self, logobj):
      if self.factory.options['json']:
         print json.dumps(logobj)
      else:
         lineno, timestamp, logclass, logmodule, message = logobj
         print str(lineno).zfill(6), timestamp, logclass.ljust(7), (logmodule + ": " if logmodule.strip() != "-" else "") + message


   def _onlog(self, topic, event):
      self._printlog(event)


   @inlineCallbacks
   def cmd_log(self):
      try:
         limit = int(self.factory.options['limit'])
      except:
         limit = 0
      self.subscribe("event:on-log", self._onlog)
      res = yield self.call("api:get-log", limit)
      for l in res:
         self._printlog(l)


   ## WIRETAP Command
   ##

   def _onwiretap(self, topic, event):
      print topic, event


   @inlineCallbacks
   def cmd_wiretap(self):
      sessionid = self.factory.options['ident']
      topic = "wiretap:%s" % sessionid
      self.subscribe(topic, self._onwiretap)
      r = yield self.call("api:set-wiretap-mode", sessionid, True)
      print "listening on", topic


   ## CONFIG Command
   ##

   @inlineCallbacks
   def cmd_config(self):

      if self.factory.config.has_key('settings'):
         r = yield self.call("api:modify-config", self.factory.config['settings'])
         pprint(r)

      if self.factory.config.has_key('appcreds'):
         appcreds = yield self.call("api:get-appcreds")
         for ac in appcreds:
            print "dropping application credential", ac['uri']
            r = yield self.call("api:delete-appcred", ac['uri'], True)
         for id, ac in self.factory.config['appcreds'].items():
            r = yield self.call("api:create-appcred", ac)
            self.factory.config['appcreds'][id] = r
            print "application credential created:"
            pprint(r)

      if self.factory.config.has_key('clientperms'):
         clientperms = yield self.call("api:get-clientperms")
         for cp in clientperms:
            print "dropping client permission ", cp['uri']
            r = yield self.call("api:delete-clientperm", cp['uri'])
         for id, cp in self.factory.config['clientperms'].items():
            if cp["require-appcred-uri"] is not None:
               k = cp["require-appcred-uri"]
               cp["require-appcred-uri"] = self.factory.config['appcreds'][k]['uri']
            r = yield self.call("api:create-clientperm", cp)
            self.factory.config['clientperms'][id] = r
            print "client permission created:"
            pprint(r)

      if self.factory.config.has_key('postrules'):
         postrules = yield self.call("api:get-postrules")
         for pr in postrules:
            print "dropping post rule", pr['uri']
            r = yield self.call("api:delete-postrule", pr['uri'])
         for id, pr in self.factory.config['postrules'].items():
            if pr["require-appcred-uri"] is not None:
               k = pr["require-appcred-uri"]
               pr["require-appcred-uri"] = self.factory.config['appcreds'][k]['uri']
            r = yield self.call("api:create-postrule", pr)
            self.factory.config['postrules'][id] = r
            print "post rule created:"
            pprint(r)

      if self.factory.config.has_key('extdirectremotes'):
         extdirectremotes = yield self.call("api:get-extdirectremotes")
         for er in extdirectremotes:
            print "dropping ext.direct remote", er['uri']
            r = yield self.call("api:delete-extdirectremote", er['uri'])
         for id, er in self.factory.config['extdirectremotes'].items():
            if er["require-appcred-uri"] is not None:
               k = er["require-appcred-uri"]
               er["require-appcred-uri"] = self.factory.config['appcreds'][k]['uri']
            r = yield self.call("api:create-extdirectremote", er)
            self.factory.config['extdirectremotes'][id] = r
            print "ext.direct remote created:"
            pprint(r)

      if self.factory.config.has_key('oraconnects'):
         oraconnects = yield self.call("api:get-oraconnects")
         for oc in oraconnects:
            print "dropping Oracle connect", oc['uri']
            r = yield self.call("api:delete-oraconnect", oc['uri'], True)
         for id, oc in self.factory.config['oraconnects'].items():
            r = yield self.call("api:create-oraconnect", oc)
            self.factory.config['oraconnects'][id] = r
            print "Oracle connect created:"
            pprint(r)

      if self.factory.config.has_key('orapushrules'):
         orapushrules = yield self.call("api:get-orapushrules")
         for op in orapushrules:
            print "dropping Oracle publication rule", op['uri']
            r = yield self.call("api:delete-orapushrule", op['uri'])
         for id, op in self.factory.config['orapushrules'].items():
            if op["oraconnect-uri"] is not None:
               k = op["oraconnect-uri"]
               op["oraconnect-uri"] = self.factory.config['oraconnects'][k]['uri']
            r = yield self.call("api:create-orapushrule", op)
            self.factory.config['orapushrules'][id] = r
            print "Oracle publication rule created:"
            pprint(r)

      if self.factory.config.has_key('oraremotes'):
         oraremotes = yield self.call("api:get-oraremotes")
         for om in oraremotes:
            print "dropping Oracle remote", om['uri']
            r = yield self.call("api:delete-oraremote", om['uri'])
         for id, om in self.factory.config['oraremotes'].items():
            if om["oraconnect-uri"] is not None:
               k = om["oraconnect-uri"]
               om["oraconnect-uri"] = self.factory.config['oraconnects'][k]['uri']
            if om["require-appcred-uri"] is not None:
               k = om["require-appcred-uri"]
               om["require-appcred-uri"] = self.factory.config['appcreds'][k]['uri']
            r = yield self.call("api:create-oraremote", om)
            self.factory.config['oraremotes'][id] = r
            print "Oracle remote created:"
            pprint(r)

      self.sendClose()



class CrossbarCLIFactory(WampClientFactory):

   protocol = CrossbarCLIProtocol

   def __init__(self, options, debug):
      self.options = options
      self.user = "admin"
      self.password = options["password"]
      self.command = options["command"]
      if self.command == 'connect':
         self.reconnect = True
      else:
         self.reconnect = False
      if options["spec"]:
         self.config = json.loads(open(options["spec"]).read())
      else:
         self.config = None
      WampClientFactory.__init__(self, options["wsuri"], debugWamp = debug)

   def startedConnecting(self, connector):
      if not self.options['json']:
         print 'connecting ..'

   #def buildProtocol(self, addr):
   #    print 'Connected.'
   #    return CrossbarCLIProtocol()

   def clientConnectionLost(self, connector, reason):
      if not self.options['json']:
         print
         print 'lost connection [%s]' % reason.value
      if self.reconnect:
         connector.connect()
      else:
         try:
            reactor.stop()
         except:
            pass

   def clientConnectionFailed(self, connector, reason):
      if not self.options['json']:
         print
         print 'connection failed [%s]' % reason.value
      if self.reconnect:
         connector.connect()
      else:
         try:
            reactor.stop()
         except:
            pass



def run():

   o = CrossbarCLIOptions()
   try:
      o.parseOptions()
   except usage.UsageError, errortext:
      print '%s %s\n' % (sys.argv[0], errortext)
      print 'Try %s --help for usage details\n' % sys.argv[0]
      print
      print "Twisted %s" % twisted.__version__
      print "AutobahnPython %s" % autobahn.version
      sys.exit(1)

   debug = o.opts['debug']
   if debug:
      log.startLogging(sys.stdout)

   if not o['json']:
      print "Using Twisted reactor class %s" % str(reactor.__class__)

   factory = CrossbarCLIFactory(o, debug)
   connectWS(factory)
   reactor.run()



if __name__ == '__main__':
   run()
