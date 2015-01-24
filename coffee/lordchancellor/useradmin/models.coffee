define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
    
  ########################################
  # Models
  ########################################

  class User extends Backbone.Model
    defaults:
      name: ''
      password: 'none'
      confirm: 'unconfirmed'

    validation:
      name:
        required: true
        msg: 'Name required.'
      password:
        required: true
      confirm:
        required: true
        equalTo: 'password'
        msg: 'The passwords do not match.'
        

  class Group extends Backbone.Model
    defaults:
      name: ''

  module.exports =
    User: User
    Group: Group
