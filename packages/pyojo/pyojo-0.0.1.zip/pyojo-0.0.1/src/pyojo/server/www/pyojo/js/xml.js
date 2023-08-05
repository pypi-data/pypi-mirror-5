/**
 * 
 * pyojo ajax functions
 * 
 * @author txema
 * @date 2012/10/01
 * @link http://www.pyojo.com/  
 * 
 */

run = function(code){
  try {eval(code)}
  catch(err){log_err(err)}
  } 

function pyojo(script) {
  require(["pyojo/"+script, "dojo/domReady!"],
    function(js) {
      js.run();
    }
  );
}

check = function(){
  console.log("--CHECK--")
  document.cookie = "state_check="+app_hash+"; path=/";
  } 

define(["dojo/request", "dojo/dom", "dojo/domReady!"], 
  function(request, dom){
    return {

      get:  function(url, query){
              request.get(url, {query: query, handleAs: "xml", headers: {"Accept": "text/xml"}}
              ).then(function(data, ioArgs) {
                       response = data.documentElement
                       nodes = response.childNodes;
                       for(i=0;i<nodes.length;i++){
                         tag = nodes[i].tagName;
                         text = nodes[i].textContent
                         if (tag == "javascript") {eval(text);}
                         if (tag == "content") {
                           target = nodes[i].getAttribute("target")
                           dom.byId(target).innerHTML = text;
                           }
                         }
                       },
            function(err, ioArgs) 
              {dom.byId("info").innerHTML = "POST ERROR: "+err;});  
            },

      post: function(url, query){
      		log('request: POST '+url);
      		  check();
              request.post(url, {query: query, 
            	  				 handleAs: "xml", 
            	  				 headers: {"Accept": "text/xml"}}
              ).then(function(data, ioArgs) {
            	  	   log('received: POST '+url);
                       response = data.documentElement;
                       nodes = response.childNodes;
                       for(i=0;i<nodes.length;i++){
                         tag = nodes[i].tagName;
                         text = nodes[i].textContent
                         if (tag == "pyojo") 
                           {check();
                            script = nodes[i].getAttribute("script");
                            call = nodes[i].getAttribute("call");
                            if (call==null) {require(["pyojo/"+script]);}
                            else {try {require(["pyojo/"+script], //, "dojo/domReady!"
                                  	   function(js) {js[call]();});}
                                  catch(err) {if (err.description){log("Error: " + err.description)}
    										  else{log("Error: " + err)}}
                                  //alert ('CALL IS '+call);
                                 }
                           }
                         if (tag == "javascript") {eval(text);} //{run(text);}
                         if (tag == "content") {
                           target = nodes[i].getAttribute("target")
                           try {dom.byId(target).innerHTML = text;}
                           catch(err) {alert(err+" "+text)}
                           }
                         if (tag == "append") {
                           target = nodes[i].getAttribute("target")
                           try {dom.byId(target).innerHTML+= text;}
                           catch(err) {alert(err+" "+text)}
                           }
                         }
                       },
            function(err, ioArgs) 
              {dom.byId("info").innerHTML = "POST ERROR: "+err;});  
            },

      put:  function(url, query){
              request.put(url, {query: query, handleAs: "xml", headers: {"Accept": "text/xml"}}
              ).then(function(data, ioArgs) {
                       response = data.documentElement
                       nodes = response.childNodes;
                       for(i=0;i<nodes.length;i++){
                         tag = nodes[i].tagName;
                         text = nodes[i].textContent
                         if (tag == "javascript") {eval(text);}
                         if (tag == "content") {
                           target = nodes[i].getAttribute("target")
                           dom.byId(target).innerHTML = text;
                           }
                         }
                       },
            function(err, ioArgs) 
              {dom.byId("info").innerHTML = "POST ERROR: "+err;});  
            },

      del:  function(url, query){
              request.del(url, {query: query, handleAs: "xml", headers: {"Accept": "text/xml"}}
              ).then(function(data, ioArgs) {
                       response = data.documentElement
                       nodes = response.childNodes;
                       for(i=0;i<nodes.length;i++){
                         tag = nodes[i].tagName;
                         text = nodes[i].textContent
                         if (tag == "javascript") {eval(text);}
                         if (tag == "content") {
                           target = nodes[i].getAttribute("target")
                           dom.byId(target).innerHTML = text;
                           }
                         }
                       },
            function(err, ioArgs) 
              {dom.byId("info").innerHTML = "POST ERROR: "+err;});  
            }

    };
});