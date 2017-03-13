/***************************************************************************
** Helper
****************************************************************************/

/**
** Wert beschränken:
** @param v Wert
** @param min Untere Schranke
** @param max Obere Schranke
** @return Wert, nicht kleiner als min, nicht größer als max
*/
function limit(v, min, max){
    return v < min ? min : (v > max ? max : v);
}

/***************************************************************************
** DOM Helper
****************************************************************************/

/**
** Enthaltensein testen:
** @param container Element, in dem enthalten sein soll
** @param containee Element, das enhalten sein soll
** @return wahr, wenn containee in container enthalten ist
*/
function containsElement(container, containee){
    if(container.contains){
        return container.contains(containee);
    }
    else if(containee){
        if(typeof containee.parentNode != "undefined"){
            while(containee && containee != container){
                containee=containee.parentNode;
            }
            return !!containee;
        }
    }
    return false;
}

/**
** Breite eines Elements holen (falls möglich):
** @param element Element
** @return Breite
*/
function getElementWidth(element){
    var w = 0;
    if(element.style){
        w = parseInt(element.style.width);
    }
    if(!w){
        w = element.width;
    }
    return w;
}

/**
** Höhe eines Elements holen (falls möglich):
** @param element Element
** @return Höhe
*/
function getElementHeight(element){
    var h = 0;
    if(element.style){
        h = parseInt(element.style.height);
    }
    if(!h){
        h = element.height;
    }
    return h;
}

/***************************************************************************
** Fader
** Prototyp um ein Element ein- und auszublenden.
****************************************************************************/

/**
** Fader einrichten:
** @param element Element, welches überblendet werden soll
** @param opacity Anfangsüberblendstärke
*/
function Fader(element, opacity){
    this.element = element;

    // Funktionen hinzufügen
    this.set = Fader_set;
    this.start = Fader_start;
    this.stop = Fader_stop;
    this.animate = Fader_animate;

    // Überblendstärke einstellen
    this.set(opacity);

    this.timer = null;
}
/**
** Überblendstärke einstellen:
** @param to Überblendstärke
*/
function Fader_set(opacity){
    this.opacity = opacity;
    this.element.style.opacity = opacity;
    this.element.style.filter = "alpha(opacity="+String(opacity * 100)+")";
}
/**
** Überblendung starten:
** @param duration Überblenddauer
** @param to Endüberblendstärke
*/
function Fader_start(duration, to){
    var me = this;
    if(this.to != to){
        this.duration = duration;
        this.starttime = (new Date).getTime() - 13;
        // Timer zurücksetzen
        if(this.timer != null){
            clearInterval(this.timer);
            this.timer = null;
        }
        this.from = this.opacity;
        this.to = to;
        // Timer starten
        this.timer = setInterval(function(){me.animate()}, 13);
        this.animate();
    }
}
/**
** Überblendung stoppen:
*/
function Fader_stop(to){
    // Timer zurücksetzen
    if(this.timer != null){
        clearInterval(this.timer);
        this.timer = null;
    }
    if(to != null){
        this.to = to;
    }
    // Endüberblendstärke einstellen
    this.set(this.to);
}
/**
** Überblendung durchführen:
*/
function Fader_animate(){
    var t;
    var time = (new Date).getTime();
    t = limit(time - this.starttime, 0, this.duration);
    
    var opacity;
    if(t < this.duration){
        opacity = this.from + (this.to - this.from) * (0.5 - (0.5 * Math.cos(Math.PI * t / this.duration)));
    }
    else{
        clearInterval(this.timer);
        this.timer = null;
        opacity = this.to;
    }
    this.set(opacity);
}

/***************************************************************************
** Info
** Prototyp um ein Info ein- und auszublenden.
****************************************************************************/

Info_opacity = 1;

Info_fader_duration = 300;

