#!/usr/bin/python

""" 
This is a module that handles rendering wiki text into html, and reverting \
HTML back into wiki syntax.  You can see the examples below of how to use \
the syntax.

== Syntax Formatting ==

    th. Wiki Syntax                             | th. Rendered Output
    <nowiki>''italic''</nowiki>                 |  ''italic''
    <nowiki>'''bold'''</nowiki>                 |  '''bold'''
    <nowiki>___underline___</nowiki>            |  ___underline___
    <nowiki>---strikeout---</nowiki>            |  ---strikeout---
    <nowiki>'''''bold italic'''''</nowiki>      | '''''bold italic'''''
    <nowiki>__'''bold underline'''__</nowiki>   | ___'''bold under'''___

== Linebreaks ==

Horizontal rules are created by having a blank linke with a repeating dash of
over 4 characters

<nowiki>----------------</nowiki>

----------------

Table of contents can be created by specifying the toc key, as such:

[toc]

== Headers ==
    
    Headers are defined by padding some text with a '=' character.  The \
    number of '=' signs that you use will determine the header level.
    
    Headers need to be on their own line to work
    
    <nowiki> = Header 1 = </nowiki>
    = Header 1 =
    
    <nowiki> == Header 2 == </nowiki>
    == Header 2 ==
    
    <nowiki> === Header 3 === </nowiki>
    === Header 3 ===
    
    <nowiki> ==== Header 4 ==== </nowiki>
    ==== Header 4 ====
    
    etc.
    
== Alignment ==
    
    Aligning can be done by using --> and <--- flags.  They need to be at the
    beginning and end of each line.
    
<nowiki>--> Align to Center <--</nowiki>

--> Align to Center <--

<nowiki>--> Align to the Right</nowiki>

--> Align to the Right.

    Floating can be achieved in the same way, only using ==> and <== flags.

<nowiki>~~> Float to Center <~~</nowiki>

~~> Float to Center <~~

<nowiki>~~> Float to the Right</nowiki>

~~> Float to the Right

== Sections ==
    
    Sections are defined by putting a ':' in front of any word.  These are
    used when putting information into groups.  It will create a <div> object
    and any following lines will be encorporated into your section.
    
    Sections need to be a word (can be separated by underscores), and will
    automatically be rendered into capitalized words.  For example,
    'example_section' will become 'Example Section' when rendered.
    
    Some predefined sections are:
    
    th. Section | Description th.
    note        | Creates a styled text box with your note text.
    warning     | Creates a styled text box for warnings (red box & text)
    todo        | Creates a styled text box for todo coding items
    sa          | Gets expanded as 'See also', and tries to match the parts \
                  to another wiki page.
    see_also    | Same as the above.
    param       | Gets expanded as 'Parameters', used to define coding params
    sdk_history | Will get sluppred up for internal use with the docgen \
                  system.
    
    <nowiki>
    :custom_section     This is a custom section.  To wrap lines around a
                        section, just include a single slash character at the
                        end of a line.
                        
                        As long as you type text with the same tab/space
                        level they will be joined together in the same section.
                        
                        
    To exit a section, just break out of the tab flow, or start a new section.
    </nowiki>
    
    :custom_section     This is a custom section.  To wrap lines around a \
                        section, just include a single slash character at the\
                        end of a line.
                        
                        As long as you type text with the same tab/space\
                        level they will be joined together in the same section.
                        
                        
    To exit a section, just break out of the tab flow, or start a new section.
    
    <nowiki>
    :note           This is a simple note
    </nowiki>
    
    :note           This is a simple note
    
    <nowiki>
    :todo           This is a todo note.
    </nowiki>
    
    :todo           This is a todo note.
    
    <nowiki>
    :info           This is an info note.
    </nowiki>
    
    :info           This is an info note.
    
    <nowiki>
    :warning        This is a warning message.
    </nowiki>
    
    :warning        This is a warning message.
    
    <nowiki>
    :error          This is an error message.
    </nowiki>
    
    :error          This is an error message.

== Links ==

    External:
    
    <nowiki>[http://www.projexsoftware.com/ Projex Software]</nowiki>
    
    [http://www.projexsoftware.com/ Projex Software]
    
    Internal:
    
    <nowiki>[[Internal:Path|Internal Text]]</nowiki>
    
    [[Internal:Path|Internal Text]]
    
    <nowiki>[img:path/to/image.png]</nowiki>
    
    [img:/path/to/image.png]

== Tables ==
    
    Tables are created by splitting a line up with pipes.  You need to have
    at least 1 space between your '|' cell to let the systme know that you
    are trying to make a table.
    
    To make a table with no header, just do:
    
    <nowiki>
    cell01          |  cell02
    cell03          |  cell04
    </nowiki>
    
    cell01          | cell02
    cell03          | cell04
    
    Additional cell options can be added to a cell by adding style information
    in a list with a td. flag somewhere in the cell.
    
    <nowiki>
    td.[text-align:right;min-width:150px] cell01   |  cell02   td.[align:left]
    td.[text-align:right] cell03                   |  cell04   td.[align:left]
    </nowiki>
    
    td.[text-align:right;min-width:150px] cell01   |  cell02   td.[align:left]
    td.[text-align:right] cell03                   |  cell04   td.[align:left]
    
    To make a table with a header, just add a row that usees the th. formatter:
    
    <nowiki>
    th. Left Header              | Right Header th.
    td.[text-align:right] cell01 |  cell02
    td.[text-align:right] cell03 |  cell04
    </nowiki>
    
    th. Left Header | Right Header th.
    td.[text-align:right] cell01 |  cell02
    td.[text-align:right] cell03 |  cell04

== Lists ==
    
    <nowiki>
    *. Unordered list item
    *. Another unordered list item
    **. Sub list item
    **. Another sub list item
    *. Another top level item
    </nowiki>
    
    *. Unordered list item
    *. Another unordered list item
    **. Sub list item
    **. Another sub list item
    *. Another top level item
    
    <nowiki>
    #. Ordered list item
    #. Another ordered list item
    ##. Sub list item
    ##. Another sub list item
    #. Another top level item
    </nowiki>
    
    #. Ordered list item
    #. Another ordered list item
    ##. Sub list item
    ##. Another sub list item
    #. Another top level item
    
    Creating a mixed list
    <nowiki>
    *. Ordered list item
    *. Another ordered list item
    *#. Sub list item
    *#*. Test middle \\
         with breaklines
    *#. Another sub list item
    *. Another top level item
    </nowiki>
    
    *. Ordered list item
    *. Another ordered list item
    *#. Sub list item
    *#*. Test middle \
         with breaklines
    *#. Another sub list item
    *. Another top level item
    
== Syntax Highlighting ==
    
    Code examples (will default to python, but can be set with the lang: key)
    
    <nowiki>
    |>>> print "testing"
    |testing
    </nowiki>
    
    |>>> print "testing"
    |testing
    
    <nowiki>
    |lang: html
    |<html>
    |  <body>
    |   <h1>Test</h1>
    |  </body>
    |</html>
    </nowiki>
    
    |lang: html
    |<html>
    |  <body>
    |   <h1>Test</h1>
    |  </body>
    |</html>

"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import logging
import re
import xml.sax.saxutils

from projex import text

logger = logging.getLogger(__name__)

EXPR_SECTION            = re.compile( '^:([^\s]+)' )
EXPR_CENTER             = re.compile( '^(--|~~)>(.*)<(--|~~)$' )
EXPR_RIGHT              = re.compile( '^(--|~~)>(.*)$' )
EXPR_LEFT               = re.compile( '^(.*)<(--|~~)$' )
EXPR_HEADER             = re.compile( '^(=+)\s*([^=]*)\s*(=+)$' )
EXPR_TOC                = re.compile( '(\[toc([^\]]*)\])' )
EXPR_INTLINK            = re.compile( '(\[{2}([^\]]*)\]{2})' )
EXPR_EXTLINK            = re.compile( '(\[(\w+://[^\]]*)\])' )
EXPR_IMG                = re.compile( '(\[img:([^\]]*)\])' )
EXPR_CODE               = re.compile( '^\s*\|(.*)$' )
EXPR_LANG               = re.compile( 'lang:\s*(.*)$' )
EXPR_ITALIC             = re.compile( "(?<='{2})(.*?)(?='{2})" )
EXPR_BOLD               = re.compile( "(?<='{3})(.*?)(?='{3})" )
EXPR_UNDERLINE          = re.compile( "(?<=_{3})(.*?)(?=_{3})" )
EXPR_STRIKEOUT          = re.compile( "(?<=-{3})(.*?)(?=-{3})" )
EXPR_NOWIKI             = re.compile( '(?<=<nowiki>)(.*?)(?=</nowiki>)' )
EXPR_LIST               = re.compile( '^\s*([\*#]+)\.\s*(.*)$' )
EXPR_TABLE_CELL         = re.compile( '((td|th)\.(\[[^]]*\])?)' )
EXPR_HR                 = re.compile( '^----+$' )
EXPR_CLASS_LINK         = re.compile( '&lt;(\w[^&]+)&gt;' )

SECTION_MAP = {
    'sa':       'See also',
    'param':    'Parameters'
}

SECTION_ICONS = (
    'note',
    'warning',
    'info',
    'error',
    'todo'
)

class UrlHandler(object):
    """ 
    Defines a url handler class that can be used when the wiki system
    attempts to render out a url.  It will take a wiki style key for a url 
    and lookup the proper http url to the target.
    """
    _current = None
    
    def __init__( self ):
        self._rootUrl = ''
    
    def resolve( self, key ):
        """
        Resolves the inputed wiki key to a url path.  This method should \
        return a url and whether or not the page exists.
        
        :param      key     | <str>
        
        :return     (<str> url, <bool> exists)
        """
        logger.debug('Key not found: ', key)
        return ('', False)
    
    def resolveClass( self, cls ):
        """
        Resolves a pointer to a class reference - this will be in the form
        of <package>.<className> and should return the documentation for the
        module and class.
        
        :param      cls | <str>
        
        :return     <str>
        """
        logger.debug('Class not found', cls)
        return ('', False)
    
    def resolveImage( self, key ):
        """
        Resolves the image path for the inputed key to a valid URL.
        
        :param      key | <str>
        
        :return     (<str> url, <bool> exists)
        """
        logger.debug('Key not found', key)
        return ('', False)
    
    def rootUrl( self ):
        """
        Returns the root url for the handler.
        
        :return     <str>
        """
        return self._rootUrl
    
    def setCurrent( self ):
        """
        Sets this handler as the current global instance.
        """
        UrlHandler._current = self
    
    def setRootUrl( self, url ):
        """
        Sets the root url for the url handler to the inputed url.
        
        :param      url | <str>
        """
        self._rootUrl = str(url)
    
    @staticmethod
    def current():
        """
        Returns the current global url handler.
        
        :return     <UrlHandler>
        """
        if ( not UrlHandler._current ):
            UrlHandler._current = UrlHandler()
        return UrlHandler._current

#------------------------------------------------------------------------------

def render( plain, urlHandler = None ):
    """
    Renders the intpued plain text wiki information into HTML rich text.
    
    :param      plain       |  <str> | \
                               Include some additional documentation
                urlHandler  |  <UlrHandler> || None
    
    :return     <str> html
    """
    if ( not plain ):
        return ''
    
    if ( not urlHandler ):
        urlHandler = UrlHandler.current()
    
    lines               = re.split('\n\r|\r\n|\n|\r', plain)
    curr_section        = ''
    curr_section_level  = 0
    html                = []
    skip                = []
    nowiki_stack        = []
    code_stack          = []
    table_stack         = []
    list_stack          = []
    section_stack       = []
    toc_data            = []
    align_div           = ''
    list_indent         = None
    ignore_list_stack   = False
    
    html.append('<div class="wiki">')
    
    for i, line in enumerate(lines):
        ignore_list_stack   = False
        sline = line.strip()
        
        # check to see if we are continuing a list entry
        if ( list_indent ):
            line_indent = len(re.match('\s*', line).group())
            
            if ( line_indent < list_indent ):
                list_indent = None
                html.append('</li>')
            else:
                ignore_list_stack   = True
        
                if ( not sline ):
                    html.append('<br/><br/>')
                    continue
        
        if ( i in skip ):
            continue
        
        # check for a center option
        center = EXPR_CENTER.match(sline)
        right  = EXPR_RIGHT.match(sline)
        left   = EXPR_LEFT.match(sline)
        
        if ( center ):
            style = center.groups()[0]
            line  = center.groups()[1].strip()
            
            if ( align_div and align_div != 'center' ):
                html.append('</div>')
                align_div = ''
            
            if ( not align_div ):
                if ( style == '--' ):
                    html.append('<div align="center">')
                else:
                    html.append('<div style="float:center">')
                align_div = 'center'
        
        # check for a right align option
        elif ( right ):
            style = right.groups()[0]
            line  = right.groups()[1]
            
            if ( align_div and align_div != 'right' ):
                html.append('</div>')
                align_div = ''
            
            if ( not align_div ):
                if ( style == '--' ):
                    html.append('<div align="right">')
                else:
                    html.append('<div style="float:right">')
                align_div = 'right'
        
        # check for a left align option
        elif ( left ):
            style = left.groups()[1]
            line  = left.groups()[0]
            
            if ( align_div and align_div != 'left' ):
                html.append('</div>')
                align_div = ''
            
            if ( not align_div ):
                if ( style == '--' ):
                    html.append('<div align="left">')
                else:
                    html.append('<div style="float:left">')
                
                align_div = 'left'
        
        # otherwise, clear alignment
        elif ( align_div ):
            html.append('</div>')
            align_div = ''
        
        # make sure we're on the same level
        if (curr_section and sline and
            (len(line) - len(line.lstrip())) < curr_section_level ):
                
            html += section_stack
            section_stack = []
            
            curr_section = ''
            curr_section_level = 0
        
        count = i
        while ( sline.endswith('\\') and count+1 < len(lines) ):
            sline += ' ' + lines[count+1].strip()
            skip.append(count)
            count += 1
        
        # check to see what is wiki protected
        if ( sline == '<nowiki>' ):
            if ( not ignore_list_stack ):
                html += list_stack
                list_stack = []
            
            html += table_stack
            table_stack = []
            
            html.append('<pre class="nowiki">')
            nowiki_stack.append( '</pre>' )
            continue
            
        elif ( sline == '</nowiki>' ):
            html += nowiki_stack
            nowiki_stack = []
            continue
            
        elif ( nowiki_stack ):
            html.append(xml.sax.saxutils.escape(line))
            continue
        
        parts = line.split( ' | ' )
        if ( len(parts) == 1 ):
            html += table_stack
            table_stack = []
        
        line = line.replace('%','%%')
        
        # strip out nowiki lines
        nowiki_dict = {}
        count = 0
        for section in EXPR_NOWIKI.findall(line)[::2]:
            nowiki_dict['nowiki_%i' % count] = section
            newtext = '%%(nowiki_%i)s' % count
            line = line.replace( '<nowiki>%s</nowiki>' % section, newtext )
            count += 1
        
        # check for a div section
        section = EXPR_SECTION.match(sline)
        if ( section ):
            html += code_stack
            code_stack = []
                
            name = section.groups()[0]
            if ( name != curr_section ):
                html += section_stack
                section_stack = []
                
                if not name in SECTION_ICONS:
                    section_stack.append('</div>')
                    mapped = SECTION_MAP.get(name, text.capitalizeWords(name))
                    templ = '<div class="wiki_section %s">'\
                            '<strong>%s</strong><br/>'
                    
                    html.append(templ % (name, mapped))
                else:
                    section_stack.append('</div>')
                    url, success = urlHandler.resolveImage('%s.png' % name)
                    url = url.replace('/img/', '/images/')
                    templ = '<div class="wiki_section %s">'\
                            '<img class="icon" src="%s"/>'
                    html.append(templ % (name, url))
                
                curr_section = name
            else:
                html.append('<br/>')
            
            sline = sline.replace( section.group(), '' )
            line = line.replace( section.group(), ' ' * len(section.group()) )
            curr_section_level = len(line) - len(line.lstrip())
        
        # check for code
        code = EXPR_CODE.match(sline)
        if ( code ):
            templ = ''
            code_line = code.groups()[0]
            
            if ( not code_stack ):
                lang = 'python'
                lang_search = EXPR_LANG.search(code_line)
                
                if ( lang_search ):
                    lang = lang_search.groups()[0]
                    code_line = code_line.replace( lang_search.group(), '' )
                    
                templ =  '<small><i>%s</i></small>' % lang
                templ += '<pre class="prettyprint lang-%s code">' % lang
                code_stack.append('</pre>')
            
            escaped = xml.sax.saxutils.escape(code_line)
            
            if ( not ignore_list_stack ):
                html += list_stack
                list_stack = []
            
            html += table_stack
            table_stack = []
            
            html.append( templ + escaped )
            continue
            
        # exit out of the code mode
        else:
            html += code_stack
            code_stack = []
        
        #----------------------------------------------------------------------
        
        # make sure we have no html data in the line
        if ( not sline ):
            html.append('</div>')
            html.append('<br/><div class="wiki">')
            continue
        
        # check for horizontal rules
        if ( EXPR_HR.match(sline) ):
            html.append( '<hr/>' )
            continue
        
        # check for headers
        header = EXPR_HEADER.match(sline)
        if ( header ):
            hopen, title, hclose = header.groups()
            hopencount = len(hopen)
            
            if ( hopencount == len(hclose) ):
                opt = (title.replace(' ', '_'), hopencount, title, hopencount)
                templ = '<a name="%s"></a><h%i class="wiki">%s</h%i>'
                add = templ % opt
                
                spacing = '#' * hopencount
                opts    = (spacing, title.replace(' ', '_'), title)
                toc_data.append('%s. [[#%s|%s]]' % opts)
                
                if ( not ignore_list_stack ):
                    html += list_stack
                    list_stack = []
                
                html += table_stack
                table_stack = []
                
                html.append(add)
                continue
        
        line = xml.sax.saxutils.escape(line)
        
        # resolve any class links
        for result in EXPR_CLASS_LINK.findall(line):
            opts = result.split()
            for i, cls in enumerate(opts):
                # ignore base classes, need modules
                if ( not '.' in cls ):
                    continue
                
                url, success = urlHandler.resolveClass(cls)
                
                if ( success ):
                    opts[i] = '<a href="%s">%s</a>' % (url, cls)
            
            info = '<span class="type">%s</span>' % ' '.join(opts)
            line = line.replace('&lt;' + result + '&gt;', info)
        
        # replace formatting options
        for section in EXPR_UNDERLINE.findall(line)[::2]:
            line = line.replace( "___%s___" % section, '<u>%s</u>' % section)
        
        for section in EXPR_STRIKEOUT.findall(line)[::2]:
            line = line.replace( "---%s---" % section, '<s>%s</s>' % section)
        
        for section in EXPR_BOLD.findall(line)[::2]:
            line = line.replace( "'''%s'''" % section, '<b>%s</b>' % section)
        
        for section in EXPR_ITALIC.findall(line)[::2]:
            line = line.replace( "''%s''" % section, '<i>%s</i>' % section)
        
        # resolve any images
        for grp, url in EXPR_IMG.findall(line):
            urlsplit = url.split('|')
            if ( len(urlsplit) == 1 ):
                last_word = re.findall('\w+', urlsplit[0])[-1]
                urlsplit.append(last_word)
            
            url, exists = urlHandler.resolveImage(urlsplit[0])
            
            templ = '<img alt="%s" src="%s"/>' % (urlsplit[-1], url)
            line = line.replace(grp, templ)
        
        # resolve any external urls
        for result in EXPR_EXTLINK.findall(line):
            grp = result[0]
            url = result[1]
            
            urlsplit = url.split()
            if ( len(urlsplit) == 1 ):
                urlsplit.append(urlsplit[0])
            
            url = urlsplit[0]
            urltext = ' '.join(urlsplit[1:])
            opt = (url, urltext)
            templ = '<a class="wiki_external" href="%s">%s</a>' % opt
            line = line.replace(grp, templ)
        
        # resolve any internal urls
        for grp, url in EXPR_INTLINK.findall(line):
            urlsplit = url.split('|')
            if ( len(urlsplit) == 1 ):
                last_word = re.findall('\w+', urlsplit[0])[-1]
                urlsplit.append(last_word)
            
            url   = urlsplit[0]
            title = '|'.join(urlsplit[1:])
            cls   = 'wiki_standard'
            
            tagsplit = url.split('#')
            if ( len(tagsplit) == 1 ):
                url = url
                tag = ''
            else:
                url = tagsplit[0]
                tag = '#'.join(tagsplit[1:])
            
            # make sure the url exists
            if ( url ):
                url, exists = urlHandler.resolve(url)
                if ( not exists ):
                    cls = 'wiki_missing'
            
            # join together the resolved url and the tag
            if ( tag ):
                url = url + '#' + tag
            
            # generate the link
            templ = '<a href="%s" class="%s">%s</a>' % (url, cls, title)
            line = line.replace(grp, templ)
        
        # process lists
        results = EXPR_LIST.match(line)
        if ( results ):
            level, linetext = results.groups()
            level_count = len(level)
            level_type  = 'ul'
            if ( level[-1] == '#' ):
                level_type = 'ol'
            
            while ( level_count > len(list_stack) ):
                html.append('<%s class="wiki">' % level_type)
                list_stack.append('</%s>' % level_type)
            
            while ( len(list_stack) > level_count ):
                html.append(list_stack[-1])
                list_stack = list_stack[:-1]
            
            space_line  = line.replace(level + '.', ' ' * (len(level) + 1))
            list_indent = len(re.match('\s*', space_line).group())
            
            html.append('<li>')
            html.append(linetext)
            
            continue
            
        elif ( not ignore_list_stack ):
            html += list_stack
            list_stack = []
        
        parts = line.split( ' | ' )
        if ( len(parts) > 1 ):
            if ( not table_stack ):
                table_stack.append( '</table>' )
                html.append( '<table class="wiki">' )
            
            cell_type = 'td'
            styles    = ''
            
            cells = []
            for part in parts:
                results = EXPR_TABLE_CELL.search(part)
                if ( not results ):
                    cells.append( '<td>%s</td>' % part.strip() )
                else:
                    grp, cell_type, styles = results.groups()
                    
                    if ( not styles ):
                        styles = ''
                    else:
                        styles = styles.strip('[]')
                    
                    part = part.replace(grp, '').strip()
                    opts = ( cell_type, styles, part, cell_type )
                    
                    cells.append( '<%s style="%s">%s</%s>' % opts )
            
            line  = '<tr>%s</tr>' % ''.join(cells)
            
            html.append( (line % nowiki_dict) )
        else:
            html += table_stack
            table_stack = []
            
            html.append(line % nowiki_dict)
    
    if ( align_div ):
        html.append('</div>')
    
    if ( list_indent ):
        html.append('</li>')
    
    html += table_stack
    html += list_stack
    html += code_stack
    html += nowiki_stack
    html += section_stack
    
    html.append('</div>')
    html_txt = '\n'.join(html)
    
    # resolve any table of contents
    for toc, options in EXPR_TOC.findall(html_txt):
        toc_wiki   = '\n\t'.join(toc_data)
        toc_html   = '<div class="toc"><div class="toc_title">Contents</div>'
        toc_html  += render(toc_wiki)
        toc_html  += '</div>'
        
        html_txt = html_txt.replace(toc, toc_html)
    
    # replace \[ and \] options
    html_txt = html_txt.replace('\[', '[').replace('\]', ']')
    
    return html_txt