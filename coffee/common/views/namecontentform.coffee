define (require, exports, module) ->
  _ = require 'underscore'
  Backbone = require 'backbone'
  Marionette = require 'marionette'

  FormView = require 'common/views/formview'
  Templates = require 'common/templates'
  
  class NameContentFormView extends FormView
    fields: ['name', 'content']
    template: Templates.name_content_form
    ui: ->
      data = {}
      for field in @fields
        data[field] = "[name=\"#{field}\"]"
      return data
      

    updateModel: ->
      for field in @fields
        value = @ui[field].val()
        if value
          @model.set field, value
      @collection.add @model
      
  module.exports = NameContentFormView
  
  
