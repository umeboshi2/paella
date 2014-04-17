define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'

  FDViews = require 'frontdoor/views'
  
  
  class Controller extends Backbone.Marionette.Controller
    make_main_content: ->
      MSGBUS.events.trigger 'sidebar:close'
      $('#header').text 'Front Door'
      user = MSGBUS.reqres.request 'current:user'
      # FIXME
      show_login_form = false
      if ! user.has('name')
        view = new FDViews.LoginView
        show_login_form = true
        #view.render()
      else
        view = new FDViews.FrontDoorMainView
      MSGBUS.events.trigger 'rcontent:show', view
          
          
    start: ->
      @make_main_content()
        

  module.exports = Controller
  
