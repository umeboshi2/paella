define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Util = require 'common/util'

  class BootStrapAppRouter extends Backbone.Marionette.AppRouter
    onRoute: (name, path, args) ->
      #console.log 'onRoute name: ' + name
      #console.log 'onRoute path: ' + path
      #console.log 'onRoute args:' + args
      Util.navbar_set_active path
      
  module.exports =
    BootStrapAppRouter: BootStrapAppRouter
