# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="utf-8"?>
<%! import time %>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
 <channel>

  ##---------------------------------------------------------------------------
  ## FEED HEADERS
  ##---------------------------------------------------------------------------

  % if params.label:
   <title>${params.label}</title>
  % endif
  % if params.name:
   <description>${params.name}</description>
  % endif
  % if params.feedUrl:
   <link>${params.feedUrl}</link>
  % endif
  % if params.copyright:
   <copyright>${params.copyright}</copyright>
  % endif
  % if params.language:
   <language>${params.language}</language>
  % endif
  <lastBuildDate>${time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time()))}</lastBuildDate>
  <generator>svnpublish/${params.svnpub.version}</generator>
  <docs>http://www.rssboard.org/rss-specification</docs>

  ##---------------------------------------------------------------------------
  ## ITEMS
  ##---------------------------------------------------------------------------

  ## TODO: check escaping...

  % for idx, revinfo in enumerate(reversed(revlist)):

   <item>
    <id>${params.reposUrl}/?rev=${revinfo.revision}</id>
    <guid isPermaLink="true">${params.reposUrl}/?rev=${revinfo.revision}</guid>
    <dc:creator>${revinfo.author}</dc:creator>
    <title>r${revinfo.revision}: ${revinfo.summary}</title>
    <link>${params.reposUrl}/?rev=${revinfo.revision}</link>
    <pubDate>${time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(revinfo.date_epoch))}</pubDate>
    <description xml:space="preserve">${revinfo.feedContent}</description>
   </item>

  % endfor

 </channel>
</rss>

