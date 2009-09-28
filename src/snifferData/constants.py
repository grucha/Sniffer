# -*- coding: utf-8 -*-
"""
ZigBee constants.
"""

# ========== MAC constants: ======================
#frame types:
TYPE_BCN = 'Beacon'
TYPE_DATA = 'Data'
TYPE_ACK = 'Ack.'
TYPE_CMD = 'Command'
FRAME_TYPE = {'000': TYPE_BCN, 
			'001': TYPE_DATA, 
			'010': TYPE_ACK, 
			'011': TYPE_CMD}

#addressing modes:
MODE_NONE = 'PAN-ID and address field are not present'
MODE_RESERVED = 'Reserved'
MODE_16 = '16-bit addressing'
MODE_64 = '64-bit addressing'
ADDR_MODE = {'00': MODE_NONE, 
			'01': MODE_RESERVED,
			'10': MODE_16, 
			'11': MODE_64}

#command types:
CMD_ASS_REQ = 'Association request'
CMD_ASS_RESP = 'Association response'
CMD_DIS_NOT = 'Disassociation notification'
CMD_DAT_REQ = 'Data request'
CMD_PAN_ID_CON = 'PAN ID conflict notification'
CMD_ORP_NOT = 'Orphan notification'
CMD_BCN_REQ = 'Beacon request'
CMD_CRD_REL = 'Coordinator realignment'
CMD_GTS_REQ = 'GTS request'
COMMAND_TYPE = {'0x1': CMD_ASS_REQ,
				'0x2': CMD_ASS_RESP,
				'0x3': CMD_DIS_NOT,
				'0x4': CMD_DAT_REQ,
				'0x5': CMD_PAN_ID_CON,
				'0x6': CMD_ORP_NOT,
				'0x7': CMD_BCN_REQ,
				'0x8': CMD_CRD_REL,
				'0x9': CMD_GTS_REQ}