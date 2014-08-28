define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  Models = require 'models'
  Templates = require 'common/templates'

  FDTemplates = require 'wiki/templates'
  AppBus = require 'wiki/msgbus'
  
  FormView = require 'common/views/formview'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends BaseSideBarView
    
  class PageListEntryView extends Backbone.Marionette.ItemView
    template: FDTemplates.page_list_entry
    
  class PageListView extends Backbone.Marionette.CompositeView
    template: FDTemplates.page_list
    childView: PageListEntryView
    childViewContainer: '.listview-list'
    # handle new page button click
    events:
      'click #add-new-page-button': 'add_new_page_pressed'
      
    add_new_page_pressed: () ->
      console.log 'add_new_page_pressed called'
      navigate_to_url '#wiki/addpage'
      
  class ShowPageView extends Backbone.Marionette.ItemView
    template: FDTemplates.show_page_view


  class EditPageView extends BaseEditPageView
    template: FDTemplates.edit_page

  class NewPageFormView extends FormView
    ui:
      name: '[name="name"]'
      content: '[name="content"]'

    template: FDTemplates.new_page_form

    createModel: ->
      new Models.Page
        validation:
          name:
            required: true
          content:
            required: true
            
      
    updateModel: ->
      collection = AppBus.reqres.request 'pages:collection'
      page_id = @ui.name.val()
      @model.set
        id: page_id
        name: page_id
        content: @ui.content.val()
      collection.add @model

    onSuccess: (model) ->
      navigate_to_url '#wiki/editpage/' + model.get 'id'

    onFailure: (model) ->
      #alert "Failed"
      
      
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    NewPageFormView: NewPageFormView
    
    