define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  
  Models = require 'useradmin/models'
  AppBus = require 'useradmin/msgbus'
  
  { BaseCollection } = require 'common/collections'
        

  ########################################
  # Collections
  ########################################
  rscroot = '/paella/rest/v0/main'
  
  class UserList extends BaseCollection
    model: Models.User
    url: "#{rscroot}/users"

  class GroupList extends BaseCollection
    model: Models.Group
    url: "#{rscroot}/groups"

  MainUserList = new UserList
  MainGroupList = new GroupList

  make_ug_collection = (user_id) ->
    class uglist extends BaseCollection
      model: Models.Group
      url: "#{rscroot}/users/#{user_id}/groups"
    return new uglist
    
  AppBus.reqres.setHandler 'get-users', ->
    MainUserList
  AppBus.reqres.setHandler 'get-groups', ->
    MainGroupList
  
  module.exports =
    MainUserList: MainUserList
    MainGroupList: MainGroupList
    make_ug_collection: make_ug_collection
    
    
