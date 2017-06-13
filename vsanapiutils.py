#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2016-2017 VMware, Inc.  All rights reserved.

This module defines basic helper functions used in the sample codes
"""

__author__ = 'VMware, Inc'

import sys
import ssl
if (sys.version_info[0] == 3):
   from urllib.request import urlopen
else:
   from urllib2 import urlopen
from xml.dom import minidom

from pyVmomi import vim, vmodl, SoapStubAdapter, VmomiSupport
# Import the vSAN API python bindings
import vsanmgmtObjects

VSAN_API_VC_SERVICE_ENDPOINT = '/vsanHealth'
VSAN_API_ESXI_SERVICE_ENDPOINT = '/vsan'

VSAN_VMODL_VERSION = "vsan.version.version3"

# Construct a stub for vSAN API access using vCenter or ESXi sessions from
# existing stubs. Corresponding vCenter or ESXi service endpoint is required.
# vCenter service endpoint is used by default.
def _GetVsanStub(
      stub, endpoint=VSAN_API_VC_SERVICE_ENDPOINT,
      context=None, version='vim.version.version11'
   ):

   hostname = stub.host.split(':')[0]
   vsanStub = SoapStubAdapter(
      host=hostname,
      path=endpoint,
      version=version,
      sslContext=context
   )
   vsanStub.cookie = stub.cookie
   return vsanStub

# Construct a stub for access vCenter side vSAN APIs.
def GetVsanVcStub(stub, context=None, version=VSAN_VMODL_VERSION):
   return _GetVsanStub(stub, endpoint=VSAN_API_VC_SERVICE_ENDPOINT,
                       context=context, version=version)

# Construct a stub for access ESXi side vSAN APIs.
def GetVsanEsxStub(stub, context=None, version=VSAN_VMODL_VERSION):
   return _GetVsanStub(stub, endpoint=VSAN_API_ESXI_SERVICE_ENDPOINT,
                       context=context, version=version)

# Construct a stub for access ESXi side vSAN APIs.
def GetVsanVcMos(vcStub, context=None, version=VSAN_VMODL_VERSION):
   vsanStub = GetVsanVcStub(vcStub, context, version=version)
   vcMos = {
      'vsan-disk-management-system' : vim.cluster.VsanVcDiskManagementSystem(
                                         'vsan-disk-management-system',
                                         vsanStub
                                      ),
      'vsan-stretched-cluster-system' : vim.cluster.VsanVcStretchedClusterSystem(
                                           'vsan-stretched-cluster-system',
                                           vsanStub
                                        ),
      'vsan-cluster-config-system' : vim.cluster.VsanVcClusterConfigSystem(
                                        'vsan-cluster-config-system',
                                        vsanStub
                                     ),
      'vsan-performance-manager' : vim.cluster.VsanPerformanceManager(
                                      'vsan-performance-manager',
                                      vsanStub
                                   ),
      'vsan-cluster-health-system' : vim.cluster.VsanVcClusterHealthSystem(
                                        'vsan-cluster-health-system',
                                        vsanStub
                                     ),
      'vsan-upgrade-systemex' : vim.VsanUpgradeSystemEx(
                                   'vsan-upgrade-systemex',
                                    vsanStub
                                ),
      'vsan-cluster-space-report-system' : vim.cluster.VsanSpaceReportSystem(
                                              'vsan-cluster-space-report-system',
                                              vsanStub
                                           ),

      'vsan-cluster-object-system' : vim.cluster.VsanObjectSystem(
                                        'vsan-cluster-object-system',
                                        vsanStub
                                        ),
      'vsan-cluster-iscsi-target-system' : vim.cluster.VsanIscsiTargetSystem(
                                              'vsan-cluster-iscsi-target-system',
                                              vsanStub
                                           ),
   }

   return vcMos

# Construct a stub for access ESXi side vSAN APIs.
def GetVsanEsxMos(esxStub, context=None, version=VSAN_VMODL_VERSION):
   vsanStub = GetVsanEsxStub(esxStub, context, version=version)
   esxMos = {
      'vsan-performance-manager' : vim.cluster.VsanPerformanceManager(
                                      'vsan-performance-manager',
                                      vsanStub
                                   ),
      'ha-vsan-health-system' : vim.host.VsanHealthSystem(
                                        'ha-vsan-health-system',
                                        vsanStub
                                     ),
      'vsan-object-system' : vim.cluster.VsanObjectSystem(
                                        'vsan-object-system',
                                        vsanStub
                                     ),
   }
   return esxMos

# Convert a vSAN Task to a Task MO binding to vCenter service.
def ConvertVsanTaskToVcTask(vsanTask, vcStub):
  vcTask = vim.Task(vsanTask._moId, vcStub)
  return vcTask

# Wait for the vCenter task and returns after tasks are completed.
def WaitForTasks(tasks, si):
   pc = si.content.propertyCollector
   taskList = [str(task) for task in tasks]

   # Create filter
   objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
         for task in tasks]
   propSpec = vmodl.query.PropertyCollector.PropertySpec(
         type=vim.Task, pathSet=[], all=True)
   filterSpec = vmodl.query.PropertyCollector.FilterSpec()
   filterSpec.objectSet = objSpecs
   filterSpec.propSet = [propSpec]
   filter = pc.CreateFilter(filterSpec, True)

   try:
      version, state = None, None

      # Loop looking for updates till the state moves to a completed state.
      while len(taskList):
         update = pc.WaitForUpdates(version)
         for filterSet in update.filterSet:
            for objSet in filterSet.objectSet:
               task = objSet.obj
               for change in objSet.changeSet:
                  if change.name == 'info':
                     state = change.val.state
                  elif change.name == 'info.state':
                     state = change.val
                  else:
                     continue

                  if not str(task) in taskList:
                     continue

                  if state == vim.TaskInfo.State.success:
                     # Remove task from taskList
                     taskList.remove(str(task))
                  elif state == vim.TaskInfo.State.error:
                     raise task.info.error
         # Move to next version
         version = update.version
   finally:
      if filter:
         filter.Destroy()

# Get the VMODL version by checking the existence of vSAN namespace.
def GetLatestVmodlVersion(hostname):
   try:
      vsanVmodlUrl = 'https://%s/sdk/vsanServiceVersions.xml' % hostname
      if (hasattr(ssl, '_create_unverified_context') and
         hasattr(ssl, '_create_default_https_context')):
         ssl._create_default_https_context = ssl._create_unverified_context
      xmldoc = minidom.parse(urlopen(vsanVmodlUrl, timeout=5))
      for element in xmldoc.getElementsByTagName('name'):
         if (element.firstChild.nodeValue == "urn:vsan"):
            return VmomiSupport.newestVersions.Get('vsan')
         else:
            return VmomiSupport.newestVersions.Get('vim')
   except Exception as e:
      # Any exception like failing to open the XML or failed to parse the
      # the content should lead to the returning of namespace with vim.
      return VmomiSupport.newestVersions.Get('vim')
