#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


########################################
############ GENERATED CODE ############
########################################

'''Generated at: 2013-01-13 19:52:39.094040'''

from ovirtsdk.xml import params
from ovirtsdk.utils.urlhelper import UrlHelper
from ovirtsdk.utils.filterhelper import FilterHelper
from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.utils.searchhelper import SearchHelper
from ovirtsdk.infrastructure.common import Base
from ovirtsdk.infrastructure.context import context
from ovirtsdk.infrastructure.errors import MissingParametersError
from ovirtsdk.infrastructure.errors import DisconnectedError
from ovirtsdk.infrastructure.errors import RequestError


class Capabilities(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError


    def get(self, id=None, **kwargs):
        '''
        [@param id: string (the id of the entity)]
        [@param **kwargs: dict (property based filtering)]

        @return VersionCaps:
        '''

        url = '/api/capabilities'

        if id:
            try :
                return VersionCaps(self.__getProxy().get(url=UrlHelper.append(url, id)),
                                   self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif kwargs:
            result = self.__getProxy().get(url=url).version
            return VersionCaps(FilterHelper.getItem(FilterHelper.filter(result, kwargs)),
                               self.context)
        else:
            raise MissingParametersError(['id', 'kwargs'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return [VersionCaps]:
        '''

        url='/api/capabilities'

        result = self.__getProxy().get(url=url).version
        return ParseHelper.toCollection(VersionCaps,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)
class Cluster(params.Cluster, Base):
    def __init__(self, cluster, context):
        Base.__init__(self, context)
        self.superclass = cluster

        self.permissions = ClusterPermissions(self, context)
        self.glustervolumes = ClusterGlusterVolumes(self, context)
        self.networks = ClusterNetworks(self, context)

    def __new__(cls, cluster, context):
        if cluster is None: return None
        obj = object.__new__(cls)
        obj.__init__(cluster, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/clusters/{cluster:id}',
                                {'{cluster:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param cluster.name: string]
        [@param cluster.description: string]
        [@param cluster.cpu.id: string]
        [@param cluster.version.major: int]
        [@param cluster.version.minor: int]
        [@param cluster.memory_policy.overcommit.percent: double]
        [@param cluster.memory_policy.transparent_hugepages.enabled: boolean]
        [@param cluster.scheduling_policy.policy: string]
        [@param cluster.scheduling_policy.thresholds.low: int]
        [@param cluster.scheduling_policy.thresholds.high: int]
        [@param cluster.scheduling_policy.thresholds.duration: int]
        [@param cluster.error_handling.on_error: string]
        [@param cluster.virt_service: boolean]
        [@param cluster.gluster_service: boolean]
        [@param cluster.threads_as_cores: boolean]
        [@param correlation_id: any string]

        @return Cluster:
        '''

        url = '/api/clusters/{cluster:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{cluster:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Cluster(result, self.context)

class ClusterGlusterVolume(params.GlusterVolume, Base):
    def __init__(self, cluster, glustervolume, context):
        Base.__init__(self, context)
        self.parentclass = cluster
        self.superclass  =  glustervolume

        self.bricks = ClusterGlusterVolumeBricks(self, context)

    def __new__(cls, cluster, glustervolume, context):
        if glustervolume is None: return None
        obj = object.__new__(cls)
        obj.__init__(cluster, glustervolume, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                   '{glustervolume:id}': self.get_id()}),
                                       headers={'Content-type':None})

    def rebalance(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.fix_layout: boolean]
        [@param action.force: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/rebalance'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def resetalloptions(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/resetalloptions'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def resetoption(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.option.name: string
        @param action.force: boolean
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/resetoption'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def setoption(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.option.name: string
        @param action.option.value: string
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/setoption'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def start(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.force: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/start'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def stop(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.force: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/stop'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                                                     '{glustervolume:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class ClusterGlusterVolumeBrick(params.GlusterBrick, Base):
    def __init__(self, clusterglustervolume, brick, context):
        Base.__init__(self, context)
        self.parentclass = clusterglustervolume
        self.superclass  =  brick

        #SUB_COLLECTIONS
    def __new__(cls, clusterglustervolume, brick, context):
        if brick is None: return None
        obj = object.__new__(cls)
        obj.__init__(clusterglustervolume, brick, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/bricks/{brick:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.parentclass.get_id(),
                                                                   '{glustervolume:id}': self.parentclass.get_id(),
                                                                   '{brick:id}': self.get_id()}),
                                       headers={'Content-type':None})

class ClusterGlusterVolumeBricks(Base):

    def __init__(self, clusterglustervolume , context):
        Base.__init__(self, context)
        self.parentclass = clusterglustervolume

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, glusterbricks, expect=None, correlation_id=None):

        '''
        @type GlusterBricks:

        @param bricks.brick: collection
        {
          @ivar brick.server_id: string
          @ivar brick.brick_dir: string
        }
        [@param bricks.brick: collection]
        {
          [@ivar brick.replica_count: unsignedShort]
          [@ivar brick.stripe_count: unsignedShort]
        }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return GlusterBricks:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/bricks'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{glustervolume:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(glusterbricks),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return ClusterGlusterVolumeBrick(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return GlusterBricks:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/bricks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{glustervolume:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return ClusterGlusterVolumeBrick(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{glustervolume:id}': self.parentclass.get_id()}),
                                           headers={}).get_brick()

            return ClusterGlusterVolumeBrick(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return GlusterBricks:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes/{glustervolume:id}/bricks'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{glustervolume:id}': self.parentclass.get_id()})).get_brick()

        return ParseHelper.toSubCollection(ClusterGlusterVolumeBrick,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class ClusterGlusterVolumes(Base):

    def __init__(self, cluster , context):
        Base.__init__(self, context)
        self.parentclass = cluster

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, glustervolume, expect=None, correlation_id=None):

        '''
        @type GlusterVolume:

        @param gluster_volume.name: string
        @param gluster_volume.volume_type: string
        @param gluster_volume.bricks.brick: collection
        {
          @ivar brick.server_id: string
          @ivar brick.brick_dir: string
        }
        [@param gluster_volume.transport_types: collection]
        {
          [@ivar transport_type: string]
        }
        [@param gluster_volume.replica_count: unsignedShort]
        [@param gluster_volume.stripe_count: unsignedShort]
        [@param gluster_volume.options.option: collection]
        {
          [@ivar option.name: string]
          [@ivar option.value: string]
        }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return GlusterVolume:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(glustervolume),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return ClusterGlusterVolume(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return GlusterVolumes:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return ClusterGlusterVolume(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                           headers={}).get_gluster_volume()

            return ClusterGlusterVolume(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]

        @return GlusterVolumes:
        '''

        url = '/api/clusters/{cluster:id}/glustervolumes'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{cluster:id}': self.parentclass.get_id()}),
                                                                   qargs={'search:query':query,'case_sensitive:matrix':case_sensitive}),
                                      headers={}).get_gluster_volume()
        return ParseHelper.toSubCollection(ClusterGlusterVolume,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class ClusterNetwork(params.Network, Base):
    def __init__(self, cluster, network, context):
        Base.__init__(self, context)
        self.parentclass = cluster
        self.superclass  =  network

        #SUB_COLLECTIONS
    def __new__(cls, cluster, network, context):
        if network is None: return None
        obj = object.__new__(cls)
        obj.__init__(cluster, network, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/clusters/{cluster:id}/networks/{network:id}',
                                {'{cluster:id}' : self.parentclass.get_id(),
                                 '{network:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param network.display: boolean]
        [@param network.usages.usage: collection]
        {
          [@ivar usage: string]
        }
        [@param correlation_id: any string]

        @return Network:
        '''

        url = '/api/clusters/{cluster:id}/networks/{network:id}'
        url = UrlHelper.replace(url, {'{cluster:id}' : self.parentclass.get_id(),
                                      '{network:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return ClusterNetwork(self.parentclass, result, self.context)

class ClusterNetworks(Base):

    def __init__(self, cluster , context):
        Base.__init__(self, context)
        self.parentclass = cluster

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, network, expect=None, correlation_id=None):

        '''
        @type Network:

        @param network.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Network:
        '''

        url = '/api/clusters/{cluster:id}/networks'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(network),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return ClusterNetwork(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Networks:
        '''

        url = '/api/clusters/{cluster:id}/networks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return ClusterNetwork(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                           headers={}).get_network()

            return ClusterNetwork(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Networks:
        '''

        url = '/api/clusters/{cluster:id}/networks'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{cluster:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_network()
        return ParseHelper.toSubCollection(ClusterNetwork,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class ClusterPermission(params.Permission, Base):
    def __init__(self, cluster, permission, context):
        Base.__init__(self, context)
        self.parentclass = cluster
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, cluster, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(cluster, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/clusters/{cluster:id}/permissions/{permission:id}',
                                {'{cluster:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class ClusterPermissions(Base):

    def __init__(self, cluster , context):
        Base.__init__(self, context)
        self.parentclass = cluster

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/clusters/{cluster:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return ClusterPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/clusters/{cluster:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return ClusterPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{cluster:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return ClusterPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/clusters/{cluster:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{cluster:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(ClusterPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Clusters(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, cluster, expect=None, correlation_id=None):
        '''
        @type Cluster:

        @param cluster.data_center.id|name: string
        @param cluster.name: string
        @param cluster.version.major: int
        @param cluster.version.minor: int
        @param cluster.cpu.id: string
        [@param cluster.description: string]
        [@param cluster.memory_policy.overcommit.percent: double]
        [@param cluster.memory_policy.transparent_hugepages.enabled: boolean]
        [@param cluster.scheduling_policy.policy: string]
        [@param cluster.scheduling_policy.thresholds.low: int]
        [@param cluster.scheduling_policy.thresholds.high: int]
        [@param cluster.scheduling_policy.thresholds.duration: int]
        [@param cluster.error_handling.on_error: string]
        [@param cluster.virt_service: boolean]
        [@param cluster.gluster_service: boolean]
        [@param cluster.threads_as_cores: boolean]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Cluster:
        '''

        url = '/api/clusters'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(cluster),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Cluster(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Clusters:
        '''

        url = '/api/clusters'

        if id:
            try :
                return Cluster(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_cluster()
            return Cluster(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Clusters:
        '''

        url='/api/clusters'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_cluster()
        return ParseHelper.toCollection(Cluster,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class DataCenter(params.DataCenter, Base):
    def __init__(self, datacenter, context):
        Base.__init__(self, context)
        self.superclass = datacenter

        self.storagedomains = DataCenterStorageDomains(self, context)
        self.quotas = DataCenterQuotas(self, context)
        self.permissions = DataCenterPermissions(self, context)

    def __new__(cls, datacenter, context):
        if datacenter is None: return None
        obj = object.__new__(cls)
        obj.__init__(datacenter, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, action=params.Action(), async=None, correlation_id=None):
        '''
        @type Action:

        [@param action.force: boolean]
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/datacenters/{datacenter:id}',
                                {'{datacenter:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(action),
                                        headers={"Correlation-Id":correlation_id})

    def update(self, correlation_id=None):
        '''
        [@param datacenter.name: string]
        [@param datacenter.storage_type: string]
        [@param datacenter.version.major: int]
        [@param datacenter.version.minor: int]
        [@param datacenter.description: string]
        [@param datacenter.storage_format: string]
        [@param correlation_id: any string]

        @return DataCenter:
        '''

        url = '/api/datacenters/{datacenter:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{datacenter:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return DataCenter(result, self.context)

class DataCenterPermission(params.Permission, Base):
    def __init__(self, datacenter, permission, context):
        Base.__init__(self, context)
        self.parentclass = datacenter
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, datacenter, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(datacenter, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/datacenters/{datacenter:id}/permissions/{permission:id}',
                                {'{datacenter:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class DataCenterPermissions(Base):

    def __init__(self, datacenter , context):
        Base.__init__(self, context)
        self.parentclass = datacenter

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/datacenters/{datacenter:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return DataCenterPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/datacenters/{datacenter:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DataCenterPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return DataCenterPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Permissions:
        '''

        url = '/api/datacenters/{datacenter:id}/permissions'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()})).get_permission()

        return ParseHelper.toSubCollection(DataCenterPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class DataCenterQuota(params.Quota, Base):
    def __init__(self, datacenter, quota, context):
        Base.__init__(self, context)
        self.parentclass = datacenter
        self.superclass  =  quota

        #SUB_COLLECTIONS
    def __new__(cls, datacenter, quota, context):
        if quota is None: return None
        obj = object.__new__(cls)
        obj.__init__(datacenter, quota, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/datacenters/{datacenter:id}/quotas/{quota:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{datacenter:id}' : self.parentclass.get_id(),
                                                                   '{quota:id}': self.get_id()}),
                                       headers={'Content-type':None})

class DataCenterQuotas(Base):

    def __init__(self, datacenter , context):
        Base.__init__(self, context)
        self.parentclass = datacenter

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, quota):

        '''
        @type Quota:


        @return Quota:
        '''

        url = '/api/datacenters/{datacenter:id}/quotas'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(quota),
                                       headers={})

        return DataCenterQuota(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Quotas:
        '''

        url = '/api/datacenters/{datacenter:id}/quotas'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DataCenterQuota(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                           headers={}).get_quota()

            return DataCenterQuota(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Quotas:
        '''

        url = '/api/datacenters/{datacenter:id}/quotas'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()})).get_quota()

        return ParseHelper.toSubCollection(DataCenterQuota,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class DataCenterStorageDomain(params.StorageDomain, Base):
    def __init__(self, datacenter, storagedomain, context):
        Base.__init__(self, context)
        self.parentclass = datacenter
        self.superclass  =  storagedomain

        #SUB_COLLECTIONS
    def __new__(cls, datacenter, storagedomain, context):
        if storagedomain is None: return None
        obj = object.__new__(cls)
        obj.__init__(datacenter, storagedomain, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/datacenters/{datacenter:id}/storagedomains/{storagedomain:id}',
                                {'{datacenter:id}' : self.parentclass.get_id(),
                                 '{storagedomain:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def activate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/datacenters/{datacenter:id}/storagedomains/{storagedomain:id}/activate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{datacenter:id}' : self.parentclass.get_id(),
                                                                     '{storagedomain:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def deactivate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/datacenters/{datacenter:id}/storagedomains/{storagedomain:id}/deactivate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{datacenter:id}' : self.parentclass.get_id(),
                                                                     '{storagedomain:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class DataCenterStorageDomains(Base):

    def __init__(self, datacenter , context):
        Base.__init__(self, context)
        self.parentclass = datacenter

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, storagedomain, expect=None, correlation_id=None):

        '''
        @type StorageDomain:

        @param storagedomain.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return StorageDomain:
        '''

        url = '/api/datacenters/{datacenter:id}/storagedomains'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(storagedomain),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return DataCenterStorageDomain(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return StorageDomains:
        '''

        url = '/api/datacenters/{datacenter:id}/storagedomains'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DataCenterStorageDomain(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{datacenter:id}': self.parentclass.get_id()}),
                                           headers={}).get_storage_domain()

            return DataCenterStorageDomain(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return StorageDomains:
        '''

        url = '/api/datacenters/{datacenter:id}/storagedomains'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{datacenter:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_storage_domain()
        return ParseHelper.toSubCollection(DataCenterStorageDomain,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class DataCenters(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, datacenter, expect=None, correlation_id=None):
        '''
        @type DataCenter:

        @param datacenter.name: string
        @param datacenter.storage_type: string
        @param datacenter.version.major: int
        @param datacenter.version.minor: int
        [@param datacenter.description: string]
        [@param datacenter.storage_format: string]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return DataCenter:
        '''

        url = '/api/datacenters'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(datacenter),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return DataCenter(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return DataCenters:
        '''

        url = '/api/datacenters'

        if id:
            try :
                return DataCenter(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_data_center()
            return DataCenter(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return DataCenters:
        '''

        url='/api/datacenters'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_data_center()
        return ParseHelper.toCollection(DataCenter,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Disk(params.Disk, Base):
    def __init__(self, disk, context):
        Base.__init__(self, context)
        self.superclass = disk

        self.statistics = DiskStatistics(self, context)
        self.permissions = DiskPermissions(self, context)

    def __new__(cls, disk, context):
        if disk is None: return None
        obj = object.__new__(cls)
        obj.__init__(disk, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/disks/{disk:id}',
                                {'{disk:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

class DiskPermission(params.Permission, Base):
    def __init__(self, disk, permission, context):
        Base.__init__(self, context)
        self.parentclass = disk
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, disk, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(disk, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/disks/{disk:id}/permissions/{permission:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{disk:id}' : self.parentclass.get_id(),
                                                                   '{permission:id}': self.get_id()}),
                                       headers={'Content-type':None})

class DiskPermissions(Base):

    def __init__(self, disk , context):
        Base.__init__(self, context)
        self.parentclass = disk

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission):

        '''
        @type Permission:


        @return Permission:
        '''

        url = '/api/disks/{disk:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={})

        return DiskPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/disks/{disk:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DiskPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return DiskPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Permissions:
        '''

        url = '/api/disks/{disk:id}/permissions'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()})).get_permission()

        return ParseHelper.toSubCollection(DiskPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class DiskStatistic(params.Statistic, Base):
    def __init__(self, disk, statistic, context):
        Base.__init__(self, context)
        self.parentclass = disk
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, disk, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(disk, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class DiskStatistics(Base):

    def __init__(self, disk , context):
        Base.__init__(self, context)
        self.parentclass = disk

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/disks/{disk:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DiskStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return DiskStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Statistics:
        '''

        url = '/api/disks/{disk:id}/statistics'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{disk:id}': self.parentclass.get_id()})).get_statistic()

        return ParseHelper.toSubCollection(DiskStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Disks(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, disk, expect=None, correlation_id=None):
        '''
        @type Disk:

        Overload 1:
          @param provisioned_size: int
          @param disk.interface: string
          @param disk.format: string
          [@param disk.alias: string]
          [@param disk.name: string]
          [@param disk.size: int]
          [@param disk.sparse: boolean]
          [@param disk.bootable: boolean]
          [@param disk.shareable: boolean]
          [@param disk.propagate_errors: boolean]
          [@param disk.wipe_after_delete: boolean]
          [@param disk.storage_domains.storage_domain: collection]
          {
            [@ivar storage_domain.id|name: string]
          }
        Overload 2:
          @param disk.interface: string
          @param disk.format: string
          @param disk.lun_storage.type: string
          @param disk.lun_storage.logical_unit: collection
          {
            @ivar logical_unit.id: string
            @ivar logical_unit.address: string
            @ivar logical_unit.port: int
            @ivar logical_unit.target: string
          }
          [@param disk.alias: string]
          [@param disk.sparse: boolean]
          [@param disk.bootable: boolean]
          [@param disk.shareable: boolean]
          [@param disk.propagate_errors: boolean]
          [@param disk.wipe_after_delete: boolean]
          [@param disk.storage_domains.storage_domain: collection]
          {
            [@ivar storage_domain.id|name: string]
          }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Disk:
        '''

        url = '/api/disks'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(disk),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Disk(result, self.context)

    def get(self, alias=None, id=None):
        '''
        [@param id   : string (the id of the entity)]
        [@param alias: string (the alias of the entity)]

        @return Disks:
        '''

        url = '/api/disks'

        if id:
            try :
                return Disk(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif alias:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'alias='+alias}),
                                           headers={}).get_disk()
            return Disk(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'alias'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Disks:
        '''

        url='/api/disks'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_disk()
        return ParseHelper.toCollection(Disk,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Domain(params.Domain, Base):
    def __init__(self, domain, context):
        Base.__init__(self, context)
        self.superclass = domain

        self.users = DomainUsers(self, context)
        self.groups = DomainGroups(self, context)

    def __new__(cls, domain, context):
        if domain is None: return None
        obj = object.__new__(cls)
        obj.__init__(domain, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class DomainGroup(params.Group, Base):
    def __init__(self, domain, group, context):
        Base.__init__(self, context)
        self.parentclass = domain
        self.superclass  =  group

        #SUB_COLLECTIONS
    def __new__(cls, domain, group, context):
        if group is None: return None
        obj = object.__new__(cls)
        obj.__init__(domain, group, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class DomainGroups(Base):

    def __init__(self, domain , context):
        Base.__init__(self, context)
        self.parentclass = domain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Groups:
        '''

        url = '/api/domains/{domain:id}/groups'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{domain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DomainGroup(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{domain:id}': self.parentclass.get_id()}),
                                           headers={}).get_group()

            return DomainGroup(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Groups:
        '''

        url = '/api/domains/{domain:id}/groups'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{domain:id}': self.parentclass.get_id()}),
                                                                   qargs={'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_group()
        return ParseHelper.toSubCollection(DomainGroup,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class DomainUser(params.User, Base):
    def __init__(self, domain, user, context):
        Base.__init__(self, context)
        self.parentclass = domain
        self.superclass  =  user

        #SUB_COLLECTIONS
    def __new__(cls, domain, user, context):
        if user is None: return None
        obj = object.__new__(cls)
        obj.__init__(domain, user, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class DomainUsers(Base):

    def __init__(self, domain , context):
        Base.__init__(self, context)
        self.parentclass = domain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Users:
        '''

        url = '/api/domains/{domain:id}/users'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{domain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return DomainUser(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{domain:id}': self.parentclass.get_id()}),
                                           headers={}).get_user()

            return DomainUser(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Users:
        '''

        url = '/api/domains/{domain:id}/users'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{domain:id}': self.parentclass.get_id()}),
                                                                   qargs={'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_user()
        return ParseHelper.toSubCollection(DomainUser,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Domains(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Domains:
        '''

        url = '/api/domains'

        if id:
            try :
                return Domain(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=url,
                                           headers={}).get_domain()
            return Domain(FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param max: int (max results)]

        @return Domains:
        '''

        url='/api/domains'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'max:matrix':max}),
                                      headers={}).get_domain()
        return ParseHelper.toCollection(Domain,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Event(params.Event, Base):
    def __init__(self, event, context):
        Base.__init__(self, context)
        self.superclass = event

        #SUB_COLLECTIONS
    def __new__(cls, event, context):
        if event is None: return None
        obj = object.__new__(cls)
        obj.__init__(event, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/events/{event:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{event:id}': self.get_id()}),
                                        headers={'Content-type':None})

class Events(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, event, expect=None, correlation_id=None):
        '''
        @type Event:

        @param event.description: string
        @param event.severity: string
        @param event.origin: string
        @param event.custom_id: int
        [@param event.flood_rate: int]
        [@param event.host.id: string]
        [@param event.user.id: string]
        [@param event.vm.id: string]
        [@param event.storage_domain.id: string]
        [@param event.template.id: string]
        [@param event.cluster.id: string]
        [@param event.data_center.id: string]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Event:
        '''

        url = '/api/events'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(event),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Event(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Events:
        '''

        url = '/api/events'

        if id:
            try :
                return Event(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_event()
            return Event(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, from_event_id=None, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param from_event_id: string (event_id)]
        [@param max: int (max results)]

        @return Events:
        '''

        url='/api/events'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'from:matrix':from_event_id,'max:matrix':max}),
                                      headers={}).get_event()
        return ParseHelper.toCollection(Event,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Group(params.Group, Base):
    def __init__(self, group, context):
        Base.__init__(self, context)
        self.superclass = group

        self.tags = GroupTags(self, context)
        self.roles = GroupRoles(self, context)
        self.permissions = GroupPermissions(self, context)

    def __new__(cls, group, context):
        if group is None: return None
        obj = object.__new__(cls)
        obj.__init__(group, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/groups/{group:id}',
                                {'{group:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

class GroupPermission(params.Permission, Base):
    def __init__(self, group, permission, context):
        Base.__init__(self, context)
        self.parentclass = group
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, group, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(group, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/groups/{group:id}/permissions/{permission:id}',
                                {'{group:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class GroupPermissions(Base):

    def __init__(self, group , context):
        Base.__init__(self, context)
        self.parentclass = group

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.role.id: string
          @param permission.data_center.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.cluster.id: string
        Overload 3:
          @param permission.role.id: string
          @param permission.host.id: string
        Overload 4:
          @param permission.role.id: string
          @param permission.storage_domain.id: string
        Overload 5:
          @param permission.role.id: string
          @param permission.vm.id: string
        Overload 6:
          @param permission.role.id: string
          @param permission.vmpool.id: string
        Overload 7:
          @param permission.role.id: string
          @param permission.template.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/groups/{group:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return GroupPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/groups/{group:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return GroupPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return GroupPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/groups/{group:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{group:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(GroupPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class GroupRole(params.Role, Base):
    def __init__(self, group, role, context):
        Base.__init__(self, context)
        self.parentclass = group
        self.superclass  =  role

        self.permits = GroupRolePermits(self, context)

    def __new__(cls, group, role, context):
        if role is None: return None
        obj = object.__new__(cls)
        obj.__init__(group, role, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/groups/{group:id}/roles/{role:id}',
                                {'{group:id}' : self.parentclass.get_id(),
                                 '{role:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class GroupRolePermit(params.Permit, Base):
    def __init__(self, grouprole, permit, context):
        Base.__init__(self, context)
        self.parentclass = grouprole
        self.superclass  =  permit

        #SUB_COLLECTIONS
    def __new__(cls, grouprole, permit, context):
        if permit is None: return None
        obj = object.__new__(cls)
        obj.__init__(grouprole, permit, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/groups/{group:id}/roles/{role:id}/permits/{permit:id}',
                                {'{group:id}' : self.parentclass.parentclass.get_id(),
                                 '{role:id}': self.parentclass.get_id(),
                                 '{permit:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class GroupRolePermits(Base):

    def __init__(self, grouprole , context):
        Base.__init__(self, context)
        self.parentclass = grouprole

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permit, expect=None, correlation_id=None):

        '''
        @type Permit:

        @param permit.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permit:
        '''

        url = '/api/groups/{group:id}/roles/{role:id}/permits'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{group:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{role:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permit),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return GroupRolePermit(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permits:
        '''

        url = '/api/groups/{group:id}/roles/{role:id}/permits'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{group:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{role:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return GroupRolePermit(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{group:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{role:id}': self.parentclass.get_id()}),
                                           headers={}).get_permit()

            return GroupRolePermit(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permits:
        '''

        url = '/api/groups/{group:id}/roles/{role:id}/permits'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{group:id}' : self.parentclass.parentclass.get_id(),
                                                                                               '{role:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permit()
        return ParseHelper.toSubCollection(GroupRolePermit,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class GroupRoles(Base):

    def __init__(self, group , context):
        Base.__init__(self, context)
        self.parentclass = group

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, role, expect=None, correlation_id=None):

        '''
        @type Role:

        @param role.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Role:
        '''

        url = '/api/groups/{group:id}/roles'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(role),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return GroupRole(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Roles:
        '''

        url = '/api/groups/{group:id}/roles'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return GroupRole(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                           headers={}).get_role()

            return GroupRole(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Roles:
        '''

        url = '/api/groups/{group:id}/roles'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{group:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_role()
        return ParseHelper.toSubCollection(GroupRole,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class GroupTag(params.Tag, Base):
    def __init__(self, group, tag, context):
        Base.__init__(self, context)
        self.parentclass = group
        self.superclass  =  tag

        #SUB_COLLECTIONS
    def __new__(cls, group, tag, context):
        if tag is None: return None
        obj = object.__new__(cls)
        obj.__init__(group, tag, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/groups/{group:id}/tags/{tag:id}',
                                {'{group:id}' : self.parentclass.get_id(),
                                 '{tag:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class GroupTags(Base):

    def __init__(self, group , context):
        Base.__init__(self, context)
        self.parentclass = group

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, tag, expect=None, correlation_id=None):

        '''
        @type Tag:

        @param tag.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/groups/{group:id}/tags'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(tag),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return GroupTag(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Tags:
        '''

        url = '/api/groups/{group:id}/tags'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return GroupTag(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{group:id}': self.parentclass.get_id()}),
                                           headers={}).get_tag()

            return GroupTag(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Tags:
        '''

        url = '/api/groups/{group:id}/tags'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{group:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_tag()
        return ParseHelper.toSubCollection(GroupTag,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Groups(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, group, correlation_id=None):
        '''
        @type Group:

        @param group.name: string
        [@param correlation_id: any string]

        @return Group:
        '''

        url = '/api/groups'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(group),
                                       headers={"Correlation-Id":correlation_id})
        return Group(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Groups:
        '''

        url = '/api/groups'

        if id:
            try :
                return Group(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_group()
            return Group(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Groups:
        '''

        url='/api/groups'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_group()
        return ParseHelper.toCollection(Group,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Host(params.Host, Base):
    def __init__(self, host, context):
        Base.__init__(self, context)
        self.superclass = host

        self.statistics = HostStatistics(self, context)
        self.tags = HostTags(self, context)
        self.hooks = HostHooks(self, context)
        self.storage = HostStorage(self, context)
        self.nics = HostNics(self, context)
        self.permissions = HostPermissions(self, context)

    def __new__(cls, host, context):
        if host is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, action=params.Action(), async=None, correlation_id=None):
        '''
        @type Action:

        [@param action.force: boolean]
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/hosts/{host:id}',
                                {'{host:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(action),
                                        headers={"Correlation-Id":correlation_id})

    def update(self, correlation_id=None):
        '''
        [@param host.name: string]
        [@param host.address: string]
        [@param host.root_password: string]
        [@param host.cluster.id: string]
        [@param host.port: int]
        [@param host.storage_manager.priority: int]
        [@param host.power_management.type: string]
        [@param host.power_management.enabled: boolean]
        [@param host.power_management.address: string]
        [@param host.power_management.user_name: string]
        [@param host.power_management.password: string]
        [@param host.power_management.options.option: collection]
        {
          [@ivar option.name: string]
          [@ivar option.value: string]
        }
        [@param host.power_management.pm_proxy: collection]
        {
          [@ivar propietary: string]
        }
        [@param host.power_management.agents.agent: collection]
        {
          [@ivar type: string]
          [@ivar address: string]
          [@ivar user_name: string]
          [@ivar password: string]
          [@ivar options.option: collection]
          {
            [@param option.name: string]
            [@param option.value: string]
          }
        }
        [@param correlation_id: any string]

        @return Host:
        '''

        url = '/api/hosts/{host:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Host(result, self.context)

    def activate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/activate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def approve(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.cluster.id|name: string]
        [@param action.async: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/approve'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def commitnetconfig(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/commitnetconfig'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def deactivate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/deactivate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def fence(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/fence'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def install(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.root_password: string]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/install'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def iscsidiscover(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.iscsi.address: string
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/iscsidiscover'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def iscsilogin(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.iscsi.address: string
        @param action.iscsi.target: string
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/iscsilogin'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

class HostHook(params.Hook, Base):
    def __init__(self, host, hook, context):
        Base.__init__(self, context)
        self.parentclass = host
        self.superclass  =  hook

        #SUB_COLLECTIONS
    def __new__(cls, host, hook, context):
        if hook is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, hook, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class HostHooks(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Hooks:
        '''

        url = '/api/hosts/{host:id}/hooks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostHook(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_hook()

            return HostHook(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Hooks:
        '''

        url = '/api/hosts/{host:id}/hooks'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()})).get_hook()

        return ParseHelper.toSubCollection(HostHook,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class HostNIC(params.HostNIC, Base):
    def __init__(self, host, nic, context):
        Base.__init__(self, context)
        self.parentclass = host
        self.superclass  =  nic

        self.statistics = HostNicStatistics(self, context)

    def __new__(cls, host, nic, context):
        if nic is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, nic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/hosts/{host:id}/nics/{nic:id}',
                                {'{host:id}' : self.parentclass.get_id(),
                                 '{nic:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, async=None, correlation_id=None):
        '''
        [@param hostnic.bonding.slaves.host_nic: collection]
        {
          [@ivar host_nic.id|name: string]
        }
        [@param hostnic.network.id|name: string]
        [@param hostnic.name: string]
        [@param hostnic.bonding.options.option: collection]
        {
          [@ivar option.name: string]
          [@ivar option.value: string]
          [@ivar type: string]
        }
        [@param hostnic.ip.gateway: string]
        [@param hostnic.boot_protocol: string]
        [@param hostnic.mac: string]
        [@param hostnic.ip.address: string]
        [@param hostnic.ip.netmask: string]
        [@param hostnic.ip.mtu: int]
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return HostNIC:
        '''

        url = '/api/hosts/{host:id}/nics/{nic:id}'
        url = UrlHelper.replace(url, {'{host:id}' : self.parentclass.get_id(),
                                      '{nic:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return HostNIC(self.parentclass, result, self.context)

    def attach(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.network.id|name: string
        [@param action.async: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/nics/{nic:id}/attach'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}' : self.parentclass.get_id(),
                                                                     '{nic:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def detach(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.async: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/nics/{nic:id}/detach'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}' : self.parentclass.get_id(),
                                                                     '{nic:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class HostNicStatistic(params.Statistic, Base):
    def __init__(self, hostnic, statistic, context):
        Base.__init__(self, context)
        self.parentclass = hostnic
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, hostnic, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(hostnic, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class HostNicStatistics(Base):

    def __init__(self, hostnic , context):
        Base.__init__(self, context)
        self.parentclass = hostnic

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/hosts/{host:id}/nics/{nic:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{nic:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostNicStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{nic:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return HostNicStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Statistics:
        '''

        url = '/api/hosts/{host:id}/nics/{nic:id}/statistics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}' : self.parentclass.parentclass.get_id(),
                                                                                               '{nic:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_statistic()
        return ParseHelper.toSubCollection(HostNicStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class HostNics(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, hostnic, expect=None, correlation_id=None):

        '''
        @type HostNIC:

        @param hostnic.network.id|name: string
        @param hostnic.name: string
        @param hostnic.bonding.slaves.host_nic: collection
        {
          @ivar host_nic.id|name: string
        }
        [@param hostnic.bonding.options.option: collection]
        {
          [@ivar option.name: string]
          [@ivar option.value: string]
          [@ivar type: string]
        }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return HostNIC:
        '''

        url = '/api/hosts/{host:id}/nics'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(hostnic),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return HostNIC(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return HostNics:
        '''

        url = '/api/hosts/{host:id}/nics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostNIC(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_host_nic()

            return HostNIC(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return HostNics:
        '''

        url = '/api/hosts/{host:id}/nics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_host_nic()
        return ParseHelper.toSubCollection(HostNIC,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

    def setupnetworks(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.host_nics.host_nic: collection]
        {
          [@ivar host_nic.network.id|name: string]
          [@ivar host_nic.name: string]
          [@ivar host_nic.ip.gateway: string]
          [@ivar host_nic.boot_protocol: string]
          [@ivar host_nic.mac: string]
          [@ivar host_nic.ip.address: string]
          [@ivar host_nic.ip.netmask: string]
          [@ivar host_nic.bonding.options.option: collection]
          {
            [@param option.name: string]
            [@param option.value: string]
            [@param option.type: string]
          }
          [@ivar bonding.slaves.host_nic: collection]
          {
            [@param host_nic.name|id: string]
          }
          [@ivar host_nic.override_configuration: boolean]
        }
        [@param action.checkConnectivity: boolean]
        [@param action.connectivityTimeout: int]
        [@param action.force: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/hosts/{host:id}/nics/setupnetworks'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{host:id}' : self.parentclass.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class HostPermission(params.Permission, Base):
    def __init__(self, host, permission, context):
        Base.__init__(self, context)
        self.parentclass = host
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, host, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/hosts/{host:id}/permissions/{permission:id}',
                                {'{host:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class HostPermissions(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/hosts/{host:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return HostPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/hosts/{host:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return HostPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/hosts/{host:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(HostPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class HostStatistic(params.Statistic, Base):
    def __init__(self, host, statistic, context):
        Base.__init__(self, context)
        self.parentclass = host
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, host, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class HostStatistics(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/hosts/{host:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return HostStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Statistics:
        '''

        url = '/api/hosts/{host:id}/statistics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_statistic()
        return ParseHelper.toSubCollection(HostStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class HostStorage(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return HostStorage:
        '''

        url = '/api/hosts/{host:id}/storage'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostStorage(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_storage()

            return HostStorage(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return HostStorage:
        '''

        url = '/api/hosts/{host:id}/storage'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_storage()
        return ParseHelper.toSubCollection(HostStorage,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class HostTag(params.Tag, Base):
    def __init__(self, host, tag, context):
        Base.__init__(self, context)
        self.parentclass = host
        self.superclass  =  tag

        #SUB_COLLECTIONS
    def __new__(cls, host, tag, context):
        if tag is None: return None
        obj = object.__new__(cls)
        obj.__init__(host, tag, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/hosts/{host:id}/tags/{tag:id}',
                                {'{host:id}' : self.parentclass.get_id(),
                                 '{tag:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class HostTags(Base):

    def __init__(self, host , context):
        Base.__init__(self, context)
        self.parentclass = host

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, tag, expect=None, correlation_id=None):

        '''
        @type Tag:

        @param tag.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/hosts/{host:id}/tags'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(tag),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return HostTag(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Tags:
        '''

        url = '/api/hosts/{host:id}/tags'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return HostTag(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{host:id}': self.parentclass.get_id()}),
                                           headers={}).get_tag()

            return HostTag(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Tags:
        '''

        url = '/api/hosts/{host:id}/tags'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{host:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_tag()
        return ParseHelper.toSubCollection(HostTag,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Hosts(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, host, expect=None, correlation_id=None):
        '''
        @type Host:

        @param host.name: string
        @param host.address: string
        @param host.root_password: string
        @param host.cluster.id|name: string
        [@param host.port: int]
        [@param host.storage_manager.priority: int]
        [@param host.power_management.type: string]
        [@param host.power_management.enabled: boolean]
        [@param host.power_management.address: string]
        [@param host.power_management.user_name: string]
        [@param host.power_management.password: string]
        [@param host.power_management.options.option: collection]
        {
          [@ivar option.name: string]
          [@ivar option.value: string]
        }
        [@param host.power_management.pm_proxy: collection]
        {
          [@ivar propietary: string]
        }
        [@param host.power_management.agents.agent: collection]
        {
          [@ivar type: string]
          [@ivar address: string]
          [@ivar user_name: string]
          [@ivar password: string]
          [@ivar options.option: collection]
          {
            [@param option.name: string]
            [@param option.value: string]
          }
        }
        [@param host.reboot_after_installation: boolean]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Host:
        '''

        url = '/api/hosts'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(host),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Host(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Hosts:
        '''

        url = '/api/hosts'

        if id:
            try :
                return Host(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_host()
            return Host(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Hosts:
        '''

        url='/api/hosts'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_host()
        return ParseHelper.toCollection(Host,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Network(params.Network, Base):
    def __init__(self, network, context):
        Base.__init__(self, context)
        self.superclass = network

        self.permissions = NetworkPermissions(self, context)

    def __new__(cls, network, context):
        if network is None: return None
        obj = object.__new__(cls)
        obj.__init__(network, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/networks/{network:id}',
                                {'{network:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param network.name: string]
        [@param network.description: string]
        [@param network.vlan.id: string]
        [@param network.ip.address: string]
        [@param network.ip.gateway: string]
        [@param network.ip.netmask: string]
        [@param network.display: boolean]
        [@param network.stp: boolean]
        [@param network.mtu: int]
        [@param correlation_id: any string]

        @return Network:
        '''

        url = '/api/networks/{network:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{network:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Network(result, self.context)

class NetworkPermission(params.Permission, Base):
    def __init__(self, network, permission, context):
        Base.__init__(self, context)
        self.parentclass = network
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, network, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(network, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/networks/{network:id}/permissions/{permission:id}',
                                {'{network:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class NetworkPermissions(Base):

    def __init__(self, network , context):
        Base.__init__(self, context)
        self.parentclass = network

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.group.id: string
          @param permission.role.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/networks/{network:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{network:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return NetworkPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/networks/{network:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{network:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return NetworkPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{network:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return NetworkPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/networks/{network:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{network:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(NetworkPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Networks(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, network, expect=None, correlation_id=None):
        '''
        @type Network:

        @param network.data_center.id|name: string
        @param network.name: string
        [@param network.description: string]
        [@param network.vlan.id: string]
        [@param network.ip.address: string]
        [@param network.ip.gateway: string]
        [@param network.ip.netmask: string]
        [@param network.display: boolean]
        [@param network.stp: boolean]
        [@param network.mtu: int]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Network:
        '''

        url = '/api/networks'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(network),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Network(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Networks:
        '''

        url = '/api/networks'

        if id:
            try :
                return Network(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_network()
            return Network(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Networks:
        '''

        url='/api/networks'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_network()
        return ParseHelper.toCollection(Network,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Role(params.Role, Base):
    def __init__(self, role, context):
        Base.__init__(self, context)
        self.superclass = role

        self.permits = RolePermits(self, context)

    def __new__(cls, role, context):
        if role is None: return None
        obj = object.__new__(cls)
        obj.__init__(role, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/roles/{role:id}',
                                {'{role:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param role.permits.permit: collection]
        {
          [@ivar permit.id: string]
        }
        [@param role.description: string]
        [@param correlation_id: any string]

        @return Role:
        '''

        url = '/api/roles/{role:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{role:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Role(result, self.context)

class RolePermit(params.Permit, Base):
    def __init__(self, role, permit, context):
        Base.__init__(self, context)
        self.parentclass = role
        self.superclass  =  permit

        #SUB_COLLECTIONS
    def __new__(cls, role, permit, context):
        if permit is None: return None
        obj = object.__new__(cls)
        obj.__init__(role, permit, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/roles/{role:id}/permits/{permit:id}',
                                {'{role:id}' : self.parentclass.get_id(),
                                 '{permit:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class RolePermits(Base):

    def __init__(self, role , context):
        Base.__init__(self, context)
        self.parentclass = role

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permit, expect=None, correlation_id=None):

        '''
        @type Permit:

        @param permit.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permit:
        '''

        url = '/api/roles/{role:id}/permits'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{role:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permit),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return RolePermit(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permits:
        '''

        url = '/api/roles/{role:id}/permits'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{role:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return RolePermit(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{role:id}': self.parentclass.get_id()}),
                                           headers={}).get_permit()

            return RolePermit(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permits:
        '''

        url = '/api/roles/{role:id}/permits'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{role:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permit()
        return ParseHelper.toSubCollection(RolePermit,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Roles(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, role, expect=None, correlation_id=None):
        '''
        @type Role:

        @param role.name: string
        @param role.permits.permit: collection
        {
          @ivar permit.id: string
        }
        [@param role.description: string]
        [@param role.administrative: boolean]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Role:
        '''

        url = '/api/roles'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(role),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Role(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Roles:
        '''

        url = '/api/roles'

        if id:
            try :
                return Role(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=url,
                                           headers={}).get_role()
            return Role(FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param max: int (max results)]

        @return Roles:
        '''

        url='/api/roles'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'max:matrix':max}),
                                      headers={}).get_role()
        return ParseHelper.toCollection(Role,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class StorageDomain(params.StorageDomain, Base):
    def __init__(self, storagedomain, context):
        Base.__init__(self, context)
        self.superclass = storagedomain

        self.files = StorageDomainFiles(self, context)
        self.templates = StorageDomainTemplates(self, context)
        self.vms = StorageDomainVMs(self, context)
        self.permissions = StorageDomainPermissions(self, context)

    def __new__(cls, storagedomain, context):
        if storagedomain is None: return None
        obj = object.__new__(cls)
        obj.__init__(storagedomain, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, storagedomain, async=None, correlation_id=None):
        '''
        @type StorageDomain:

        @param storagedomain.host.id|name: string
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/storagedomains/{storagedomain:id}',
                                {'{storagedomain:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(storagedomain),
                                        headers={"Correlation-Id":correlation_id})

    def update(self, correlation_id=None):
        '''
        Overload 1:
          [@param storagedomain.name: string]
        Overload 2:
          @param storagedomain.storage.logical_unit: collection
          {
            @ivar logical_unit.address: string
            @ivar logical_unit.port: int
            @ivar logical_unit.target: string
            @ivar logical_unit.username: string
            @ivar logical_unit.password: string
            @ivar logical_unit.serial: string
            @ivar logical_unit.vendor_id: string
            @ivar logical_unit.product_id: string
            @ivar logical_unit.lun_mapping: int
            @ivar logical_unit.portal: string
            @ivar logical_unit.paths: int
            @ivar logical_unit.id: string
          }
          [@param storagedomain.name: string]
          [@param storagedomain.storage.override_luns: boolean]
        [@param correlation_id: any string]

        @return StorageDomain:
        '''

        url = '/api/storagedomains/{storagedomain:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{storagedomain:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return StorageDomain(result, self.context)

class StorageDomainFile(params.File, Base):
    def __init__(self, storagedomain, file, context):
        Base.__init__(self, context)
        self.parentclass = storagedomain
        self.superclass  =  file

        #SUB_COLLECTIONS
    def __new__(cls, storagedomain, file, context):
        if file is None: return None
        obj = object.__new__(cls)
        obj.__init__(storagedomain, file, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class StorageDomainFiles(Base):

    def __init__(self, storagedomain , context):
        Base.__init__(self, context)
        self.parentclass = storagedomain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Files:
        '''

        url = '/api/storagedomains/{storagedomain:id}/files'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return StorageDomainFile(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                           headers={}).get_file()

            return StorageDomainFile(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Files:
        '''

        url = '/api/storagedomains/{storagedomain:id}/files'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   qargs={'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_file()
        return ParseHelper.toSubCollection(StorageDomainFile,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class StorageDomainPermission(params.Permission, Base):
    def __init__(self, storagedomain, permission, context):
        Base.__init__(self, context)
        self.parentclass = storagedomain
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, storagedomain, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(storagedomain, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/storagedomains/{storagedomain:id}/permissions/{permission:id}',
                                {'{storagedomain:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class StorageDomainPermissions(Base):

    def __init__(self, storagedomain , context):
        Base.__init__(self, context)
        self.parentclass = storagedomain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/storagedomains/{storagedomain:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return StorageDomainPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/storagedomains/{storagedomain:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return StorageDomainPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return StorageDomainPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/storagedomains/{storagedomain:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(StorageDomainPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class StorageDomainTemplate(params.Template, Base):
    def __init__(self, storagedomain, template, context):
        Base.__init__(self, context)
        self.parentclass = storagedomain
        self.superclass  =  template

        #SUB_COLLECTIONS
    def __new__(cls, storagedomain, template, context):
        if template is None: return None
        obj = object.__new__(cls)
        obj.__init__(storagedomain, template, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/storagedomains/{storagedomain:id}/templates/{template:id}',
                                {'{storagedomain:id}' : self.parentclass.get_id(),
                                 '{template:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def import_template(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.cluster.id|name: string
        [@param action.storage_domain.id|name: string]
        [@param action.clone: boolen]
        [@param action.exclusive: boolen]
        [@param action.template.name: string]
        [@param action.vm.disks.disk: collection]
        {
          [@ivar disk.id: string]
        }
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/storagedomains/{storagedomain:id}/templates/{template:id}/import'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{storagedomain:id}' : self.parentclass.get_id(),
                                                                     '{template:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class StorageDomainTemplates(Base):

    def __init__(self, storagedomain , context):
        Base.__init__(self, context)
        self.parentclass = storagedomain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Templates:
        '''

        url = '/api/storagedomains/{storagedomain:id}/templates'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return StorageDomainTemplate(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                           headers={}).get_template()

            return StorageDomainTemplate(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Templates:
        '''

        url = '/api/storagedomains/{storagedomain:id}/templates'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_template()
        return ParseHelper.toSubCollection(StorageDomainTemplate,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class StorageDomainVM(params.VM, Base):
    def __init__(self, storagedomain, vm, context):
        Base.__init__(self, context)
        self.parentclass = storagedomain
        self.superclass  =  vm

        #SUB_COLLECTIONS
    def __new__(cls, storagedomain, vm, context):
        if vm is None: return None
        obj = object.__new__(cls)
        obj.__init__(storagedomain, vm, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/storagedomains/{storagedomain:id}/vms/{vm:id}',
                                {'{storagedomain:id}' : self.parentclass.get_id(),
                                 '{vm:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def import_vm(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.cluster.id|name: string
        [@param action.storage_domain.id|name: string]
        [@param action.vm.snapshots.collapse_snapshots: boolean]
        [@param action.clone: boolen]
        [@param action.exclusive: boolen]
        [@param action.vm.name: string]
        [@param action.vm.disks.disk: collection]
        {
          [@ivar disk.id: string]
        }
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/storagedomains/{storagedomain:id}/vms/{vm:id}/import'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{storagedomain:id}' : self.parentclass.get_id(),
                                                                     '{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class StorageDomainVMs(Base):

    def __init__(self, storagedomain , context):
        Base.__init__(self, context)
        self.parentclass = storagedomain

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return VMs:
        '''

        url = '/api/storagedomains/{storagedomain:id}/vms'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return StorageDomainVM(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{storagedomain:id}': self.parentclass.get_id()}),
                                           headers={}).get_vm()

            return StorageDomainVM(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return VMs:
        '''

        url = '/api/storagedomains/{storagedomain:id}/vms'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{storagedomain:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_vm()
        return ParseHelper.toSubCollection(StorageDomainVM,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class StorageDomains(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, storagedomain, expect=None, correlation_id=None):
        '''
        @type StorageDomain:

        Overload 1:
          @param storagedomain.host.id|name: string
          @param storagedomain.type: string
          @param storagedomain.storage.type: string
          @param storagedomain.format: boolean
          @param storagedomain.storage.address: string
          @param storagedomain.storage.logical_unit: collection
          {
            @ivar logical_unit.address: string
            @ivar logical_unit.port: int
            @ivar logical_unit.target: string
            @ivar logical_unit.username: string
            @ivar logical_unit.password: string
            @ivar logical_unit.serial: string
            @ivar logical_unit.vendor_id: string
            @ivar logical_unit.product_id: string
            @ivar logical_unit.lun_mapping: int
            @ivar logical_unit.portal: string
            @ivar logical_unit.paths: int
            @ivar logical_unit.id: string
          }
          [@param storagedomain.name: string]
          [@param storagedomain.storage.override_luns: boolean]
        Overload 2:
          @param storagedomain.host.id|name: string
          @param storagedomain.type: string
          @param storagedomain.storage.type: string
          @param storagedomain.format: boolean
          @param storagedomain.storage.address: string
          @param storagedomain.storage.path: string
          [@param storagedomain.name: string]
        Overload 3:
          @param storagedomain.host.id|name: string
          @param storagedomain.type: string
          @param storagedomain.storage.type: string
          @param storagedomain.format: boolean
          @param storagedomain.storage.path: string
          [@param storagedomain.name: string]
        Overload 4:
          @param storagedomain.host.id|name: string
          @param storagedomain.type: string
          @param storagedomain.storage.type: string
          @param storagedomain.format: boolean
          @param storagedomain.storage.path: string
          @param storagedomain.storage.vfs_type: string
          [@param storagedomain.name: string]
          [@param storagedomain.storage.address: string]
          [@param storagedomain.storage.mount_options: string]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return StorageDomain:
        '''

        url = '/api/storagedomains'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(storagedomain),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return StorageDomain(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return StorageDomains:
        '''

        url = '/api/storagedomains'

        if id:
            try :
                return StorageDomain(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_storage_domain()
            return StorageDomain(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return StorageDomains:
        '''

        url='/api/storagedomains'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_storage_domain()
        return ParseHelper.toCollection(StorageDomain,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Tag(params.Tag, Base):
    def __init__(self, tag, context):
        Base.__init__(self, context)
        self.superclass = tag

        #SUB_COLLECTIONS
    def __new__(cls, tag, context):
        if tag is None: return None
        obj = object.__new__(cls)
        obj.__init__(tag, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/tags/{tag:id}',
                                {'{tag:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param tag.name: string]
        [@param tag.description: string]
        [@param tag.parent.name: string]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/tags/{tag:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{tag:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Tag(result, self.context)

class Tags(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, tag, correlation_id=None):
        '''
        @type Tag:

        @param tag.name: string
        [@param tag.description: string]
        [@param tag.parent.name: string]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/tags'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(tag),
                                       headers={"Correlation-Id":correlation_id})
        return Tag(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Tags:
        '''

        url = '/api/tags'

        if id:
            try :
                return Tag(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=url,
                                           headers={}).get_tag()
            return Tag(FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param max: int (max results)]

        @return Tags:
        '''

        url='/api/tags'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'max:matrix':max}),
                                      headers={}).get_tag()
        return ParseHelper.toCollection(Tag,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class Template(params.Template, Base):
    def __init__(self, template, context):
        Base.__init__(self, context)
        self.superclass = template

        self.nics = TemplateNics(self, context)
        self.cdroms = TemplateCdRoms(self, context)
        self.disks = TemplateDisks(self, context)
        self.permissions = TemplatePermissions(self, context)

    def __new__(cls, template, context):
        if template is None: return None
        obj = object.__new__(cls)
        obj.__init__(template, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/templates/{template:id}',
                                {'{template:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param template.name: string]
        [@param template.memory: long]
        [@param template.cpu.topology.cores: int]
        [@param template.high_availability.enabled: boolean]
        [@param template.os.cmdline: string]
        [@param template.origin: string]
        [@param template.high_availability.priority: int]
        [@param template.timezone: string]
        [@param template.domain.name: string]
        [@param template.type: string]
        [@param template.stateless: boolean]
        [@param template.delete_protected: boolean]
        [@param template.placement_policy.affinity: string]
        [@param template.description: string]
        [@param template.custom_properties.custom_property: collection]
        {
          [@ivar custom_property.name: string]
          [@ivar custom_property.value: string]
        }
        [@param template.os.type: string]
        [@param template.os.boot: collection]
        {
          [@ivar boot.dev: string]
        }
        [@param template.cpu.topology.sockets: int]
        [@param template.os.kernel: string]
        [@param template.display.type: string]
        [@param template.display.monitors: int]
        [@param template.display.allow_override: boolean]
        [@param template.display.smartcard_enabled: boolean]
        [@param template.os.initRd: string]
        [@param template.usb.enabled: boolean]
        [@param template.usb.type: string]
        [@param correlation_id: any string]

        @return Template:
        '''

        url = '/api/templates/{template:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{template:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return Template(result, self.context)

    def export(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.storage_domain.id|name: string
        [@param action.async: boolean]
        [@param action.exclusive: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/templates/{template:id}/export'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{template:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

class TemplateCdRom(params.CdRom, Base):
    def __init__(self, template, cdrom, context):
        Base.__init__(self, context)
        self.parentclass = template
        self.superclass  =  cdrom

        #SUB_COLLECTIONS
    def __new__(cls, template, cdrom, context):
        if cdrom is None: return None
        obj = object.__new__(cls)
        obj.__init__(template, cdrom, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class TemplateCdRoms(Base):

    def __init__(self, template , context):
        Base.__init__(self, context)
        self.parentclass = template

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return CdRoms:
        '''

        url = '/api/templates/{template:id}/cdroms'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return TemplateCdRom(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                           headers={}).get_cdrom()

            return TemplateCdRom(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return CdRoms:
        '''

        url = '/api/templates/{template:id}/cdroms'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{template:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_cdrom()
        return ParseHelper.toSubCollection(TemplateCdRom,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class TemplateDisk(params.Disk, Base):
    def __init__(self, template, disk, context):
        Base.__init__(self, context)
        self.parentclass = template
        self.superclass  =  disk

        #SUB_COLLECTIONS
    def __new__(cls, template, disk, context):
        if disk is None: return None
        obj = object.__new__(cls)
        obj.__init__(template, disk, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, action=params.Action(), async=None, correlation_id=None):
        '''
        @type Action:

        [@param action.storage_domain.id: string]
        [@param action.force: boolean]
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/templates/{template:id}/disks/{disk:id}',
                                {'{template:id}' : self.parentclass.get_id(),
                                 '{disk:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(action),
                                        headers={"Correlation-Id":correlation_id})

    def copy(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param storagedomain.id|name: string
        [@param action.async: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/templates/{template:id}/disks/{disk:id}/copy'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{template:id}' : self.parentclass.get_id(),
                                                                     '{disk:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class TemplateDisks(Base):

    def __init__(self, template , context):
        Base.__init__(self, context)
        self.parentclass = template

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Disks:
        '''

        url = '/api/templates/{template:id}/disks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return TemplateDisk(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                           headers={}).get_disk()

            return TemplateDisk(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Disks:
        '''

        url = '/api/templates/{template:id}/disks'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{template:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_disk()
        return ParseHelper.toSubCollection(TemplateDisk,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class TemplateNic(params.NIC, Base):
    def __init__(self, template, nic, context):
        Base.__init__(self, context)
        self.parentclass = template
        self.superclass  =  nic

        #SUB_COLLECTIONS
    def __new__(cls, template, nic, context):
        if nic is None: return None
        obj = object.__new__(cls)
        obj.__init__(template, nic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/templates/{template:id}/nics/{nic:id}',
                                {'{template:id}' : self.parentclass.get_id(),
                                 '{nic:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param nic.network.id|name: string]
        [@param nic.linked: boolean]
        [@param nic.name: string]
        [@param nic.mac.address: string]
        [@param nic.interface: string]
        [@param nic.port_mirroring.networks.network: collection]
        {
          [@ivar network.id: string]
        }
        [@param correlation_id: any string]

        @return NIC:
        '''

        url = '/api/templates/{template:id}/nics/{nic:id}'
        url = UrlHelper.replace(url, {'{template:id}' : self.parentclass.get_id(),
                                      '{nic:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return TemplateNic(self.parentclass, result, self.context)

class TemplateNics(Base):

    def __init__(self, template , context):
        Base.__init__(self, context)
        self.parentclass = template

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, nic, expect=None, correlation_id=None):

        '''
        @type NIC:

        @param nic.network.id|name: string
        @param nic.name: string
        [@param nic.linked: boolean]
        [@param nic.mac.address: string]
        [@param nic.interface: string]
        [@param nic.port_mirroring.networks.network: collection]
        {
          [@ivar network.id: string]
        }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return NIC:
        '''

        url = '/api/templates/{template:id}/nics'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(nic),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return TemplateNic(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Nics:
        '''

        url = '/api/templates/{template:id}/nics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return TemplateNic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                           headers={}).get_nic()

            return TemplateNic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Nics:
        '''

        url = '/api/templates/{template:id}/nics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{template:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_nic()
        return ParseHelper.toSubCollection(TemplateNic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class TemplatePermission(params.Permission, Base):
    def __init__(self, template, permission, context):
        Base.__init__(self, context)
        self.parentclass = template
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, template, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(template, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/templates/{template:id}/permissions/{permission:id}',
                                {'{template:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class TemplatePermissions(Base):

    def __init__(self, template , context):
        Base.__init__(self, context)
        self.parentclass = template

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/templates/{template:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return TemplatePermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/templates/{template:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return TemplatePermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{template:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return TemplatePermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/templates/{template:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{template:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(TemplatePermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Templates(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, template, expect=None, correlation_id=None):
        '''
        @type Template:

        @param template.vm.id|name: string
        @param template.name: string
        [@param template.memory: long]
        [@param template.cpu.topology.cores: int]
        [@param template.high_availability.enabled: boolean]
        [@param template.os.cmdline: string]
        [@param template.origin: string]
        [@param template.high_availability.priority: int]
        [@param template.timezone: string]
        [@param template.domain.name: string]
        [@param template.type: string]
        [@param template.stateless: boolean]
        [@param template.delete_protected: boolean]
        [@param template.placement_policy.affinity: string]
        [@param template.description: string]
        [@param template.custom_properties.custom_property: collection]
        {
          [@ivar custom_property.name: string]
          [@ivar custom_property.value: string]
        }
        [@param template.os.type: string]
        [@param template.os.boot: collection]
        {
          [@ivar boot.dev: string]
        }
        [@param template.cpu.topology.sockets: int]
        [@param template.os.kernel: string]
        [@param template.display.type: string]
        [@param template.display.monitors: int]
        [@param template.display.allow_override: boolean]
        [@param template.display.smartcard_enabled: boolean]
        [@param template.os.initRd: string]
        [@param template.usb.enabled: boolean]
        [@param template.usb.type: string]
        [@param template.vm.disks.disk: collection]
        {
          [@ivar disk.id: string]
          [@ivar storage_domains.storage_domain: collection]
          {
            [@param storage_domain.id: string]
          }
        }
        [@param template.cpu.cpu_tune.vcpu_pin: collection]
        {
          [@ivar vcpu_pin.vcpu: int]
          [@ivar vcpu_pin.cpu_set: string]
        }
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Template:
        '''

        url = '/api/templates'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(template),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return Template(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Templates:
        '''

        url = '/api/templates'

        if id:
            try :
                return Template(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_template()
            return Template(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Templates:
        '''

        url='/api/templates'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_template()
        return ParseHelper.toCollection(Template,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class User(params.User, Base):
    def __init__(self, user, context):
        Base.__init__(self, context)
        self.superclass = user

        self.tags = UserTags(self, context)
        self.roles = UserRoles(self, context)
        self.permissions = UserPermissions(self, context)

    def __new__(cls, user, context):
        if user is None: return None
        obj = object.__new__(cls)
        obj.__init__(user, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/users/{user:id}',
                                {'{user:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

class UserPermission(params.Permission, Base):
    def __init__(self, user, permission, context):
        Base.__init__(self, context)
        self.parentclass = user
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, user, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(user, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/users/{user:id}/permissions/{permission:id}',
                                {'{user:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class UserPermissions(Base):

    def __init__(self, user , context):
        Base.__init__(self, context)
        self.parentclass = user

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.role.id: string
          @param permission.data_center.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.cluster.id: string
        Overload 3:
          @param permission.role.id: string
          @param permission.host.id: string
        Overload 4:
          @param permission.role.id: string
          @param permission.storage_domain.id: string
        Overload 5:
          @param permission.role.id: string
          @param permission.vm.id: string
        Overload 6:
          @param permission.role.id: string
          @param permission.vmpool.id: string
        Overload 7:
          @param permission.role.id: string
          @param permission.template.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/users/{user:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return UserPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/users/{user:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return UserPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return UserPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/users/{user:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{user:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(UserPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class UserRole(params.Role, Base):
    def __init__(self, user, role, context):
        Base.__init__(self, context)
        self.parentclass = user
        self.superclass  =  role

        self.permits = UserRolePermits(self, context)

    def __new__(cls, user, role, context):
        if role is None: return None
        obj = object.__new__(cls)
        obj.__init__(user, role, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/users/{user:id}/roles/{role:id}',
                                {'{user:id}' : self.parentclass.get_id(),
                                 '{role:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class UserRolePermit(params.Permit, Base):
    def __init__(self, userrole, permit, context):
        Base.__init__(self, context)
        self.parentclass = userrole
        self.superclass  =  permit

        #SUB_COLLECTIONS
    def __new__(cls, userrole, permit, context):
        if permit is None: return None
        obj = object.__new__(cls)
        obj.__init__(userrole, permit, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/users/{user:id}/roles/{role:id}/permits/{permit:id}',
                                {'{user:id}' : self.parentclass.parentclass.get_id(),
                                 '{role:id}': self.parentclass.get_id(),
                                 '{permit:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class UserRolePermits(Base):

    def __init__(self, userrole , context):
        Base.__init__(self, context)
        self.parentclass = userrole

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permit, expect=None, correlation_id=None):

        '''
        @type Permit:

        @param permit.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permit:
        '''

        url = '/api/users/{user:id}/roles/{role:id}/permits'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{user:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{role:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permit),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return UserRolePermit(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permits:
        '''

        url = '/api/users/{user:id}/roles/{role:id}/permits'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{user:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{role:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return UserRolePermit(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{user:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{role:id}': self.parentclass.get_id()}),
                                           headers={}).get_permit()

            return UserRolePermit(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permits:
        '''

        url = '/api/users/{user:id}/roles/{role:id}/permits'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{user:id}' : self.parentclass.parentclass.get_id(),
                                                                                               '{role:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permit()
        return ParseHelper.toSubCollection(UserRolePermit,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class UserRoles(Base):

    def __init__(self, user , context):
        Base.__init__(self, context)
        self.parentclass = user

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, role, expect=None, correlation_id=None):

        '''
        @type Role:

        @param role.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Role:
        '''

        url = '/api/users/{user:id}/roles'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(role),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return UserRole(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Roles:
        '''

        url = '/api/users/{user:id}/roles'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return UserRole(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                           headers={}).get_role()

            return UserRole(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Roles:
        '''

        url = '/api/users/{user:id}/roles'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{user:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_role()
        return ParseHelper.toSubCollection(UserRole,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class UserTag(params.Tag, Base):
    def __init__(self, user, tag, context):
        Base.__init__(self, context)
        self.parentclass = user
        self.superclass  =  tag

        #SUB_COLLECTIONS
    def __new__(cls, user, tag, context):
        if tag is None: return None
        obj = object.__new__(cls)
        obj.__init__(user, tag, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/users/{user:id}/tags/{tag:id}',
                                {'{user:id}' : self.parentclass.get_id(),
                                 '{tag:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class UserTags(Base):

    def __init__(self, user , context):
        Base.__init__(self, context)
        self.parentclass = user

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, tag, expect=None, correlation_id=None):

        '''
        @type Tag:

        @param tag.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/users/{user:id}/tags'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(tag),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return UserTag(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Tags:
        '''

        url = '/api/users/{user:id}/tags'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return UserTag(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{user:id}': self.parentclass.get_id()}),
                                           headers={}).get_tag()

            return UserTag(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Tags:
        '''

        url = '/api/users/{user:id}/tags'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{user:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_tag()
        return ParseHelper.toSubCollection(UserTag,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class Users(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, user, expect=None, correlation_id=None):
        '''
        @type User:

        @param user.user_name: string
        @param user.domain.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return User:
        '''

        url = '/api/users'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(user),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return User(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Users:
        '''

        url = '/api/users'

        if id:
            try :
                return User(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_user()
            return User(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return Users:
        '''

        url='/api/users'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_user()
        return ParseHelper.toCollection(User,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class VM(params.VM, Base):
    def __init__(self, vm, context):
        Base.__init__(self, context)
        self.superclass = vm

        self.cdroms = VMCdRoms(self, context)
        self.statistics = VMStatistics(self, context)
        self.tags = VMTags(self, context)
        self.nics = VMNics(self, context)
        self.disks = VMDisks(self, context)
        self.reporteddevices = VMReportedDevices(self, context)
        self.snapshots = VMSnapshots(self, context)
        self.permissions = VMPermissions(self, context)

    def __new__(cls, vm, context):
        if vm is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, action=params.Action(), async=None, correlation_id=None):
        '''
        @type Action:

        [@param action.force: boolean]
        [@param action.vm.disks.detach_only: boolean]
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}',
                                {'{vm:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(action),
                                        headers={"Correlation-Id":correlation_id})

    def update(self, correlation_id=None):
        '''
        [@param vm.name: string]
        [@param vm.cluster.id|name: string]
        [@param vm.timezone: string]
        [@param vm.os.boot: collection]
        {
          [@ivar boot.dev: string]
        }
        [@param vm.custom_properties.custom_property: collection]
        {
          [@ivar custom_property.name: string]
          [@ivar custom_property.value: string]
        }
        [@param vm.os.type: string]
        [@param vm.usb.enabled: boolean]
        [@param vm.usb.type: string]
        [@param vm.type: string]
        [@param vm.os.initRd: string]
        [@param vm.display.monitors: int]
        [@param vm.display.type: string]
        [@param vm.display.allow_override: boolean]
        [@param vm.display.smartcard_enabled: boolean]
        [@param vm.os.cmdline: string]
        [@param vm.cpu.topology.cores: int]
        [@param vm.memory: long]
        [@param vm.high_availability.priority: int]
        [@param vm.high_availability.enabled: boolean]
        [@param vm.domain.name: string]
        [@param vm.description: string]
        [@param vm.stateless: boolean]
        [@param vm.delete_protected: boolean]
        [@param vm.cpu.topology.sockets: int]
        [@param vm.placement_policy.affinity: string]
        [@param vm.placement_policy.host.id|name: string]
        [@param vm.origin: string]
        [@param vm.os.kernel: string]
        [@param vm.payloads.payload: collection]
        {
          [@ivar payload.type: string]
          [@ivar payload.file.name: string]
          [@ivar payload.file.content: string]
        }
        [@param vm.cpu.cpu_tune.vcpu_pin: collection]
        {
          [@ivar vcpu_pin.vcpu: int]
          [@ivar vcpu_pin.cpu_set: string]
        }
        [@param correlation_id: any string]

        @return VM:
        '''

        url = '/api/vms/{vm:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return VM(result, self.context)

    def cancelmigration(self, action=params.Action()):
        '''
        @type Action:


        @return Action:
        '''

        url = '/api/vms/{vm:id}/cancelmigration'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={})
        return result

    def detach(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/detach'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def export(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.async: boolean]
        [@param action.exclusive: boolean]
        [@param action.discard_snapshots: boolean]
        [@param action.storage_domain.id|name: string]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/export'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def migrate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.host.id|name: string]
        [@param action.async: boolean]
        [@param action.force: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/migrate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def move(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param action.storage_domain.id|name: string
        [@param action.async: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/move'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def shutdown(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/shutdown'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def start(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.vm.os.initRd: string]
        [@param action.vm.domain.name: string]
        [@param action.vm.placement_policy.host.id|name: string]
        [@param action.vm.placement_policy.affinity: string]
        [@param action.async: boolean]
        [@param action.vm.os.kernel: string]
        [@param action.grace_period.expiry: long]
        [@param action.vm.display.type: string]
        [@param action.vm.stateless: boolean]
        [@param action.vm.os.cmdline: string]
        [@param action.vm.domain.user.username: string]
        [@param action.pause: boolean]
        [@param action.vm.os.boot: collection]
        {
          [@ivar boot.dev: string]
        }
        [@param action.vm.domain.user.password: string]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/start'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def stop(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/stop'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def suspend(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/suspend'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

    def ticket(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/ticket'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

class VMCdRom(params.CdRom, Base):
    def __init__(self, vm, cdrom, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  cdrom

        #SUB_COLLECTIONS
    def __new__(cls, vm, cdrom, context):
        if cdrom is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, cdrom, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/cdroms/{cdrom:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{cdrom:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, async=None, current=None, correlation_id=None):
        '''
        [@param cdrom.file.id: string]
        [@param async: boolean (true|false)]
        [@param current: boolean (true|false)]
        [@param correlation_id: any string]

        @return CdRom:
        '''

        url = '/api/vms/{vm:id}/cdroms/{cdrom:id}'
        url = UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                      '{cdrom:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {'async:matrix':async,'current:matrix':current}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return VMCdRom(self.parentclass, result, self.context)

class VMCdRoms(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, cdrom, expect=None, correlation_id=None):

        '''
        @type CdRom:

        @param cdrom.file.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return CdRom:
        '''

        url = '/api/vms/{vm:id}/cdroms'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(cdrom),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMCdRom(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return CdRoms:
        '''

        url = '/api/vms/{vm:id}/cdroms'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMCdRom(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_cdrom()

            return VMCdRom(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return CdRoms:
        '''

        url = '/api/vms/{vm:id}/cdroms'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_cdrom()
        return ParseHelper.toSubCollection(VMCdRom,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMDisk(params.Disk, Base):
    def __init__(self, vm, disk, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  disk

        self.statistics = VMDiskStatistics(self, context)
        self.permissions = VMDiskPermissions(self, context)

    def __new__(cls, vm, disk, context):
        if disk is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, disk, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, action=params.Action(), async=None, correlation_id=None):
        '''
        @type Action:

        @param action.detach: boolean
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/disks/{disk:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{disk:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        body=ParseHelper.toXml(action),
                                        headers={"Correlation-Id":correlation_id})

    def update(self, correlation_id=None):
        '''
        [@param size: int]
        [@param provisioned_size: int]
        [@param disk.interface: string]
        [@param disk.format: string]
        [@param disk.sparse: boolean]
        [@param disk.bootable: boolean]
        [@param disk.shareable: boolean]
        [@param disk.propagate_errors: boolean]
        [@param disk.wipe_after_delete: boolean]
        [@param correlation_id: any string]

        @return Disk:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}'
        url = UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                      '{disk:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return VMDisk(self.parentclass, result, self.context)

    def activate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/activate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{disk:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def deactivate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/deactivate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{disk:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def move(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        @param storagedomain.id|name: string
        [@param action.async: boolean]
        [@param action.grace_period.expiry: long]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/move'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{disk:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class VMDiskPermission(params.Permission, Base):
    def __init__(self, vmdisk, permission, context):
        Base.__init__(self, context)
        self.parentclass = vmdisk
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, vmdisk, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmdisk, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self):
        '''
        @return None:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/permissions/{permission:id}'

        return self.__getProxy().delete(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                   '{disk:id}': self.parentclass.get_id(),
                                                                   '{permission:id}': self.get_id()}),
                                       headers={'Content-type':None})

class VMDiskPermissions(Base):

    def __init__(self, vmdisk , context):
        Base.__init__(self, context)
        self.parentclass = vmdisk

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission):

        '''
        @type Permission:


        @return Permission:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{disk:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={})

        return VMDiskPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{disk:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMDiskPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{disk:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return VMDiskPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Permissions:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/permissions'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{disk:id}': self.parentclass.get_id()})).get_permission()

        return ParseHelper.toSubCollection(VMDiskPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMDiskStatistic(params.Statistic, Base):
    def __init__(self, vmdisk, statistic, context):
        Base.__init__(self, context)
        self.parentclass = vmdisk
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, vmdisk, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmdisk, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMDiskStatistics(Base):

    def __init__(self, vmdisk , context):
        Base.__init__(self, context)
        self.parentclass = vmdisk

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{disk:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMDiskStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{disk:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return VMDiskStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/disks/{disk:id}/statistics'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{disk:id}': self.parentclass.get_id()})).get_statistic()

        return ParseHelper.toSubCollection(VMDiskStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMDisks(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, disk, expect=None, correlation_id=None):

        '''
        @type Disk:

        Overload 1:
          @param provisioned_size: int
          @param disk.interface: string
          @param disk.format: string
          [@param disk.alias: string]
          [@param disk.name: string]
          [@param disk.size: int]
          [@param disk.sparse: boolean]
          [@param disk.bootable: boolean]
          [@param disk.shareable: boolean]
          [@param disk.propagate_errors: boolean]
          [@param disk.wipe_after_delete: boolean]
          [@param disk.storage_domains.storage_domain: collection]
          {
            [@ivar storage_domain.id|name: string]
          }
        Overload 2:
          @param disk.interface: string
          @param disk.format: string
          @param disk.lun_storage.type: string
          @param disk.lun_storage.logical_unit: collection
          {
            @ivar logical_unit.id: string
            @ivar logical_unit.address: string
            @ivar logical_unit.port: int
            @ivar logical_unit.target: string
          }
          [@param disk.alias: string]
          [@param disk.sparse: boolean]
          [@param disk.bootable: boolean]
          [@param disk.shareable: boolean]
          [@param disk.propagate_errors: boolean]
          [@param disk.wipe_after_delete: boolean]
          [@param disk.storage_domains.storage_domain: collection]
          {
            [@ivar storage_domain.id|name: string]
          }
        Overload 3:
          @param disk.id: string
          [@param disk.active: boolean]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Disk:
        '''

        url = '/api/vms/{vm:id}/disks'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(disk),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMDisk(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Disks:
        '''

        url = '/api/vms/{vm:id}/disks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMDisk(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_disk()

            return VMDisk(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Disks:
        '''

        url = '/api/vms/{vm:id}/disks'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_disk()
        return ParseHelper.toSubCollection(VMDisk,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMNic(params.NIC, Base):
    def __init__(self, vm, nic, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  nic

        self.statistics = VMNicStatistics(self, context)
        self.reporteddevices = VMNicReporteddevices(self, context)

    def __new__(cls, vm, nic, context):
        if nic is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, nic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/nics/{nic:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{nic:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param nic.network.id|name: string]
        [@param nic.linked: boolean]
        [@param nic.name: string]
        [@param nic.mac.address: string]
        [@param nic.interface: string]
        [@param nic.port_mirroring.networks.network: collection]
        {
          [@ivar network.id: string]
        }
        [@param nic.plugged: boolean]
        [@param correlation_id: any string]

        @return NIC:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}'
        url = UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                      '{nic:id}': self.get_id()})

        result = self.__getProxy().update(url=SearchHelper.appendQuery(url, {}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})

        return VMNic(self.parentclass, result, self.context)

    def activate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/activate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{nic:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

    def deactivate(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/deactivate'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{nic:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class VMNicReporteddevice(params.ReportedDevice, Base):
    def __init__(self, vmnic, reporteddevice, context):
        Base.__init__(self, context)
        self.parentclass = vmnic
        self.superclass  =  reporteddevice

        #SUB_COLLECTIONS
    def __new__(cls, vmnic, reporteddevice, context):
        if reporteddevice is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmnic, reporteddevice, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMNicReporteddevices(Base):

    def __init__(self, vmnic , context):
        Base.__init__(self, context)
        self.parentclass = vmnic

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return ReportedDevices:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/reporteddevices'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{nic:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMNicReporteddevice(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{nic:id}': self.parentclass.get_id()}),
                                           headers={}).get_reported_device()

            return VMNicReporteddevice(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return ReportedDevices:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/reporteddevices'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{nic:id}': self.parentclass.get_id()})).get_reported_device()

        return ParseHelper.toSubCollection(VMNicReporteddevice,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMNicStatistic(params.Statistic, Base):
    def __init__(self, vmnic, statistic, context):
        Base.__init__(self, context)
        self.parentclass = vmnic
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, vmnic, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmnic, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMNicStatistics(Base):

    def __init__(self, vmnic , context):
        Base.__init__(self, context)
        self.parentclass = vmnic

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{nic:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMNicStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{nic:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return VMNicStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/nics/{nic:id}/statistics'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{nic:id}': self.parentclass.get_id()})).get_statistic()

        return ParseHelper.toSubCollection(VMNicStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMNics(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, nic, expect=None, correlation_id=None):

        '''
        @type NIC:

        @param nic.name: string
        [@param nic.network.id|name: string]
        [@param nic.linked: boolean]
        [@param nic.mac.address: string]
        [@param nic.interface: string]
        [@param nic.port_mirroring.networks.network: collection]
        {
          [@ivar network.id: string]
        }
        [@param nic.plugged: boolean]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return NIC:
        '''

        url = '/api/vms/{vm:id}/nics'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(nic),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMNic(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Nics:
        '''

        url = '/api/vms/{vm:id}/nics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMNic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_nic()

            return VMNic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Nics:
        '''

        url = '/api/vms/{vm:id}/nics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_nic()
        return ParseHelper.toSubCollection(VMNic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMPermission(params.Permission, Base):
    def __init__(self, vm, permission, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, vm, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/permissions/{permission:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class VMPermissions(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/vms/{vm:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/vms/{vm:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return VMPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/vms/{vm:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(VMPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMReportedDevice(params.ReportedDevice, Base):
    def __init__(self, vm, reporteddevice, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  reporteddevice

        #SUB_COLLECTIONS
    def __new__(cls, vm, reporteddevice, context):
        if reporteddevice is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, reporteddevice, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMReportedDevices(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return ReportedDevices:
        '''

        url = '/api/vms/{vm:id}/reporteddevices'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMReportedDevice(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_reported_device()

            return VMReportedDevice(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return ReportedDevices:
        '''

        url = '/api/vms/{vm:id}/reporteddevices'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()})).get_reported_device()

        return ParseHelper.toSubCollection(VMReportedDevice,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMSnapshot(params.Snapshot, Base):
    def __init__(self, vm, snapshot, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  snapshot

        self.nics = VMSnapshotNics(self, context)
        self.cdroms = VMSnapshotCdroms(self, context)
        self.disks = VMSnapshotDisks(self, context)

    def __new__(cls, vm, snapshot, context):
        if snapshot is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, snapshot, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/snapshots/{snapshot:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{snapshot:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

    def restore(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/restore'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.get_id(),
                                                                     '{snapshot:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})

        return result

class VMSnapshotCdrom(params.CdRom, Base):
    def __init__(self, vmsnapshot, cdrom, context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot
        self.superclass  =  cdrom

        #SUB_COLLECTIONS
    def __new__(cls, vmsnapshot, cdrom, context):
        if cdrom is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmsnapshot, cdrom, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMSnapshotCdroms(Base):

    def __init__(self, vmsnapshot , context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return CdRoms:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/cdroms'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{snapshot:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMSnapshotCdrom(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{snapshot:id}': self.parentclass.get_id()}),
                                           headers={}).get_cdrom()

            return VMSnapshotCdrom(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return CdRoms:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/cdroms'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{snapshot:id}': self.parentclass.get_id()})).get_cdrom()

        return ParseHelper.toSubCollection(VMSnapshotCdrom,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMSnapshotDisk(params.Disk, Base):
    def __init__(self, vmsnapshot, disk, context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot
        self.superclass  =  disk

        #SUB_COLLECTIONS
    def __new__(cls, vmsnapshot, disk, context):
        if disk is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmsnapshot, disk, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMSnapshotDisks(Base):

    def __init__(self, vmsnapshot , context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Disks:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/disks'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{snapshot:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMSnapshotDisk(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{snapshot:id}': self.parentclass.get_id()}),
                                           headers={}).get_disk()

            return VMSnapshotDisk(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Disks:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/disks'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{snapshot:id}': self.parentclass.get_id()})).get_disk()

        return ParseHelper.toSubCollection(VMSnapshotDisk,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMSnapshotNic(params.NIC, Base):
    def __init__(self, vmsnapshot, nic, context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot
        self.superclass  =  nic

        #SUB_COLLECTIONS
    def __new__(cls, vmsnapshot, nic, context):
        if nic is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmsnapshot, nic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMSnapshotNics(Base):

    def __init__(self, vmsnapshot , context):
        Base.__init__(self, context)
        self.parentclass = vmsnapshot

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Nics:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/nics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                                           '{snapshot:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMSnapshotNic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                      '{snapshot:id}': self.parentclass.get_id()}),
                                           headers={}).get_nic()

            return VMSnapshotNic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]

        @return Nics:
        '''

        url = '/api/vms/{vm:id}/snapshots/{snapshot:id}/nics'

        result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}' : self.parentclass.parentclass.get_id(),
                                                                  '{snapshot:id}': self.parentclass.get_id()})).get_nic()

        return ParseHelper.toSubCollection(VMSnapshotNic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMSnapshots(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, snapshot, expect=None, correlation_id=None):

        '''
        @type Snapshot:

        @param snapshot.description: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Snapshot:
        '''

        url = '/api/vms/{vm:id}/snapshots'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(snapshot),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMSnapshot(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Snapshots:
        '''

        url = '/api/vms/{vm:id}/snapshots'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMSnapshot(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_snapshot()

            return VMSnapshot(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Snapshots:
        '''

        url = '/api/vms/{vm:id}/snapshots'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_snapshot()
        return ParseHelper.toSubCollection(VMSnapshot,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMStatistic(params.Statistic, Base):
    def __init__(self, vm, statistic, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  statistic

        #SUB_COLLECTIONS
    def __new__(cls, vm, statistic, context):
        if statistic is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, statistic, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VMStatistics(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/statistics'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMStatistic(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_statistic()

            return VMStatistic(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Statistics:
        '''

        url = '/api/vms/{vm:id}/statistics'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_statistic()
        return ParseHelper.toSubCollection(VMStatistic,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMTag(params.Tag, Base):
    def __init__(self, vm, tag, context):
        Base.__init__(self, context)
        self.parentclass = vm
        self.superclass  =  tag

        #SUB_COLLECTIONS
    def __new__(cls, vm, tag, context):
        if tag is None: return None
        obj = object.__new__(cls)
        obj.__init__(vm, tag, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vms/{vm:id}/tags/{tag:id}',
                                {'{vm:id}' : self.parentclass.get_id(),
                                 '{tag:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class VMTags(Base):

    def __init__(self, vm , context):
        Base.__init__(self, context)
        self.parentclass = vm

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, tag, expect=None, correlation_id=None):

        '''
        @type Tag:

        @param tag.id|name: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Tag:
        '''

        url = '/api/vms/{vm:id}/tags'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(tag),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VMTag(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Tags:
        '''

        url = '/api/vms/{vm:id}/tags'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VMTag(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vm:id}': self.parentclass.get_id()}),
                                           headers={}).get_tag()

            return VMTag(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Tags:
        '''

        url = '/api/vms/{vm:id}/tags'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vm:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_tag()
        return ParseHelper.toSubCollection(VMTag,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VMs(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, vm, correlation_id=None, expect=None):
        '''
        @type VM:

        @param vm.name: string
        @param vm.template.id|name: string
        @param vm.cluster.id|name: string
        [@param vm.quota.id: string]
        [@param vm.timezone: string]
        [@param vm.os.boot: collection]
        {
          [@ivar boot.dev: string]
        }
        [@param vm.custom_properties.custom_property: collection]
        {
          [@ivar custom_property.name: string]
          [@ivar custom_property.value: string]
        }
        [@param vm.os.type: string]
        [@param vm.usb.enabled: boolean]
        [@param vm.usb.type: string]
        [@param vm.type: string]
        [@param vm.os.initRd: string]
        [@param vm.display.monitors: int]
        [@param vm.display.type: string]
        [@param vm.display.allow_override: boolean]
        [@param vm.display.smartcard_enabled: boolean]
        [@param vm.os.cmdline: string]
        [@param vm.cpu.topology.cores: int]
        [@param vm.memory: long]
        [@param vm.high_availability.priority: int]
        [@param vm.high_availability.enabled: boolean]
        [@param vm.domain.name: string]
        [@param vm.description: string]
        [@param vm.stateless: boolean]
        [@param vm.delete_protected: boolean]
        [@param vm.cpu.topology.sockets: int]
        [@param vm.placement_policy.affinity: string]
        [@param vm.placement_policy.host.id|name: string]
        [@param vm.origin: string]
        [@param vm.os.kernel: string]
        [@param vm.disks.clone: boolean]
        [@param vm.payloads.payload: collection]
        {
          [@ivar payload.type: string]
          [@ivar payload.file.name: string]
          [@ivar payload.file.content: string]
        }
        [@param vm.cpu.cpu_tune.vcpu_pin: collection]
        {
          [@ivar vcpu_pin.vcpu: int]
          [@ivar vcpu_pin.cpu_set: string]
        }
        [@param correlation_id: any string]
        [@param expect: 201-created]

        @return VM:
        '''

        url = '/api/vms'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(vm),
                                       headers={"Correlation-Id":correlation_id, "Expect":expect})
        return VM(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return VMs:
        '''

        url = '/api/vms'

        if id:
            try :
                return VM(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_vm()
            return VM(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return VMs:
        '''

        url='/api/vms'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_vm()
        return ParseHelper.toCollection(VM,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

class VersionCaps(params.VersionCaps, Base):
    def __init__(self, versioncaps, context):
        Base.__init__(self, context)
        self.superclass = versioncaps

        #SUB_COLLECTIONS
    def __new__(cls, versioncaps, context):
        if versioncaps is None: return None
        obj = object.__new__(cls)
        obj.__init__(versioncaps, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

class VmPool(params.VmPool, Base):
    def __init__(self, vmpool, context):
        Base.__init__(self, context)
        self.superclass = vmpool

        self.permissions = VmPoolPermissions(self, context)

    def __new__(cls, vmpool, context):
        if vmpool is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmpool, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vmpools/{vmpool:id}',
                                {'{vmpool:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                       headers={"Correlation-Id":correlation_id,"Content-type":None})

    def update(self, correlation_id=None):
        '''
        [@param vmpool.cluster.id|name: string]
        [@param vmpool.template.id|name: string]
        [@param vmpool.name: string]
        [@param vmpool.size: int]
        [@param correlation_id: any string]

        @return VmPool:
        '''

        url = '/api/vmpools/{vmpool:id}'

        result = self.__getProxy().update(url=UrlHelper.replace(url, {'{vmpool:id}': self.get_id()}),
                                          body=ParseHelper.toXml(self.superclass),
                                          headers={"Correlation-Id":correlation_id})
        return VmPool(result, self.context)

    def allocatevm(self, action=params.Action(), correlation_id=None):
        '''
        @type Action:

        [@param action.async: boolean]
        [@param correlation_id: any string]

        @return Action:
        '''

        url = '/api/vmpools/{vmpool:id}/allocatevm'

        result = self.__getProxy().request(method='POST',
                                           url=UrlHelper.replace(url, {'{vmpool:id}': self.get_id()}),
                                           body=ParseHelper.toXml(action),
                                           headers={"Correlation-Id":correlation_id})
        return result

class VmPoolPermission(params.Permission, Base):
    def __init__(self, vmpool, permission, context):
        Base.__init__(self, context)
        self.parentclass = vmpool
        self.superclass  =  permission

        #SUB_COLLECTIONS
    def __new__(cls, vmpool, permission, context):
        if permission is None: return None
        obj = object.__new__(cls)
        obj.__init__(vmpool, permission, context)
        return obj

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def delete(self, async=None, correlation_id=None):
        '''
        [@param async: boolean (true|false)]
        [@param correlation_id: any string]

        @return None:
        '''

        url = UrlHelper.replace('/api/vmpools/{vmpool:id}/permissions/{permission:id}',
                                {'{vmpool:id}' : self.parentclass.get_id(),
                                 '{permission:id}': self.get_id()})

        return self.__getProxy().delete(url=SearchHelper.appendQuery(url, {'async:matrix':async}),
                                        headers={"Correlation-Id":correlation_id,"Content-type":None})

class VmPoolPermissions(Base):

    def __init__(self, vmpool , context):
        Base.__init__(self, context)
        self.parentclass = vmpool

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, permission, expect=None, correlation_id=None):

        '''
        @type Permission:

        Overload 1:
          @param permission.user.id: string
          @param permission.role.id: string
        Overload 2:
          @param permission.role.id: string
          @param permission.group.id: string
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return Permission:
        '''

        url = '/api/vmpools/{vmpool:id}/permissions'

        result = self.__getProxy().add(url=UrlHelper.replace(url, {'{vmpool:id}': self.parentclass.get_id()}),
                                       body=ParseHelper.toXml(permission),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})

        return VmPoolPermission(self.parentclass, result, self.context)

    def get(self, name=None, id=None):

        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return Permissions:
        '''

        url = '/api/vmpools/{vmpool:id}/permissions'

        if id:
            try :
                result = self.__getProxy().get(url=UrlHelper.append(UrlHelper.replace(url, {'{vmpool:id}': self.parentclass.get_id()}),
                                                                   id),
                                               headers={})
                return VmPoolPermission(self.parentclass, result, self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=UrlHelper.replace(url, {'{vmpool:id}': self.parentclass.get_id()}),
                                           headers={}).get_permission()

            return VmPoolPermission(self.parentclass,
                                              FilterHelper.getItem(FilterHelper.filter(result, {'name':name})),
                                              self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)"]
        [@param max: int (max results)]

        @return Permissions:
        '''

        url = '/api/vmpools/{vmpool:id}/permissions'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url=UrlHelper.replace(url=url,
                                                                                           args={'{vmpool:id}': self.parentclass.get_id()}),
                                                                   qargs={'max:matrix':max}),
                                      headers={}).get_permission()
        return ParseHelper.toSubCollection(VmPoolPermission,
                                           self.parentclass,
                                           FilterHelper.filter(result, kwargs),
                                           context=self.context)

class VmPools(Base):
    def __init__(self, context):
        Base.__init__(self, context)

    def __getProxy(self):
        proxy = context.manager[self.context].get('proxy')
        if proxy:
            return proxy
        #This may happen only if sdk was explicitly disconnected
        #using .disconnect() method, but resource instance ref. is
        #still available at client's code.
        raise DisconnectedError

    def add(self, vmpool, expect=None, correlation_id=None):
        '''
        @type VmPool:

        @param vmpool.cluster.id|name: string
        @param vmpool.template.id|name: string
        @param vmpool.name: string
        [@param vmpool.size: int]
        [@param expect: 201-created]
        [@param correlation_id: any string]

        @return VmPool:
        '''

        url = '/api/vmpools'

        result = self.__getProxy().add(url=url,
                                       body=ParseHelper.toXml(vmpool),
                                       headers={"Expect":expect, "Correlation-Id":correlation_id})
        return VmPool(result, self.context)

    def get(self, name=None, id=None):
        '''
        [@param id  : string (the id of the entity)]
        [@param name: string (the name of the entity)]

        @return VmPools:
        '''

        url = '/api/vmpools'

        if id:
            try :
                return VmPool(self.__getProxy().get(url=UrlHelper.append(url, id),
                                                               headers={}),
                                         self.context)
            except RequestError, err:
                if err.status and err.status == 404:
                    return None
                raise err
        elif name:
            result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':'name='+name}),
                                           headers={}).get_vmpool()
            return VmPool(FilterHelper.getItem(result),
                                     self.context)
        else:
            raise MissingParametersError(['id', 'name'])

    def list(self, query=None, case_sensitive=True, max=None, **kwargs):
        '''
        [@param **kwargs: dict (property based filtering)]
        [@param query: string (oVirt engine search dialect query)]
        [@param case_sensitive: boolean (true|false)]
        [@param max: int (max results)]

        @return VmPools:
        '''

        url='/api/vmpools'

        result = self.__getProxy().get(url=SearchHelper.appendQuery(url, {'search:query':query,'case_sensitive:matrix':case_sensitive,'max:matrix':max}),
                                      headers={}).get_vmpool()
        return ParseHelper.toCollection(VmPool,
                                        FilterHelper.filter(result, kwargs),
                                        context=self.context)

