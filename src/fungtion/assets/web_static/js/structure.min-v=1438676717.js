var lastScript="",currentWin=window,main_pv=null;
function detach(a,b,c){if(currentWin==window){if("pv"==a)currentWin=window.open(b,"_blank","resizable=1,status=1,toolbar=1,location=1,height=700,width=700"),main_pv=pv_viewer;else{currentWin=window.open("","_blank","resizable=1,status=1,toolbar=1,location=1,height=700,width=700");var e='<div id="popup_structure" style="background-color:#fff;width:100%;height:100%">'+$("#biounit_div_astex").clone().html()+"</div><script>function showSnapshot(str){ window.open(str);}\x3c/script>";setTimeout(function(){currentWin.document.write(e);
currentWin.document.close();lastScript="";$(currentWin).on("beforeunload",function(){attachAstex()});setTimeout(function(){$(".alignTbl").first().alignment("viewerInitialised")},100)},250)}$("#biounit_div_astex").html('<div align="center" style="padding-top:100px;"><input type="button" onclick="currentWin.close();"style="text-align:center;font-style:italic;font-size:1.2em;" value="Click to reattach"></div>').css("background-color","#BBB");$("#left-panel").removeClass("col-sm-8");$("#right-panel").hide();
$(".alignTbl").alignment("resizeToParent")}}function attachPV(){pv_viewer=main_pv;currentWin=window;$("#left-panel").addClass("col-sm-8");$("#right-panel").show();$("#pv").height($("#viewerWrapper").width());"undefined"!=typeof superposeTemplates&&superposeTemplates(!0);$(".alignTbl").alignment("resizeToParent")}
function attachAstex(){$("#biounit_div_astex").html($("#popup_structure",currentWin.document).clone().html());currentWin=window;lastScript="";$("#left-panel").addClass("col-sm-8");$("#right-panel").show();$(".alignTbl").alignment("resizeToParent");"undefined"!=typeof superposeTemplates&&superposeTemplates(!0);"undefined"!=typeof attachModel&&attachModel();setTimeout(function(){$(".alignTbl").first().alignment("viewerInitialised")},100)}
function astexExec(a,b){if(b||lastScript!=a){lastScript=a;if(currentWin.document.getElementById("astex")){try{currentWin.document.getElementById("astex").execute(a)}catch(c){return!1}return!0}return!1}}function chainStringAstex(a,b){var c=b?" and molecule "+b:"";if(!a)return""+c;if(1==a.length)return" chain '"+a+"'"+c;for(var e=" (",f=0;f<a.length;f++)0<f&&(e+=" or "),e+=" chain '"+a[f]+"'"+c;return e+")"}
function centerOnLigand(a,b){0<$("#pv:visible",currentWin.document).length&&centerOnLigandPV(a,b);0<$("#astex:visible",currentWin.document).length&&centerOnLigandAstex(a)}function highlightLigand(a,b,c){$(".hoverResidue").removeClass("hoverResidue");0<$("#pv:visible",currentWin.document).length?highlightLigandPV(a,b,c):highlightLigandAstex(a,b,c)}
function selectResidues(a,b,c){0<$("#pv:visible",currentWin.document).length&&selectResiduesPV(a,b,c);0<$("#astex:visible",currentWin.document).length&&selectResiduesAstex(a,b,c)}var lastresRange=null,currentSelection=null;function highlightResRange(a,b,c,e,f){0<$("#pv:visible",currentWin.document).length&&highlightResRangePV(a,b,c,e,f);0<$("#astex:visible",currentWin.document).length&&highlightResRangeAstex(a,b,c,e,f)}
function clearHighlightResRange(){var a=null!=currentSelection?" color red "+currentSelection+";":"";astexExec(a+" display lines off all; label clear all; object ribbon transparency 255; object remove hover;");lastresRange=a}function centerResRange(a,b,c,e){0<$("#pv:visible",currentWin.document).length&&centerResRangePV(a,b,c,e);0<$("#astex:visible",currentWin.document).length&&centerResRangeAstex(a,b,c,e)}
function selectResiduesAstex(a,b,c){b?(a=chainStringAstex(a),astexExec("display lines off all; label clear all; display sticks off all;display sticks on residue "+b+(0<a.length?" and"+a:"")+(c?" and molecule "+c:"")+";display lines on residue "+b+(0<a.length?" and"+a:"")+(c?" and molecule "+c:"")+";object ribbon transparency 240;label '%R %r%c' atom CA and residue "+b+(0<a.length?" and"+a:"")+";")):astexExec("center "+chainStringAstex(a)+"; display lines off aminoacid or chain '-'; clip 100 -100;")}
function highlightResRangeAstex(a,b,c,e,f){if(b||c){"model-template"==a&&(a="A");if(e){currentSelection=chainStringAstex(a,f)+" and residue ";for(var g=b;g<=c;g++)currentSelection+=g+" "}var h=null!=currentSelection?" select "+currentSelection+";":"";if(!e&&a){h+="append "+chainStringAstex(a,f)+" and residue ";for(g=b;g<=c;g++)h+=g+" ";h+=";"}h=h.replace("schematic -name ribbon all;","");null!=lastresRange&&lastresRange==h||astexExec(h+"color red current; schematic -name hover current; object ribbon transparency 240; select none;");
lastresRange=h}else!a||1>a.length?astexExec("object hover display off;object ribbon transparency 255;"):(a=chainStringAstex(a),astexExec("color '(150,0,0)' "+a+";schematic -name hover "+a+";object hover display on; object ribbon transparency 240;"))}function centerOnLigandAstex(a){for(var b="",c=0;c<a.length;c++)b+="append chain '_' and residue "+a[c]+";";astexExec(b+"select sphere 20 around current; center current; select none; clip 100 -100;")}
function highlightLigandAstex(a,b,c){var e="label clear all; select chain '_';color white current;cylinder_radius .8 current;ball_radius .8 current;select aminoacid;exclude chain '_';display lines off current; display sticks off current;select none;";if(a){for(var f=0;f<a.length;f++)e+="append chain '_' and residue "+a[f]+(c?" and molecule model_"+c:"")+";";e+=" cylinder_radius .4 current; ball_radius 1.6 current;"}if(b&&0<b.length){var g=null!=$.cookie("label_contacts")&&"true"==$.cookie("label_contacts");
a=[];for(f=0;f<b.length;f++)b[f]&&"_"!=b[f].charAt(0)&&(res=b[f].substring(1),chain=b[f].charAt(0),e+="append residue "+res+" and chain '"+chain+"'"+(c?" and molecule model_"+c:"")+";",g&&(e+="label '%R %r%c' atom CA and residue "+res+" and chain '"+chain+(c?" and molecule model_"+c:"")+";"),a[chain]||(a[chain]=[]),a[chain].push(res));for(var h in a)for(b=c?$("#alignTbl"+c+" tr[keyseqchain="+h+"]").find("span").toArray():$(".alignTbl tr[chain="+h+"]").find("span").toArray(),f=0;f<a[h].length;f++)for(g=
0;g<b.length;g++)if(b[g].getAttribute("s")==a[h][f]){b[g].className="hoverResidue";break}e+="display sticks on current;display lines on current;"}astexExec(e+"color_by_atom; select none;")}function centerResRangeAstex(a,b,c,e){"model-template"==a&&(a="A");for(a="center sphere 20 around "+chainStringAstex(a,e)+" and residue";b<=c;b++)a+=" "+b;astexExec(a+"; clip 100 -100;")}function setColorForAtom(a,b,c){var e=a.structure().createEmptyView();e.addAtom(b);a.colorBy(pv.color.uniform(c),e)}
var prevPicked=null;
document.getElementById("pv").addEventListener("mousemove",function(a){var b=pv_viewer.boundingClientRect();a=pv_viewer.pick({x:a.clientX-b.left,y:a.clientY-b.top});if(null===prevPicked||null===a||a.target()!==prevPicked.atom){null!==prevPicked&&setColorForAtom(prevPicked.node,prevPicked.atom,prevPicked.color);if(null!==a){var b=a.target(),c=b.qualifiedName(),e=[0,0,0,0];a.node().getColorForAtom(b,e);prevPicked={atom:b,color:e,node:a.node()};setColorForAtom(a.node(),b,"red");"_"===c.charAt(0)&&(c=
b.residue().name()+" "+b.residue().num());$("body").trigger("highlightResidue",[a.object().geom.name(),c]);document.getElementById("pv_status").innerHTML=c}else document.getElementById("pv_status").innerHTML="",prevPicked=null;pv_viewer.requestRedraw()}});
function selectResiduesPV(a,b,c){pv_viewer.rm((c?c+"_":"")+"res");var e=c?pv_viewer.get(c):pv_viewer.get("template");null!=e&&(e=e.structure(),b?(a=e.select({chain:a}).residueSelect(function(a){return a.num()==b}),pv_viewer.ballsAndSticks((c?c+"_":"")+"res",a)):(pv_viewer.fitTo(e.select({cnames:a.split("")})),pv_viewer.requestRedraw()))}
function centerResRangePV(a,b,c,e){e=e?pv_viewer.get(e):pv_viewer.get("template");null!=e&&(e=e.structure().residueSelect(function(e){return e.chain().name()==a&&e.num()>=b&&e.num()<=c}),pv_viewer.fitTo(e),pv_viewer.requestRedraw())}function highlightResRangePV(a,b,c,e,f){}
function centerOnLigandPV(a,b){var c=pv_viewer.get((b?"model_"+b:"template")+".ligands");null!=c&&(c=c.structure(),c=c.residueSelect(function(b){for(var c=0;c<a.length;c++)if(b.num()==a[c])return!0}),pv_viewer.fitTo(c),pv_viewer.requestRedraw())}
function highlightLigandPV(a,b,c){pv_viewer.hide("*ligands");pv_viewer.rm("*ligandContactsHL");var e=c?"model_"+c:"template",f=pv_viewer.get(e+".ligands");if(null!=f){f=f.structure();pv_viewer.show(e+".ligands_lines");a&&(f=f.residueSelect(function(b){for(var c=0;c<a.length;c++)if(b.num()==a[c])return!0}),pv_viewer.ballsAndSticks(e+"ligands",f));var g={};if(b&&0<b.length){for(f=0;f<b.length;f++)b[f]&&"_"!=b[f].charAt(0)&&(res=b[f].substring(1),chain=b[f].charAt(0),g[chain]||(g[chain]=[]),g[chain].push(res));
b=pv_viewer.get(e).structure().residueSelect(function(a){var b=a.chain().name();a=a.num();if(b=g[b])for(var c=0;c<b.length;c++)if(a==b[c])return!0});pv_viewer.lines(e+"ligandContactsHL",b);for(var h in g)for(b=c?$("#alignTbl"+c+" tr[keyseqchain="+h+"]").find("span").toArray():$(".alignTbl tr[chain="+h+"]").find("span").toArray(),f=0;f<g[h].length;f++)for(e=0;e<b.length;e++)if(b[e].getAttribute("s")==g[h][f]){b[e].className="hoverResidue";break}}pv_viewer.requestRedraw()}}
function takeSnapshotPV(){var a=window.open("","_blank","resizable=1,status=0,toolbar=0,location=0,height="+$("#pv").height()+",width="+$("#pv").width());d=pv_viewer.imageData();a.document.write('<html><body><img src="'+d+'"></body></html>');a.document.close()};

//////////////////////////////////////////////
function spinAstex(spinOn)
{
$.cookie('astex_spin',spinOn,{ expires: 365, path: '/' });
 if(!astexExec('astex.Spin -active '+spinOn+';'))
		alert('You need to select the 3D option below the structure image,'
				+'\nand / or enable Java in your browser for this feature to work') ;
}
function takeSnapshot()
{
	if(typeof astexExec=='undefined' || !astexExec('takeSnapshot',true))
	alert('You need to select the 3D option below the structure image,'
			+'\nand / or enable Java in your browser for this feature to work') ;
}
function showSnapshot(str)
{
	window.open(str);
}
function resetStructure()
{
	if($('#astex:visible',currentWin.document).length>0)
	{
		clearHighlightResRange();
		astexExec("center all;object hover display off; object ribbon transparency 255;");
		$('.alignTbl').alignment('astexReady');
	}
	if($('#pv:visible',currentWin.document).length>0)
	{
		pv_viewer.show('*ligands');
		pv_viewer.hide('*ligands_lines');
		pv_viewer.rm('*res');
		pv_viewer.autoZoom();
		pv_viewer.requestRedraw();
	}

	
}

