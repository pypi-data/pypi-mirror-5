$(function() {

  function display_error(msg) {
    var error_div = document.getElementById('error-message');

    if(msg == undefined || msg == '') {
      error_div.innerHTML = '';
      error_div.style.display = 'none';
    } else {
      error_div.innerHTML = msg;
      error_div.style.display = 'block';
    }
  }

    var MyfileView = Backbone.View.extend({
        el: $('#myfile-view'),
        template: _.template($('#myfile-template').html()),
        events: {
            "change #myfile": "event_select",
            "drop #myfile-drop": "event_drop",
            "dragover #myfile-drop": "event_dragover",
            "click #myfile-drop": "event_clickdrop",
            "click #myfile-trash": "event_trash",
        },
        initialize: function() {
            this.render();
        },
        render: function() {
            this.$el.html(this.template({myfile: this.myfile}));
            return this;
        },
        fileSelect: function(files) {
            this.myfile = files[0];
            this.render();
        },
        event_select: function(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            this.fileSelect(evt.target.files);
        },
        event_drop: function(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            this.fileSelect(evt.originalEvent.dataTransfer.files);
        },
        event_dragover: function(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            evt.originalEvent.dataTransfer.dropEffect = 'copy';
        },
        event_clickdrop: function(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            $('#myfile').trigger('click');
        },
        event_trash: function(evt) {
            this.myfile = null;
            this.render();
        },
    });

    var FlaskupView = Backbone.View.extend({
        el: $('#flaskup-app'),
        events: {
            'click #btn-submit': 'upload',
        },
        initialize: function() {
            this.myfileview = new MyfileView();
        },
        upload: function(evt) {
            var xhr = new XMLHttpRequest();
            var form = document.getElementById('form-upload');
            var fd = new FormData(form);

            fd.append('myfile', this.myfileview.myfile);

            // event listners
            var view = this;
            xhr.upload.onprogress = function(evt) {
                // display modal
                $('#upload_modal').modal();

                if (evt.lengthComputable) {
                    // update the view
                    view.update_progress_dialog(evt);
                }
            };

            xhr.onload = function(evt) {
                // upload is done (100%)
                view.update_progress_dialog(evt);

                // parse response from the server
                var response;
                try {
                    response = JSON.parse(evt.target.responseText);
                } catch(e) {
                    response = {
                        message: 'There was an error attempting to upload the file.',
                    };
                }

                // something goes wrong, display the error message
                if(evt.target.status != 200) {
                    $('#upload_modal').modal('hide');
                    display_error(response.message);
                    return;
                }

                // follow the link returned by the server
                document.location.href = response.url;
            };

            /*
            xhr.upload.addEventListener("loadstart", this.upload_loadstart, false);
            xhr.upload.addEventListener("progress", this.upload_progress, false);
            xhr.addEventListener("load", this.upload_complete, false);
            xhr.addEventListener("error", this.upload_failed, false);
            xhr.addEventListener("abort", this.upload_canceled, false);
            */


            // POST form
            xhr.open("POST", "/upload");
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.send(fd);

            // store our xhr, so we can abort it
            this.xhr = xhr;

            return false;
        },
        upload_loadstart: function(evt) {
            // upload begins, initialize some variables
            this.upload_last_datetime = new Date();
            this.upload_last_size = 0;
            this.upload_speed = 0;
        },
upload_failed: function(evt) {
                   display_error('There was an error attempting to upload the file.');
               },
upload_canceled: function(evt) {
                     // reset progress bar
                     var bar = document.getElementById('bar');
                     bar.setAttribute('style', 'width: 0%;');
                     // hide modal
                     $('#upload_modal').modal('hide');
                 },
        update_progress_dialog: function(evt) {
            // compute the upload speed, only once a second
            var current_datetime = new Date();
            if(current_datetime - this.upload_last_datetime > 1000) {
                // compute differences between current and last values
                var diff_datetime = (current_datetime - this.upload_last_datetime) / 1000;
                var diff_size = evt.loaded - this.upload_last_size;
                upload_speed = diff_size / diff_datetime;
                // store current values
                this.upload_last_datetime = current_datetime;
                this.upload_last_size = evt.loaded;
            }

            // update progress bar (width)
            var percent = evt.loaded * 100 / evt.total;
            var bar = document.getElementById('bar');
            bar.setAttribute('style', 'width: ' + percent + '%;');

            // display informations about the current upload
            if(percent == 100) {
                upload_percent_text.innerHTML = '100%';
                upload_info_text.innerHTML = readable_size(evt.loaded) + ' / '
                    + readable_size(evt.total);
            } else {
                upload_percent_text.innerHTML = percent.toFixed(1) + '%';
                upload_info_text.innerHTML = readable_size(evt.loaded) + ' / '
                    + readable_size(evt.total) + ' @ ' + readable_size(upload_speed) + '/s';
            }
        },
    });

    var App = new FlaskupView;

});
