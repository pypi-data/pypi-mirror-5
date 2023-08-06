## -*- encoding: utf-8 -*-
<%inherit file="/layout.mako" />
<%page cached="False" />
<%
request = data['request']
user = request.get_remote_user()
form = data['form']
message = data['message']
title = data['title'].encode('utf-8', 'replace')
oid = data['oid']
%>

<%def name="extra_js()">
<%
media_prefix = data['MEDIA_URL']
%>
<script type="text/javascript" src="${media_prefix}js/jquery/jquery.autocomplete.min.js">
</script>
</%def>

<div class="fl col400 whitebg ui-rounded b1">

<h2>Edit: "${title}"</h2>

<form id="editEntryForm" action="." method="POST"> 
 <table>
  <tbody>
  ${form.as_table()}
  </tbody>
 </table>
 <input id="saveBtn" type="submit" value="Save changes" />
</form>
</div>

${extra_js()}
