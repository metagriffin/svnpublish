# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: unit test for "email" svnpublish engine module
# auth: griffin <griffin@uberdev.org>
# date: 2011/05/14
# copy: (C) CopyLoose 2011 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import sys, unittest, os, yaml, logging, six, genemail
import genemail.testing, pxml
from aadict import aadict

from svnpublish import framework, subversion, revinfo
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
class TestEmail(TestCase, pxml.XmlTestMixin, genemail.testing.EmailTestMixin):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestEmail, self).setUp()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.sender = genemail.DebugSender()
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.options.genemail.sender = self.sender
    self.options.configOrder     = ['all']
    self.options.publishOnly     = ['content']
    self.options.genemail.default.boundary = 'MIMEBOUNDARY=z1'

  #----------------------------------------------------------------------------
  def test_email_dryrun(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.dryrun = True
    registerAllConfig('all', '''\
publish:
  - engine: email
    recipients: rcpt@example.com
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0)
    self.assertMultiLineEqual(self.logput.getvalue(), '''\
dry-run mode enabled: not executing any "write" actions
publishing point "/" not in options.publishOnly - skipping
processing publishing point "content"
processing publishing point "content", engine "email"
loading engine "email" (callable: svnpublish.engine.email.publish_email)
using framework email manager template "engine-email/truncated"
dry-run: commit-notification from None to rcpt@example.com
  subject: [SVN|TESTLABEL] r3 by svnuser - simple update with text changes
''')
    self.assertEqual(len(self.sender.emails), 0)

  #----------------------------------------------------------------------------
  def test_email_simple(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    registerAllConfig('all', '''\
publish:
  - engine: email
    recipients: rcpt@example.com
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    chk = '''\
Content-Type: multipart/alternative; boundary="==MIMEBOUNDARY=z1-alt-2=="
MIME-Version: 1.0
To: rcpt@example.com
From: "svnpublish" <noreply@localhost>
Date: Fri, 13 Feb 2009 23:31:30 -0000
Subject: [SVN|TESTLABEL] r3 by svnuser - simple update with text changes

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit

testName

**revision 3** by **svnuser** on **2011-04-29T02:57:23Z**

Log Message

    ''' + '''
    simple update with text changes

Overview

Changes to repository directory
[content](https://svn.example.com/repos/content):

Modified

  * [content/textfile.txt](https://svn.example.com/repos/content/textfile.txt)

Detail

    ''' + '''
    Modified: content/textfile.txt
    ===================================================================
    --- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
    +++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
    @@ -1 +1 @@
    -this is a sample textfile.txt.
    +this is a sample textfile.txt with changes.

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
 <head>
  <title>[SVN|TESTLABEL] r3 by svnuser - simple update with text changes</title>
  <base href="https://svn.example.com/repos" />
 </head>
 <body>
  <div class="clamp" style="background: #fff;font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
   <div class="clampHead">
    <table border="0" cellpadding="0" cellspacing="0" class="border" style="width: 100%">
     <tr class="t" style="height: 4px;background: #666">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
     </tr>
     <tr class="c">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #666" />
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
       <table border="0" cellpadding="0" cellspacing="0" class="outer" style="width: 100%">
        <tr class="c">
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
          <table border="0" cellpadding="0" cellspacing="0" class="row">
           <tr>
            <td class="ol" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #666;color: #fff;font-variant: small-caps;width: 0" />
            <td class="ll" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #666;color: #fff;font-variant: small-caps;width: 10px" />
            <td class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-size: 120%;background: #666;color: #fff;font-variant: small-caps">testName</td>
            <td class="lr" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #666;color: #fff;font-variant: small-caps;width: 10px" />
            <td class="il" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd" />
            <td class="info" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
             <b>revision 3</b>
             <span style="color: #333">by</span> <b>svnuser</b>
             <span style="color: #333">on</span> <b>2011-04-29T02:57:23Z</b>
            </td>
            <td class="ir" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd" />
            <td class="or" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
           </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd" />
        </tr>
       </table>
      </td>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #666" />
     </tr>
     <tr class="b" style="height: 4px;background: #666">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
     </tr>
    </table>
   </div>
   <div class="clampBody" style="font-size: 10pt">
    <table border="0" cellpadding="0" cellspacing="0" class="section logmsg" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner" style="background: #aaa;border: 1px solid black;border-bottom-style: none">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"><div class="label">Log Message</div></td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
           <pre class="logmsg" style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0;max-height: 15.7em;overflow: hidden">simple update with text changes</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table border="0" cellpadding="0" cellspacing="0" class="section changes" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner" style="background: #aaa;border: 1px solid black;border-bottom-style: none">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"><div class="label">Overview</div></td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
           <div class="intro">
            Changes to repository directory <a href="https://svn.example.com/repos/content">content</a>:
           </div>
          <table border="0" cellpadding="0" cellspacing="0" class="hasroot" style="padding-top: 0.5em">
             <tr class="change modified">
              <th align="left" class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold" valign="top">Modified</th>
              <td align="left" class="list" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" valign="top">
               <ul class="changelist">
                 <li><a href="https://svn.example.com/repos/content/textfile.txt">content/textfile.txt</a></li>
               </ul>
              </td>
             </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table border="0" cellpadding="0" cellspacing="0" class="section diff" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner" style="background: #aaa;border: 1px solid black;border-bottom-style: none">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"><div class="label">Detail</div></td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps" />
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table border="0" cellpadding="0" cellspacing="0" class="inner">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <pre style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0">Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif" />
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px" />
        </tr>
       </table>
      </td>
     </tr>
    </table>
   </div>
  </div>
 </body>
</html>
--==MIMEBOUNDARY=z1-alt-2==--
'''

    self.assertEqual(len(self.sender.emails), 1)
    eml = self.sender.emails[0]
    self.assertEqual(eml['mailfrom'], 'noreply@localhost')
    self.assertEqual(eml['recipients'], ['rcpt@example.com'])
    self.assertEmailEqual(eml['message'], chk)

  #----------------------------------------------------------------------------
  def test_email_styled(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    registerAllConfig('all', '''\
publish:
  - engine: email
    recipients: rcpt@example.com
    style: |
      div.clampHead table.border > tr.t,
      div.clampHead table.border > tr.b {height:4px;background:#042d5a;}
      div.clampHead table.border > tr.c > td.l,
      div.clampHead table.border > tr.c > td.r {width:4px;background:#042d5a;}
      div.clampHead .ol {background:#042d5a;}
      div.clampHead .ll,
      div.clampHead .lr,
      div.clampHead .label {background:#042d5a;color:#f8991c;}
      table.section > tr.head table {background:#f8991c;}
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    chk = '''\
Content-Type: multipart/alternative; boundary="==MIMEBOUNDARY=z1-alt-2=="
MIME-Version: 1.0
To: rcpt@example.com
From: "svnpublish" <noreply@localhost>
Date: Fri, 13 Feb 2009 23:31:30 -0000
Subject: [SVN|TESTLABEL] r3 by svnuser - simple update with text changes

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit

testName

**revision 3** by **svnuser** on **2011-04-29T02:57:23Z**

Log Message

    ''' + '''
    simple update with text changes

Overview

Changes to repository directory
[content](https://svn.example.com/repos/content):

Modified

  * [content/textfile.txt](https://svn.example.com/repos/content/textfile.txt)

Detail

    ''' + '''
    Modified: content/textfile.txt
    ===================================================================
    --- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
    +++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
    @@ -1 +1 @@
    -this is a sample textfile.txt.
    +this is a sample textfile.txt with changes.

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>[SVN|TESTLABEL] r3 by svnuser - simple update with text changes</title>
  <base href="https://svn.example.com/repos"/>
 </head>
 <body>
  <div class="clamp" style="background: #fff;font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
   <div class="clampHead">
    <table class="border" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="t" style="height: 4px;background: #042d5a">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
     </tr>
     <tr class="c">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #042d5a"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
       <table class="outer" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
        <tr class="c">
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
          <table class="row" cellpadding="0" cellspacing="0" border="0">
           <tr>
            <td class="ol" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;color: #fff;font-variant: small-caps;width: 0;background: #042d5a"/>
            <td class="ll" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-variant: small-caps;width: 10px;background: #042d5a;color: #f8991c"/>
            <td class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-size: 120%;font-variant: small-caps;background: #042d5a;color: #f8991c">testName</td>
            <td class="lr" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-variant: small-caps;width: 10px;background: #042d5a;color: #f8991c"/>
            <td class="il" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd"/>
            <td class="info" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
             <b>revision 3</b>
             <span style="color: #333">by</span> <b>svnuser</b>
             <span style="color: #333">on</span> <b>2011-04-29T02:57:23Z</b>
            </td>
            <td class="ir" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd"/>
            <td class="or" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
           </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd"/>
        </tr>
       </table>
      </td>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #042d5a"/>
     </tr>
     <tr class="b" style="height: 4px;background: #042d5a">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
     </tr>
    </table>
   </div>
   <div class="clampBody" style="font-size: 10pt">
    <table class="section logmsg" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Log Message</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
           <pre class="logmsg" style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0;max-height: 15.7em;overflow: hidden">simple update with text changes</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table class="section changes" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Overview</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <div class="intro">
            Changes to repository directory <a href="https://svn.example.com/repos/content">content</a>:
           </div>
          <table class="hasroot" cellpadding="0" cellspacing="0" border="0" style="padding-top: 0.5em">
           <tr class="change modified">
            <th align="left" valign="top" class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold">Modified</th>
            <td align="left" valign="top" class="list" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
             <ul class="changelist">
              <li>
               <a href="https://svn.example.com/repos/content/textfile.txt">content/textfile.txt</a>
              </li>
             </ul>
            </td>
           </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table class="section diff" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Detail</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <pre style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0">Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
   </div>
  </div>
 </body>
</html>

--==MIMEBOUNDARY=z1-alt-2==--
'''

    self.assertEqual(len(self.sender.emails), 1)
    self.assertEqual(self.sender.emails[0]['mailfrom'], 'noreply@localhost')
    self.assertEqual(self.sender.emails[0]['recipients'], ['rcpt@example.com'])
    self.assertEmailEqual(self.sender.emails[0]['message'], chk)

  #----------------------------------------------------------------------------
  def test_email_styledGlobal(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.update(yaml.load('''\
engines:
  email:
    defaults:
      style: |
        div.clampHead table.border > tr.t,
        div.clampHead table.border > tr.b {height:4px;background:#042d5a;}
        div.clampHead table.border > tr.c > td.l,
        div.clampHead table.border > tr.c > td.r {width:4px;background:#042d5a;}
        div.clampHead .ol {background:#042d5a;}
        div.clampHead .ll,
        div.clampHead .lr,
        div.clampHead .label {background:#042d5a;color:#f8991c;}
        table.section > tr.head table {background:#f8991c;}
'''))
    registerAllConfig('all', '''\
publish:
  - engine: email
    recipients: rcpt@example.com
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    chk = '''\
Content-Type: multipart/alternative; boundary="==MIMEBOUNDARY=z1-alt-2=="
MIME-Version: 1.0
To: rcpt@example.com
From: "svnpublish" <noreply@localhost>
Date: Fri, 13 Feb 2009 23:31:30 -0000
Subject: [SVN|TESTLABEL] r3 by svnuser - simple update with text changes

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit

testName

**revision 3** by **svnuser** on **2011-04-29T02:57:23Z**

Log Message

    ''' + '''
    simple update with text changes

Overview

Changes to repository directory
[content](https://svn.example.com/repos/content):

Modified

  * [content/textfile.txt](https://svn.example.com/repos/content/textfile.txt)

Detail

    ''' + '''
    Modified: content/textfile.txt
    ===================================================================
    --- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
    +++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
    @@ -1 +1 @@
    -this is a sample textfile.txt.
    +this is a sample textfile.txt with changes.

--==MIMEBOUNDARY=z1-alt-2==
MIME-Version: 1.0
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>[SVN|TESTLABEL] r3 by svnuser - simple update with text changes</title>
  <base href="https://svn.example.com/repos"/>
 </head>
 <body>
  <div class="clamp" style="background: #fff;font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
   <div class="clampHead">
    <table border="0" cellpadding="0" cellspacing="0" class="border" style="width: 100%">
     <tr class="t" style="height: 4px;background: #042d5a">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
     </tr>
     <tr class="c">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #042d5a"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
       <table class="outer" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
        <tr class="c">
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
          <table class="row" cellpadding="0" cellspacing="0" border="0">
           <tr>
            <td class="ol" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;color: #fff;font-variant: small-caps;width: 0;background: #042d5a"/>
            <td class="ll" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-variant: small-caps;width: 10px;background: #042d5a;color: #f8991c"/>
            <td class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-size: 120%;font-variant: small-caps;background: #042d5a;color: #f8991c">testName</td>
            <td class="lr" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-variant: small-caps;width: 10px;background: #042d5a;color: #f8991c"/>
            <td class="il" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd"/>
            <td class="info" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd">
             <b>revision 3</b>
             <span style="color: #333">by</span> <b>svnuser</b>
             <span style="color: #333">on</span> <b>2011-04-29T02:57:23Z</b>
            </td>
            <td class="ir" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;background: #ddd"/>
            <td class="or" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
           </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;background: #ddd"/>
        </tr>
       </table>
      </td>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 4px;background: #042d5a"/>
     </tr>
     <tr class="b" style="height: 4px;background: #042d5a">
      <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
      <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
     </tr>
    </table>
   </div>
   <div class="clampBody" style="font-size: 10pt">
    <table class="section logmsg" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Log Message</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <pre class="logmsg" style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0;max-height: 15.7em;overflow: hidden">simple update with text changes</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table class="section changes" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Overview</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <div class="intro">
            Changes to repository directory <a href="https://svn.example.com/repos/content">content</a>:
           </div>
          <table class="hasroot" cellpadding="0" cellspacing="0" border="0" style="padding-top: 0.5em">
           <tr class="change modified">
            <th align="left" valign="top" class="label" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold">Modified</th>
            <td align="left" valign="top" class="list" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
             <ul class="changelist">
              <li>
               <a href="https://svn.example.com/repos/content/textfile.txt">content/textfile.txt</a>
              </li>
             </ul>
            </td>
           </tr>
          </table>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
    <table class="section diff" cellpadding="0" cellspacing="0" border="0" style="width: 100%">
     <tr class="head">
      <td class="cc" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;padding-top: 1em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid black;border-bottom-style: none;background: #f8991c">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps">
          <div class="label">Detail</div>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;font-weight: bold;font-variant: small-caps"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px;font-weight: bold;font-variant: small-caps"/>
        </tr>
       </table>
      </td>
     </tr>
     <tr class="body">
      <td style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;border-top: 1px solid black;border-bottom: 1px solid black;background: #ddd;padding-top: 0.5em;padding-bottom: 0.4em">
       <table class="inner" cellpadding="0" cellspacing="0" border="0">
        <tr class="t">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="c">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif">
          <pre style="font-family: &quot;Lucida Console&quot;, Consolas, &quot;Andale Mono&quot;, &quot;Lucida Sans Typewriter&quot;, &quot;DejaVu Sans Mono&quot;, &quot;Bitstream Vera Sans Mono&quot;, &quot;Liberation Mono&quot;, &quot;Nimbus Mono L&quot;, Monaco, &quot;Courier New&quot;, Courier, monospace;margin: 0;border: 0;padding: 0">Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

</pre>
         </td>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
        <tr class="b">
         <td class="l" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
         <td class="c" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif"/>
         <td class="r" style="font: 10pt &quot;Trebuchet MS&quot;, lucida, geneva, verdana, sans-serif;width: 10px"/>
        </tr>
       </table>
      </td>
     </tr>
    </table>
   </div>
  </div>
 </body>
</html>

--==MIMEBOUNDARY=z1-alt-2==--
'''

    self.assertEqual(len(self.sender.emails), 1)
    self.assertEqual(self.sender.emails[0]['mailfrom'], 'noreply@localhost')
    self.assertEqual(self.sender.emails[0]['recipients'], ['rcpt@example.com'])
    self.assertEmailEqual(self.sender.emails[0]['message'], chk)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
