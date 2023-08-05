"""TestTrack Python Interface

`TestTrack Pro`_ is the Issue Management software from `Seapine Software`_.

`TestTrack`_ is a registered trademark of `Seapine Software`_.

This library uses the `suds`_ library to talk to the TestTrack SDK SOAP API
and includes some helpful extensions for managing your client code and
interactions.

Seapine documentation provides a number of python samples for interacting
with the `TestTrack SOAP API`_, but there are a number of problems with their
`TestTrack Python Tutorial`_.

The sample tutorial has syntax and functional errors, and does not work with
the latest versions of `TestTrack`_ and `suds`_. Even with the versions of
python and the `suds`_ library mentioned, the code will crash due to WSDL
non-compliance issues when custom fields are used.

This module addresses these issues as well as provides a more managed interface
to simplify development.


TestTrack API 'cookie' Management
---------------------------------

The `TestTrack SDK`_ SOAP API uses a client cookie argument on almost every
call. You end up writting code where every API call starts with ``cookie``.

.. code:: python
    
    # What object types can I query?
    adt = server.service.getTableList(cookie)
    
    # What field data is available for a given object type?
    atc = server.service.getColumnsForTable(cookie, tablename)
    
    # What filters are available?
    af = server.service.getFilterList(cookie)
    
    # Get defect 42
    d = server.service.getDefect(cookie, 42)

    # log out
    server.service.DatabaseLogoff(cookie)

You can view this argument as an implicit self for this python interface to
that API. That is you do not need to supply the cookie argument, as it will
be managed for you in the client object.

.. code:: python

    import testtrackpro
    ttp = testtrackpro.TTP('http://hostname/', 'Project', 'username', 'password')
    adt = ttp.getTableList()
    atc = ttp.getColumnsForTable(tablename)
    defect = ttp.getDefect(1) # maps to getDefect(cookie, 42)
    ttp.DatabaseLogoff()

Python Contexts
---------------

Due to the implicit write locks (with 15 min timeout) on all edit API calls,
clients normally would have to be very careful to trap all exceptions and
capture any and all locked entities and un lock them as part of the exception
handling. Thankfully python provides contexts via the 'with' statement that
are designed for exactly this problem.

All `suds`_ objects returned be API calls which start with the string 'edit'
will return `suds`_ objects which have been extended to be python contexts
which can be used with the ``with`` statement:

.. code:: python

    with ttp.editDefect(42) as defect:
        defect.priority = "Immediate"

At the end of the ``with`` block, a call to ``ttp.saveDefect(defect)`` will be
made automatically, saving any pending edits, and releasing the lock.
Explicit calls to ``saveDefect`` or ``cancelSaveDefect`` also work within
the context block.

If an exception occurs, then a call to ``ttp.cancelSaveDefect(defect.recordid)``
will be made automatically to release the lock, without saving the defect.

Also the TTP instance object is also a context object, and will log the session
out when used in a ``with`` statement.

.. code:: python

    with testtrackpro.TTP('http://hostname/', 'Project', 'username', 'password') as ttp:
        defect = ttp.getDefect(42)
    ## ttp.DatabaseLogOff() implicitly called on success or error




.. _suds: https://fedorahosted.org/suds/
.. _suds plugins: https://fedorahosted.org/suds/wiki/Documentation#PLUGINS
.. _Seapine Software: http://www.seapine.com/
.. _TestTrack: http://www.seapine.com/testtrack.html
.. _TestTrack Pro: http://www.seapine.com/ttpro.html
.. _TestTrack SOAP API: http://labs.seapine.com/TestTrackSDK.php
.. _TestTrack SDK: http://labs.seapine.com/TestTrackSDK.php
.. _TestTrack Python Tutorial: http://labs.seapine.com/wiki/index.php/TestTrack_SOAP_SDK_Tutorial_-_Python


Module Documentation
--------------------

"""
import logging
import re
import suds
import contextlib
import functools
import urlparse

## Exception Error Transformations
import urllib2 #.URLError
import xml.sax._exceptions  #.SAXParseException

## Deal with TestTrackPro WSDL non-conformities
import suds.plugin     ## cleanup TestTrack data vs dateTime WSDL errors
import suds.mx.encoded ## monkey patch for polymorphic arrays

