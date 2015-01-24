define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Wreqr = Backbone.Wreqr
  Util = require 'common/util'

  class BootStrapAppRouter extends Backbone.Marionette.AppRouter
    onRoute: (name, path, args) ->
      #console.log "onRoute name: #{name}, path: #{path}, args: #{args}"
      Util.navbar_set_active path
      
  module.exports =
    BootStrapAppRouter: BootStrapAppRouter
