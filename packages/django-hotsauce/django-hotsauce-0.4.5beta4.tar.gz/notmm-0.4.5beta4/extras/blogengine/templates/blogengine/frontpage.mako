## coding: UTF-8
## New template for gthcfoundation.org (wintergreen style)
##
<%def name="pagetitle()">
F420 > FrontPage
</%def>

<%
media_prefix = data['MEDIA_URL']
recent_changes = data['recent_changes']
%>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
 <title>${self.pagetitle()}</title>
 <script src="${media_prefix}js/jquery-ui-1.10.3/js/jquery-1.9.1.js"></script>
 <script src="${media_prefix}js/jquery-ui-1.10.3/js/jquery-ui-1.10.3.custom.min.js"></script>
 <script src="${media_prefix}js/tm_api-2.0/src/colorlist.min.js"> </script>
 <script src="${media_prefix}js/tm_api-2.0/src/dialog.js"></script>
 <script src="${media_prefix}js/setup.js"></script>
 <link href="${media_prefix}css/ui-style.css" rel="stylesheet">
 <link href="${media_prefix}css/reset.css"  rel="stylesheet">
 <link href="${media_prefix}css/layout.css" rel="stylesheet">
 <link href="${media_prefix}css/ui-colorlist.css" rel="stylesheet">
 <link href="${media_prefix}css/ui-base.css" rel="stylesheet">
 <link href="${media_prefix}css/ui-css3.css" rel="stylesheet">
 <link href="${media_prefix}css/ui-tablesorter.css" rel="stylesheet">
 <link href="${media_prefix}js/jquery-ui-1.10.3/css/cupertino/jquery-ui-1.10.3.custom.css" rel="stylesheet" media="screen" />
 <link href="${media_prefix}favicon.ico" rel="shortcut icon" />

 <meta charset="UTF-8"> 

 <meta name="Author" content="http://gthcfoundation.org">
 <meta name="Keywords" content="gthc, gthc.org, greenteahackersclub, green tea hackers club, green tea, 420, 420Linux, F420, fondation 420, marijuana, liberty, freedom, free speech, free software, hacking, python, django hotsauce, notmm, web development, web design, software, technology, science">
</head>
##<body style="background: url(${media_prefix}img/bg2.jpg) 0 30% no-repeat;">
<body>
<div id="content" style="background: rgba(200,200,200,0.60)">
<div id="page">

 
 <div id="header">
 <a href="/frontpage/" style="border: none">
  <img src="${media_prefix}img/5th_logo.png"/>
 </a>
 <div id="ui-breadcrump">
 </div>
 </div>
 <br class="clear">
 
 <!-- 1st column top left -->
 <div class="fl col200">
 
 <div class="b1 ui-rounded ui-generic whitebg">
 <%def name="pagemenu(title='Navigation')">
  <h2 class="pinkbg">${title}</h2>
  ## TODO: use YAML for editing menus?
  ## invoke with self.pagemenu(title='Page title', ...) 
  <ul class="colorList greybg2">

   <li><a href="/software/">» Softwares</a></li>
   <li><a href="/hg/">» Public repositories</a></li>
   
   <li><a href="/blog/">» Blog</a></li>
   <li><a href="/wiki/">» Wiki</a></li>
   ## <li><a href="/about/">» About</a>
   <li><a href="/contact/">» Contact</a>

   ##<!-- <li><a href="research.html">Research</a></li> -->
   ##<li><a href="/resources/">» Resources</a></li>
   ##<!-- <li><a href="/artworks/">» Artworks</a></li> -->

  </ul>
 </%def>
 ${self.pagemenu()}
 </div>
 </div>
 <!-- col2 (middle) -->
 <div id="pagecontent" class="fl col400">
 <%def name="pagecontent()">
 <div class="b1 ui-rounded ui-generic whitebg">
 ${self.recentposts()} 
 </div>
 </%def>
  ${self.pagecontent()}
 </div>
 <div id="col3" class="fl col250">
 <div class="b1 ui-rounded uigeneric whitebg">
  <h2 class="pinkbg">Recent Changes</h2>
  <ul id="recent-changes" class="colorList greybg2">
  % for item in recent_changes['entries']:
    <li><a href="${item.link}">${item.title}</a></li>
  % endfor
  </ul>
 </div>

 <br class="clear"/>
</div>
</div>
</body>
</html>

<%def name="recentposts()" cached="False">
<%
entries = data['blogentry_set']
%>
<%namespace file="test.mako" import="latest_posts" />
${latest_posts(entries)}
</%def>

<script type="text/javascript">
;(function($j){
$j('#'+'ui-breadcrump').append('<p>You are here: ' + window.location + '</p>')})
(jQuery);    
</script>