__version__ = [0,1,1]
__version_string__ = '.'.join(str(x) for x in __version__)

__author__ = 'Doug Napoleone'
__email__ = 'doug.napoleone+testtrackpro@gmail.com'


_bad_date_as_datetime_re = re.compile(
    '\<element name="(?P<name>date(?!time)[a-z]+|[a-z]+date|date)" type="xsd:dateTime"')
_bad_date_as_datetime_replace = '<element name="\g<name>" type="xsd:date"'

class _TTPWSDLFixPlugin(suds.plugin.DocumentPlugin):
    """There is a very bad bug in the TestTrack WSDL. There are a number
    of entries that set the type to be 'dateTime' when the data returned
    is always just of type 'date'. This causes SUDS to crash in parsing
    the result (like for a getDefect!) To fix this we use a plugin
    that will pre-processes the WSDL result. We are also not using
    the cache for loading the WSDL because of this, so we do not cause
    problems for other clients, just in case.
    """
    def loaded(self, context):
        if not context.url.endswith('ttsoapcgi.wsdl'):
            return
        context.document = _bad_date_as_datetime_re.sub(
            _bad_date_as_datetime_replace, context.document)

_ttpwsdlfixplugin = _TTPWSDLFixPlugin()



class TTPAPIError(Exception):
    """Base Exception for all API errors.
    """
    pass

class TTPConnectionError(TTPAPIError):
    """Errors communicating with the TestTrack SOAP Service.
    """
    pass

class TTPLogonError(TTPAPIError):
    """Errors with authentication against the TestTrack SOAP Service.
    """
    pass


