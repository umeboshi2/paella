define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'views/templates'

  FDTemplates = require 'frontdoor/templates'
  FormView = require 'common/form_view'

  require 'ace'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends Backbone.Marionette.ItemView
    template: Templates.main_sidebar

  class PageListEntryView extends Backbone.Marionette.ItemView
    template: FDTemplates.page_list_entry
    
  class PageListView extends Backbone.Marionette.CompositeView
    template: FDTemplates.page_list
    childView: PageListEntryView
    className: '.listview-list'

  class ShowPageView extends Backbone.Marionette.ItemView
    template: FDTemplates.show_page_view

  class EditPageView extends Backbone.Marionette.ItemView
    template: FDTemplates.edit_page

    onDomRefresh: () ->
      savebutton = $ '#save-button'
      savebutton.hide()
      editor = ace.edit('editor')
      editor.setTheme 'ace/theme/twilight'
      session = editor.getSession()
      session.setMode('ace/mode/markdown')
      content = @model.get 'content'
      editor.setValue(content)

      session.on('change', () ->
        savebutton.show()
      )
      
      savebutton.click =>
        @model.set('content', editor.getValue())
        response = @model.save()
        response.done ->
          console.log 'Model successfully saved.'
          savebutton.hide()
      window.editor = editor
          
          
          
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    
    