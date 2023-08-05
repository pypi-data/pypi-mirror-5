// Returns javascript code to send a message.
// 
// :param __message__: Message to show at the browser.
//
// This is intended to be used in pyojo async calls, it waits for the DOM.

define(["dojo/domReady!"], 
function(){
  return {run: function(){
                 alert("__message__");
               }
      };
  }
);