class TTP(object):
    """Client for communicating with the TestTrack SOAP Service.

    :param str url: [required] URL to the TestTrack SOAP WSDL File, or CGI EXE.
                    should be a url which looks like
                    ``http://127.0.0.1/ttsoapcgi.wsdl`` or can be the base
                    website url ``http://hostname/``.
    :param str database_name: Name of the database (Project) to login to.
                    May be supplied later in the :py:meth:`DatabaseLogon` or
                    :py:meth:`ProjectLogon` methods.
    :param str username: Username to authenticate with.
                    May be supplied later in the :py:meth:`DatabaseLogon` or
                    :py:meth:`ProjectLogon` methods.    
    :param str password: Password to authenticate with.
                    May be supplied later in the :py:meth:`DatabaseLogon` or
                    :py:meth:`ProjectLogon` methods.
    :param long cookie: Cookie value from another SOAP client session. Useful
                    for cloning a client session. If you use this argument,
                    you should not supply the ``database_name``, ``username``,
                    or ``password`` arguments.
    :param list plugins: List of optional `suds plugins`_.
    """
    def __init__(self, url,
                 database_name=None, username=None, password=None,
                 cookie=None, plugins=None):
        self.__method_cache = {}
        if not url.endswith('ttsoapcgi.wsdl'):
            if url.endswith('ttsoapcgi.exe'):
                url = urlparse.urlunsplit(urlparse.urlparse(url)[:2]+('',)*3)
            if not url.endswith('/'):
                url += '/'
            url += 'ttsoapcgi.wsdl'
        self._wsdl_url = url
        self._cookie = cookie
        self._database_name = database_name
        self._username = username
        self._password = password
        self._client = None
        
        if not plugins:
            plugins = []
        plugins.append(_ttpwsdlfixplugin)
        
        try:
            self._client = suds.client.Client(
                self._wsdl_url, cache=None, plugins=plugins)
        except urllib2.URLError, e:
            raise TTPConnectionError(e)
        except xml.sax._exceptions.SAXParseException, e:
            raise TTPConnectionError(
                "Library could not connect to the TestTrackPro Soap API.  "
                "Either this installation of TestTrackPro does not support "
                "the API, or the url, %s, is incorrect.\n\nError: %s" % (
                    self._wsdl_url, e))

        if not cookie and database_name and username and password:
            self.DatabaseLogon()

    def _call_method(self, method, *args, **kwdargs):
        try:
            return method(self._cookie, *args, **kwdargs)
        except urllib2.URLError, e:
            raise TTPConnectionError(e)
        except suds.WebFault, e:
            raise TTPAPIError(e)
    
    def _call_context_method(self, method_name, table, modifier, method,
                             entity, *args, **kwdargs):
        ## allow for non-context entities for save and record id's for cancel
        context = None
        if hasattr(entity, '__context__'):
            context = self._get_edit_context(entity)
            if context.table != table:
                raise TTPAPIError("Wrong type. Calling "+method_name+
                                  ' on a '+context.cname+' '+modifier+'.')
        res = self._call_method(method, entity, *args, **kwdargs)
        if context:
            context._locked = False
        return res

    def _get_edit_context(self, entity):
        if not hasattr(entity, '__context__'):
            raise TTPAPIError("entity does not have an edit context.")
        context = entity.__context__()
        if context._ttp is not self:
            raise TTPAPIError("entity is not from this client instance.")
        return context
    
    def _build_partial(self, method_name):
        try:
            method = getattr(self._client.service, method_name)
        except suds.MethodNotFound, e:
            raise TTPAPIError(e)
        return functools.partial(self._call_method, method)
        
    def __build_method(self, method_name, method):
        if method_name.startswith('edit'):
            return functools.partial(_TTPEditContext.call_method,
                                     self, method_name, method)
        if method_name.startswith('save'):
            return functools.partial(self._call_context_method,
                    method_name, method_name[4:], 'entity', method)
        if method_name.startswith('cancelSave'):
            return functools.partial(self._call_context_method,
                    method_name, method_name[10:], 'recordid', method)
        return functools.partial(self._call_method, method)

    def __getattr__(self, name):
        if name.startswith('__'):
            ## prevents people from accessing '__len__' and other names which
            ## would overload things badly. Access through _client for those
            raise AttributeError("'%s' Object has no such attribute '%s'" %
                                 self.__class__.__name__, name)
        try:
            if not self.__method_cache.has_key(name):
                method = getattr(self._client.service, name)
                self.__method_cache[name] = self.__build_method(name, method)
        except suds.MethodNotFound, e:
            raise TTPAPIError(e)
        return self.__method_cache[name]
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.DatabaseLogoff(ignore_exceptions=True)
        
    def create(self, name):
        """Factory Creation for TTPAPI structures
        
        :param str name: SOAP Entity type name.
        
        .. code:: python
        
            ## Create a new defect
            # Create the CDefect object.
            defect = ttp.create("CDefect")
            #suds doesn't automatically initialize the record id
            defect.recordid = 0;
            defect.summary = "This is a new defect"
            defect.product = "My Product"
            defect.priority = "Immediate"
            
            # Add the defect to TestTrack.
            lNewNum = ttp.addDefect(defect)        
            
            
            ## Create a new project
            project = ttp.create("CProject")
            project.database = ttp.create("CDatabase")
            project.database.name = "MyProject"
            project.options = ttp.create("ArrayOfCProjectDataOption")
            project.options.append(ttp.create("CProjectDataOption"))
            project.options.append(ttp.create("CProjectDataOption"))
            project.options.append(ttp.create("CProjectDataOption"))
            project.options[0].name = "TestTrack Pro"  # add TTP functionality.
            project.options[1].name = "TestTrack TCM"  # add TCM functionality.
            project.options[2].name = "TestTrack RM"   # add RM functionality.
            
            # Add the project to TestTrack.
            ttp.ProjectLogon(project, username, password)
        
        """
        return self._client.factory.create(name)
    
    def save(self, entity, *args, **kwdargs):
        """Save the edit locked context entity.
        
        :param CType entity: edit entity returned by a editXXXX method call.
        
        This is handy when you have a an entity but can not easilly get to it's
        type programatically. This is useful when you recieve polymorphic
        array data back from the TestTrack SOAP API.
    
        In ortherwords you can do this:
        
        .. code:: python
        
            with ttp.editDefect(a) as defecta, ttp.editDefect(b) as defectb:
                defecta.something = "value"
                ttp.save(defect) ## release the lock immediatly
                defectb.other = defecta.other
            ## defectb is saved
        
        Calling ``ttp.saveDefect(defecta)`` is also safe and
        will prevent the call to ``saveDefect(defecta)`` at the end of the
        context block.
        
        .. WARNING:: If you are using edit contexts then calls to
                     ``saveDefect`` with a ``CDefect`` for the same defect
                     from a different API call will result in ``saveDefect``
                     being called again at the end of the context causing
                     an error.
                     
        Example of errorful code:
        
        .. code:: python
        
            def bad():
                getdefect = ttp.getDefect(24)
                with ttp.editDefectBeRecordId(getdefect.recordid) as defect:
                    getdefect.priority = "Immediate"
                    ttp.saveDefect(getdefect)
                ## at this point saveDefect(defect) will be called and will
                ## cause an error as there is no longer an edit lock on
                ## the defect.
        
        Correct way:
        
        .. code:: python
        
            def good(recordid):
                with ttp.editDefectByRecordId(recordid) as defect:
                    ttp.cancelSave(defect)
                ## or
                with ttp.editDefectByRecordId(recordid) as defect:
                    ttp.cancelSaveDefect(defect.recordid)
        """
        return self._get_edit_context(entity).save(*args, **kwdargs)
        
    def cancelSave(self, entity):
        """Cancel the save of the edit locked context entity.
        
        :param CType entity: edit entity returned by a editXXXX method call.
        
        This is handy when you have a an entity but can not easilly get to it's
        type programatically. This is useful when you recieve polymorphic
        array data back from the TestTrack SOAP API.
    
        In ortherwords you can do this:
        
        .. code:: python
        
            with ttp.editDefect(defectnum) as defect:
                defect.something = "value"
                if badthing:
                    ttp.cancelSave(defect)
        
        Calling ``ttp.cancelSaveDefect(defect.recordid)`` is also safe and
        will prevent the call to ``saveDefect`` at the end of the context
        block.
        
        .. WARNING:: If you are using edit contexts then calls to
                     ``cancelSaveDefect`` with a ``recordid`` for the entity
                     in the context which comes from a different structure
                     will cause an error.
                     
        Example of errorful code:
        
        .. code:: python
        
            def bad(recordid):
                with ttp.editDefectBeRecordId(recordid) as defect:
                    ttp.cancelSaveDefect(recordid) ## bad
                ## at this point saveDefect(defect) will be called
        
        Correct way:
        
        .. code:: python
        
            def good(recordid):
                with ttp.editDefectByRecordId(recordid) as defect:
                    ttp.cancelSave(defect)
                ## or
                with ttp.editDefectByRecordId(recordid) as defect:
                    ttp.cancelSaveDefect(defect.recordid)
        """
        return self._get_edit_context(entity).cancelSave()
        
    def getProjectList(self, username=None, password=None):
        """Return a list of CProject entities which the user has access to
        on the server.
        
        :param str username: Username to authenticate with. If not supplied,
                    and one was supplied on client construction, the client
                    stored version will be used. This will not update the
                    client state.
        :param str password: PAssword to authenticate with. If not supplied,
                    and one was supplied on client construction, the client
                    stored version will be used. This will not update the
                    client state.

        The ``username`` and ``password`` are only required if
        they were not supplied on client creation. If supplied they will NOT
        replace the client stored username, password, or client cookie.
        """
        if not username and self._username:
            username = self._username
        if not password and self._password:
            password = self._password
        if not username or not password:
            raise TTPAPIError("Must supply a username and password")
        
        try:
            result = self._client.service.getProjectList(username, password)
        except urllib2.URLError, e:
            raise TTPConnectionError(e)
        except suds.WebFault, e:
            raise TTPLogonError(e)
        return result

    def ProjectLogon(self, CProject=None, username=None, password=None):
        """Logon to the SOAP API and retrieve a new client cookie.
        
        :param CProject CProject: CProject entity describing a TestTrack
                        Project Database. It is recommended to use the
                        :py:meth:`getProjectList` method to retrieve a
                        valid CProject entity.
        :param str username: Username to authenticate with. If supplied, this
                        will update the client stored ``username``. If not
                        supplied, it will use the client stored value if one
                        exists, and error otherwise.
        :param str password: Password to authenticate with. If supplied, this
                        will update the client stored ``username``. If not
                        supplied, it will use the client stored value if one
                        exists, and error otherwise.

        The appropriate CProject entity can be retrieved using the
        :py:meth:`getProjectList` method, of constructing one using the
        :py:meth:`create` method.
        
        If the client is currently logged on, it will first logoff. If the
        ``username`` and or ``password`` are supplied they will update the
        client stored versions of these values. If they are not supplied, then
        the versions supplied on construction will be used.
        
        This is now the prefered way to logon to TestTrack now that the
        :py:meth:`DatabaseLogon` method has been depricated.
        
        """
        if self._cookie:
            self.DatabaseLogoff()
        database_name = CProject.database.name
        if database_name:
            self._database_name = database_name
        if username:
            self._username = username
        if password:
            self._password = username
        if not self._database_name or not self._username or not self._password:
            raise TTPAPIError(
                "Must supply a valid CProject, username, and password.")
        try:
            self._cookie = self._client.service.ProjectLogon(
                CProject, self._username, self._password)
        except urllib2.URLError, e:
            raise TTPConnectionError(e)
        except suds.WebFault, e:
            raise TTPLogonError(e)
            
    def DatabaseLogon(self, database_name=None, username=None, password=None):
        """Logon to the SOAP API and retrieve a new client cookie.
        
        :param str database_name: Project database name to login to.
        :param str username: Username to authenticate with. If supplied, this
                        will update the client stored ``username``. If not
                        supplied, it will use the client stored value if one
                        exists, and error otherwise.
        :param str password: Password to authenticate with. If supplied, this
                        will update the client stored ``username``. If not
                        supplied, it will use the client stored value if one
                        exists, and error otherwise.
        
        If the client is currently logged on, it will first logoff. If the
        ``username`` and or ``password`` are supplied they will update the
        client stored versions of these values. If they are not supplied, then
        the versions supplied on construction will be used.
        
        .. warning:: The :py:meth:`DatabaseLogon` API method has been
                     depricated by Seapine, and should no longer be used.
                     The :py:meth:`ProjectLogon` API method should be used
                     instead.
        """
        if self._cookie:
            self.DatabaseLogoff()
        if database_name:
            self._database_name = database_name
        if username:
            self._username = username
        if password:
            self._password = username
        if not self._database_name or not self._username or not self._password:
            raise TTPAPIError(
                "Must supply a valid database_name, username, and password.")
        try:
            self._cookie = self._client.service.DatabaseLogon(
                self._database_name, self._username, self._password)
        except urllib2.URLError, e:
            raise TTPConnectionError(e)
        except suds.WebFault, e:
            raise TTPLogonError(e)
            
    def DatabaseLogoff(self, ignore_exceptions=False):
        """Log out of the SOAP API session, and release the stored client
        cookie.
        
        :param bool ignore_exceptions: Set this to true to ignore connection
                        and authentication based API errors.
        
        It can be useful to ignore connection and authenticaiton based errors
        when logging out, especially when using the client as a context.
        If there was an error communicating with the client, we want to ignore
        further errors due to the implicit logoff at the end of the context
        to preserve the ogitional initial connection error.
        """
        if not self._cookie or not self._client:
            return
        try:
            self._client.service.DatabaseLogoff(self._cookie)
            self._cookie = None
        except Exception, e:
            self._cookie = None
            if str(e) != "Server raised fault: 'Session Dropped.'":
                if not ignore_exceptions:
                    raise TTPLogonError(e)
                else:
                    logging.warn(
                            "Exception while attempting to logout "
                            "with a call to: DatabaseLogoff\dError: " + str(e))
    
