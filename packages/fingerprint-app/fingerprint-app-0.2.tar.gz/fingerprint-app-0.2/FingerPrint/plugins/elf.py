#!/usr/bin/python
#
# LC
#
# base class for the fingerprint plugin classes
#

import os
from subprocess import PIPE, Popen
import StringIO
import re
import logging

logger = logging.getLogger('fingerprint')

from FingerPrint.swirl import SwirlFile, Dependency
from FingerPrint.plugins import PluginManager
from FingerPrint.utils import getOutputAsList

"""This is the implementation for ELF files
Requirements:
 - /usr/lib/rpm/find-requires /usr/lib/rpm/find-provides from rpm
 - lsconfig in the path

"""


class ElfPlugin(PluginManager):
    """this plugin manages all ELF file format"""

    pluginName="ELF"

    #internal
    _ldconfig_64bits = "x86-64"
    _pathCache = {}

    #may in the future we could also use 
    #objdump -p
    _RPM_FIND_DEPS=os.path.dirname( globals()["__file__"] ) + "/find-requires"
    _RPM_FIND_PROV=os.path.dirname( globals()["__file__"] ) + "/find-provides"

    @classmethod
    def getPathToLibrary(cls, dependency, useCache = True, rpath = []):
        """ given a dependency it find the path of the library which provides 
        that dependency """
        soname = dependency.getMajor()
        if useCache and dependency.getName() in cls._pathCache :
            return cls._pathCache[dependency.getName()]
        #for each library we have in the system
        pathToScan = cls.systemPath[:] + rpath
        if "LD_LIBRARY_PATH" in os.environ:
            #we need to scan the LD_LIBRARY_PATH too
            pathToScan += os.environ["LD_LIBRARY_PATH"].split(':')
        # remove duplicate
        pathToScan = list(set(pathToScan))
        for path in pathToScan:
            path = os.path.normpath(path)
            provider = path + '/' + soname
            if os.path.isfile(provider) and \
                cls._checkMinor(provider, dependency.getName()):
                #we found the soname and minor are there return true
                cls._pathCache[dependency.getName()] = provider
                return provider
        for line in getOutputAsList(["/sbin/ldconfig","-p"])[0]:
            # TODO it needs to handle in a better way the hwcap field
            # if dependency is 64 and library is 64 or
            # dependency is 32 and library is 32:
            if len(line) > 0 and soname in line and 'hwcap' not in line and \
                ( (dependency.is64bits() and cls._ldconfig_64bits in line) or \
                (dependency.is32bits() and not cls._ldconfig_64bits in line) ):
                temp = line.split('=>')
                if len(temp) == 2:
                    provider=temp[1].strip()
                    if cls._checkMinor(provider, dependency.getName()):
                        cls._pathCache[dependency.getName()] = provider
                        return provider
        #the dependency could not be located
        return None


    @classmethod
    def _checkMinor(cls, libPath, depName):
        """ check if libPath provides the depName (major and minor) """
        realProvider = os.path.realpath(libPath)
        for line in getOutputAsList(['bash', cls._RPM_FIND_PROV], realProvider)[0]:
            if len(line) > 0 and depName in line:
                return True
        return False


    @classmethod
    def _setDepsRequs(cls, swirlFile, swirl):
        """given a SwirlFile object add all the dependency and all 
        the provides to it """

        # find rpath first
        rpath = getOutputAsList(["bash","-c", "objdump -x %s |grep RPATH|awk '{print $2}'" % swirlFile.path ])[0]
        if len( rpath ) > 0:
            swirlFile.rpaths = rpath[0].split(":")
        #find deps
        for line in getOutputAsList(['bash', cls._RPM_FIND_DEPS], swirlFile.path)[0]:
            if len(line) > 0:
                newDep = Dependency.fromString( line )
                swirlFile.addDependency( newDep )
                p = cls.getPathToLibrary( newDep , useCache = True, rpath = swirlFile.rpaths)
                if not p:
                    # a dependency was not found complain loudly
                    logger.error("Unable to find library %s" % newDep)
                    continue
                if p and not swirl.isFileTracked(p):
                    # p not null and p is not already in swirl
                    cls.getSwirl(p, swirl)
        
        #find provides
        for line in getOutputAsList(['bash', cls._RPM_FIND_PROV], swirlFile.path)[0]:
            if len(line) > 0 :
                newProv = Dependency.fromString(line)
                swirlFile.addProvide(newProv)
        

    @classmethod
    def getSwirl(cls, fileName, swirl):
        """helper function given a filename it return a SwirlFile
        if the given plugin does not support the given fileName should just 
        return None
        ATT: only one plugin should return a SwirlFile for a given file
        """
        fd=open(fileName)
        magic = fd.read(4)
        if magic == '\x7f\x45\x4c\x46':
            #it's an elf see specs
            #http://www.sco.com/developers/gabi/1998-04-29/ch4.eheader.html#elfid
            swirlFile = swirl.createSwirlFile( fileName )
            if swirlFile.staticDependencies :
                # we already did this file, do not do it again
                return swirlFile
            swirlFile.setPluginName( cls.pluginName )
        else:
            #not an elf
            return None
        bitness = fd.read(1)
        if bitness == '\x01':
            swirlFile.set32bits()
        elif bitness == '\x02':
            swirlFile.set64bits()
        fd.seek(11, 1)
        execness = fd.read(2)
        if execness == '\x02\x00':
            # it is an executable
            swirlFile.executable = True
        else:
            swirlFile.executable = False
        swirlFile.type = 'ELF'
        fd.close()
        cls._setDepsRequs(swirlFile, swirl)
        return swirlFile

       
