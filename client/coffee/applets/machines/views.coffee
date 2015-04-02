define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  CommonTemplates = require 'common/templates'
  FormView = require 'common/views/formview'
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
  PageableView = require 'common/views/pageable'
  NameContentFormView = require 'common/views/namecontentform'

  Util = require 'common/util'
  
  FDTemplates = require 'frontdoor/templates'
  
  Templates = require 'machines/templates'
  AppBus = require 'machines/msgbus'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends BaseSideBarView

  class SimpleMachineEntryView extends Backbone.Marionette.ItemView
    template: Templates.machine_name_entry

  class SimpleMachineListView extends PageableView
    childView: SimpleMachineEntryView
    childViewContainer: '.listview-list'
    itemSelector: '.machine'
    template: Templates.simple_machine_list
    ui: () ->
      super
        container: @childViewContainer

  class BasicMachineView extends FormView
    fields: ['arch', 'ostype', 'release', 'iface']
    recipeFields: ['recipe', 'raid_recipe']
    template: Templates.view_machine
    
    ui: () ->
      data = {}
      for fieldlist in [@fields, @recipeFields]
        for field in fieldlist
          data[field] = "[name=\"#{field}\"]"
      data['set_install_button'] = '#set-install-button'
      return data

    events:
      'click @ui.set_install_button': 'setInstallClicked'

    # model is fetched and passed to view constructor
    createModel: ->
      @model

    updateModel: ->
      window.fview = @
      update = {}
      for field in @fields
        value = @ui[field].val()
        if value != @model.get field
          console.log 'updateModel', field, value
          @model.set field, value
      # FIXME: I don't like magic names like this.
      no_recipe_marker = '<No Recipe>'
      for rfield in @recipeFields
        value = @ui[rfield].val()
        if value != no_recipe_marker
          console.log 'set rfield', rfield, 'to', value
          @model.set rfield, value
          continue
        if value == no_recipe_marker and @model.has rfield
          console.log "remove #{rfield} from", @model
          #@model.unset rfield
          @model.set rfield, null
          
    setInstallClicked: ->
      # http://stackoverflow.com/questions/16876970/marionette-itemview-how-to-re-render-model-on-change
      url = '/paella/rest/v0/main/admin/machines'
      action = 'install'
      if @model.get('pxeconfig')
        action = 'stage_over'
      data =
        uuid: @model.get 'uuid'
        action: action
      settings =
        type: 'POST'
        url: url
        data: JSON.stringify data
        accepts: 'application/json'
        contentType: 'application/json'
      response = $.ajax settings
      response.done =>
        mresponse = @model.fetch()
        mresponse.done =>
          @render()
      
      
  class NewMachineView extends FormView
    fields: ['name', 'uuid']
    template: Templates.new_machine_form
    
    ui: () ->
      data = {}
      for field in @fields
        data[field] = "[name=\"#{field}\"]"
      return data

    # model is fetched and passed to view constructor
    createModel: ->
      @model

    updateModel: ->
      window.fview = @
      update = {}
      for field in @fields
        value = @ui[field].val()
        if value != @model.get field
          console.log 'updateModel', field, value
          @model.set field, value
      @model.set 'action', 'submit'
      @collection.add @model
         
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    SimpleMachineListView: SimpleMachineListView
    BasicMachineView: BasicMachineView
    NewMachineView: NewMachineView
    
