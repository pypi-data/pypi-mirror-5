define(["jquery"],function(e){var t,n;return n=function(e){var t,n,r,i;return t=document.location.host,r=document.location.protocol,i="//"+t,n=r+i,e===n||e.slice(0,n.length+1)===n+"/"||e===i||e.slice(0,i.length+1)===i+"/"||!/^(\/\/|http:|https:).*/.test(e)},t=function(e){return/^(GET|HEAD|OPTIONS|TRACE)$/.test(e)},e.ajaxPrefilter(function(e,r,i){if(!t(e.type)&&n(e.url))return i.setRequestHeader("X-CSRFToken",App.CSRF_TOKEN)})});