
let menuicon  = "36px";
let menuwidth = "320px";
let menuid = $('div.menu-board');
let iconid = $('div.icon');
let labelid = $('div.label')

function domos_open()       { menuid.css("width", menuwidth); iconid.css("width", menuicon); labelid.css("display", 'block');}
function domos_close()      { menuid.css("width", menuicon); labelid.css("display", 'none'); }
function domos_toggle()     { menuid.css('width')==menuicon ? domos_open(): domos_close(); }
function imagePreview(id)   { $('.imagepreview').attr('src', id.attr('src')); $('#imagemodal').css("display", "block"); }
function cssClassToggle(id, status, classOn, classOff) { status==true? id.removeClass(classOff).addClass(classOn): id.removeClass(classOn).addClass(classOff); }
function plotModal(url)     { $('#plot-modal iframe').attr('src', url); $('#plot-modal').show();}
function navtab(tab) { var i; var x = document.getElementsByClassName("navtab"); for (i = 0; i < x.length; i++) {x[i].style.display = "none";} document.getElementById(tab).style.display = "block";}

//domos_open();
domos_close();
