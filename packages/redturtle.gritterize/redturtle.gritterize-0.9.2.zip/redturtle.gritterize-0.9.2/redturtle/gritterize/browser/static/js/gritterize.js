/*
We want to manage portal messages with gritter!
*/
(function(igritter, jq, document) {
  "use strict";
  igritter = igritter || {};
  igritter.query = 'dl.portalMessage:visible';
  igritter.config = igritter.config || {time: {}};
  /* 
   * from a dl make a gritter element like this
   * 
   * {
   *   title: "Info",
   *   text: "An info...",
   *   class_name: "portalMessage info",
   * }
   *
   */
  igritter.message2gritter = function () {
    var message, mygritter;
    message = jq(this);
    mygritter = {title: message.find('dt').html(),
                 text: message.find('dd').html(),
                 class_name: message.attr('class')
                };
    if (mygritter.title && mygritter.text) {
      mygritter.time = igritter.config.time[mygritter.class_name];
      if (mygritter.time) {
        mygritter.sticky = false;
      } else {
        mygritter.sticky = true;
      }
      message.remove();
      return jq.gritter.add(mygritter);
    } 
    return -1;
  };

  igritter.get_messages = function () {
    return jq(igritter.query).each(igritter.message2gritter);
  };

  igritter.init = function() {
    var messages = igritter.get_messages();
    return messages;
  };

  jq(document).ready(igritter.init);
}(document.igritter, jQuery, document));
