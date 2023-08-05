function basename(path) {
  if(path)
    return path.replace(/\\/g, '/').replace(/.*\//, '');
  else
    return path;
}

function dirname(path) {
  if(path)
    return path.replace(/\\/g, '/').replace(/\/[^\/]*$/, '');
  else
    return path;
}

var AugerOfflineExtension = ExtensionBase.extend({
  
  init : function() {
    this._super();
    
    this.name = 'augeroffline';
    
    this.factories = {
      full : new AugerOfflineFactory()
    };
  }
});

var AugerOfflineFactory = ExtensionFactoryFull
    .extend({
      
      init : function() {
        this._super();
        var _this = this;
        
        this.name = 'AugerOffline';
        this.constructor = AugerOfflineContent;
        
        var moduleConfigObj = {
          "Radio Modules" : "standardRdModuleConfig.xml",
          "SD Reconstruction Modules" : "standardSdRecModuleConfig.xml",
          "Hybrid Reconstruction Modules" : "standardHdRecModuleConfig.xml",
          "SdHAS Modules" : "standardSdHASRecModuleConfig.xml",
          "Fd Modules" : "standardFdRecModuleConfig.xml"
        };
        
        var detectorConfigObj = {
          "standardSdRealDetConfig" : "standardSdRealDetConfig.xml",
          "standardFdRealDetConfig" : "standardFdRealDetConfig.xml",
          "standardRdRealDetConfig" : "standardRdRealDetConfig.xml"
        };
        
        this.defaultConfig = {
          backgroundColor : {
            descr : 'The background color of this extension',
            select : [ 'white', 'red', 'blue' ],
            type : 'string',
            value : 'white'
          },
          moduleConfig : {
            descr : 'Filename of the module config xml files. The xml file needs to be in the folder \"$AUGEROFFLINEROOT/share/auger-offline/config/\". Only the modules specified in this xml files will be available in the Offline extension.',
            type : 'object',
            value : moduleConfigObj
          },
          detectorConfig : {
            descr : 'Filename of the detector config xml files. The xml file needs to be in the folder \"$AUGEROFFLINEROOT/share/auger-offline/config/\". Only the detector config specified in this xml files will be written to the bootstrap.xml file.',
            type : 'object',
            value : detectorConfigObj
          },
          
          userModules : {
            descr : 'User Modules',
            type : 'list',
            value : [ "userModuleA", "userModuleB" ]
          }
        };
        
        this.menuEntries = [ {
          label : 'new AugerOffline ...',
          icon : 'ui-icon-plus',
          callback : function() {
            _this._create();
          }
        } ];
        
        this.fileHandlers = {
          txt : {
            priority : 1,
            callback : function() {
              console.log('txt file Handler for', _this._id, arguments);
            }
          }
        };
        
        this.urlChannelHandlers = {
          augerofflineUrlChannel1 : {
            priority : 1,
            callback : function() {
              console
                  .log(
                      'url channel "augerofflineUrlChannel1" called, and passed to',
                      _this._id, arguments);
            }
          }
        };
      }
    });

var AugerOfflineContent = ExtensionContentFull
    .extend({
      
      addUserModule : function() {
        $.Topic("msg.prompt").publish({
          text : "name of user module",
          callback : function(name) {
          }
        });
      },
      
      setAllInfoLevelTo : function(listModuleSequence) {
        var _this = this;
        _logger.debug("creating dialog");
        $(
            "<div>set all info level to <input type=\"text\" id=\"infolevel\" size=5 /></div>")
            .dialog(
                {
                  autoOpen : true,
                  modal : true,
                  title : 'Infolevel',
                  buttons : [ {
                    text : 'submit',
                    icons : {
                      primary : 'ui-icon-play'
                    },
                    click : function() {
                      $(this).dialog('close');
                      _this.transmitModuleSequence($(listModuleSequence));
                      var infolevel = $(this).find("#infolevel").attr("value");
                      var request = $
                          .ajax({
                            url : Vispa.urlHandler
                                .dynamic("extensions/augeroffline/setAllInfoLevelTo"),
                            type : "POST",
                            data : {
                              workspace_id : Vispa.workspaceManager
                                  .getWorkspace().id,
                              infolevel : infolevel
                            }
                          });
                    }
                  } ]
                });
      },
      
      submitToJobSubmission : function() {
        var _this = this;
        
        _logger.debug("submitToJobDialog()");
        
        var submit_job_diablog;
        
        var module_list_template = $
            .ajax({
              url : Vispa.urlHandler
                  .dynamic("/extensions/augeroffline/static/html/submit_job_dialog.html"),
              type : 'GET',
              async : false,
              success : function(response) {
                submit_job_diablog = response;
                _logger.debug("ajax request successful");
              }
            });
        
        _logger.debug(submit_job_diablog);
        
        _logger.debug($("#set_input_files", submit_job_diablog));
        
        var submit_job_dialog = $(submit_job_diablog)
            .dialog(
                {
                  modal : false,
                  draggable : true,
                  width : 600,
                  title : "select input files",
                  resizable : true,
                  buttons : [ {
                    text : 'submit',
                    icons : {
                      primary : 'ui-icon-play'
                    },
                    click : function() {
                      $(this).dialog('close');
                      var AugerOfflinePath = "";
                      var request_auger_offline_path = $
                          .ajax({
                            url : Vispa.urlHandler
                                .dynamic("extensions/augeroffline/get_auger_offline_path"),
                            type : "POST",
                            data : {
                              workspace_id : Vispa.workspaceManager
                                  .getWorkspace().id
                            }
                          });
                      $.when(request_auger_offline_path)
                          .done(
                              function(data) {
                                AugerOfflinePath = data;
                                var files = $("#filename", ".submit-job-dialog")
                                    .attr("value");
                                var file_type = $("#filetype",
                                    ".submit-job-dialog").attr("value");
                                var output_folder = $("#output_folder",
                                    ".submit-job-dialog").attr("value");
                                var jobs = [ {
                                  command : "python " + AugerOfflinePath
                                      + "/executeOffline",
                                  arguments : [
                                      "-b " + AugerOfflinePath
                                          + "/bootstrap.xml",
                                      "--userAugerOffline " + AugerOfflinePath
                                          + "/userAugerOffline",
                                      "--fileType " + file_type,
                                      "--dataFiles " + files ],
                                  outputPath : output_folder
                                } ];
                                Vispa.extensionManager.getFactory(
                                    "jobsubmission", "jobmanagement")._create({
                                  jobs : jobs
                                });
                              });
                    }
                  } ]
                
                });
        
        $("#filename", submit_job_dialog).attr({
          value : _this.input_file_names
        })
        $("#output_folder", submit_job_dialog).attr({
          value : dirname(_this.bootstrap_path)
        });
        $("#filetype", submit_job_dialog).attr({
          value : basename(_this.input_file_type)
        });
        
        $("#set_input_files", ".submit-job-dialog").button().click(function() {
          window.setTimeout(function() {
            $.Topic("ext.file.selector").publish({
              path : "$HOME/Offline",
              multimode : true,
              callback : function(files) {
                console.log(files);
                $("#filename", ".submit-job-dialog").attr({
                  value : files
                });
              }
            });
          }, 0);
        });
        
        $("#set_output_folder", ".submit-job-dialog").button().click(
            function() {
              $.Topic("ext.file.selector").publish({
                path : "$HOME/Offline",
                multimode : false,
                callback : function(files) {
                  $("#output_folder", ".submit-job-dialog").attr({
                    value : files
                  });
                }
              });
            });
        
        //        
        // var content = $("<div />");
        //        
        // var table = $("<table />").appendTo(content);
        //        
        // var body = $("<tbody />").appendTo(table);
        //        
        // var tr = $("<tr />").appendTo(body);
        // $("<th />").text("input files").appendTo(tr);
        //        
        // var input_files = $("<input />").attr({
        // id : "filename",
        // type : "text",
        // value : "filename",
        // size: 50,
        // alt : "filename"
        // }).appendTo($("<th />")).appendTo(tr);
        //        
        // $("<button />").button({
        // label : "open input files"
        // }).click(function() {
        // window.setTimeout(function() {
        // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH", multimode:
        // true,
        // callback: function(files) {
        // console.log(files);
        // input_files.attr({value: files});
        // }});
        // },0);
        // }).appendTo($("<th />")).appendTo(tr);
        //        
        // // file type
        // tr = $("<tr />").appendTo(body);
        // $("<th />").text("file type").appendTo(tr);
        // var input_type = $("<input />").attr({
        // id : "filetype",
        // type : "text",
        // size: 50,
        // value : "Offline"
        // }).appendTo($("<th />")).appendTo(tr);
        //        
        // // output path
        // tr = $("<tr />").appendTo(body);
        // $("<th />").text("output folder").appendTo(tr);
        //        
        // var output_folder = $("<input />").attr({
        // id : "outputpath",
        // type : "text",
        // size: 50,
        // value : "output path"
        // }).appendTo($("<th />")).appendTo(tr);
        //        
        // $("<button />").button({
        // label : "set output folder"
        // }).click(function() {
        // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH", multimode:
        // false,
        // callback: function(files) {
        // output_folder.attr({value: files});
        // }});
        // }).appendTo($("<th />")).appendTo(tr);
        //        
        
      },
      
      saveXMLFiles : function(module_list) {
        var _this = this;
        var request = $
            .ajax({
              url : Vispa.urlHandler
                  .dynamic("/extensions/augeroffline/static/html/save_xml_files_dialog.html"),
              type : 'GET',
              async : false
            });
        
        $.when(request).done(function(dialog_template) {
            var module_options_dialog = $(dialog_template).dialog({
              modal : false,
              draggable : true,
              width : 600,
              title : "save XML files",
              resizable : true,
              buttons : [{
                    text : 'save',
                    icons : {
                      primary : 'ui-icon-disk'
                    },
                    click : function() {
                      _this.input_file_names = $("#filename_input",module_options_dialog).val();
                      _this.input_file_type = $("#filetype_input",module_options_dialog).val();
                      var output_folder = $("#output_folder",module_options_dialog).val();
                      var bootstrap_filename = basename($("#filename_bootstrap",module_options_dialog).val());
                      _this.bootstrap_path = $.Helpers.joinPath(output_folder,bootstrap_filename);
                      _this.moduleSequenceFilename = $("#filename_modulesequence",module_options_dialog).val();
                      _this.event_file_reader_filename = $("#filename_eventfilereader",module_options_dialog).val();
                      var path_relative = $("#path_relative",module_options_dialog).is(':checked');
                      var module_sequence = _this.generateModuleSequence(module_list);
                      var request = $.ajax({
                            url : Vispa.urlHandler.dynamic("extensions/augeroffline/saveXMLFiles"),
                            type : "POST",
                            data : JSON.stringify({
                                workspace_id : Vispa.workspaceManager.getWorkspace().id,
                                input_files : _this.input_file_names,
                                input_file_type : _this.input_file_type,
                                output_folder : output_folder,
                                filename_bootstrap : bootstrap_filename,
                                filename_modulesequence : _this.moduleSequenceFilename,
                                filename_eventfilereader : _this.event_file_reader_filename,
                                path_relative : path_relative,
                                module_sequence : module_sequence
                            }),
                            contentType : "application/json"
                          });
                      $.when(request).done(function(data) {
                        _logger.debug(data);
                        if(data.success) {
                          $("<div>"+data.data+"</div>").dialog({ 
                            title: "Info",
                            close: function( event, ui ) { $(module_options_dialog).dialog('destroy') },
                            buttons: {
                              Ok: function() {
                                $( this ).dialog( "close" );
                              }
                            }
                          });
//                          $(this).dialog('destroy');
                        } else {
                          $("<div>"+data.msg+"</div>").dialog({ 
                            title: "Info",
                            buttons: {
                              Ok: function() {
                                $( this ).dialog( "close" );
                              }
                            }
                          });
                        }
                      });
                      
                    }
                  }, {
                    text : 'cancel',
                    icon : {
                      primary : 'ui-icon-close'
                    },
                    click : function() {
                      $(this).dialog('close');
                    }
                  } ]
                });
                  
              _logger.debug(module_options_dialog);
              // set default value
              console.log(_this.bootstrap_path);
              _logger.debug("_this.bootstrap_path: "+_this.bootstrap_path);
              if(_this.bootstrap_path) {
                $("#output_folder", module_options_dialog).attr({value : dirname(_this.bootstrap_path)});
              }
              if(_this.moduleSequenceFilename) {
                $("#filename_bootstrap", module_options_dialog).val(basename(_this.bootstrap_path));
              }
              if(_this.moduleSequenceFilename) {
                $("#filename_modulesequence", module_options_dialog).val(basename(_this.moduleSequenceFilename));
              }
              $("#filename_input", module_options_dialog).attr({value : _this.input_file_names});
              $("#filetype_input", module_options_dialog).attr({value : _this.input_file_type});
              if(_this.event_file_reader_filename) {
                $("#filename_eventfilereader", module_options_dialog).attr({value : basename(_this.event_file_reader_filename)});
              }
              
              // / add functionality to buttons
              $("#set_output_folder", module_options_dialog).button({
                icons : {
                  primary : "ui-icon-folder-open"
                }
              }).click(function() {
                window.setTimeout(function() {
                  $.Topic("ext.file.selector").publish({
                    path : "$HOME/Offline",
                    multimode : false,
                    callback : function(files) {
                      $("#output_folder", module_options_dialog).attr({
                        value : files
                      });
                    }
                  });
                }, 0);
              });
                  
                  // $("#set_bootstrap_filename", ".save-xml-files-dialog")
                  // .button()
                  // .click(function() {
                  // window.setTimeout(function() {
                  // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH",
                  // multimode: false,
                  // callback: function(files) {
                  // $("#bootstrap_filename",".save-xml-files-dialog").attr({value:
                  // files});
                  // }});
                  // },0);
                  // });
                  //          
                  // $("#set_modulesequence_filename", ".save-xml-files-dialog")
                  // .button()
                  // .click(function() {
                  // window.setTimeout(function() {
                  // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH",
                  // multimode: false,
                  // callback: function(files) {
                  // $("#modulesequence_filename",".save-xml-files-dialog").attr({value:
                  // files});
                  // }});
                  // },0);
                  // });
                  //          
                  // $("#set_eventfilereader_filename",
                  // ".save-xml-files-dialog")
                  // .button()
                  // .click(function() {
                  // window.setTimeout(function() {
                  // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH",
                  // multimode: false,
                  // callback: function(files) {
                  // $("#eventfilereader_filename",".save-xml-files-dialog").attr({value:
                  // files});
                  // }});
                  // },0);
                  // });
                  
                  $("#set_input_files", module_options_dialog).button({
                    icons : {
                      primary : "ui-icon-folder-open"
                    }
                  }).click(function() {
                    window.setTimeout(function() {
                      $.Topic("ext.file.selector").publish({
                        path : "$HOME/Offline",
                        multimode : true,
                        callback : function(files) {
                          $("#filename_input", module_options_dialog).attr({
                            value : files
                          });
                        }
                      });
                    }, 0);
                  });
                  
                });
        
      },
      
      transmitModuleSequence : function(moduleList) {
        var _this = this;
        var vModuleList = _this.generateModuleSequence(moduleList);
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/setModuleSequence"),
          type : "POST",
          data : JSON.stringify({
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            moduleSequence : vModuleList
          }),
          contentType : "application/json"
        });
      },
      
      saveModuleSequence : function(moduleList, filepath) {
        var _this = this;
        var vModuleList = _this.generateModuleSequence(moduleList);
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/saveModuleSequence"),
          type : "POST",
          data : JSON.stringify({
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            moduleSequence : vModuleList,
            filepath : filepath
          }),
          contentType : "application/json"
        });
        $.when(request).done(function() {
          _logger.debug("ajax done;");
          return true;
        });
      },
      
      saveBootstrap : function(filepath) {
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/saveBootstrap"),
          type : "POST",
          data : JSON.stringify({
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            filepath : filepath
          }),
          contentType : "application/json"
        });
      },
      
      generateModuleSequence : function(moduleList) {
        var vModuleList = [];
        $.each($(moduleList).children(), function(index, element) {
          // skip disabled modules
          if ($(element).hasClass("ui-state-disabled")) {
            return true;
          }
          var extraInfo = "";
          var moduleName = "";
          if ($(element).hasClass("loop")) {
            extraInfo = $(element).find("#name").attr("title");
            moduleName = $(element).find("#name").text();
          } else {
            moduleName = $(element).text();
          }
          vModuleList.push([ moduleName, extraInfo ]);
          _logger.debug(index, "[" + moduleName + "," + extraInfo + "]");
        });
        return vModuleList;
      },
      
      openBootstrap : function(listModuleSequence, bootstrap_path) {
        var _this = this;
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/openBootstrapXML"),
          type : "POST",
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            path : bootstrap_path
          }
        });
        $
            .when(request)
            .done(
                function(data) {
                  _logger.debug("ajax request returned:");
                  _logger.debug("moduleSequence: " + data['moduleSequence']);
                  moduleSequence = data['data'].moduleSequence;
                  _this.input_file_names = data['data'].input_file_names;
                  _logger.debug("input_file_names: " + _this.input_file_names);
                  _this.input_file_type = data['data'].input_file_type;
                  _this.moduleSequenceFilename = data['data'].moduleSequenceFilename;
                  _this.event_file_reader_filename = data['data'].event_file_reader_filename;
                  _this.setModuleSequence(moduleSequence, listModuleSequence);
                });
      },
      
      // this function generates the html code for the modulesequence contained
      // in the variable "moduleSequence". The html node to put the html code in
      // is "listModuleSequence".
      setModuleSequence : function(moduleSequence, listModuleSequence) {
        var _this = this;
        listModuleSequence.empty();
        
        vUids = [];
        for ( var i = 0; i < moduleSequence.length; ++i) {
          var li = "";
          if (moduleSequence[i][0] == "loop") {
            var uid = $.Helpers.guid();
            vUids.push(uid);
            li = $("<li>")
                .attr({
                  id : uid,
                })
                .addClass(
                    "ui-state-default ui-corner-all steering-symbol in-module-sequence loop")
                .appendTo(listModuleSequence);
            $("<span id='numTimes'>numTimes=" + $(li).attr("title") + "</span>")
                .appendTo(li);
          } else if (moduleSequence[i][0] == "try") {
            var uid = $.Helpers.guid();
            vUids.push(uid);
            li = $("<li>")
                .attr({
                  id : uid
                })
                .addClass(
                    "ui-state-default ui-corner-all steering-symbol in-module-sequence try")
                .appendTo(listModuleSequence);
          } else if (moduleSequence[i][0] == "loop stop"
              || moduleSequence[i][0] == "try stop") {
            var uid = vUids.pop();
            li = $("<li>")
                .attr({
                  id : uid
                })
                .addClass(
                    "ui-state-default ui-corner-all steering-symbol-stop in-module-sequence")
                .appendTo(listModuleSequence);
          } else {
            li = $("<li>")
                .addClass(
                    "ui-state-default ui-corner-all offline-module in-module-sequence")
                .appendTo(listModuleSequence);
          }
          $("<span class='module-name' id='name' title='"
                  + moduleSequence[i][1] + "'>" + moduleSequence[i][0]
                  + "</span>").prependTo(li);
          
          // add sort handler
          $(li).addClass("ui-state-default in-module-sequence")
              .removeClass("ui-draggable")
              .hover(function() {
                _this.addOverlayOptions(this, listModuleSequence);
              }, function() {
                $(this).find(".overlay-options").remove();
              })
              .addClass("ui-corner-all")
              .prepend(
                  "<span style='float: left;' class='ui-icon ui-icon-carat-2-n-s sort-handle'></span>");
        }
        _this.identLi(listModuleSequence);
      },
      
      loadModuleSequence : function(listModuleSequence, module_sequence_path) {
        var _this = this;
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/loadModuleSequence"),
          type : "POST",
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            path : module_sequence_path
          // path :
          // "/home/cglaser/software/Offline/install/share/auger-offline/doc/ExampleApplications/RdHybridReconstruction/ModuleSequence.xml"
          }
        });
        moduleSequence = [];
        $.when(request).done(function(data) {
          _logger.debug("ajax request returned:");
          _logger.debug("moduleSequence: " + data['moduleSequence']);
          moduleSequence = data['data'].moduleSequence;
          _this.setModuleSequence(moduleSequence, listModuleSequence);
        });
      },
      
      changeLoopTimes : function(obj) {
        var _this = this;
        var nTimes = $("#" + _this._id + "_form_loopoptions").find(
            "input:first").attr("value");
        if (!($.Helpers.isInt(parseInt(nTimes)) || nTimes == "unbounded")) {
          alert("Input invalid! NumTimes has to be an integer or \"unbounded\"");
          return 0;
        }
        $(obj).attr("title", nTimes);
        $(obj).next().text("numTimes=" + nTimes);
      },
      
      showLoopOptions : function(obj) {
        var _this = this;
        $(".module-options").remove();
        var divLoopOptions = $("<div />").addClass("module-options").appendTo(
            _this.nodes.content);
        var form = $("<form />").attr({
          id : _this._id + "_form_loopoptions",
        }).appendTo(divLoopOptions);
        
        $("<span> numTimes = </span>").appendTo(form);
        $("<input />").attr({
          type : "text",
          value : $(obj).find("#name").attr("title"),
          alt : $(obj).find("#name").attr("title"),
          name : "nLoops"
        }).appendTo(form);
        
        $("<button />").button({
          label : "save"
        }).attr({
          type : 'submit',
          value : 'save'
        }).appendTo(form);
        
        $("<input />").button({
          label : "close"
        }).click(function() {
          divLoopOptions.remove();
        }).appendTo(form);
        
        // override submit function
        form.submit(function(event) {
          event.preventDefault();
          _logger.debug($(obj).find("#name"));
          _this.changeLoopTimes($(obj).find("#name"));
          divLoopOptions.remove();
          return false;
        });
      },
      
      showModuleOptions : function(moduleName) {
        var _this = this;
        // remove old module option div if exists
        $(".module-options").remove();
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/getModuleOptions"),
          type : "POST",
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            moduleName : moduleName
          }
        });
        // var request2 = $.ajax({
        // url:
        // Vispa.urlHandler.dynamic("/extensions/augeroffline/static/html/module_options.html"),
        // type: 'GET',
        // async: false,
        // success: function(response) {
        // module_option_template = response;
        // }
        // });
        //        
        // $.when(request, request2).done(
        // function(data1, data2) {
        //                
        // }
        // );
        
        $.when(request).done(
                function(data) {
                  dictOfOptions = data['data'].dictOfOptions;
                  _logger.debug(dictOfOptions);
                  var no_options = false;
                  if (dictOfOptions == -1 || dictOfOptions.length == 0) {
                    no_options = true;
                    $.Topic('msg.log').publish('info', {
                      text : "Module " + moduleName + " has not options",
                      icon : 'ui-icon-notice'
                    });
                  }
                  
                  var divModuleOptions = $("<div />")
                      .addClass("module-options");
                  if (no_options) {
                    divModuleOptions.text("Module " + moduleName
                        + " has no options.");
                  } else {
                    var form = $("<form />").attr({
                      id : _this._id + "_form_moduleoptions",
                      name : moduleName
                    }).appendTo(divModuleOptions);
                    var table = $("<table />").appendTo(form);
                    
                    var thead = $("<tr />").appendTo(
                        $("<thead />").appendTo(table));
                    $("<th \>").text("option").appendTo(thead);
                    $("<th \>").text("value").appendTo(thead);
                    $("<th \>").text("unit").appendTo(thead);
                    
                    var body = $("<tbody />").appendTo(table);
                    
                    // loop through option dictionary
                    // sort dictionary
                    keys = Object.keys(dictOfOptions);
                    keys.sort();
                    $
                        .each(
                            keys,
                            function(index, key) {
                              value = dictOfOptions[key]
                              // check if option has additional childs
                              if (!("value" in value)) {
                                // value has additional childs
                                var tr = $("<tr \>").appendTo(body);
                                $("<th>" + key + "</th>").appendTo(tr);
                                
                                var parent = key;
                                $
                                    .each(
                                        value,
                                        function(key, value) {
                                          _logger.debug("child " + key + ":"
                                              + value);
                                          _logger.debug(value);
                                          var tr = $("<tr \>").appendTo(body);
                                          $("<th style='padding-left:10px' />")
                                              .text(key).appendTo(tr);
                                          
                                          // value
                                          var th = $("<th />").appendTo(tr);
                                          $("<input />")
                                              .attr(
                                                  {
                                                    type : "text",
                                                    value : value["value"],
                                                    alt : value["default_value"],
                                                    current_value : value["value"],
                                                    default_value : value["default_value"],
                                                    name : key,
                                                    parent : parent
                                                  
                                                  }).appendTo(th);
                                          $("<span />")
                                              .addClass(
                                                  'ui-icon ui-icon-arrowrefresh-1-w overlay-icon')
                                              .attr({
                                                title : "revert to default"
                                              })
                                              .click(
                                                  function() {
                                                    var input = $(this)
                                                        .parent().find("input");
                                                    $(input)
                                                        .attr(
                                                            {
                                                              value : $(input)
                                                                  .attr(
                                                                      'default_value')
                                                            });
                                                    _logger
                                                        .debug("reverting to "
                                                            + $(input)
                                                                .attr(
                                                                    'default_value'));
                                                  }).appendTo(th);
                                          
                                          // unit
                                          if (value["unit"]) {
                                            var th = $("<th />").appendTo(tr);
                                            $("<input />")
                                                .attr(
                                                    {
                                                      type : "text",
                                                      value : value["unit"],
                                                      alt : value["default_unit"],
                                                      current_value : value["unit"],
                                                      default_value : value["default_unit"],
                                                      name : "unit"
                                                    }).appendTo(th);
                                            $("<span />")
                                                .addClass(
                                                    'ui-corner-all ui-icon ui-icon-arrowrefresh-1-w overlay-icon')
                                                .attr({
                                                  title : "revert to default"
                                                })
                                                .click(
                                                    function() {
                                                      var input = $(this)
                                                          .parent().find(
                                                              "input");
                                                      $(input)
                                                          .attr(
                                                              {
                                                                value : $(input)
                                                                    .attr(
                                                                        'default_value')
                                                              });
                                                      _logger
                                                          .debug("reverting to "
                                                              + $(input)
                                                                  .attr(
                                                                      'default_value'));
                                                    }).appendTo(th);
                                          } else {
                                            $("<th />").appendTo(tr);
                                          }
                                        });
                              } else {
                                
                                var tr = $("<tr \>").appendTo(body);
                                
                                $("<th />").text(key).appendTo(tr);
                                
                                // value
                                var th = $("<th />").appendTo(tr);
                                _logger.debug("value: " + value["value"]);
                                if (value["value"] != "") {
                                  $("<input />").attr({
                                    type : "text",
                                    value : value["value"],
                                    alt : value["default_value"],
                                    current_value : value["value"],
                                    default_value : value["default_value"],
                                    name : key
                                  
                                  }).appendTo(th);
                                } else {
                                  _logger.debug("value is = \"\"");
                                  $("<input />").attr({
                                    type : "text",
                                    value : "",
                                    alt : "",
                                    name : key
                                  
                                  }).appendTo(th);
                                }
                                $("<span />")
                                    // ui-state-default ui-corner-all
                                    .addClass(
                                        'ui-icon ui-icon-arrowrefresh-1-w overlay-icon')
                                    .attr({
                                      title : "revert to default"
                                    })
                                    .click(
                                        function() {
                                          var input = $(this).parent().find(
                                              "input");
                                          $(input).attr(
                                              {
                                                value : $(input).attr(
                                                    'default_value')
                                              });
                                          _logger.debug("reverting to "
                                              + $(input).attr('default_value'));
                                        }).appendTo(th);
                                
                                // unit
                                if (value["unit"]) {
                                  var th = $("<th />").appendTo(tr);
                                  $("<input />").attr({
                                    type : "text",
                                    value : value["unit"],
                                    alt : value["default_unit"],
                                    current_value : value["unit"],
                                    default_value : value["default_unit"],
                                    name : "unit"
                                  }).appendTo(th);
                                  $("<span />")
                                      // ui-state-default ui-corner-all
                                      .addClass(
                                          'ui-icon ui-icon-arrowrefresh-1-w overlay-icon')
                                      .attr({
                                        title : "revert to default"
                                      }).click(
                                          function() {
                                            var input = $(this).parent().find(
                                                "input");
                                            $(input).attr(
                                                {
                                                  value : $(input).attr(
                                                      'default_value')
                                                });
                                            _logger.debug("reverting to "
                                                + $(input)
                                                    .attr('default_value'));
                                          }).appendTo(th);
                                } else {
                                  $("<th />").appendTo(tr);
                                }
                              }
                            });
                    // override submit function
                    form.submit(function(event) {
                      event.preventDefault();
                      // event.stopPropagation();
                      _this.submitModuleOptions(this, moduleName);
                      divModuleOptions.remove();
                      return false;
                    });
                    
                    table.tablesorter();
                  }
                  divModuleOptions.dialog({
                    modal : false,
                    draggable : true,
                    width : 600,
                    title : "Module options for module " + moduleName,
                    resizable : true,
                    buttons : [ {
                      text : 'save',
                      icons : {
                        primary : 'ui-icon-disk'
                      },
                      click : function() {
                        form.submit();
                      }
                    
                    }, {
                      text : 'reset',
                      alt : 'reset all values to default',
                      icon : {
                        primary : 'ui-icon-close'
                      },
                      click : function() {
                        _this.resetModuleOptions(this);
                      }
                    }, {
                      text : 'close',
                      icon : {
                        primary : 'ui-icon-close'
                      },
                      click : function() {
                        $(this).dialog('close');
                      }
                    } ]
                  });
                  
                  // $("<input />").button({
                  // label : "save"
                  // }).attr({
                  // type : 'submit'
                  // }).appendTo(form);
                  //                  
                  // $("<input />").button({
                  // label : "reset",
                  // alt : "reset all values to default"
                  // }).click(function() {
                  // _this.resetModuleOptions(this);
                  // }).appendTo(form);
                  //                  
                  // $("<input />").button({
                  // label : "close"
                  // }).click(function() {
                  // divModuleOptions.remove();
                  // }).appendTo(form);
                  
                });
      },
      
      resetModuleOptions : function(obj) {
        _logger.debug("reset");
        $(obj).parent().find("input").each(function(index, element) {
          _logger.debug(element);
          $(element).attr({
            value : $(element).attr('alt')
          });
          _logger.debug("reverting to " + $(element).attr('alt'));
        });
      },
      
      resetAllModuleOptions : function() {
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/resetAllModuleOptions"),
          type : "POST",
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id
          }
        });
        $.when(request).done(function(data) {
          if (data['result'] == 0) {
            $.Topic('msg.log').publish('info', {
              text : "all module options reset",
              icon : 'ui-icon-check'
            });
          } else {
            $.Topic('msg.log').publish('info', {
              text : "a problem occured while reseting module options",
              icon : 'ui-icon-alert'
            });
          }
        });
      },
      
      identLiSingle : function(obj) {
        var prev = $(obj).prevAll();
        var nLoops = 0;
        $.each(prev, function(index, element) {
          if ($(element).hasClass("steering-symbol")) {
            nLoops += 1;
          }
          if ($(element).hasClass("steering-symbol-stop")) {
            nLoops -= 1;
          }
        });
        if ($(obj).hasClass("steering-symbol-stop")) {
          nLoops -= 1;
        }
        
        $.Helpers.removeClass(obj, "in-loop-*");
        
        if (nLoops > 0) {
          $(obj).addClass("in-loop-" + nLoops);
        }
      },
      
      identLi : function(obj) {
        var _this = this;
        $.each($(obj).children(), function(index, element) {
          _this.identLiSingle(element);
        });
      },
      
      to_be_implemented: function() {
        $("<div>This feature will be implemented soon!</div>").dialog({
          modal:true,
          title:'info',
          buttons: {
            Ok: function() {
              $( this ).dialog( "close" );
            }
          }
        });
      },
      
      init : function(config) {
        this._super(config);
        var _this = this;
        
        // attributes
        this.nodes = {};
        this.menuEntries = [
            {
              label : 'submit job',
              icon : 'ui-icon-play',
              callback : function() {
                _this.to_be_implemented();
//                _this.submitToJobSubmission();
              }
            },
            {
              label : 'submit to job designer',
              icon : 'ui-icon-play',
              callback : function() {
                _this.to_be_implemented();
//                _this.submitToJobSubmission();
              }
            },
            {
              label : 'open bootstrap.xml',
              icon : 'ui-icon-document',
              callback : function() {
                // $.Topic("ext.file.selector").publish({path:
                // "$AUGEROFFLINEROOT/share/auger-offline/doc/", multimode:
                // false,
                $.Topic("ext.file.selector").publish(
                    {
                      path : "$AUGEROFFLINEROOT/share/auger-offline/doc/StandardApplications",
                      multimode : false,
                      callback : function(file) {
                        _this.bootstrap_path = file;
                        _this.openBootstrap($(".module-sequence",
                            _this.nodes.content), file);
                      }
                    });
              }
            },
            {
              label : 'open module sequence',
              icon : 'ui-icon-document',
              callback : function() {
                // $.Topic("ext.file.selector").publish({path:
                // "$AUGEROFFLINEROOT/share/auger-offline/doc/", multimode:
                // false,
                $.Topic("ext.file.selector").publish(
                    {
                      path : "$AUGEROFFLINEROOT/share/auger-offline/doc/StandardApplications",
                      multimode : false,
                      callback : function(file) {
                        _this.moduleSequenceFilename = file;
                        _this.loadModuleSequence($(".module-sequence",
                            _this.nodes.content), file);
                      }
                    });
              }
            },
            {
              label : 'save XML files',
              icon : 'ui-icon-disk',
              callback : function() {
                _this.saveXMLFiles($(".module-sequence", _this.nodes.content));
              }
            },
            {
              label : 'save ModuleSequence',
              icon : 'ui-icon-disk',
              callback : function() {
                $.Topic("ext.file.selector").publish({
                    path : "$HOME/Offline",
                    multimode : false,
                    callback : function(file) {
                      _this.saveModuleSequence($(".module-sequence", _this.nodes.content), file);
                    }
                });
              }
            },
            {
              label : 'reset all module options to default',
              icon : 'ui-icon-play',
              callback : function() {
                _this.resetAllModuleOptions();
              }
            },
            {
              label : 'set all infolevel to ...',
              icon : 'ui-icon-triangle-1-e',
              callback : function() {
                _this.setAllInfoLevelTo($(".module-sequence",
                    _this.nodes.content));
              }
            }

        ];
        
        
        console.log(this._config);
      },
      
      submitModuleOptions : function(form, moduleName) {
        var _this = this;
        
        _logger.debug("moduleName = " + moduleName);
        
        var changedModuleOptions = [];
        // $("#" + _this._id + "_form_moduleoptions")
        $(form).find($("tbody")).children().each(
            function(index, element) {
              var moduleOption = $(this).find("input:first").attr("name");
              var oldOptionValue = $(this).find("input:first").attr(
                  "current_value");
              var defaultOptionValue = $(this).find("input:first").attr(
                  "default_value");
              var newOptionValue = $(this).find("input:first").attr("value");
              var newOptionUnit = $(this).find("input[name='unit']").attr(
                  "value");
              var oldOptionUnit = $(this).find("input[name='unit']").attr(
                  "current_value");
              var defaultOptionUnit = $(this).find("input[name='unit']").attr(
                  "default_value");
              var parent = $(this).find("input:first").attr("parent");
              if ((newOptionValue != oldOptionValue)
                  || (newOptionUnit != oldOptionUnit)) {
                row = [ moduleOption, newOptionValue, newOptionUnit, parent ];
                changedModuleOptions.push(row);
              }
              ;
            });
        _logger.debug("changed module Options = " + changedModuleOptions);
        if (changedModuleOptions.length > 0) {
          _logger.debug(JSON.stringify(changedModuleOptions));
          var request = $.ajax({
            url : Vispa.urlHandler
                .dynamic("extensions/augeroffline/setModuleOptions"),
            type : "POST",
            data : JSON.stringify({
              workspace_id : Vispa.workspaceManager.getWorkspace().id,
              moduleName : moduleName,
              moduleOptions : changedModuleOptions
            }),
            contentType : "application/json"
          });
          $.when(request).done(function(data) {
            if (data['result'] == 0) {
              $.Topic('msg.log').publish('info', {
                text : "module options saved",
                icon : 'ui-icon-check'
              });
            }
          });
        }
        ;
        return true;
      },
      
      addOverlayOptions : function(obj, listModuleSequence) {
        var _this = this;
        var position = $(obj).position();
        var div = $('<div />').addClass("overlay-options").css({
          top : position.top
        }).appendTo(obj);
        
        $('<span />')
            .addClass(
                'ui-state-default ui-corner-all ui-icon ui-icon-trash overlay-icon')
            .click(function() {
              _logger.info("trash click");
              if ($(obj).hasClass("steering-symbol")) {
                var id = $(obj).attr("id");
                _logger.debug(id);
                $("#" + id).remove();
                $("#" + id).remove();
              } else {
                $(obj).remove();
              }
              
              window.setTimeout(function() {
                $(".module-options").remove();
              }, 100);
              
              _this.identLi(listModuleSequence);
            }).appendTo(div);
        
        if (!$(obj).hasClass("steering-symbol")) {
          $('<span />')
              .addClass(
                  'ui-state-default ui-corner-all ui-icon ui-icon-cancel overlay-icon')
              .click(function() {
                $(obj).toggleClass("ui-state-disabled");
              }).appendTo(div);
        }
      },
      
      addControlButtons : function(obj) {
        console.log(obj);
        $('<span />').addClass(
            'ui-state-default ui-corner-all ui-icon ui-icon-trash').css(
            'float', 'right').appendTo(obj).click(function() {
          $(obj).parent().remove();
        });
        return;
      },
      
      getAvailableModules : function() {
        var _this = this;
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/get_available_modules"),
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id
          },
          type : "POST"
        });
        
        $.when(request).done(function(data) {
          return data['data'];
        });
      },
      addModuleList : function(listOfModules, category, listModuleSequence) {
        var _this = this;
        var request = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/getListOfModules"),
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            category : category
          },
          type : "POST"
        });
        
        $.when(request).done(
            function(data) {
              moduleNames = data['listOfModules'];
              
              $.each(moduleNames, function(index, moduleName) {
                
                li = $("<li>").css({
                  'z-index' : 9
                }).addClass("ui-state-default ui-corner-all offline-module")
                    .draggable({
                      helper : "clone",
                      revert : "invalid",
                      iframeFix : true,
                      connectToSortable : $(listModuleSequence)
                    }).appendTo(listOfModules);
                $("<span class='module-name'>" + moduleName + "</span>")
                    .appendTo(li);
              });
            });
        
      },
      
      applyConfig : function() {
        
        $(
            "<div>You need to reload the page for the changes to take effect.</div>")
            .dialog({
              modal : true,
              title : 'info',
              buttons : {
                Ok : function() {
                  $(this).dialog("close");
                }
              }
            })
        // backgroundColor
        // $(this.nodes.content).css('background-color',
        // this._config.backgroundColor);
        // var request = $.ajax({
        // url : Vispa.urlHandler.dynamic("extensions/augeroffline/initialize"),
        // type : "POST",
        // data : {
        // workspace_id : Vispa.workspaceManager.getWorkspace().id,
        // moduleConfig : this._config.moduleConfig,
        // detectorConfig : this._config.detectorConfig
        // }
        // });
        // $.when(request).done(
        // function(data) {
        // if (data == 0) {
        // $.Topic('msg.notify').publish({
        // text : "AugerOffline extension successfully initialized",
        // icon : 'ui-icon-check'
        // });
        // } else if (data == 1) {
        // alert("One or more module config files can not be read in. The
        // modules that are contained in this file will not be available.");
        // $
        // .Topic('msg.notify')
        // .publish(
        // {
        // text : "One or more module config files can not be read in. The
        // modules that are contained in this file will not be available.",
        // icon : 'ui-icon-alert'
        // });
        // } else if (data == 2) {
        // alert("All module config files can not be read in. No modules will be
        // available.");
        // $
        // .Topic('msg.notify')
        // .publish(
        // {
        // text : "All module config files can not be read in. No modules will
        // be available.",
        // icon : 'ui-icon-alert'
        // });
        // } else {
        // $
        // .Topic('msg.notify')
        // .publish(
        // {
        // text : "A problem occured when initalizing AugerOffline extension.",
        // icon : 'ui-icon-alert'
        // });
        // }
        //                  
        // });
      },
      
      ready: function() {
        return this;
      },
      
      render : function(node) {
        
        var _this = this;
        var _logger = $.Logger("ExtensionManager.AugerOffline");
        
        _this.nodes.content = $('<div />').addClass('offline-full-body').css(
            'background-color', _this._config.backgroundColor).get(0);
        
        
        // return _this.nodes.content;
        
        var request_initialize = $.ajax({
          url : Vispa.urlHandler.dynamic("extensions/augeroffline/initialize"),
          type : "POST",
          async : true,
          data : JSON.stringify({
            workspace_id : Vispa.workspaceManager.getWorkspace().id,
            moduleConfig : _this._config.moduleConfig,
            detectorConfig : _this._config.detectorConfig
          }),
          contentType : "application/json"
        });
        var module_list_template = $.ajax({
          url : Vispa.urlHandler
              .dynamic("/extensions/augeroffline/static/html/modulelist.html"),
          type : 'GET',
          async : true
        });
        var request_available_modules = $.ajax({
          url : Vispa.urlHandler
              .dynamic("extensions/augeroffline/get_available_modules"),
          data : {
            workspace_id : Vispa.workspaceManager.getWorkspace().id
          },
          type : "POST"
        });
        $.when(request_initialize,module_list_template,request_available_modules).done(
              
                function(data, data2, data3) {
                  _this._setLoading(false);
                  _logger.debug(data);
                  if (data[0] == 0) {
                    $.Topic('msg.log').publish(
                            'info',
                            {
                              text : "AugerOffline extension successfully initialized!",
                              icon : 'ui-icon-check'
                            });
                  } else {
                    if (data[0] == 1) {
                      $.Topic('msg.log')
                          .publish(
                              'warning',
                              {
                                text : "Not all module or detector configuration files could be found!",
                                icon : 'ui-icon-notice'
                              });
                    } else {
                      {
                        $.Topic('msg.log')
                            .publish(
                                'warning',
                                {
                                  text : "A problem occured while initializing AugerOffline Extension!",
                                  icon : 'ui-icon-notice'
                                });
                      }
                    }
                  }
                  var moduleSequence = $("<div />").addClass(
                      "div-module-sequence ui-widget").appendTo(
                      _this.nodes.content);
                  
                  _logger.debug("screen height: " + screen.height);
                  
                  $("<h2>").addClass(
                      "ui-widget-header module-sequence-headline").text(
                      "Module Sequence").appendTo(moduleSequence);
                  var div_scroll = $("<div />").addClass(
                      "div-module-sequence-scroll").appendTo(moduleSequence);
                  var pageHeight = $(window).height();
                  var navHeight = pageHeight - 200;
                  jQuery(div_scroll).css({'max-height': navHeight + 'px;'});
                  
                  // $(div_scroll).slimScroll({
                  // size: '10px',
                  // height: 'auto',
                  // // alwaysVisible: true,
                  // wheelStep: 1
                  // });
                  
                  var listModuleSequence = $("<ol>", {
                    id : "list2"
                  }).addClass("module-sequence").appendTo(div_scroll);
                  // _this.listModuleSequence = listModuleSequence;
                  
                  // definition of steering symbols
                  var steering_symbols = [ {
                    'steering-symbol-name' : 'loop',
                    'class' : 'loop'
                  }, {
                    'steering-symbol-name' : 'try',
                    'class' : 'try'
                  } ];
                  var directives = {
                    'steering-symbol' : {
                      class : function(params) {
                        return params.value + " " + this.class;
                      }
                    }
                  }

                  
                  // add template of module list to html page
                  $(data2[0]).appendTo(_this.nodes.content);
                  $(".steering-symbol-list", _this.nodes.content)
                      .render(steering_symbols, directives, {
                        debug : true
                      });

                  var modulelist = data3[0]['data'].listOfModules;
                  
                  $(".div-module-list", _this.nodes.content).render(modulelist);
                  
                  // make accordion
                  var div_left = $(".div-left",
                      _this.nodes.content);
                  $(div_left).accordion({
                    collapsible : true,
                    header : "h3",
                    heightStyle : "content"
                  }).sortable(
                      {
                        axis : "y",
                        handle : "h3",
                        stop : function(event, ui) {
                          // IE doesn't register the blur when
                          // sorting
                          // so trigger focusout handlers to
                          // remove .ui-state-focus
                          ui.item.children("h3")
                              .triggerHandler("focusout");
                        }
                      });
                  $(div_left).find('li').draggable({
                    helper : "clone",
                    revert : "invalid",
                    iframeFix : true,
                    connectToSortable : $(listModuleSequence)
                  }).css({
                    'z-index' : 9
                  });
                  
                  /*
                   *  // add offline modules
                   * $.each($.parseJSON(_this._config.moduleConfig),
                   * function(key, value) { $("<h3>").text(key).appendTo(allModules);
                   * var modules = $("<div />", { id : key
                   * }).appendTo(allModules); var listOfModules = $("<ul />").addClass(
                   * "dropfalse module-list").appendTo(modules);
                   * _this.addModuleList(listOfModules, key,
                   * listModuleSequence); });
                   * 
                   * 
                   *  // add "all" modules $("<h3>").text("All
                   * Modules").appendTo(allModules); var modules = $("<div />", {
                   * id : "All Modules" }).appendTo(allModules); var
                   * listOfModules = $("<ul />").addClass( "dropfalse
                   * module-list").appendTo(modules);
                   * _this.addModuleList(listOfModules, "All Modules",
                   * listModuleSequence);
                   * 
                   * 
                   * 
                   *  // user modules $("<h3>").text("User
                   * Modules").appendTo(allModules);
                   * 
                   * var userModules = $("<div />", { id : "userModules"
                   * }).appendTo(allModules);
                   * 
                   * $("<button />").button({ label : "add User Module"
                   * }).click(function() { _this.addUserModule();
                   * }).appendTo(userModules); $("<button />").button({ label :
                   * "set path to userAugerOffline" }).click(function() {
                   * _this.setUserAugerOffline(); }).appendTo(userModules);
                   * 
                   * var listOfUserModules = $("<ul />").addClass( "dropfalse
                   * module-list").appendTo(userModules);
                   * $(_this._config.userModules) .each( function(index,
                   * element) { _logger.debug(element); _logger.debug(this);
                   * 
                   * var li_2 = $("<li>") .css({ 'z-index' : 9 }) .addClass(
                   * "ui-state-default ui-corner-all offline-module
                   * user-module") .draggable({ helper : "clone", revert :
                   * "invalid", iframeFix : true, connectToSortable :
                   * $(listModuleSequence) }).appendTo(listOfUserModules); $( "<span
                   * class='module-name' id='name'>" + element + "</span>").appendTo(li_2);
                   * });
                   */

                  listModuleSequence
                      .sortable({
                        handle : ".sort-handle",
                        stop : function(event, ui) {
                          _this.identLi($(ui.item).parent());
                        },
                        // change: function(event, ui) {
                        // identLi($(ui.helper));
                        // },
                        receive : function(event, ui) {
                          
                          console.log($(this).data());
                          var currentItem = $(this).data().uiSortable.currentItem;
                          
                          if (!$(currentItem).hasClass("in-module-sequence")) {
                            if ($(currentItem).hasClass("steering-symbol")) {
                              var uid = $.Helpers.guid();
                              _logger.debug("set uid = " + uid);
                              $(currentItem).attr("id", uid);
                              $(currentItem).find("#name").attr("title",
                                  "unbounded");
                              
                              var li = $("<li />")
                                  .addClass(
                                      "ui-state-default ui-corner-all  in-module-sequence steering-symbol-stop")
                                  .attr("id", uid).insertAfter($(currentItem));
                              
                              $("<span style='float: left;' class='ui-icon ui-icon-carat-2-n-s sort-handle'></span>")
                                  .appendTo(li);
                              $("<span / >").text(
                                  $(currentItem).text() + " stop").appendTo(
                                  $(li));
                              
                              if ($(currentItem).hasClass("loop")) {
                                $(currentItem).find("#name").after(
                                    $("<span id='numTimes'>numTimes="
                                        + $(currentItem).find("#name").attr(
                                            "title") + "</span>"));
                              }
                            }
                            
                            $(currentItem)
                                .addClass("ui-state-default in-module-sequence")
                                .removeClass("ui-draggable")
                                .hover(
                                    function() {
                                      _this.addOverlayOptions(this,listModuleSequence);
                                    },
                                    function() {
                                      $(this).find(".overlay-options").remove();
                                    })
                                .addClass("ui-corner-all")
                                .prepend(
                                    "<span style='float: left;' class='ui-icon ui-icon-carat-2-n-s sort-handle'></span>");
                          }
                          
                          _this.identLi($(currentItem).parent());
                          
                        },
                        axis : "y"
                      });
                  // listModuleSequence.disableSelection();
                  listModuleSequence.selectable({
                    cancel : ".overlay-options,.sort-handle",
                    selecting : function(event, ui) {
                      if ($(".ui-selected, .ui-selecting").length > 1) {
                        $(ui.selecting).removeClass("ui-selecting");
                      }
                    },
                    create : function(event, ui) {
                      console.log("selectable created");
                    },
                    selected : function(event, ui) {
                      console.log("selected");
                      if ($(ui.selected).hasClass("offline-module")) {
                        _logger.debug("module-identifier: "
                            + $(ui.selected).text());
                        _this.showModuleOptions($(ui.selected).text());
                      }
                      if ($(ui.selected).hasClass("loop")) {
                        _this.showLoopOptions($(ui.selected));
                      }
                      
                    }
                  // unselected : function(event, ui) {
                  // _logger.debug($(ui.unselected).text());
                  
                  // if ($(ui.unselected).hasClass("loop")) {
                  // _this.changeLoopTimes($(ui.unselected).find("#name"));
                  // }
                  // if ($(ui.unselected).hasClass("offline-module")) {
                  // _this.submitModuleOptions($("#" + _this._id
                  // + "_form_moduleoptions"), $(ui.unselected).text());
                  // }
                  // $(".module-options").remove();
                  // }
                  });
                  listModuleSequence
                      .find("li")
                      .addClass("ui-corner-all")
                      .prepend(
                          "<div class='handle'><span class='ui-icon ui-icon-carat-2-n-s'></span></div>");
                  
                  // window.setTimeout(function() {
                  // var kids =
                  // $(".module-sequence").children().each(function(){console.log(this);});
                  // }, 500)
                  
                  // $(listModuleSequence)
                  // .children()
                  // .hover(
                  // function() {
                  // $('<span />')
                  // .addClass('ui-state-default ui-corner-all ui-icon
                  // ui-icon-trash')
                  // .css('float', 'right')
                  // .appendTo(this)
                  // .click(function() {
                  // console.debug($(this).parent());
                  // $(this)
                  // .parent()
                  // .remove();
                  // });
                  // },
                  // // addControlButtons(this),
                  // function () {
                  // $(this).find("span").remove();
                  // }
                  // );
                  
//                  var divButton = $("<div />").addClass("div-button").appendTo(
//                      _this.nodes.content);
//                  
//                  $("<button />").button({
//                    label : "generate module sequence"
//                  }).click(function() {
//                    _this.generateModuleSequence($(listModuleSequence));
//                  }).css({
//                    "padding" : 5
//                  }).appendTo(divButton);
//                  
                  // $("<button />").button({
                  // label : "load module sequence"
                  // }).click(function() {
                  // _this.loadModuleSequence(listModuleSequence);
                  // $.Topic('msg.notify').publish({
                  // text : "Foo Bar Test",
                  // icon : 'ui-icon-check'
                  // });
                  // $.Topic('msg.log').publish('info', {
                  // text : "Foo Bar Test",
                  // icon : 'ui-icon-check'
                  // });
                  // }).css({
                  // "padding" : 5
                  // })
                  // // .text("generate module sequence")
                  // .appendTo(divButton);
                  
                  // $("<button />").button({
                  // label : "open bootstrap.xml"
                  // }).click(function() {
                  // // $.Topic("ext.file.selector").publish({path:
                  // "$AUGEROFFLINEROOT/share/auger-offline/doc/", multimode:
                  // false,
                  // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH",
                  // multimode: false,
                  // callback: function(file) {
                  // _this.bootstrap_path = file;
                  // _this.openBootstrap(listModuleSequence, file);
                  // }});
                  // }).css({
                  // "padding" : 5
                  // })
                  // .appendTo(divButton);
                  
//                  $("<button />").button({
//                    label : "submit job"
//                  }).click(function() {
//                    _this.submitToJobSubmission();
//                  }).css({
//                    "padding" : 5
//                  }).appendTo(divButton);
//                  
//                  $("<button />").button({
//                    label : "submit to job designer"
//                  }).click(
//                      function() {
//                        
//                        var optionList = [];
//                        
//                        // add default options
//                        optionList.push([ {
//                          name : "Input Files",
//                          group : "EventFileReader",
//                          optionString : '--dataFiles',
//                          value : "file1 file2",
//                          decorator : '',
//                          active : true
//                        } ]);
//                        _logger.debug("{command:executeOffline.py, optionList:"
//                            + optionList + "}");
//                        Vispa.extensionManager.getFactory("jobdesigner",
//                            "jobmanagement")._create({
//                          command : "executeOffline.py",
//                          optionList : optionList
//                        });
//                      }).css({
//                    "padding" : 5
//                  }).appendTo(divButton);
                  
                  // $("<button />").button({
                  // label : "save modulesequence"
                  // }).click(function() {
                  // $.Topic("ext.file.selector").publish({path: "$HOME/RWTH",
                  // multimode: false,
                  // callback: function(file) {
                  // _this.saveModuleSequence($(listModuleSequence), file);
                  // }});
                  // }).css({
                  // "padding" : 5
                  // }).appendTo(divButton);
                  
//                  $("<button />").button({
//                    label : "save bootstrap.xml"
//                  }).click(function() {
//                    $.Topic("ext.file.selector").publish({
//                      path : "$HOME/RWTH",
//                      multimode : false,
//                      callback : function(file) {
//                        _this.saveBootstrap(file);
//                      }
//                    });
//                  }).css({
//                    "padding" : 5
//                  }).appendTo(divButton);
//                  
//                  $("<button />").button({
//                    label : "save XML files"
//                  }).click(function() {
//                    _this.saveXMLFiles($(listModuleSequence));
//                  }).css({
//                    "padding" : 5
//                  }).appendTo(divButton);
//                  
                  // $("<button />").button({
                  // label : "set all infolevel to"
                  // }).click(function() {
                  // _this.setAllInfoLevelTo($(listModuleSequence));
                  // }).css({
                  // "padding" : 5
                  // }).appendTo(divButton);
                  
//                  $("form").submit(function() {
//                    $.Logger.info("sumbit button pressed");
//                    alert("submit pressed");
//                    return false;
                });
                  
      
        $(node).append(this.nodes.content);
        return this;
      
    }});

$(function() {
  // register the Extension
  $.Topic('extman.register').publish(AugerOfflineExtension);
});
