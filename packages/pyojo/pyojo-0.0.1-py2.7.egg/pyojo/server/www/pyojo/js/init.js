/**
 * 
 * pyojo initialization
 * 
 * @author txema
 * @date 2012/10/01
 * @link http://www.pyojo.com/  
 * 
 */

function status(text) {
require(["dojo/dom","dojo/domReady!"],
    function(dom) {
      try {dom.byId('status').innerHTML= text;}
      catch(err) {console.log('pyojo: '+text);}
      try {log("Status: "+ text);}
      catch(err) {}
      
    }
);}

function log(text) {
require(["dojo/dom","dojo/domReady!"],
    function(dom) {
      try {dom.byId('log').innerHTML+= text+'\n';}
      catch(err) {console.log('pyojo.log: '+text);}
    }
);}


function log_err(err) {
	if (err.description){alert("JS Error: " + err.description)}
    else{alert("JS Error: " + err)}
}

function log_warn(err) {
	if (err.description){log("JS Warn: " + err.description)}
    else{log("JS Warning: " + err)}
}


function vx() {
  var x = 0;
  if( typeof( window.innerWidth ) == 'number' ) {x = window.innerWidth;}
  else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight )) 
    {x = document.documentElement.clientWidth;} 
  else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) 
    {x = document.body.clientWidth;}
  return x;
  }

function vy() {
  var y = 0;
  if( typeof( window.innerHeight) == 'number' ) {y = window.innerHeight;} 
  else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight )) 
    {y = document.documentElement.clientHeight;} 
  else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) 
    {y = document.body.clientHeight;}
  return y;
  }





