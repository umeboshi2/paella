define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'jellyfish/templates'

  Models = require 'jellyfish/models'
  FormView = require 'common/form_view'

  class JellyfishView extends Backbone.Marionette.ItemView

  class PageListEntryView extends Backbone.Marionette.ItemView
    template: Templates.page_list_entry
    
  class PageListView extends Backbone.Marionette.CollectionView
    template: Templates.page_list
    itemView: PageListEntryView
    
  class ShowPageView extends Backbone.Marionette.ItemView
    template: Templates.page_view

  class BaseEditPageView extends FormView

  class EditPageView extends Backbone.Marionette.ItemView
    template: Templates.edit_page

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
          
          
      
  module.exports =
    JellyfishView: JellyfishView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    