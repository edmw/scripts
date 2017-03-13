$.blockUI.defaults.css.width = "100%";
$.blockUI.defaults.css.left = "0px";
$.blockUI.defaults.css.top = "20%";
$.blockUI.defaults.css.border = "none";
$.blockUI.defaults.css.background = "transparent";

function showInfo(){
	$.blockUI({message: $('#info')});
	$('#info').click($.unblockUI);
}
function hideInfo(){
	$.unblockUI();
}

function nextImage(){
	var href = $('link[rel=next]').attr('href')
	if (href) {
		document.location = href;
	}
}

function prevImage(){
	var href = $('link[rel=prev]').attr('href');
	if (href) {
		document.location = href;
	}
}

function showIndex(){
	var href = $('link[rel=index]').attr('href');
	if (href) {
		document.location = href;
	}
}

function centerImage(){
	$("#image").css('top', ($("#content").height()-$("#image").height())/2+"px");
}

$(document).ready(function(){
	$("#information img").hover(
	  function(){
	    var src = $(this).attr("src");
	    if (src.indexOf("0.png") == -1) {
	    	$(this).attr("src", $(this).attr("src").replace(".png", "!.png"));
	    }
	  },
	  function(){
	    var src = $(this).attr("src");
	    if (src.indexOf("0.png") == -1) {
	    	$(this).attr("src", $(this).attr("src").replace("!.png", ".png"));
	    }
	  }
	);
	$("#navigation img").hover(
	  function(){
	    var src = $(this).attr("src");
	    if (src.indexOf("0.png") == -1) { 
	    	$(this).attr("src", $(this).attr("src").replace(".png", "!.png"));
	    }
	  },
	  function(){
	    var src = $(this).attr("src");
	    if (src.indexOf("0.png") == -1) {
	    	$(this).attr("src", $(this).attr("src").replace("!.png", ".png"));
	    }
	  }
	);

	$(document).keyup(
		function(event){
			switch(event.keyCode){
				case 39: nextImage(); break;
				case 37: prevImage(); break;
				case 38: showIndex(); break;
				case 40: break;
				case 73: // i
					if($("#info").css("display") == 'none') showInfo();
					break;
				case 27: // escape
					if($("#info").css("display") != 'none') hideInfo();
					break;
				case 32: // space
					if($("#info").css("display") != 'none'){
						hideInfo();
					}
					else{
						nextImage();
					}
					event.stopImmediatePropagation();
					break;
				//default: alert(event.keyCode);
			}
		}
	);
	$("#infobutton").click(showInfo);
});

