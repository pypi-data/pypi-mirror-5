
function toggle(id) {
    var el = document.getElementById(id);
    var link = document.getElementById('link' + id);
    if (el.style.display == 'none') {
        el.style.display = 'block';
		link.innerHTML = 'hide' + link.innerHTML.substring(4);
    } else {
        el.style.display = 'none';
		link.innerHTML = 'show' + link.innerHTML.substring(4);
	}
}

function placeFocus() {
    document.queryform.sent.focus();
}

function entsub(e) {
     var key;
     if(window.event)
          key = window.event.keyCode;     //IE
     else
          key = e.which;     //firefox
     if(key == 13)
          ajaxFunction();
}

function ajaxFunction() {
	var xmlhttp;
	if (window.XMLHttpRequest) {
	  // code for IE7+, Firefox, Chrome, Opera, Safari
	  xmlhttp=new XMLHttpRequest();
	} else if (window.ActiveXObject) {
	  // code for IE6, IE5
	  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	} else {
	  alert("Your browser does not support XMLHTTP!");
	}

    var div = document.createElement('div');
	div.innerHTML = '[...wait for it...]';
    document.getElementById('result').appendChild(div);
    window.scroll(0, document.height); // scroll to bottom of page

	xmlhttp.onreadystatechange=function() {
		if(xmlhttp.readyState==4) { // && xmlhttp.status==200) {
		  div.innerHTML = xmlhttp.responseText;
		  window.scroll(0, document.height); // scroll to bottom of page
	  }
	};
	var objfun = document.queryform.objfun;
	var marg = document.queryform.marg;
	url = "parse?sent=" + encodeURIComponent(document.queryform.sent.value)
			+ "&objfun=" + encodeURIComponent(objfun.options[objfun.selectedIndex].value)
			+ "&marg=" + encodeURIComponent(marg.options[marg.selectedIndex].value);
	xmlhttp.open("GET", url, true);
	xmlhttp.send(null);
	document.queryform.sent.value = '';
}	

