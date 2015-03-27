# BotcontrolPlugin

0.4 Notes

BigBrotherBot - Bot Control Plugin for Insurgency

Change Log:
- added delay between rcon commands so as not to overload server
- added number param to the !kbt command so you can multiple bots with one command.

Known Anomalies:
- EVT_CLIENT_DISCONNECT and KICK events are not getting fired for bots currently so list is simply cleared on game exit event
- When the plugin first starts, it may take a minute or two of playing before all bots become registered with the plugin

Current commands:

'botkick' or 'kb'
kicks a bot by name
!kb [name]

'botkickall' or 'kba'
kicks all bots on record and clears list

'botkickteam' or 'kbt'
kicks a bot from certain team
!kbt ['ins' or 'sec'] [number, optional]

'botadd' or 'ab'
adds one or more bots
!ab [number, optional]

'botlist' or 'bl'
list current bots on record and their user ids for use with kickid or sm_kick commands

'botclear' or 'bclear'
clears bot list - for debugging purposes only
