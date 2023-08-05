// Sets a DOM node's HTML
//
// :param __target__: id of the node
// :param __text__: text contents or HTML

require(["dojo/dom", "dojo/domReady!"],
function(dom) {
  text = '__text__';
  try {dom.byId('__target__').innerHTML += text;}
  catch(err) {alert(err+": "+text)}
  }
);