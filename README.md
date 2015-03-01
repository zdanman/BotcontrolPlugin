# BotcontrolPlugin
BigBrotherBot - Bot Control Plugin for Insurgency

Known Issues:
- EVT_CLIENT_DISCONNECT and KICK events are not getting fired for bots currently so list is simply clear on game exit event

Current commands:

'botkick' or 'kb'
kicks a bot by name
!kb [name]

'botkickall' or 'kba'
kicks all bots on record and clears list

'botkickteam' or 'kbt'
kicks a bot from certain team
!kbt ['ins' or 'sec']

'botadd' or 'ab'
adds one or more bots
!ab [number, optional]

'botlist' or 'bl'
list current bots on record and their user ids for use with kickid or sm_kick commands

'botclear' or 'bclear'
clears bot list - for debugging purposes only
