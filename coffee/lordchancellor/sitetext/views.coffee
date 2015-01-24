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
      # Since the models in the page collection
      # use the name attribute for id, but the
      # database backend uses a regular id attribute, and
      # a unique constraint on the name, when adding a
      # model, it must use the id attribute to make a
      # POST request, instead of a PUT request.
      # FIXME: learn more about backbone rest operations
      new Models.PostPageModel
        
    updateModel: ->
      collection = AppBus.reqres.request 'get-pages'
      page_id = @ui.name.val()
      @model.set
        name: page_id
        content: @ui.content.val()
      collection.add @model
      # for some reason this model disappears
      # by the time @onSuccess is called, so
      # we set a property for the new page
      # name that can be reached by @onSuccess
      @new_page_name = page_id
      
    onSuccess: (model) ->
      #console.log "model #{model} --> #{@new_page_name}"
      # This model passed as a parameter is undefined,
      # presumably because we used a different model
      # type for the post, so we refresh the collection
      # before we load the edit page. 
      collection = AppBus.reqres.request 'get-pages'
      response = collection.fetch()
      response.done =>
        navigate_to_url "#sitetext/editpage/#{@new_page_name}"

    onFailure: (model) ->
      #alert "Failed"
      
      
      
  module.exports =
    SideBarView: SideBarView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    NewPageFormView: NewPageFormView
    
