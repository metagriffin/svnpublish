# -*- coding: utf-8 -*-
<%!
import re
from svnpublish.reposchange import RepositoryChange
from svnpublish.util import size2str
from svnpublish import framework
%>\
<!DOCTYPE html>
<html
 lang="en"
 xml:lang="en"
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://pythonhosted.org/genemail/xmlns/1.0"
 >
 <head>
  <title email:subject="content">[${(options.label or 'NOLABEL').upper()}] svnpublish executed with
   % if errorCount <= 0:
     ${messageCount} message${'s' if messageCount != 1 else ''}
   % else:
     ${errorCount} error${'s' if errorCount != 1 else ''}
   % endif
  </title>
  <style type="text/css">

body > div
{
  background:           #ffffff;
  font:                 10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;
}

#ClampHead
{
  background:           #ffdddd;
  border:               4px solid #ff0000;
  padding:              0px;
}

#ClampHead div.label
{
  padding:              .2em .6em;
  display:              inline;
  background:           #ff0000;
  color:                #ffffff;
}

#ClampHead div.label > span
{
  font-weight:          bold;
  font-size:            120%;
}

#ClampHead div.subject
{
  padding:              .2em .6em;
  display:              inline;
}

#ClampHead div.subject span
{
  color:                #333333;
}

div.command,
div.message
{
  margin:               3em;
  display:              table;
  border:               1px dotted #000000;
  background:           #ffdddd;
  padding:              1em 2em;
}

  </style>
 </head>
 <body>
  <div id="ClampOuter">
   <div id="ClampHead">
    <div class="label"><span>${options.name}</span></div>
    <div class="subject">
     <b>svnpublish executed</b>
     <span>with</span> <b>${errorCount} error${errorCount} error${'s' if errorCount != 1 else ''}</b>
     <span>and</span> <b>${messageCount} message${'s' if messageCount != 1 else ''}</b>
    </div>
   </div>
   <div id="ClampBody">
    <p>svnpublish executed uncleanly when invoked with:</p>
    <div class="command">
     <pre>${command}</pre>
    </div>
    <p>svnpublish generated the following messages:</p>
    <div class="message">
     <pre>${messages}</pre>
    </div>
    <p>
svnpublish hopes that things will run smoother next time - especially
if you take care of these issues! ;-)
    </p>
    <p>Thank you for using <b>svnpublish</b>!</p>
   </div>
   <div id="ClampFoot">
    <p>svnpublish v${framework.version}</p>
    <p>[<a href="https://www.github.com/metagriffin/svnpublish/">svnpublish home page</a>]</p>
   </div>
  </div>
 </body>
</html>
