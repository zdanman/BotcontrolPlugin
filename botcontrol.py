#
# BotControl plugin for Insurgency - BigBrotherBot (B3) (www.bigbrotherbot.net)
# (c) 2015 - Dan Caldwell (cidclan.net / acedev.net)
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#

__author__ = 'Dan Caldwell'
__version__ = '0.3.5'

import b3
import b3.cron
import b3.plugin
import b3.events
import b3.clients
import b3.functions
import json

import re
import StringIO
import string
import time
import random
import copy

from b3.functions import sanitizeMe
from ConfigParser import NoOptionError

########################################################################################################################
##                                                                                                                    ##
##  MAIN PLUGIN XLRSTATS - HANDLES ALL CORE STATISTICS FUNCTIONALITY                                                  ##
##                                                                                                                    ##
########################################################################################################################

class BotcontrolPlugin(b3.plugin.Plugin):

    min_level_cmd = 100
    _botList = {}

    ####################################################################################################################
    #                                                                                                                  #
    #    STARTUP                                                                                                       #
    #                                                                                                                  #
    ####################################################################################################################

    def onLoadConfig(self):
        """
        Load config
        """
        self.debug('onLoadConfig called')
        try:
            self._min_level_cmd = self.config.getint('settings', 'min_level_cmd')
        except:
            self._min_level_vote = 100

        # get the plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('could not find admin plugin')
        else:
            self._adminPlugin.registerCommand(self, 'botkick', self._min_level_cmd, self.cmd_KickBot, 'kb')
            self._adminPlugin.registerCommand(self, 'botkickall', self._min_level_cmd, self.cmd_KickBotAll, 'kba')
            self._adminPlugin.registerCommand(self, 'botkickteam', self._min_level_cmd, self.cmd_KickBotTeam, 'kbt')
            self._adminPlugin.registerCommand(self, 'botadd', self._min_level_cmd, self.cmd_AddBot, 'ab')
            self._adminPlugin.registerCommand(self, 'botlist', self._min_level_cmd, self.cmd_BotStatus, 'bl')
            self._adminPlugin.registerCommand(self, 'botclear', self._min_level_cmd, self.cmd_BotClearList, 'bclear')
        return

    def onStartup(self):
        """
        Initialize plugin.
        """
        self.debug('onStartup called')

        self.registerEvent(self.console.getEventID('EVT_CLIENT_CONNECT'), self.onConnect)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_DISCONNECT'), self.onDisconnect)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_KICK'), self.onKick)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_JOIN'), self.onJoin)
        self.registerEvent(self.console.getEventID('EVT_GAME_EXIT'), self.onExit)
        return

    def onExit(self, event):
        """
        Do clean up...
        """
        self.debug('BotControlEvent: onExit called')
        # clear the list - onDisconnect doesnt seem to be working for bots
        # do this until this is fixed
        self.debug('clearing bot list')
        self._botList.clear()
        return


    def cmd_BotClearList(self, data, client, cmd=None):
        """
        Clear bot list (usually for debugging purposes)
        """
        self.debug('BotControlEvent: BotClearList command called')
        self.debug('clearing bot list')
        self._botList.clear()
        return


    def onKick(self, event):
        """
        Handle a bot kick
        """
        self.debug('BotControlEvent: onKick called')
        onDisconnect(self, event)
        return

    def onDisconnect(self, event):
        """
        Handle a client leaving the game.  whether kick or disconnect
        """
        self.debug('BotControlEvent: onDisconnect called')
        if event.client is None:
            return
        self.verbose('outputing event...')
        self.verbose('event = %s', event)
        self.verbose(vars(event.client))
        if event.client.bot:
            self.verbose('bot noticed. searching for bot (guid = %s) in list...', event.client.guid)
            if event.client.guid in self._botList:
                self.verbose('bot found - removing...')
                del self._botList[event.client.guid]
            else:
                self.debug('Notice! Bot NOT existing in list! ')
        return

    def onConnect(self, event):
        """
        Handle a client joining the game.
        """
        self.debug('BotControlEvent: onConnect called')
        if event.client is None:
            return
        self.verbose('outputing event...')
        self.verbose('event = %s', event)
        self.verbose(vars(event.client))
        if event.client.bot:
            self.verbose('bot found and registered (guid = %s, name = %s)', event.client.guid, event.client.name)
            self._botList[event.client.guid] = event.client
        return

    def onJoin(self, event):
        """
        Handle a client joining the game.
        """
        self.debug('BotControlEvent: onJoin called')
        if event.client is None:
            return
        self.verbose('outputing event...')
        self.verbose('event = %s', event)
        self.verbose(vars(event.client))
        if event.client.bot:
            self.verbose('bot found and registered (guid = %s, name = %s)', event.client.guid, event.client.name)
            self._botList[event.client.guid] = event.client
        return

    def cmd_AddBot(self, data, client, cmd=None):
        """
        Add one or more bots to a team
        """
        self.debug('BotControlEvent: AddBot command called')

        _num = 1
        if data is not None:
            try:
                _num = int(data)
            except:
                _num = 1

        if _num < 1:
            _num = 1
        if _num > 20:
            _num = 20

        self.console.say('Adding %s bot(s)...' % _num)
        self.console.output.write('ins_bot_add %s' % _num)

        return


    def cmd_KickBotTeam(self, data, client, cmd=None):
        """
        Kick a bot from a team
        """
        # b3.TEAM_RED = 2 (security), b3.TEAM_BLUE = 3 (insurgents)

        self.debug('BotControlEvent: KickBotTeam command called')

        if 'ins' in data:
            client.message('issuing bot kick from Insurgents')
            self.console.output.write('ins_bot_kick_t2')
        elif 'sec' in data:
            client.message('issuing bot kick from Security')
            self.console.output.write('ins_bot_kick_t1')
        else:
            client.message('No team specified')
            client.message('use sec or ins')
            self.debug('No Team Selected!')
            return

        return

    def cmd_KickBot(self, data, client, cmd=None):
        """
        Kick a bot
        """
        self.debug('BotControlEvent: KickBot command called')

        if len(data) < 3:
            client.message('failed. name not long enough.')
            return

        self.verbose('Searching for bot under name:%s;', data)

        #search for bot
        _found = None
        for k,b in self._botList.iteritems():
            self.verbose('%s - %s;', k, b)
            if data.lower() in b.name.lower():
                self.verbose('Bot found (%s);  Kicking...', b)
                g = b.guid.lower()
                g = g.replace('bot', '')
                client.message('Kicking bot (%s)...' % b.name)
                self.console.output.write('kickid %s' % g)
                _found = k
                break

        if _found is not None:
            del self._botList[_found]
        else:
            self.debug('Notice! No bots found by that name!')
            client.message('No bots found by that name (or list has not been updated yet)')

        return

    def cmd_KickBotAll(self, data, client, cmd=None):
        """
        Kick all bots
        """
        self.debug('BotControlEvent: KickBotAll command called')

        for k,b in self._botList.iteritems():
            self.verbose('%s - %s;', k, b)
            g = b.guid.lower()
            g = g.replace('bot', '')
            client.message('Kicking bot (%s)...' % b.name)
            self.console.output.write('kickid %s' % g)

        self._botList.clear()
        
        self.console.say('All registered bots were kicked...')

        return

    def cmd_BotStatus(self, data, client, cmd=None):
        """
        List bots with their ids
        """
        self.debug('BotControlEvent: BotStatus command called')

        _count = 0
        for k,b in self._botList.iteritems():
            g = b.guid.lower()
            g = g.replace('bot', '')
            client.message( "%s (ID:%s)" % (b.name, g) )
            _count = _count + 1
        client.message( "%s bots total" % _count)

        return
