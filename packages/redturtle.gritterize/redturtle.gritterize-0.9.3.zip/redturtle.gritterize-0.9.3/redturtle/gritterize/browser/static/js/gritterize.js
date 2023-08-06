/*
 *We want to manage portal messages with gritter!
 *
 * from a dl make a gritter element like this
 *
 * {
 *   title: "Info",
 *   text: "An info...",
 *   class_name: "portalMessage info",
 * }
 *
 */
(function(igritter, jq, document) {
  "use strict";
  igritter = igritter || {};
  igritter.query = 'dl.portalMessage:visible';
  igritter.config = igritter.config || {time: {}};
  /* Customize this function to get a title */
  igritter.get_title = function(message) {
    return message.find('dt').html();
  };
  /* Customize this function to get a text */
  igritter.get_text = function(message) {
    return message.find('dd').html();
  };

  /* Customize this function to get a class */
  igritter.get_class = function(message) {
    return message.attr('class');
  };

  /* This will add a gritter based on a config object */
  igritter.add_gritter = function(mygritter) {
    // we add a gritter only if we have enough data
    if (!(mygritter.title && mygritter.text)) {
      return -1;
    }

    // The time can be specified also
    mygritter.time = igritter.config.time[mygritter.class_name];
    if (mygritter.time) {
      mygritter.sticky = false;
    } else {
      mygritter.sticky = true;
    }

    // optionally remove the target object
    if (mygritter.remove && mygritter.target) {
      mygritter.target.remove();
    }
    return jq.gritter.add(mygritter);
  };

  igritter.message2gritter = function (message_id, message, mygritter) {
    mygritter = mygritter || {};
    message = jq(message);
    mygritter = {title: igritter.get_title(message),
                 text: igritter.get_text(message),
                 class_name: igritter.get_class(message),
                 target: message,
                 remove: true
                };
    return igritter.add_gritter(mygritter);
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