function Info(element, container){
    var me = this;

    // methods
    this.setHead = Info_sethead;
    this.setText = Info_settext;
    
    this.display = Info_display;
    this.show = Info_show;
    this.hide = Info_hide;
    this.expand = Info_expand;
    this.shrink = Info_shrink;
    
    this.isHidden = Info_ishidden;
    this.isExpanded = Info_isexpanded;
    this.isShrinked = Info_isshrinked;
            
    this.element = element;
    this.container = container;

    this.visible = 0;
    this.expanded = 0;

    // setup container
    container.style.width = getElementWidth(element);
    container.style.height = getElementHeight(element);
    container.onmouseover = function(e){
        if(me.isHidden()) me.show();
    };
    container.onmouseout = function(e){
        e = e||window.event;
        if(!containsElement(me.container, e.relatedTarget||e.toElement)){
            me.shrink();
            me.hide();
        }
    };
    container.onmousemove = function(e){
        if(me.isHidden()) me.show();
    };

    // create info
    this.icon = Info_buildicon();
    this.head = Info_buildhead(this.icon);
    this.text = Info_buildtext();
    this.info = Info_buildinfo(this.head, this.text);
    
    this.icon.onclick = function(e){
        if(me.isExpanded()) me.shrink();
        else me.expand();
    };
    this.icon.onmouseover = function(e){
        if(me.isShrinked()) me.expand();
    };
    
    // create fader
    this.fader = new Fader(this.info, 0);
    
    // setup info
    this.info.style.left = 10;
    this.info.style.right = 10;
    this.info.onmouseover = function(e){
        me.fader.start(Info_fader_duration, 1.0);
    };
    
    // add info to container
    container.appendChild(this.info);
}
function Info_buildbutton(name, href){
    var element = document.createElement("a");
    element.setAttribute("href", href);
    var image = document.createElement("img");
    image.setAttribute("src", "../images/" + name + ".png");
    image.className = "Info_button";
    element.appendChild(image);
    return element;
}
function Info_buildicon(){
    var element = document.createElement("img");
    element.setAttribute("src", "../images/icon_i.png");
    element.setAttribute("title", "Informationen der Aufnahme anzeigen");
    element.className = "Info_headicon";
    return element;
}
function Info_buildhead(icon){
    var element = document.createElement("div");
    element.className = "Info_head";
    element.appendChild(icon);
    element.appendChild(document.createElement("span"));
    return element;
}
function Info_buildtext(){
    var element = document.createElement("div");
    element.className = "Info_text";
    return element;
}
function Info_buildinfo(head, text){
    var info = document.createElement("div");
    info.className = "Info";
    info.appendChild(head);
    info.appendChild(text);
    return info;
}
function Info_sethead(head){
    this.head.lastChild.innerHTML = head;
}
function Info_settext(text){
    this.text.innerHTML = text;
}
function Info_setup(href){
    this.button_up.setAttribute("href", href);
}
function Info_expand(){
    this.info.style.background = "white";
    this.info.style.border = "solid 1px black";
    this.text.style.display = "block";
    this.expanded = 1;
}
function Info_shrink(){
    this.info.style.background = "transparent";
    this.info.style.border = "solid 1px transparent";
    this.text.style.display = "none";
    this.expanded = 0;
}
function Info_isexpanded(){
    return this.expanded == 1;
}
function Info_isshrinked(){
    return this.expanded == 0;
}
function Info_display(opacity){
    this.fader.set(opacity);
    this.info.style.visibility = "visible";
    this.info.style.display = "block";
    this.visible = 1;
}
function Info_show(){
    this.fader.set(Info_opacity);
    this.info.style.visibility = "visible";
    this.visible = 1;
}
function Info_hide(){
    this.fader.set(0);
    this.info.style.visibility = "hidden";
    this.visible = 0;
}
function Info_ishidden(){
    return this.visible == 0;
}

/**
** Info zu einem Bild hinzufügen:
** @param imageid Id des Bildes, welches mit einem Info versehen werden soll.
** @param headid Id des Absatzes, welcher den Kopf für das Info enthält.
** @param textid Id des Absatzes, welcher den Text für das Info enthält.
*/
function addInfo(imageid, headid, textid){
    var image = document.getElementById(imageid);
    var text = document.getElementById(textid);
    var head = document.getElementById(headid);

    // DIV um das Bild erzeugen:
    //   DIV erzeugen,
    //   Bild durch DIV ersetzen,
    //   Bild in DIV einfügen
    var imagecontainer = document.createElement("div");
    imagecontainer.className = "Info_container";
    image.parentNode.replaceChild(imagecontainer, image);
    imagecontainer.appendChild(image);
    imagecontainer.style.position = "relative";
    
    var i = new Info(image, imagecontainer);

    if(head){
        i.setHead(head.innerHTML);
    }
    if(text){
        i.setText(text.innerHTML);
    }

    i.display(0);
    i.hide();
}
