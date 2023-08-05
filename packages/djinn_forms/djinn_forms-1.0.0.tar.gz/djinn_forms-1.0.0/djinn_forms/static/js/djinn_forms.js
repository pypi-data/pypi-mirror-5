/**
 * Djinn forms JS lib. Mainly helper functions for form widget handling.
 */

if (djinn == undefined) {
    var djinn = {};
}


djinn.forms = {};


/**
 * Set link data to widget input.
 */
djinn.forms.set_link = function(url, content_type, obj_id, title, extra_args) {

  var val = url + "::" + content_type + "::" + obj_id;
  val += "::" + (extra_args['target'] || "");

  $("#id_" + extra_args['tgt']).val(val);
  $("#" + extra_args['tgt'] + "_link").html(title || url);

  $("#MyModal").modal("hide");
};


/**
 * Initialize file uploader widget.
 */
djinn.forms.init_fileuploader = function(options) {

  var defaults = {
    url: '/fileupload',
    dataType: 'json',
    done: function (e, data) {
      
      var valuetgt = $($(e.target).data("valuefield"));
      var tgt = $(e.target);
      
      if (tgt.attr("multiple")) {
        $(tgt.data("target")).append(data.result.html);        
        valuetgt.val(valuetgt.val() + "," + data.result.attachment_ids.join(","));
      } else {
        $(tgt.data("target")).html(data.result.html);
        valuetgt.val(data.result.attachment_ids.join(","));
      }
      $(tgt.data("progress") + " .bar").css("width", "100%");

      if (tgt.data("callback")) {
        
        var callback = eval(tgt.data("callback"));
        callback.apply(null, tgt);
      }

      $(document).triggerHandler("djinn_forms_fileupload_done", [e.target, data.result]);
    },
    send: function(e, data) {
      $(document).triggerHandler("djinn_forms_fileupload_send", [e.target]);
    },
    progress: function (e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      $($(e.target).data("progress") + " .bar").css("width", progress + "%");
    }
  };
  
  if (options) {
    $.extend(defaults, options);
  }
  
  $("input[type='file']").each(function() {
      
      if ($(this).data("uploadurl")) {
        defaults['url'] = $(this).data("uploadurl");
      }
      defaults['dropZone'] = $(this).attr("id");

      defaults['formData'] = {
        "attachment_id": $(this).hasClass("field") ? $($(this).data("valuefield")).val() : "",
        "attachment_type": $(this).data("attachmenttype"),
        "edit_type": $(this).hasClass("field") ? "field": "attachment"
      }
      
      $(this).fileupload(defaults);
    });
};


djinn.forms.remove_attachment = function(elt, attachment_id) {

  var input = $(elt.parents(".fileupload").find("input[type='file']").eq(0).data("valuefield"));

  pg.remove_value(input, attachment_id, ",");

  $(document).triggerHandler("djinn_forms_fileupload_remove", elt);
};
