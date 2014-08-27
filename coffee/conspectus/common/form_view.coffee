# https://github.com/scottaj/marionette-form-view-demo
# 

define (require, exports, module) ->
  _ = require 'underscore'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Validation = require 'validation'
    
  class FormView extends Backbone.Marionette.ItemView

    constructor: ->
      super

      @listenTo this, 'render', @hideActivityIndicator
      @listenTo this, 'render', @prepareModel
      @listenTo this, 'save:form:success', @success
      @listenTo this, 'save:form:failure', @failure

    delegateEvents: (events)->
      @ui = _.extend @_baseUI(), _.result(this, 'ui')
      @events = _.extend @_baseEvents(), _.result(this, 'events')
      super events

    tagName: 'form'

    _baseUI: ->
      submit: 'input[type="submit"]'
      activityIndicator: '.spinner'

    _baseEvents: ->
      eventHash =
        'change [data-validation]': @validateField
        'blur [data-validation]':   @validateField
        'keyup [data-validation]':  @validateField

      eventHash["click #{@ui.submit}"] = @processForm
      eventHash

    createModel: ->
      throw new Error 'implement #createModel in your FormView subclass to return a Backbone model'

    prepareModel: ->
      @model = @createModel()
      @setupValidation()

    validateField: (e) ->
      validation = $(e.target).attr('data-validation')
      value = $(e.target).val()
      if @model.preValidate validation, value
        @invalid @, validation
      else
        @valid @, validation

    processForm: (e) ->
      e.preventDefault()
      @showActivityIndicator()

      @updateModel()
      @saveModel()

    updateModel: ->
      throw new Error 'implement #updateModel in your FormView subclass to update the attributes of @model'

    saveModel: ->
      callbacks =
        success: => @trigger 'save:form:success', @model
        error: => @trigger 'save:form:failure', @model

      @model.save {}, callbacks

    success: (model) ->
      @render()
      @onSuccess(model)

    onSuccess: (model) -> null

    failure: (model) ->
      @hideActivityIndicator()
      @onFailure(model)

    onFailure: (model) -> null

    showActivityIndicator: ->
      @ui.activityIndicator.show()
      @ui.submit.hide()

    hideActivityIndicator: ->
      @ui.activityIndicator.hide()
      @ui.submit.show()

    setupValidation: ->
      Backbone.Validation.unbind this
      Backbone.Validation.bind this,
        valid: @valid
        invalid: @invalid

    valid: (view, attr, selector) =>
      @$("[data-validation=#{attr}]").parent()
        .removeClass('has-error')
        .addClass('has-success')

    invalid: (view, attr, error, selector) =>
      @failure(@model)
      @$("[data-validation=#{attr}]").parent()
        .removeClass('has-success')
        .addClass('has-error')

  module.exports = FormView
  