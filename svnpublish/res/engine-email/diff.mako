# -*- coding: utf-8 -*-

## TODO: share with engine-rss/item...

<%!

import re, parsedifflib
from svnpublish.util import size2str

#------------------------------------------------------------------------------
def truncateData(data, maxBytes, maxLines):
  snip = None
  if maxLines is not None:
    lines = data.split('\n')
    if len(lines) > maxLines:
      snip = len('\n'.join(lines[maxLines:]))
      data = '\n'.join(lines[:maxLines])
    lines = []
  if maxBytes is not None and len(data) > maxBytes:
    if snip is None:
      snip = 0
    snip += len(data) - maxBytes
    data = data[:maxBytes]
  return data, snip

#------------------------------------------------------------------------------
def cleanseData(data, rssCompat):
  if not rssCompat:
    return data
  # todo: note: i do not particularly like the following regex
  #       substitution, but certain RSS readers have trouble with
  #       ascii control characters... argh... from below:
  # todo: turn this into a mako filter somehow? the issue is the
  #       "rssCompat" argument...
  return re.sub('[^ -~\w\d\t\n\r]+', '?', data)

%>

##-----------------------------------------------------------------------------
<%def name="renderPlain(revinfo, maxBytes=None, maxLines=None, rssCompat=False)">
  <% data, snip = truncateData(revinfo.diff, maxBytes, maxLines) %>
  <pre>${cleanseData(data, rssCompat)}</pre>
  % if snip is not None:
    <pre class="snip">[...snip: ${size2str(snip)}...]</pre>
  % endif
</%def>

##-----------------------------------------------------------------------------
<%def name="renderTable(revinfo, maxBytes=None, maxLines=None, rssCompat=False)">
  <% data, snip = truncateData(revinfo.diff, maxBytes, maxLines) %>

  % for typ, obj in parsedifflib.parse_svnlook(data, { \
      'lineNumbers'          : True, \
      'intraLineDiff'        : True, \
      'propertyUnifiedDiff'  : True, \
      }):

    % if typ == parsedifflib.Event.PATCH_START:
      <div class="file-diff">

    % elif typ == parsedifflib.Event.PATCH_END:
      </div>

    % elif typ == parsedifflib.Event.ENTRY_START:
      <table class="file-diff-entry" width="100%" border="0" cellpadding="0" cellspacing="0">
        <thead>
          <tr>
            <th colspan="3">
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="name">${obj.comment}</td>
                  % if obj.type == parsedifflib.Entry.TYPE_CONTENT:
                    <td align="right" class="sigs">
                      <span class="pre">${obj.srcsig or '?'}</span>
                      to <span class="post">${obj.tgtsig or '?'}</span>
                    </td>
                  % endif
                </tr>
              </table>
            </th>
          </tr>
        </thead>
        <tbody>

    % elif typ == parsedifflib.Event.ENTRY_END:
        </tbody>
      </table>

    % elif typ == parsedifflib.Event.LINE_LOC:
      <tr class="file-diff-line line-location">
        <td class="diff-line-num"><span class="line-num-content">...</span></td>
        <td class="diff-line-num"><span class="line-num-content">...</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre">${cleanseData(obj.line or '', rssCompat)}</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.LINE_NOTE:
      <tr class="file-diff-line line-note">
        <td class="diff-line-num"><span class="line-num-content">...</span></td>
        <td class="diff-line-num"><span class="line-num-content">...</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre">${cleanseData(obj.line or '', rssCompat)}</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.LINE_SAME:
      <tr class="file-diff-line line-same">
        <td class="diff-line-num"><span class="line-num-content">${obj.oldnum or ''}</span></td>
        <td class="diff-line-num"><span class="line-num-content">${obj.newnum or ''}</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre"> ${cleanseData(obj.line or '', rssCompat)}</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.LINE_DELETE:
      <tr class="file-diff-line line-deleted">
        <td class="diff-line-num"><span class="line-num-content">${obj.oldnum or ''}</span></td>
        <td class="diff-line-num"><span class="line-num-content">${obj.newnum or ''}</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre">-\
            % for styp, sobj in obj.segments \
                or [(parsedifflib.Event.SEGMENT_SAME, parsedifflib.Segment(obj.line))]:
              % if styp == parsedifflib.Event.SEGMENT_SAME:
${cleanseData(sobj.text or '', rssCompat)}\
              % else:
<em>${cleanseData(sobj.text or '', rssCompat)}</em>\
              % endif
            % endfor
</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.LINE_ADD:
      <tr class="file-diff-line line-added">
        <td class="diff-line-num"><span class="line-num-content">${obj.oldnum or ''}</span></td>
        <td class="diff-line-num"><span class="line-num-content">${obj.newnum or ''}</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre">+\
            % for styp, sobj in obj.segments \
                or [(parsedifflib.Event.SEGMENT_SAME, parsedifflib.Segment(obj.line))]:
              % if styp == parsedifflib.Event.SEGMENT_SAME:
${cleanseData(sobj.text or '', rssCompat)}\
              % else:
<em>${cleanseData(sobj.text or '', rssCompat)}</em>\
              % endif
            % endfor
</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.PROPENTRY_START:
      <tr class="file-diff-line line-note">
        <td class="diff-line-num"><span class="line-num-content">&gt;&gt;&gt;</span></td>
        <td class="diff-line-num"><span class="line-num-content">&gt;&gt;&gt;</span></td>
        <td class="diff-line-code">
          <pre class="diff-line-pre">${cleanseData(obj.head or '', rssCompat)}</pre>
        </td>
      </tr>

    % elif typ == parsedifflib.Event.PROPENTRY_END:
      ## nada!

    % else:
      <tr><td colspan="3">Unknown diff event: ${repr(typ)} / ${repr(obj)}</td></tr>

    % endif

  % endfor

  % if snip is not None:
    <pre class="snip">[...snip: ${size2str(snip)}...]</pre>
  % endif
</%def>
