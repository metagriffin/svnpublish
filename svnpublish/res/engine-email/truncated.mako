# -*- coding: utf-8 -*-
<%!
from svnpublish.reposchange import RepositoryChange
from svnpublish.util import size2str, tsl
from svnpublish import framework
%>\
<%namespace file="diff.mako" name="diff"/>\
<!DOCTYPE html>
<html
 lang="en"
 xml:lang="en"
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://pythonhosted.org/genemail/xmlns/1.0"
 >
 <head>
  <title
   email:subject="content"
   >[SVN|${params.label.upper()}] r${revinfo.revision} by ${revinfo.author} - ${revinfo.summary}</title>
  <base href="${params.reposUrl}"/>
  <meta name="generator" content="svnpublish/v${framework.version}"/>
  % if style:
   <style type="text/css">${style}</style>
  % endif
 </head>
 <body>
  <div class="clamp">
   ## PLEASE NOTE: i humbly apologize for the use of tables here...
   ##   i would have used DIVs, but microsoft, for some *very* brain-dead
   ##   reason, decided to switch the outlook HTML rendering engine from
   ##   IE to WORD... and thereby set us back one decade... ijiots.
   <div class="clampHead">
    <table class="border" cellpadding="0" cellspacing="0" border="0">
     <tr class="t">
      <td class="l"></td>
      <td class="c"></td>
      <td class="r"></td>
     </tr>
     <tr class="c">
      <td class="l"></td>
      <td class="c">
       <table class="outer" cellpadding="0" cellspacing="0" border="0">
        <tr class="c">
         <td class="c">
          <table class="row" cellpadding="0" cellspacing="0" border="0">
           <tr>
            <td class="ol"></td>
            <td class="ll"></td>
            <td class="label">${params.name}</td>
            <td class="lr"></td>
            <td class="il"></td>
            <td class="info">
             <span>revision</span> <b>${revinfo.revision}</b>
             <span>by</span> <b>${revinfo.author}</b>
             <span>on</span> <b>${revinfo.date}</b>
            </td>
            <td class="ir"></td>
            <td class="or"></td>
           </tr>
          </table>
         </td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
      <td class="r"></td>
     </tr>
     <tr class="b">
      <td class="l"></td>
      <td class="c"></td>
      <td class="r"></td>
     </tr>
    </table>
   </div>
   <div class="clampBody">

    <table class="section logmsg" cellpadding="0" cellspacing="0" border="0">
     <tr class="head">
      <td class="cc">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c"><div class="label">Log Message</div></td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td>
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c">
          % if len(revinfo.log.strip()) <= 0:
           <pre class="logmsg none">(none)</pre>
          % else:
           <pre class="logmsg"
            >${'\n'.join(revinfo.log.strip().split('\n')[:12])}</pre>
           % if len(revinfo.log.strip().split('\n')) > 12:
            <pre class="snip">[...snip...]</pre>
           % endif
          % endif
         </td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
    </table>

    <table class="section changes" cellpadding="0" cellspacing="0" border="0">
     <tr class="head">
      <td class="cc">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c"><div class="label">Overview</div></td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td>
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c">
          % if len(params.root) > 0:
           <div class="intro">
            Changes to repository directory <a href="${params.reposUrl}/${params.root}">${params.root}</a>:
           </div>
          % endif
          <table
           class="${'hasroot' if len(params.root) > 0 else ''}"
           cellpadding="0" cellspacing="0" border="0">
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
             <tr class="change ${changes[code]['label'].lower()}">
              <th align="left" valign="top" class="label">${changes[code]['label']}</th>
              <td align="left" valign="top" class="list">
               <ul class="changelist">
                % for entry in changes[code]['entries']:
                 <li><a href="${params.reposUrl}/${entry.path}">${entry.path}</a></li>
                % endfor
               </ul>
              </td>
             </tr>
            % endif
           % endfor
          </table>
         </td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
    </table>

    <table class="section diff" cellpadding="0" cellspacing="0" border="0">
     <tr class="head">
      <td class="cc">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c"><div class="label">Detail</div></td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td>
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
        <tr class="c">
         <td class="l"></td>
         <td class="c">
          % if genemail_format == 'text':
           ${diff.renderPlain(revinfo, maxBytes=524288, maxLines=8192, rssCompat=False)}
          % else:
           ${diff.renderTable(revinfo, maxBytes=524288, maxLines=8192, rssCompat=False)}
          % endif
         </td>
         <td class="r"></td>
        </tr>
        <tr class="b">
         <td class="l"></td>
         <td class="c"></td>
         <td class="r"></td>
        </tr>
       </table>
      </td>
     </tr>
    </table>

    <div class="credits">
     Generated by
     svnpublish/v${framework.version}
     on ${tsl()}.
    </div>
   </div>
  </div>
 </body>
</html>