class _long(long):
    pass

class _TTPEditContext(object):
    
    @classmethod
    def call_method(cls, ttp, method_name, method, *args, **kwdargs):
        context = cls(ttp, method_name, method, *args, **kwdargs)
        entity = context.entity
        entity.__enter__ = context.__enter__
        entity.__exit__ = context.__exit__
        entity.__context__ = context.__context__
        entity.recordid = _long(entity.recordid)
        entity.recordid.__context__ = context.__context__
        return entity
    
    def __init__(self, ttp, method_name, method, *args, **kwdargs):
        self._locked = False
        self._ttp = ttp
        self._method_name = method_name
        if method_name.endswith('ByRecordID'):
            self._editbyid_name = method_name
            self._edit_name = method_name[:-10]
        else:
            self._editbyid_name = method_name + 'ByRecordID'
            self._edit_name = method_name
        self._table = self._edit_name[4:]
        self._name = 'C' + self._table
        self._cancel_name = 'cancelSave' + self._table
        self._save_name = 'save' + self._table
        self._save = ttp._build_partial(self._save_name)
        self._cancel = ttp._build_partial(self._cancel_name)
        self._entity = ttp._call_method(method, *args, **kwdargs)
        self._locked = True
    
    def __context__(self):
        return self
    
    def __enter__(self):
        return self._entity
    
    def __exit__(self, exc_type, exc_value, traceback):
        if not self._locked:
            return

        if exc_type:
            try:
                self.cancelSave()
            except Exception, e:
                logging.warn(
                    "Exception while attempting to release an edit lock "
                    "with a call to: " + self._cancel_name +
                    "\n    Error: " + str(e))
        else:
            try:
                self.save()
            except Exception, e:
                logging.warn(
                    "Exception while attempting to release an edit lock "
                    "with a call to: " + self._save_name +
                    "\n    Error: " + str(e))
                try:
                    self.cancelSave()
                except Exception, ex:
                    logging.warn(
                        "Exception while attempting to release an edit lock "
                        "with a call to: " + self._cancel_name +
                        "\n    After a failed call to: " + self._save_name +
                        "\n    Error: " + str(ex))
                ## re-raise the exception on the save
                raise e
    
    def __getattr__(self, name):
        return getattr(self._entity, name)

    def __setattr__(self, name, value):
        if not name.startswith('_') and hasattr(self._entity, name):
            return setattr(self._entity, name, value)
        return object.__setattr__(self, name, value)
    
    @property   
    def entity(self):
        return self._entity
    
    @property
    def table(self):
        return self._table
    
    @property
    def cname(self):
        return self._name
    
    def save(self, *args, **kwdargs):
        #print self._save_name,
        if not self._locked:
            #print "already unlocked"
            return
        #print "unlocking"
        res = self._save(self._entity,*args,**kwdargs)
        self._locked = False
        return res
        
    def cancelSave(self):
        #print self._cancel_name,
        if not self._locked:
            #print "already unlocked"
            return
        #print "unlocking"
        res = self._cancel(self._entity.recordid)
        self._locked = False
        return res
    
