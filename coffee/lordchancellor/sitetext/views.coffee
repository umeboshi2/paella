define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  Models = require 'sitetext/models'

  Templates = require 'sitetext/templates'
  AppBus = require 'sitetext/msgbus'
  
  FormView = require 'common/views/formview'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
    
  class SideBarView extends BaseSideBarView

  class PageListEntryView extends Backbone.Marionette.ItemView
    template: Templates.page_list_entry

  class PageListView extends Backbone.Marionette.CompositeView
    template: Templates.page_list
    childView: PageListEntryView
    childViewContainer: '.listview-list'

  class ShowPageView extends Backbone.Marionette.ItemView
    template: Templates.page_view
      
  class EditPageView extends BaseEditPageView
    template: Templates.edit_page

  class NewPageFormView extends FormView
    ui:
      name: '[name="name"]'
      content: '[name="content"]'

    template: Templates.new_page_form

    createModel: ->
      new Models.PageModel
        validation:
          name:
            required: true
          content:
            required: true
            
      
    updateModel: ->
      collection = AppBus.reqres.request 'get-pages'
      page_id = @ui.name.val()
      @model.set
        name: page_id
        content: @ui.content.val()
      collection.add @model

    onSuccess: (model) ->
      console.log 'model ' + model + '-->' + @model
      navigate_to_url '#sitetext/editpage/' + model.get 'id'

    onFailure: (model) ->
      #alert "Failed"
      
      
      
  module.exports =
    SideBarView: SideBarView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    NewPageFormView: NewPageFormView
    