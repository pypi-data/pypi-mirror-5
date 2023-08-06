# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2012 Hewlett Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
HP3Par REST Client

.. module: HP3ParClient
.. moduleauthor: Walter A. Boring IV

:Author: Walter A. Boring IV
:Description: This is the 3PAR Client that talks to 3PAR's REST WSAPI Service.  
It provides the ability to provision 3PAR volumes, VLUNs, CPGs.

This client requires and works with 3Par InForm 3.1.2-mu2 firmware

"""

import logging
import os
import urlparse
import httplib2
import time
import pprint

from hp3parclient import http,exceptions


class HP3ParClient:
    """
    The 3PAR REST API Client

    :param api_url: The url to the WSAPI service on 3PAR 
                    ie. http://<3par server>:8080/api/v1
    :type api_url: str

    """

    PORT_MODE_TARGET=2
    PORT_MODE_INITIATOR=3
    PORT_MODE_PEER=4

    PORT_TYPE_HOST=1
    PORT_TYPE_DISK=2
    PORT_TYPE_FREE=3
    PORT_TYPE_RCIP=6
    PORT_TYPE=ISCSI=7

    PORT_PROTO_FC=1
    PORT_PROTO_ISCSI=2
    PORT_PROTO_IP=4

    PORT_STATE_READY=4
    PORT_STATE_SYNC=5
    PORT_STATE_OFFLINE=10

    HOST_EDIT_ADD=1
    HOST_EDIT_REMOVE=2
    # build contains major minor mj=3 min=01 build=422
    HP3PAR_WS_MIN_BUILD_VERSION = 30102422

    def __init__(self, api_url):
        self.api_url = api_url
        self.http = http.HTTPJSONRESTClient(self.api_url)
        api_version = None
        try :
            api_version = self.getWsApiVersion()
        except Exception as e:
            raise exceptions.UnsupportedVersion('Either, the 3PAR WS is not running or the version of the WS is invalid.')

        # Note the build contains major, minor and build
        # e.g. 30102422 is 3 01 02 422
        # therefore all we need to compare is the build
        if (api_version is None or api_version['build'] < self.HP3PAR_WS_MIN_BUILD_VERSION):
            raise exceptions.UnsupportedVersion('Invalid 3PAR WS API, requires version, 3.1.2 MU2')

    def getWsApiVersion(self):
        """
        Get the 3PAR WS API version

        :returns: None

        """
        try :
            host_url = self.api_url.split('/api')
            self.http.set_url(host_url[0])
            response, body = self.http.get('/api')
            return body
        finally:
            self.http.set_url(self.api_url)

    def debug_rest(self,flag):
        """
        This is useful for debugging requests to 3PAR

        :param flag: set to True to enable debugging
        :type flag: bool

        """
        self.http.set_debug_flag(flag)

    def login(self, username, password, optional=None):
        """
        This authenticates against the 3Par wsapi server and creates a session.

        :param username: The username
        :type username: str
        :param password: The Password
        :type password: str

        :returns: None

        """
        self.http.authenticate(username, password, optional)

    def logout(self):
        """
        This destroys the session and logs out from the 3PAR server

        :returns: None

        """
        self.http.unauthenticate()


    ##Volume methods
    def getVolumes(self):
        """ 
        Get the list of Volumes

        :returns: list of Volumes
        """
        response, body = self.http.get('/volumes')
        return body

    def getVolume(self, name):
        """ 
        Get information about a volume

        :param name: The name of the volume to find
        :type name: str

        :returns: volume
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_VOL - volume doesn't exist
        """
        response, body = self.http.get('/volumes/%s' % name)
        return body

    def createVolume(self, name, cpgName, sizeMiB, optional=None):
        """ Create a new volume

        :param name: the name of the volume
        :type name: str
        :param cpgName: the name of the destination CPG 
        :type cpgName: str
        :param sizeMiB: size in MiB for the volume
        :type sizeMiB: int
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
             'id': 12, 
             'comment': 'some comment', 
             'snapCPG' :'CPG name', 
             'ssSpcAllocWarningPct' : 12,
             'ssSpcAllocLimitPct': 22,
             'tpvv' : True,
             'usrSpcAllocWarningPct': 22,
             'usrSpcAllocLimitPct': 22,
             'expirationHours': 256,
             'retentionHours': 256 
            }

        :returns: List of Volumes

        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT - Invalid Parameter
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - TOO_LARGE - Volume size above limit
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - NO_SPACE - Not Enough space is available 
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_SV - Volume Exists already

        """
        info = {'name': name, 'cpg': cpgName, 'sizeMiB': sizeMiB}
        if optional:
            info = self._mergeDict(info, optional)

        response, body = self.http.post('/volumes', body=info)
        return body

    def deleteVolume(self, name):
        """ 
        Delete a volume
        
        :param name: the name of the volume
        :type name: str
        
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - RETAINED - Volume retention time has not expired
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - HAS_RO_CHILD - Volume has read-only child
        """
        response, body = self.http.delete('/volumes/%s' % name)
        return body


    def createSnapshot(self, name, copyOfName, optional=None): 
        """ 
        Create a snapshot of an existing Volume

        :param name: Name of the Snapshot
        :type name: str
        :param copyOfName: The volume you want to snapshot
        :type copyOfName: str
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = { 
                'id' : 12, # Specifies the ID of the volume, next by default
                'comment' : "some comment", 
                'readOnly' : True, # Read Only
                'expirationHours' : 36 # time from now to expire
                'retentionHours' : 12 # time from now to expire 
            }

        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        """
        parameters = {'name' : name}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action' : 'createSnapshot',
                'parameters' : parameters}

        response, body = self.http.post('/volumes/%s' % copyOfName, body=info)
        return body


    ##Host methods

    def getHosts(self):
        """ 
        Get information about every Host on the 3Par array

        :returns: list of Hosts
        """
        response, body = self.http.get('/hosts')
        return body

    def getHost(self, name):
        """ 
        Get information about a Host

        :param name: The name of the Host to find
        :type name: str

        :returns: host dict
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_HOST - HOST doesn't exist
        """
        response, body = self.http.get('/hosts/%s' % name)
        return body

    def createHost(self, name, iscsiNames=None, FCWwns=None, optional=None):
        """
        Create a new Host entry
        TODO: get the list of thrown exceptions 

        :param name: The name of the host
        :type name: str
        :param iscsiNames: Array if iscsi iqns
        :type name: array
        :param FCWwns: Array if Fibre Channel World Wide Names
        :type name: array
        :param optional: The optional stuff
        :type optional: dict
        
        .. code-block:: python

            optional = { 
                'domain' : 'myDomain', # Create the host in the specified domain, or default domain if unspecified.
                'forceTearDown' : False, # If True, force to tear down low-priority VLUN exports.
                'iSCSINames' : True, # Read Only
                'descriptors' : {'location' : 'earth', 'IPAddr' : '10.10.10.10', 'os': 'linux',
                              'model' : 'ex', 'contact': 'Smith', 'comment' : 'Joe's box}
 
            }
        
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_MISSING_REQUIRED - Name not specified. 
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_PARAM_CONFLICT - FCWWNs and iSCSINames are both specified.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_EXCEEDS_LENGTH - Host name, domain name, or iSCSI name is too long.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_EMPTY_STR - Input string (for domain name, iSCSI name, etc.) is empty.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_ILLEGAL_CHAR - Any error from host-name or domain-name parsing.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_TOO_MANY_WWN_OR_iSCSI - More than 1024 WWNs or iSCSI names are specified.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_WRONG_TYPE - The length of WWN is not 16. WWN specification contains non-hexadecimal digit.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_PATH - host WWN/iSCSI name already used by another host
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_HOST - host name is already used.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - NO_SPACE - No space to create host.
        """
        info = {'name' : name}

        if iscsiNames:
            iscsi = {'iSCSINames' : iscsiNames}
            info = self._mergeDict(info, iscsi)

        if FCWwns:
            fc = {'FCWWNs' : FCWwns}
            info = self._mergeDict(info, fc)

        if optional:
            info = self._mergeDict(info, optional)

        response, body = self.http.post('/hosts', body=info)
        return body
    
    def modifyHost(self, name, mod_request):
        """
        Modify an existing Host entry

        :param name: The name of the host
        :type name: str
        :param mod_request: Objects for Host Modification Request
        :type mod_request: dict
        
        .. code-block:: python

            mod_request = { 
                'newName' : 'myNewName', # New name of the host
                'pathOperation' : 1, # If adding, adds the WWN or iSCSI name to the existing host.
                'FCWWNs' : [], # One or more WWN to set for the host.
                'iSCSINames' : [], # One or more iSCSI names to set for the host.
 
            }
        
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT - Missing host name.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_PARAM_CONFLICT - Both iSCSINames & FCWWNs are specified. (lot of other possibilities)
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_ONE_REQUIRED - iSCSINames or FCWwns missing.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_ONE_REQUIRED - No path operation specified.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_BAD_ENUM_VALUE - Invalid enum value.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_MISSING_REQUIRED - Required fields missing.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_EXCEEDS_LENGTH - Host descriptor argument length, new host name, or iSCSI name is too long.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_ILLEGAL_CHAR - Error parsing host or iSCSI name.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_HOST - New host name is already used.
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_HOST - Host to be modified does not exist.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_TOO_MANY_WWN_OR_iSCSI - More than 1024 WWNs or iSCSI names are specified.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_WRONG_TYPE - Input value is of the wrong type.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_PATH - WWN or iSCSI name is already claimed by other host.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_BAD_LENGTH - CHAP hex secret length is not 16 bytes, or chap ASCII secret length is not 12 to 16 characters.
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NO_INITIATOR_CHAP - Setting target CHAP without initiator CHAP.
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_CHAP - Remove non-existing CHAP.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - NON_UNIQUE_CHAP_SECRET - CHAP secret is not unique.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXPORTED_VLUN - Setting persona with active export; remove a host path on an active export.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - NON_EXISTENT_PATH - Remove a non-existing path.
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - LUN_HOSTPERSONA_CONFLICT - LUN number and persona capability conflict.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_DUP_PATH - Duplicate path specified.
        """
        response, body = self.http.put('/hosts/%s' % name, body=mod_request)
        return body    

    def deleteHost(self, name):
        """
        Delete a Host

        :param name: Host Name
        :type name: str

        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_HOST - HOST Not Found 
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` -  IN_USE - The HOST Cannot be removed because it's in use.
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied

        """
        reponse, body = self.http.delete('/hosts/%s' % name)

    def getHostVLUNs(self, hostName):
        """
        Get all of the VLUNs on a specific Host

        :param name: Host name
        :type name: str

        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_HOST - HOST Not Found 
        """

        host = self.getHost(hostName)
        allVLUNs = self.getVLUNs()

        vluns = []

        if allVLUNs:
            for vlun in allVLUNs['members']:
                if vlun['hostname'] == hostName:
                    vluns.append(vlun)
                    
        if len(vluns) < 1 :
            raise exceptions.HTTPNotFound({'code':'NON_EXISTENT_HOST', 'desc': 'HOST Not Found'})
           
        return vluns


    ## PORT Methods
    def getPorts(self):
        """
        Get the list of ports on the 3Par

        :returns: list of Ports
        """
        response, body = self.http.get('/ports')
        return body


    def _getProtocolPorts(self, protocol, state=None):
        return_ports = []
        ports = self.getPorts()
        if ports:
            for port in ports['members']:
                if port['protocol'] == protocol:
                    if state is None:
                        return_ports.append(port)
                    elif port['linkState'] == state:
                        return_ports.append(port)
                        
        return return_ports
            
    def getFCPorts(self, state=None):
        """ 
        Get a list of Fibre Channel Ports

        :returns: list of Fibre Channel Ports
        """
        return self._getProtocolPorts(1, state)

    def getiSCSIPorts(self, state=None):
        """ 
        Get a list of iSCSI Ports

        :returns: list of iSCSI Ports
        """
        return self._getProtocolPorts(2, state)

    def getIPPorts(self, state=None):
        """ 
        Get a list of IP Ports

        :returns: list of IP Ports
        """
        return self._getProtocolPorts(4, state)


    ##CPG methods
    def getCPGs(self):
        """ 
        Get entire list of CPGs

        :returns: list of cpgs
        """
        response, body = self.http.get('/cpgs')
        return body


    def getCPG(self, name):
        """ 
        Get information about a CPG

        :param name: The name of the CPG to find
        :type name: str

        :returns: cpg dict
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` -  NON_EXISTENT_CPG - CPG doesn't exist
        """
        response, body = self.http.get('/cpgs/%s' % name)
        return body

    def createCPG(self, name, optional=None):
        """ 
        Create a CPG

        :param name: CPG Name
        :type name: str
        :param optional: Optional parameters
        :type optional: dict

        .. code-block:: python

            optional = {
                'growthIncrementMiB' : 100,
                'growthLimitMiB' : 1024,
                'usedLDWarningAlertMiB' : 200,
                'domain' : 'MyDomain',
                'LDLayout' : {'RAIDType' : 1, 'setSize' : 100, 'HA': 0,
                              'chunkletPosPref' : 2, 'diskPatterns': []}
            }

        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT Invalid URI Syntax 
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - NON_EXISTENT_DOMAIN - Domain doesn't exist
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - NO_SPACE - Not Enough space is available.
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - BAD_CPG_PATTERN  A Pattern in a CPG specifies illegal values
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        :raises: :class:`~hp3parclient.exceptions.HTTPConflict` - EXISTENT_CPG - CPG Exists already 

        """
        info = {'name': name}
        if optional:
            info = self._mergeDict(info, optional)

        reponse, body = self.http.post('/cpgs', body=info)
        return body
    
    def deleteCPG(self, name):
        """
        Delete a CPG

        :param name: CPG Name
        :type name: str

        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_CPG - CPG Not Found 
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` -  IN_USE - The CPG Cannot be removed because it's in use.
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied

        """
        reponse, body = self.http.delete('/cpgs/%s' % name)



    ## VLUN methods

    ## Virtual-LUN, or VLUN, is a pairing between a virtual volume and a
    ## logical unit number (LUN), expressed as either a VLUN template or an active
    ## VLUN

    ## A VLUN template sets up an association between a virtual volume and a
    ## LUN-host, LUN-port, or LUN-host-port combination by establishing the export
    ## rule, or the manner in which the Volume is exported. 


    def getVLUNs(self):
        """ 
        Get VLUNs
        
        :returns: Array of VLUNs
        """
        reponse, body = self.http.get('/vluns')
        return body

    def getVLUN(self, volumeName):
        """ 
        Get information about a VLUN

        :param volumeName: The volume name of the VLUN to find
        :type name: str

        :returns: VLUN

        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` -  NON_EXISTENT_VLUN - VLUN doesn't exist

        """
        vluns = self.getVLUNs()
        if vluns:
            for vlun in vluns['members']:
                if vlun['volumeName'] == volumeName:
                    return vlun

        raise exceptions.HTTPNotFound({'code':'NON_EXISTENT_VLUN', 'desc': "VLUN '%s' was not found" % volumeName})

    def createVLUN(self, volumeName, lun=None, hostname=None, portPos=None, noVcn=None,
                   overrideLowerPriority=None, auto=False):
        """ 
        Create a new VLUN

        When creating a VLUN, the volumeName is required. The lun member is
        not required if auto is set to True.
        Either hostname or portPos (or both in the case of matched sets) is
        also required.  The noVcn and overrideLowerPriority members are
        optional.

        :param volumeName: Name of the volume to be exported
        :type volumeName: str
        :param lun: The new LUN id
        :type lun: int
        :param hostname:  Name of the host which the volume is to be exported.
        :type hostname: str
        :param portPos: 'portPos' (dict) - System port of VLUN exported to. It includes node number, slot number, and card port number
        :type portPos: dict
        :param noVcn: A VLUN change notification (VCN) not be issued after export (-novcn). Default: False.
        :type noVcn: bool
        :param overrideLowerPriority: Existing lower priority VLUNs will
                be overridden (-ovrd). Use only if hostname member exists. Default:
                False.
        :type overrideLowerPriority: bool

        :returns: the location of the VLUN

        """
        info = {'volumeName': volumeName}
        
        if lun:
            info['lun'] = lun

        if hostname:
            info['hostname'] = hostname

        if portPos:
            info['portPos'] = portPos

        if noVcn:
            info['noVcn'] = noVcn

        if overrideLowerPriority:
            info['overrideLowerPriority'] = overrideLowerPriority
            
        if auto:
            info['autoLun'] = True
            info['maxAutoLun'] = 0
            info['lun'] = 0

        headers, body = self.http.post('/vluns', body=info)
        if headers:
            location = headers['location'].replace('/api/v1/vluns/', '')
            return location
        else:
            return None
        
    def deleteVLUN(self, volumeName, lunID, hostname=None, port=None):
        """ 
        Delete a VLUN
        
        :param volumeName: the volume name of the VLUN
        :type name: str
        :param lunID: The LUN ID 
        :type lunID: int
        :param hostname: Name of the host which the volume is exported. For VLUN of port type,the value is empty
        :type hostname: str
        :param port: Specifies the system port of the VLUN export.  It includes the system node number, PCI bus slot number, and card port number on the FC card in the format <node>:<slot>:<port>
        :type port: str


        
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_MISSING_REQUIRED - Incomplete VLUN info. Missing volumeName or lun, or both hostname and port. 
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_PORT_SELECTION - Specified port is invalid. 
        :raises: :class:`~hp3parclient.exceptions.HTTPBadRequest` - INV_INPUT_EXCEEDS_RANGE - The LUN specified exceeds expected range.
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_HOST - The host does not exist
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_VLUN - The VLUN does not exist
        :raises: :class:`~hp3parclient.exceptions.HTTPNotFound` - NON_EXISTENT_PORT - The port does not exist
        :raises: :class:`~hp3parclient.exceptions.HTTPForbidden` - PERM_DENIED - Permission denied
        """

        vlun = "%s,%s" % (volumeName, lunID)

        if hostname:
            vlun += ",%s" % hostname

        if port:
            vlun += ",%s:%s:%s" % (port['node'], port['slot'], port['cardPort'])


        response, body = self.http.delete('/vluns/%s' % vlun)



    def _mergeDict(self, dict1, dict2):
        """
        Safely merge 2 dictionaries together
        
        :param dict1: The first dictionary
        :type dict1: dict
        :param dict2: The second dictionary
        :type dict2: dict

        :returns: dict

        :raises Exception: dict1, dict2 is not a dictionary
        """
        if type(dict1) is not dict:
            raise Exception("dict1 is not a dictionary")
        if type(dict2) is not dict:
            raise Exception("dict2 is not a dictionary")
        
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3