def _polymprphic_cast(self, content):
    """TestTrack WSDL has polymorphic arrays.
    That is it has a CEntityArray of SOAP Array Type CEntity. It then will
    return CEntityArrays that contain entities which inherit from CEntity in
    violation of Section 5 of the SOAP Standard. This is not a problem for
    suds to extract the data, but it is a major problem for suds to encode
    and send such arrays.
    
    So this is a replacement for the cast operation on encoding that we
    monkey patch into the appropriate class in suds. We double check the
    sxtype metadata to make sure it matches the object class instead of
    relyng on it matching the parent array element type. If it does not
    match, then we find the proper one and set that.
    """
    
    aty = content.aty[1]
    resolved = content.type.resolve()
    array = suds.mx.encoded.Factory.object(resolved.name)
    array.item = []
    query = suds.mx.encoded.TypeQuery(aty)
    ref = query.execute(self.schema)
    if ref is None:
        raise suds.mx.encoded.TypeNotFound(qref)
    for x in content.value:
        if isinstance(x, (list, tuple)):
            array.item.append(x)
            continue
        if isinstance(x, suds.mx.encoded.Object):
            md = x.__metadata__
            ## removing:
            #md.sxtype = ref
            ## and replacing with:
            polyname = x.__class__.__name__
            if ref.name == polyname:
                md.sxtype = ref
            else:
                query = suds.mx.encoded.TypeQuery((polyname, aty[1]))
                polyref = query.execute(self.schema)
                md.sxtype = polyref
            ## end replacement
            array.item.append(x) 
            continue
        if isinstance(x, dict):
            x = suds.mx.encoded.Factory.object(ref.name, x)
            md = x.__metadata__
            md.sxtype = ref
            array.item.append(x) 
            continue
        x = suds.mx.encoded.Factory.property(ref.name, x)
        md = x.__metadata__
        md.sxtype = ref
        array.item.append(x)
    content.value = array
    return self
    
suds.mx.encoded.Encoded.cast = _polymprphic_cast
