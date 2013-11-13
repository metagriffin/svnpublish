# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/05/15
# copy: (C) Copyright 2011-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import sys, unittest, os, yaml, logging, six, pickle, re
import genemail, fso, pxml
from aadict import aadict

from svnpublish import framework, api, subversion, revinfo
from ..test_helper import TestCase, registerAllConfig

#------------------------------------------------------------------------------
class TestRss(TestCase, pxml.XmlTestMixin):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestRss, self).setUp()
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
    self.fso = fso.push()

  #----------------------------------------------------------------------------
  def tearDown(self):
    super(TestRss, self).tearDown()
    fso.pop()

  #----------------------------------------------------------------------------
  def test_rss_simple(self):
    svnrev  = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:        rss
    label:         My RSS
    name:          My Real Simple Sindication
    output:        /tmp/svnpublish-unittest-engine-rss/output.rss
    feedUrl:       http://rss.example.com/rss.xml
    onCacheError:  ignore
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:/tmp/svnpublish-unittest-engine-rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss.pkl',
      ])
    rsschk = '''<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
 <channel>
  <title>My RSS</title>
  <description>My Real Simple Sindication</description>
  <link>http://rss.example.com/rss.xml</link>
  <lastBuildDate>Fri, 13 Feb 2009 23:31:30 GMT</lastBuildDate>
  <generator>svnpublish/''' + framework.version + '''</generator>
  <docs>http://www.rssboard.org/rss-specification</docs>
  <item>
   <id>https://svn.example.com/repos/?rev=3</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=3</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r3: simple update with text changes</title>
   <link>https://svn.example.com/repos/?rev=3</link>
   <pubDate>Fri, 29 Apr 2011 02:57:23 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 3&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:57:23Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;simple update with text changes&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;Modified&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item>
 </channel>
</rss>'''
    self.assertXmlEqual(
      self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss'].content,
      rsschk)
    chk = [revinfo.FilteredRevisionInfo(
      revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3'), 'content')]
    self.assertMultiLineEqual(
      self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss.pkl'].content,
      pickle.dumps(chk))

  #----------------------------------------------------------------------------
  def test_rss_templateFromRes(self):
    svnrev  = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:        rss
    label:         My RSS
    name:          My Real Simple Sindication
    output:        /tmp/svnpublish-unittest-engine-rss/output.rss
    feedUrl:       http://rss.example.com/rss.xml
    onCacheError:  ignore
    template-feed: svnpublish-res:engine-rss-default-feed.gst
    template-item: svnpublish-res:engine-rss-default-item.gst
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:/tmp/svnpublish-unittest-engine-rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss.pkl'
      ])
    rsschk = '''<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
 <channel>
  <title>My RSS</title>
  <description>My Real Simple Sindication</description>
  <link>http://rss.example.com/rss.xml</link>
  <lastBuildDate>Fri, 13 Feb 2009 23:31:30 GMT</lastBuildDate>
  <generator>svnpublish/''' + framework.version + '''</generator>
  <docs>http://www.rssboard.org/rss-specification</docs>
  <item>
   <id>https://svn.example.com/repos/?rev=3</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=3</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r3: simple update with text changes</title>
   <link>https://svn.example.com/repos/?rev=3</link>
   <pubDate>Fri, 29 Apr 2011 02:57:23 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 3&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:57:23Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;simple update with text changes&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;Modified&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item>
 </channel>
</rss>'''
    self.assertXmlEqual(
      self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss'].content,
      rsschk)

  #----------------------------------------------------------------------------
  def test_rss_pickle(self):
    # populating with r3 pickle...
    r3revlist = [revinfo.FilteredRevisionInfo(
      revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3'), 'content')]
    if not os.path.exists('/tmp/svnpublish-unittest-engine-rss'):
      os.makedirs('/tmp/svnpublish-unittest-engine-rss')
    with open('/tmp/svnpublish-unittest-engine-rss/output.rss.pkl', 'wb') as fp:
      fp.write(pickle.dumps(r3revlist))
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:  rss
    label:   My RSS
    name:    My Real Simple Sindication
    output:  /tmp/svnpublish-unittest-engine-rss/output.rss
    feedUrl: http://rss.example.com/rss.xml
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:/tmp/svnpublish-unittest-engine-rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss.pkl',
      ])
    rsschk = '''<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
 <channel>
  <title>My RSS</title>
  <description>My Real Simple Sindication</description>
  <link>http://rss.example.com/rss.xml</link>
  <lastBuildDate>Fri, 13 Feb 2009 23:31:30 GMT</lastBuildDate>
  <generator>svnpublish/''' + framework.version + '''</generator>
  <docs>http://www.rssboard.org/rss-specification</docs>
  <item>
   <id>https://svn.example.com/repos/?rev=4</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=4</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r4: addition of svn:eol-style property</title>
   <link>https://svn.example.com/repos/?rev=4</link>
   <pubDate>Fri, 29 Apr 2011 02:59:21 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 4&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:59:21Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;addition of svn:eol-style property&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;PropChange&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;
Property changes on: content/textfile.txt
___________________________________________________________________
Added: svn:eol-style
   + LF

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item><item>
   <id>https://svn.example.com/repos/?rev=3</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=3</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r3: simple update with text changes</title>
   <link>https://svn.example.com/repos/?rev=3</link>
   <pubDate>Fri, 29 Apr 2011 02:57:23 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 3&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:57:23Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;simple update with text changes&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;Modified&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item>
 </channel>
</rss>'''
    self.assertXmlEqual(
      self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss'].content,
      rsschk)
    pklchk = [
      revinfo.FilteredRevisionInfo(
        revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3'), 'content'),
      revinfo.FilteredRevisionInfo(
        revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4'), 'content')]
    self.assertMultiLineEqual(
      repr(pickle.loads(self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss.pkl'].content)),
      repr(pickle.loads(pickle.dumps(pklchk))))

  #----------------------------------------------------------------------------
  def test_rss_pickle_remap(self):
    # populating with r3 pickle, but with the wrong svn repository dirname...
    if not os.path.exists('/tmp/svnpublish-unittest-engine-rss'):
      os.makedirs('/tmp/svnpublish-unittest-engine-rss')
    with open('/tmp/svnpublish-unittest-engine-rss/output.rss.pkl', 'wb') as fp:
      fp.write(
        pickle.dumps(
          [revinfo.FilteredRevisionInfo(
              revinfo.RevisionInfo(
                subversion.Subversion('old-repos-location'), '3'),
              'content')]))
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:        rss
    label:         My RSS
    name:          My Real Simple Sindication
    output:        /tmp/svnpublish-unittest-engine-rss/output.rss
    feedUrl:       http://rss.example.com/rss.xml
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:/tmp/svnpublish-unittest-engine-rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss.pkl',
      ])
    rsschk = '''<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
 <channel>
  <title>My RSS</title>
  <description>My Real Simple Sindication</description>
  <link>http://rss.example.com/rss.xml</link>
  <lastBuildDate>Fri, 13 Feb 2009 23:31:30 GMT</lastBuildDate>
  <generator>svnpublish/''' + framework.version + '''</generator>
  <docs>http://www.rssboard.org/rss-specification</docs>
  <item>
   <id>https://svn.example.com/repos/?rev=4</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=4</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r4: addition of svn:eol-style property</title>
   <link>https://svn.example.com/repos/?rev=4</link>
   <pubDate>Fri, 29 Apr 2011 02:59:21 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 4&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:59:21Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;addition of svn:eol-style property&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;PropChange&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;
Property changes on: content/textfile.txt
___________________________________________________________________
Added: svn:eol-style
   + LF

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item><item>
   <id>https://svn.example.com/repos/?rev=3</id>
   <guid isPermaLink="true">https://svn.example.com/repos/?rev=3</guid>
   <dc:creator>svnuser</dc:creator>
   <title>r3: simple update with text changes</title>
   <link>https://svn.example.com/repos/?rev=3</link>
   <pubDate>Fri, 29 Apr 2011 02:57:23 GMT</pubDate>
   <description xml:space="preserve">&lt;div style="background:#fff;font:10pt 'Trebuchet MS',lucida,geneva,verdana,sans-serif;"&gt;
 &lt;div style="background:#ddd;border:4px solid #666;padding:0px;"&gt;
  &lt;div style="padding:.2em .6em;display:inline;background:#666;color:#fff;"&gt;
   &lt;span style="font-weight:bold;font-size:120%;"&gt;My Real Simple Sindication&lt;/span&gt;
  &lt;/div&gt;
  &lt;div style="padding:.2em .6em;display:inline;"&gt;
   &lt;b&gt;revision 3&lt;/b&gt;
   &lt;span style="color:#333;"&gt;by&lt;/span&gt; &lt;b&gt;svnuser&lt;/b&gt;
   &lt;span style="color:#333;"&gt;on&lt;/span&gt; &lt;b&gt;2011-04-29T02:57:23Z&lt;/b&gt;
  &lt;/div&gt;
 &lt;/div&gt;
 &lt;div style="font-size:10pt;"&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Log Message&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;max-height:15.7em;line-height:1em;overflow:hidden;"&gt;simple update with text changes&lt;/pre&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Overview&lt;/b&gt;&lt;/legend&gt;
    &lt;div&gt;
     Changes to repository directory &lt;a href="https://svn.example.com/repos/content"&gt;content&lt;/a&gt;:
    &lt;/div&gt;
   &lt;table cellpadding="0" cellspacing="0" border="0"&gt;
      &lt;tr&gt;
       &lt;td
        align="left"
        valign="top"
        style="padding:.7em 1em 0em 0em;font-weight:bold;"&gt;Modified&lt;/td&gt;
       &lt;td align="left" valign="top" style="padding-top:.7em;"&gt;
        &lt;ul style="margin-top:0px;"&gt;
          &lt;li&gt;&lt;a href="https://svn.example.com/repos/content/textfile.txt"&gt;content/textfile.txt&lt;/a&gt;&lt;/li&gt;
        &lt;/ul&gt;
       &lt;/td&gt;
      &lt;/tr&gt;
   &lt;/table&gt;
  &lt;/fieldset&gt;
  &lt;fieldset style="margin:.5em 0em 0em 0em;border:1px solid black;border-width:1px 0px;background:#ddd;"&gt;
   &lt;legend style="padding:.0em .6em;font-size:8pt;background:#aaa;border:1px solid black;"&gt;&lt;b&gt;Detail&lt;/b&gt;&lt;/legend&gt;
   &lt;pre style="margin:0px;border:0px;padding:0px;line-height:1em;"
    &gt;Modified: content/textfile.txt
===================================================================
--- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
+++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
@@ -1 +1 @@
-this is a sample textfile.txt.
+this is a sample textfile.txt with changes.

&lt;/pre&gt;
  &lt;/fieldset&gt;
 &lt;/div&gt;
&lt;/div&gt;
</description>
  </item>
 </channel>
</rss>'''
    self.assertXmlEqual(
      self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss'].content,
      rsschk)
    pklchk = [
      revinfo.FilteredRevisionInfo(
        revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3'), 'content'),
      revinfo.FilteredRevisionInfo(
        revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4'), 'content')]
    self.assertMultiLineEqual(
      repr(pickle.loads(self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss.pkl'].content)),
      repr(pickle.loads(pickle.dumps(pklchk))))

  #----------------------------------------------------------------------------
  def test_rss_regeneration(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '5')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['/']
    registerAllConfig('all', '''\
publish:
  - engine:        rss
    label:         My RSS Feed
    name:          My Real Simple Sindication
    output:        /tmp/svnpublish-unittest-engine-rss/output.rss
    feedUrl:       http://rss.example.com/rss.xml
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:/tmp/svnpublish-unittest-engine-rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss',
      'add:/tmp/svnpublish-unittest-engine-rss/output.rss.pkl',
      ])
    rssout = self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss'].content
    self.assertEqual(
      [m.group(1) for m in re.finditer('<title>(.*)</title>',rssout)],
      [
        'My RSS Feed',
        'r5: added a genshi-compile test file',
        'r4: addition of svn:eol-style property',
        'r3: simple update with text changes',
        'r2: moved entire tree structure',
        'r1: created an initial project hierarchy',
      ])
    chk = [
      revinfo.FilteredRevisionInfo(revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1'), '/'),
      revinfo.FilteredRevisionInfo(revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '2'), '/'),
      revinfo.FilteredRevisionInfo(revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3'), '/'),
      revinfo.FilteredRevisionInfo(revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4'), '/'),
      revinfo.FilteredRevisionInfo(revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '5'), '/'),
      ]
    self.assertMultiLineEqual(
      repr(
        pickle.loads(
          self.fso.entries['/tmp/svnpublish-unittest-engine-rss/output.rss.pkl'].content)),
      repr(chk))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
