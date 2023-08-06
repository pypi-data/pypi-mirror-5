# ------------------------------------------------------------------------------
import os.path, time
import appy
from appy.gen.mail import sendMail
from appy.shared.utils import executeCommand
from appy.gen.wrappers import AbstractWrapper
from appy.gen.installer import loggedUsers
from appy.px import Px

# ------------------------------------------------------------------------------
_PY = 'Please specify a file corresponding to a Python interpreter ' \
      '(ie "/usr/bin/python").'
FILE_NOT_FOUND = 'Path "%s" was not found.'
VALUE_NOT_FILE = 'Path "%s" is not a file. ' + _PY
NO_PYTHON = "Name '%s' does not starts with 'python'. " + _PY
NOT_UNO_ENABLED_PYTHON = '"%s" is not a UNO-enabled Python interpreter. ' \
                         'To check if a Python interpreter is UNO-enabled, ' \
                         'launch it and type "import uno". If you have no ' \
                         'ImportError exception it is ok.'

# ------------------------------------------------------------------------------
class ToolWrapper(AbstractWrapper):

    pxHome = Px('''
     <table width="300px" height="240px" align="center">
      <tr valign="middle">
       <td align="center">::_('front_page_text')</td>
      </tr>
     </table>''', template=AbstractWrapper.pxTemplate, hook='content')

    # Show on query list or grid, the field content for a given object.
    pxQueryField = Px('''<x>
     <!-- Title -->
     <x if="field.name == 'title'"
        var2="navInfo='search.%s.%s.%d.%d' % \
                (className, searchName, startNumber+currentNumber, totalNumber);
              cssClass=zobj.getCssFor('title')">
      <x>::zobj.getSupTitle(navInfo)</x>
      <a href=":zobj.getUrl(nav=navInfo, page=zobj.getDefaultViewPage())"
         if="enableLinks" class=":cssClass">:zobj.Title()</a><span
         if="not enableLinks" class=":cssClass">:zobj.Title()</span><span
         style=":showSubTitles and 'display:inline' or 'display:none'"
         name="subTitle">::zobj.getSubTitle()</span>

      <!-- Actions: edit, delete -->
      <div if="zobj.mayAct()">
       <a if="zobj.mayEdit()"
          var2="navInfo='search.%s.%s.%d.%d' % \
               (className, searchName, loop.zobj.nb+1+startNumber, totalNumber)"
          href=":zobj.getUrl(mode='edit', page=zobj.getDefaultEditPage(), \
                             nav=navInfo)">
        <img src=":url('edit')" title=":_('object_edit')"/></a>
       <img if="zobj.mayDelete()" class="clickable" src=":url('delete')"
            title=":_('object_delete')"
            onClick=":'onDeleteObject(%s)' % q(zobj.UID())"/>
      </div>
     </x>
     <!-- Any other field -->
     <x if="field.name != 'title'">
      <x var="layoutType='cell'; innerRef=True"
         if="zobj.showField(field.name, 'result')">field.pxView</x>
     </x>
    </x>''')

    # Show query results as a list.
    pxQueryResultList = Px('''
     <table class="list" width="100%">
      <!-- Headers, with filters and sort arrows -->
      <tr if="showHeaders">
       <th for="column in columns"
           var2="widget=column['field'];
                 sortable=ztool.isSortable(field.name, className, 'search');
                 filterable=widget.filterable"
           width=":column['width']" align=":column['align']">
        <x>::ztool.truncateText(_(field.labelId))</x>
        <x>:self.pxSortAndFilter</x><x>:self.pxShowDetails</x>
       </th>
      </tr>

      <!-- Results -->
      <tr for="zobj in zobjects" id="query_row" valign="top"
          var2="currentNumber=currentNumber + 1;
                obj=zobj.appy()"
          class=":loop.zobj.odd and 'even' or 'odd'">
        <td for="column in columns"
            var2="widget=column['field']" id=":'field_%s' % field.name"
            width=":column['width']"
            align=":column['align']">:self.pxQueryField</td>
      </tr>
     </table>''')

    # Show query results as a grid.
    pxQueryResultGrid = Px('''
     <table width="100%"
            var="modeElems=resultMode.split('_');
                 cols=(len(modeElems)==2) and int(modeElems[1]) or 4;
                 rows=ztool.splitList(zobjects, cols)">
      <tr for="row in rows" valign="middle">
       <td for="zobj in row" width=":'%d%%' % (100/cols)" align="center"
           style="padding-top: 25px" var2="obj=zobj.appy()">
        <x var="currentNumber=currentNumber + 1"
           for="column in columns"
           var2="widget = column['field']">:self.pxQueryField</x>
       </td>
      </tr>
     </table>''')

    # Show paginated query results as a list or grid.
    pxQueryResult = Px('''
     <div id="queryResult"
          var="_=ztool.translate;
               className=req['className'];
               refInfo=ztool.getRefInfo();
               refObject=refInfo[0];
               refField=refInfo[1];
               refUrlPart=refObject and ('&amp;ref=%s:%s' % (refObject.UID(), \
                                                             refField)) or '';
               startNumber=req.get('startNumber', '0');
               startNumber=int(startNumber);
               searchName=req.get('search', '');
               searchDescr=ztool.getSearch(className, searchName, descr=True);
               sortKey=req.get('sortKey', '');
               sortOrder=req.get('sortOrder', 'asc');
               filterKey=req.get('filterKey', '');
               filterValue=req.get('filterValue', '');
               queryResult=ztool.executeQuery(className, \
                   search=searchDescr['search'], startNumber=startNumber, \
                   remember=True, sortBy=sortKey, sortOrder=sortOrder, \
                   filterKey=filterKey, filterValue=filterValue, \
                   refObject=refObject, refField=refField);
               zobjects=queryResult['objects'];
               totalNumber=queryResult['totalNumber'];
               batchSize=queryResult['batchSize'];
               batchNumber=len(zobjects);
               ajaxHookId='queryResult';
               navBaseCall='askQueryResult(%s,%s,%s,%s,**v**)' % \
                 (q(ajaxHookId), q(ztool.absolute_url()), q(className), \
                  q(searchName));
               newSearchUrl='%s/ui/search?className=%s%s' % \
                   (ztool.absolute_url(), className, refUrlPart);
               showSubTitles=req.get('showSubTitles', 'true') == 'true';
               resultMode=ztool.getResultMode(className)">

      <x if="zobjects">
       <!-- Display here POD templates if required. -->
       <table var="widgets=ztool.getResultPodFields(className);
                   layoutType='view'"
              if="zobjects and widgets" align=":dright">
        <tr>
         <td var="zobj=zobjects[0]; obj=zobj.appy()"
             for="field in widgets">:field.pxView</td>
        </tr>
       </table>

       <!-- The title of the search -->
       <p>
        <x>:searchDescr['translated']</x> (<x>:totalNumber</x>)
        <x if="showNewSearch and (searchName == 'customSearch')">&nbsp;&mdash;
         &nbsp;<i><a href=":newSearchUrl">:_('search_new')</a></i>
        </x>
       </p>
       <table width="100%">
        <tr>
         <!-- Search description -->
         <td if="searchDescr['translatedDescr']">
          <span class="discreet">:searchDescr['translatedDescr']</span><br/>
         </td>
         <!-- Appy (top) navigation -->
         <td align=":dright" width="25%"><x>:self.pxAppyNavigate</x></td>
        </tr>
       </table>

       <!-- Results, as a list or grid -->
       <x var="columnLayouts=ztool.getResultColumnsLayouts(className, refInfo);
               columns=zobjects[0].getColumnsSpecifiers(columnLayouts, dir);
               currentNumber=0">
        <x if="resultMode == 'list'">:self.pxQueryResultList</x>
        <x if="resultMode != 'list'">:self.pxQueryResultGrid</x>
       </x>

       <!-- Appy (bottom) navigation -->
       <x>:self.pxAppyNavigate</x>
      </x>

      <x if="not zobjects">
       <x>:_('query_no_result')></x>
       <x if="showNewSearch and (searchName == 'customSearch')"><br/>
        <i class="discreet"><a href=":newSearchUrl">:_('search_new')</a></i></x>
      </x>
    </div>''')

    pxQuery = Px('''
     <x var="className=req['className'];
             searchName=req.get('search', '');
             cssJs=None;
             showNewSearch=True;
             showHeaders=True;
             enableLinks=True">
      <x>:self.pxPagePrologue</x><x>:self.pxQueryResult</x>
     </x>''', template=AbstractWrapper.pxTemplate, hook='content')

    pxSearch = Px('''
     <x var="className=req['className'];
             refInfo=req.get('ref', None);
             searchInfo=ztool.getSearchInfo(className, refInfo);
             cssJs={};
             x=ztool.getCssJs(searchInfo['fields'], 'edit', cssJs)">

      <!-- Include type-specific CSS and JS. -->
      <link for="cssFile in cssJs['css']" rel="stylesheet" type="text/css"
            href=":url(cssFile)"/>
      <script for="jsFile in cssJs['js']" type="text/javascript"
              src=":url(jsFile)"></script>

      <!-- Search title -->
      <h1><x>:_('%s_plural'%className)</x> &ndash;
          <x>:_('search_title')</x></h1>
      <br/>
      <!-- Form for searching objects of request/className. -->
      <form name="search" action=":ztool.absolute_url()+'/do'" method="post">
       <input type="hidden" name="action" value="SearchObjects"/>
       <input type="hidden" name="className" value=":className"/>
       <input if="refInfo" type="hidden" name="ref" value=":refInfo"/>

       <table width="100%">
        <tr for="searchRow in ztool.getGroupedSearchFields(searchInfo)"
            valign="top">
         <td for="field in searchRow"
             var2="scolspan=field and field.scolspan or 1"
             colspan=":scolspan"
             width=":'%d%%' % ((100/searchInfo['nbOfColumns'])*scolspan)">
           <x if="field"
              var2="name=field.name;
                    widgetName='w_%s' % name">field.pxSearch</x>
           <br class="discreet"/>
         </td>
        </tr>
       </table>

       <!-- Submit button -->
       <p align=":dright"><br/>
        <input type="submit" class="button" value=":_('search_button')"
               style=":url('buttonSearch', bg=True)"/>
       </p>
      </form>
     </x>''', template=AbstractWrapper.pxTemplate, hook='content')

    pxImport = Px('''
     <x var="className=req['className'];
             importElems=ztool.getImportElements(className);
             allAreImported=True">
      <x>:self.pxPagePrologue</x>
      <script type="text/javascript"><![CDATA[
      var importedElemsShown = false;
      function toggleViewableElements() {
        var rows = document.getElementsByName('importedElem');
        var newDisplay = 'table-row';
        if (isIe) newDisplay = 'block';
        if (importedElemsShown) newDisplay = 'none';
        for (var i=0; i<rows.length; i++) {
          rows[i].style.display = newDisplay;
        }
        importedElemsShown = !importedElemsShown;
      }
      var checkBoxesChecked = true;
      function toggleCheckboxes() {
        var checkBoxes = document.getElementsByName('cbElem');
        var newCheckValue = true;
        if (checkBoxesChecked) newCheckValue = false;
        for (var i=0; i<checkBoxes.length; i++) {
           checkBoxes[i].checked = newCheckValue;
        }
        checkBoxesChecked = newCheckValue;
      }
      function importSingleElement(importPath) {
        var f = document.forms['importElements'];
        f.importPath.value = importPath;
        f.submit();
      }
      function importManyElements() {
        var f = document.forms['importElements'];
        var importPaths = '';
        // Get the values of the checkboxes
        var checkBoxes = document.getElementsByName('cbElem');
        for (var i=0; i<checkBoxes.length; i++) {
          if (checkBoxes[i].checked) {
            importPaths += checkBoxes[i].value + '|';
          }
        }
        if (! importPaths) alert(no_elem_selected);
        else {
          f.importPath.value = importPaths;
          f.submit();
        }
      }]]>
      </script>

      <!-- Form for importing several elements at once. -->
      <form name="importElements"
            action=":ztool.absolute_url()+'/do'" method="post">
       <input type="hidden" name="action" value="ImportObjects"/>
       <input type="hidden" name="className" value=":className"/>
       <input type="hidden" name="importPath" value=""/>
      </form>

      <h1>:_('import_title')"></h1><br/>
      <table class="list" width="100%">
       <tr>
        <th for="columnHeader in importElems[0]">
         <img if="loop.columnHeader.nb == 0" src=":url('eye')"
              title="_('import_show_hide')" class="clickable"
              onClick="toggleViewableElements()" align=":dleft" />
         <x>:columnHeader</x>
        </th>
        <th></th>
        <th width="20px"><img src=":url('select_elems')" class="clickable"
            title=":_('select_delesect')" onClick="toggleCheckboxes()"/></th>
       </tr>
       <tr for="row in importElems[1]"
           var2="alreadyImported=ztool.isAlreadyImported(className, row[0]);
                 allAreImported=allAreImported and alreadyImported;
                 odd=loop.row.odd"
           id=":alreadyImported and 'importedElem' or 'notImportedElem'"
           name=":alreadyImported and 'importedElem' or 'notImportedElem'"
           style=":alreadyImported and 'display:none' or 'display:table-row'"
           class=":odd and 'even' or 'odd'">
        <td for="elem in row[1:]">:elem</td>
        <td>
         <input type="button" if="not alreadyImported"
                onClick=":'importSingleElement(%s)' % q(row[0])"
                value=":_('query_import')"/>
         <x if="alreadyImported">:_('import_already')</x>
        </td>
        <td align="center">
         <input if="not alreadyImported" type="checkbox" checked="checked"
                id="cbElem" name="cbElem" value="row[0]"/>
        </td>
       </tr>
       <tr if="not importElems[1] or allAreImported">
        <td colspan="15">:_('query_no_result')</td></tr>
      </table>

      <!-- Button for importing several elements at once. -->
      <p align=":dright"><br/>
       <input if="importElems[1] and not allAreImported"
              type="button" onClick="importManyElements()"
              value=":_('import_many')"/>
      </p>
     </x>''', template=AbstractWrapper.pxTemplate, hook='content')

    def validPythonWithUno(self, value):
        '''This method represents the validator for field unoEnabledPython.'''
        if value:
            if not os.path.exists(value):
                return FILE_NOT_FOUND % value
            if not os.path.isfile(value):
                return VALUE_NOT_FILE % value
            if not os.path.basename(value).startswith('python'):
                return NO_PYTHON % value
            if os.system('%s -c "import uno"' % value):
                return NOT_UNO_ENABLED_PYTHON % value
        return True

    def isManager(self):
        '''Some pages on the tool can only be accessed by managers.'''
        if self.user.has_role('Manager'): return 'view'

    def isManagerEdit(self):
        '''Some pages on the tool can only be accessed by managers, also in
           edit mode.'''
        if self.user.has_role('Manager'): return True

    def computeConnectedUsers(self):
        '''Computes a table showing users that are currently connected.'''
        res = '<table cellpadding="0" cellspacing="0" class="list">' \
              '<tr><th></th><th>%s</th></tr>' % \
              self.translate('last_user_access')
        rows = []
        for userId, lastAccess in loggedUsers.items():
            user = self.search1('User', noSecurity=True, login=userId)
            if not user: continue # Could have been deleted in the meanwhile
            fmt = '%s (%s)' % (self.dateFormat, self.hourFormat)
            access = time.strftime(fmt, time.localtime(lastAccess))
            rows.append('<tr><td><a href="%s">%s</a></td><td>%s</td></tr>' % \
                        (user.o.absolute_url(), user.title,access))
        return res + '\n'.join(rows) + '</table>'

    podOutputFormats = ('odt', 'pdf', 'doc', 'rtf', 'ods', 'xls')
    def getPodOutputFormats(self):
        '''Gets the available output formats for POD documents.'''
        return [(of, self.translate(of)) for of in self.podOutputFormats]

    def getInitiator(self, field=False):
        '''Retrieves the object that triggered the creation of the object
           being currently created (if any), or the name of the field in this
           object if p_field is given.'''
        nav = self.o.REQUEST.get('nav', '')
        if not nav or not nav.startswith('ref.'): return
        if not field: return self.getObject(nav.split('.')[1])
        return nav.split('.')[2].split(':')[0]

    def getObject(self, uid):
        '''Allow to retrieve an object from its unique identifier p_uid.'''
        return self.o.getObject(uid, appy=True)

    def getDiskFolder(self):
        '''Returns the disk folder where the Appy application is stored.'''
        return self.o.config.diskFolder

    def getClass(self, zopeName):
        '''Gets the Appy class corresponding to technical p_zopeName.'''
        return self.o.getAppyClass(zopeName)

    def getAttributeName(self, attributeType, klass, attrName=None):
        '''Some names of Tool attributes are not easy to guess. For example,
           the attribute that stores the names of the columns to display in
           query results for class A that is in package x.y is
           "tool.resultColumnsForx_y_A". This method generates the attribute
           name based on p_attributeType, a p_klass from the application, and a
           p_attrName (given only if needed). p_attributeType may be:

           "podTemplate"
               Stores the pod template for p_attrName.

           "formats"
               Stores the output format(s) of a given pod template for
               p_attrName.

           "resultColumns"
               Stores the list of columns that must be shown when displaying
               instances of a given root p_klass.

           "numberOfSearchColumns"
               Determines in how many columns the search screen for p_klass
               is rendered.

           "searchFields"
               Determines, among all indexed fields for p_klass, which one will
               really be used in the search screen.
        '''
        fullClassName = self.o.getPortalType(klass)
        res = '%sFor%s' % (attributeType, fullClassName)
        if attrName: res += '_%s' % attrName
        return res

    def getAvailableLanguages(self):
        '''Returns the list of available languages for this application.'''
        return [(t.id, t.title) for t in self.translations]

    def convert(self, fileName, format):
        '''Launches a UNO-enabled Python interpreter as defined in the self for
           converting, using OpenOffice in server mode, a file named p_fileName
           into an output p_format.'''
        convScript = '%s/pod/converter.py' % os.path.dirname(appy.__file__)
        cmd = '%s %s "%s" %s -p%d' % (self.unoEnabledPython, convScript,
                                      fileName, format, self.openOfficePort)
        self.log('Executing %s...' % cmd)
        return executeCommand(cmd) # The result can contain an error message

    def sendMail(self, to, subject, body, attachments=None):
        '''Sends a mail. See doc for appy.gen.mail.sendMail.'''
        sendMail(self, to, subject, body, attachments=attachments)

    def refreshSecurity(self):
        '''Refreshes, on every object in the database, security-related,
           workflow-managed information.'''
        context = {'nb': 0}
        for className in self.o.getProductConfig().allClassNames:
            self.compute(className, context=context, noSecurity=True,
                         expression="ctx['nb'] += int(obj.o.refreshSecurity())")
        msg = 'Security refresh: %d object(s) updated.' % context['nb']
        self.log(msg)

    def refreshCatalog(self, startObject=None):
        '''Reindex all Appy objects. For some unknown reason, method
           catalog.refreshCatalog is not able to recatalog Appy objects.'''
        if not startObject:
            # This is a global refresh. Clear the catalog completely, and then
            # reindex all Appy-managed objects, ie those in folders "config"
            # and "data".
            # First, clear the catalog.
            self.log('Recomputing the whole catalog...')
            app = self.o.getParentNode()
            app.catalog._catalog.clear()
            nb = 1
            failed = []
            for obj in app.config.objectValues():
                subNb, subFailed = self.refreshCatalog(startObject=obj)
                nb += subNb
                failed += subFailed
            try:
                app.config.reindex()
            except:
                failed.append(app.config)
            # Then, refresh objects in the "data" folder.
            for obj in app.data.objectValues():
                subNb, subFailed = self.refreshCatalog(startObject=obj)
                nb += subNb
                failed += subFailed
            # Re-try to index all objects for which reindexation has failed.
            for obj in failed: obj.reindex()
            if failed:
                failMsg = ' (%d retried)' % len(failed)
            else:
                failMsg = ''
            self.log('%d object(s) were reindexed%s.' % (nb, failMsg))
        else:
            nb = 1
            failed = []
            for obj in startObject.objectValues():
                subNb, subFailed = self.refreshCatalog(startObject=obj)
                nb += subNb
                failed += subFailed
            try:
                startObject.reindex()
            except Exception, e:
                failed.append(startObject)
            return nb, failed

    def validate(self, new, errors):
        '''Validates that uploaded POD templates and output types are
           compatible.'''
        page = self.request.get('page', 'main')
        if page == 'documents':
            # Check that uploaded templates and output formats are compatible.
            for fieldName in dir(new):
                # Ignore fields which are not POD templates.
                if not fieldName.startswith('podTemplate'): continue
                # Get the file name, either from the newly uploaded file or
                # from the existing file stored in the database.
                if getattr(new, fieldName):
                    fileName = getattr(new, fieldName).filename
                else:
                    fileName = getattr(self, fieldName).name
                # Get the extension of the uploaded file.
                ext = os.path.splitext(fileName)[1][1:]
                # Get the chosen output formats for this template.
                formatsFieldName = 'formatsFor%s' % fieldName[14:]
                formats = getattr(new, formatsFieldName)
                error = False
                if ext == 'odt':
                    error = ('ods' in formats) or ('xls' in formats)
                elif ext == 'ods':
                    error = ('odt' in formats) or ('pdf' in formats) or \
                            ('doc' in formats) or ('rtf' in formats)
                if error:
                    msg = 'This (these) format(s) cannot be used with ' \
                          'this template.'
                    setattr(errors, formatsFieldName, msg)
        return self._callCustom('validate', new, errors)
# ------------------------------------------------------------------------------
