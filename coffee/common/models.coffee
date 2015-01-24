define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'

  class User extends Backbone.Model
    defaults:
      objtype: 'user'
      
  class Group extends Backbone.Model
    defaults:
      objtype: 'group'
      
  class CurrentUser extends Backbone.Model
    
  make_current_user_model = (url) ->
    user = new CurrentUser
    user.url = url
    return user
      

  set_get_current_user_handler = (msgbus, url) ->
    user = make_current_user_model url
    #window.user = user
    msgbus.reqres.setHandler 'get-current-user', () ->
      user
      
  module.exports =
    User: User
    Group: Group
    make_current_user_model: make_current_user_model
    set_get_current_user_handler: set_get_current_user_handler
    