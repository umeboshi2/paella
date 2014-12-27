define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'

  { navigate_to_url } = require 'common/util'

  require 'jquery-ui'

  ace = require 'ace/ace'
    
  # FIXME - if require 'ace' is directly below the preceding line,
  # it doesn't seem to import properly.  If it is separated
  # by a blank line, it will be imported properly.  If it is
  # above the line, the extra newline isn't necessary.
  #
  #
  # The editor container requires an 'id' attribute.
  # IMPORTANT! - the editor container needs a stylesheet
  # entry to describe the size of the text area, or it
  # will be invisible!  Either write an entry in the
  # css, or adjust the styling of the container imperatively.    
  class BaseEditPageView extends Backbone.Marionette.ItemView
    # These initial attributes can be overridden in
    # the subclass.  The template needs a "save button"
    # that will be hidden until changes occur in the
    # content.
    save_button: '#save-button'
    editorContainer: 'editor'
    editorTheme: 'ace/theme/twilight'
    editorMode: 'ace/mode/markdown'
    contentAttribute: 'content'
    
    onDomRefresh: () ->
      savebutton = $ @save_button
      savebutton.hide()
      editor = ace.edit(@editorContainer)
      editor_el = $ @editorContainer
      @$el.resizable
        # FIXME! the resizing is a bit off
        stop: (event, ui) ->
          $(editor.container).css 'height', ui.size.height + 'px'
          $(editor.container).css 'width', ui.size.width + 'px'
          editor.resize()
      editor.setTheme @editorTheme
      session = editor.getSession()
      session.setMode @editorMode
      content = @model.get @contentAttribute
      editor.setValue content

      session.on 'change', () ->
        savebutton.show()

      savebutton.click =>
        @model.set @contentAttribute, editor.getValue()
        response = @model.save()
        response.done ->
          # FIXME make a basic method to display alert div
          # or something
          #console.log 'Model successfully saved.'
          savebutton.hide()
            
  module.exports = BaseEditPageView