define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'demoapp/templates'
  Models = require 'demoapp/models'
  
  require 'jquery-ui'
  
  class SideBarView extends Backbone.Marionette.ItemView
    template: Templates.sidebar
    events:
      'click .maincalendar': 'maincalendar_pressed'
      'click .listmeetings': 'list_meetings_pressed'
      
    _navigate: (url) ->
      r = new Backbone.Router
      r.navigate url, trigger:true
      
    maincalendar_pressed: () ->
      console.log 'maincalendar_pressed called'
      @_navigate '#demoapp'
      
    list_meetings_pressed: () ->
      console.log 'list_meetings_pressed called'
      @_navigate '#demoapp/listmeetings'
      
  class ShowPageView extends Backbone.Marionette.ItemView
    template: Templates.page_view

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
    SideBarView: SideBarView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    
    
