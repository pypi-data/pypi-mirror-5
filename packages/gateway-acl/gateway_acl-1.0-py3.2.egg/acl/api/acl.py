'''
Created on Aug 27, 2013

@package: gateway acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for ACL access.
'''

from .access import Access, Entry, Property
from .filter import Filter
from ally.api.config import DELETE, UPDATE, prototype
from ally.api.option import SliceAndTotal # @UnusedImport
from ally.api.type import Iter
from ally.support.api.util_service import modelId
import abc # @UnusedImport

# --------------------------------------------------------------------

class IAclPrototype(metaclass=abc.ABCMeta):
    '''
    The ACL access prototype service used for allowing accesses based on other entities.
    '''
    
    @prototype
    def getAcls(self, accessId:Access, **options:SliceAndTotal) -> lambda p: Iter(modelId(p.ACL)):
        '''
        Provides the ACL objects for the provided access id.
        
        @param accessId: integer
            The access id to provide the ACL for.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(ACL.identifier)
            An iterator containing the ACL objects identifiers.
        '''

    @prototype    
    def getAccesses(self, identifier:lambda p: p.ACL, **options:SliceAndTotal) -> Iter(Access.Id):
        '''
        Provides the allowed access for the ACL object identifier.
        
        @param identifier: object
            The ACL object identifier to provide the access for.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(Access.Id)
            An iterator containing the access ids.
        '''
    
    @prototype
    def getEntriesFiltered(self, identifier:lambda p: p.ACL, accessId:Access) -> Iter(Entry.Position):
        '''
        Provides the filtered entries position for the ACL object identifier and access id.
        
        @param identifier: object
            The ACL object identifier to provide the filtered entries for.
        @param accessId: integer
            The access id.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(Entry.Position)
            An iterator containing the entries positions that are filtered.
        '''
        
    @prototype
    def getEntryFilters(self, identifier:lambda p: p.ACL, accessId:Access, position:Entry) -> Iter(Filter.Name):
        '''
        Provides the filters for the ACL object identifier with access and entry position.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param entryPosition: integer
            The entry position.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(Filter.Name)
            An iterator containing the filters.
        '''
        
    @prototype
    def getPropertiesFiltered(self, identifier:lambda p: p.ACL, accessId:Access) -> Iter(Property.Name):
        '''
        Provides the filtered properties for the ACL object identifier and access id.
        
        @param identifier: object
            The ACL object identifier to provide the filtered properties for.
        @param accessId: integer
            The access id.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(Property.Name)
            An iterator containing the property names that are filtered.
        '''
        
    @prototype
    def getPropertyFilters(self, identifier:lambda p: p.ACL, accessId:Access, propName:Property) -> Iter(Filter.Name):
        '''
        Provides the filters for the ACL object identifier with access and property name.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param propertyName: string
            The property name.
        @param options: key arguments
            The result iteration options.
        @return: Iterable(Filter.Name)
            An iterator containing the filters.
        '''
    
    @prototype
    def addAcl(self, identifier:lambda p: modelId(p.ACL), accessId:Access.Id):
        '''
        Adds a new access for the ACL object.
        The ACL object will also propagate to the shadow, shadowing and shadowed accesses.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id to add.
        '''
        
    @prototype(method=DELETE)
    def remAcl(self, identifier:lambda p: p.ACL, accessId:Access) -> bool:
        '''
        Removes the access for ACL object.
        The ACL object will also propagate to the shadow, shadowing and shadowed accesses.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id to remove.
        @return: boolean
            True if a ACL object has been successfully removed, False otherwise. 
        '''
    
    @prototype
    def addEntryFilter(self, identifier:lambda p: modelId(p.ACL), accessId:Access.Id,
                       entryPosition:Entry.Position, filterName:Filter.Name):
        '''
        Adds a filter to a ACL object access entry.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param entryPosition: integer
            The entry position.
        @param filterName: string
            The filter name.
        '''
        
    @prototype(method=DELETE)
    def remEntryFilter(self, identifier:lambda p: p.ACL, accessId:Access.Id,
                       entryPosition:Entry, filterName:Filter.Name) -> bool:
        '''
        Removes an filter from the ACL object access entry.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param entryPosition: integer
            The entry position.
        @param filterName: string
            The filter name.
        @return: boolean
            True if a filter has been successfully removed for entry, False otherwise.
        '''
        
    @prototype
    def addPropertyFilter(self, identifier:lambda p: modelId(p.ACL), accessId:Access.Id,
                          propertyName:Property, filterName:Filter.Name):
        '''
        Adds a filter to a ACL object access property.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param propertyName: string
            The property name.
        @param filterName: string
            The filter name.
        '''
        
    @prototype(method=DELETE)
    def remPropertyFilter(self, identifier:lambda p: p.ACL, accessId:Access.Id,
                          propertyName:Property, filterName:Filter.Name) -> bool:
        '''
        Removes an filter from the ACL object access property.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param entryPosition: integer
            The entry position.
        @param propertyName: string
            The property name.
        @return: boolean
            True if a filter has been successfully removed for property, False otherwise.
        '''
    
    @prototype(method=UPDATE)
    def registerFilter(self, identifier:lambda p: modelId(p.ACL), accessId:Access.Id,
                       filterName:Filter.Name, place:str=None) -> bool:
        '''
        Register a new filter for access, the place is used only when the filter matches multiple entries in the access
        path, the location of the filter will be marked '@'. The register will also propagate to the shadow, shadowing and 
        shadowed accesses.
        
        @param identifier: object
            The ACL object identifier.
        @param accessId: integer
            The access id.
        @param filterName: string
            The filter name.
        @param place: string
            The filter place.
        @return: boolean
            True if a filter has been successfully registered, False otherwise.
        '''
