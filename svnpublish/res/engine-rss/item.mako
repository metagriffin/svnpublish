# -*- coding: utf-8 -*-
<%!
import re
from svnpublish.reposchange import RepositoryChange
from svnpublish.util import size2str
%>\
## TODO: convert this to a stylesheet + inlining thereof. and use LESS!
## TODO: check whether or not this data is being escaped or not...
<div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;">
 <div style="background:#ddd;border:4px solid #666;padding:0px;">
  <div style="padding:.2em .6em;display:inline;background:#666;color:#fff;">
   <span style="font-weight:bold;font-size:120%;">${params.name}</span>
  </div>
  <div style="padding:.2em .6em;display:inline;">
   <b>revision ${revinfo.revision}</b>
   <span style="color:#333;">by</span> <b>${revinfo.author}</b>
   <span style="color:#333;">on</span> <b>${revinfo.date}</b>
  </div>
 </div>
 <div style="font-size:10pt;">
  ##---------------------------------------------------------------------------
  ## log
  <fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;">
   <legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"><b>Log Message</b></legend>
   <pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;">\
% if revinfo.log:
${revinfo.log}\
% else:
<em>(none)</em>\
% endif
</pre>
  </fieldset>
  ##---------------------------------------------------------------------------
  ## change summary
  <fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;">
   <legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"><b>Overview</b></legend>
   % if len(params.root) > 0:
    <div>
     Changes to repository directory <a href="${params.reposUrl}/${params.root}">${params.root}</a>:
    </div>
   % endif
   <table cellpadding="0" cellspacing="0" border="0">
<%
## TODO: i18n...
changes = {
  RepositoryChange.Content.ADDED:    {'label': 'Added', 'entries': []},
  RepositoryChange.Content.MODIFIED: {'label': 'Modified', 'entries': []},
  RepositoryChange.Content.DELETED:  {'label': 'Deleted', 'entries': []},
  RepositoryChange.Content.NONE:     {'label': 'PropChange', 'entries': []},
}
for e in revinfo.changes:
  changes[e.content]['entries'].append(e)
%>\
    % for code in (RepositoryChange.Content.ADDED, \
                   RepositoryChange.Content.MODIFIED, \
                   RepositoryChange.Content.DELETED, \
                   RepositoryChange.Content.NONE):
     % if len(changes[code]['entries']) > 0:
      <tr>
       <td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;">${changes[code]['label']}</td>
       <td align="left" valign="top" style="padding-top:.7em;">
        <ul style="margin-top:0px;">
         % for entry in changes[code]['entries']:
          <li><a href="${params.reposUrl}/${entry.path}">${entry.path}</a></li>
         % endfor
        </ul>
       </td>
      </tr>
     % endif
    % endfor
   </table>
  </fieldset>
  ##---------------------------------------------------------------------------
  ## diff
  <fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;">
   <legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"><b>Detail</b></legend>
   ## todo: note: i do not particularly like the following regex substitution, but certain
   ## RSS readers have trouble with ascii control characters... argh... from below:
   ## ${re.sub('[^ -~\w\d\t\n\r]+', '?', revinfo.diff[:16384])}
   ## TODO: turn this into a mako filter!...
   ## TODO: share with engine-email/truncated...
   <pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    >${re.sub('[^ -~\w\d\t\n\r]+', '?', revinfo.diff[:16384])}</pre>
   % if len(revinfo.diff) > 16384:
    <pre
     style="margin:1em 0px 0px 0px;border:0px;padding:0px;line-height:1em;font-style:italic;color:#f00;"
     >[...snip: ${size2str(len(revinfo.diff) - 16384)}...]</pre>
   % endif
  </fieldset>
 </div>
</div>
