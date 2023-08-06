var modified_timestamp;
var _base_url = location.href.split(/[\?\#]/)[0];
if (_base_url.slice(-10)=='index_html')
  _base_url = _base_url.slice(0,-10);
if (_base_url.charAt(_base_url.length-1)=='/')
  _base_url = _base_url.substring(0, _base_url.length-1);

function clearAutoRefreshTitle() {
  document.title = document.title.replace(/\(automatically refreshed\) /,'');
}


function checkRefresh() {
   if (!modified_timestamp) return false;
   
   $.get(_base_url+'/getModifyTimestamp?nocache='+(Math.random()+"").substr(2, 5),{}, function(resp) {
      if (resp && modified_timestamp && parseInt(resp) != parseInt(modified_timestamp)) {
         modified_timestamp = resp;
         $('#outlook-outer').load(_base_url+'/show_outlook?nocache='+(Math.random()+"").substr(2, 5));
         if (document.title.indexOf("(automatically refreshed) ")==-1)
           document.title = "(automatically refreshed) " + document.title;
         refreshinterval = orig_refreshinterval;
         $('#outlook-outer').click(clearAutoRefreshTitle);
      }
   });
}

var refreshinterval,orig_refreshinterval;
refreshinterval=orig_refreshinterval=5; // seconds
function startautorefresh() {
  checkRefresh();
  r_timer=window.setTimeout(startautorefresh, refreshinterval*1000);
  refreshinterval+= refreshinterval*0.07;
}

$(function() {
   // Initiall set modified_timestamp
   $.get(_base_url+'/getModifyTimestamp', {}, function(resp) {
      if (resp) modified_timestamp = resp;
   });
   
   setTimeout(function() {
      startautorefresh();
   }, 3*1000);
   

});

 
  
function _deldraft(draftid, method) {
  $('li.draft-'+draftid).remove();
  $.post(method, {id:draftid, return_show_drafts:1}, function(resp) {
      $('#issuedraftsouter').html(resp);
  });
  return false;  
}
function deldraft(draftid) { return _deldraft(draftid, 'DeleteDraftIssue'); }
function deldraftfollowup(draftid) { return _deldraft(draftid, 'DeleteDraftFollowup'); }


