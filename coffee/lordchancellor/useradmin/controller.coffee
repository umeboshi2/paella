define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'useradmin/views'
  AppBus = require 'useradmin/msgbus'
  
  { SideBarController } = require 'common/controllers'
  
  #    'useradmin/viewuser/:id': 'view_user'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'List Users'
        url: '#useradmin/listusers'
      }
      {
        name: 'Add User'
        url: '#useradmin/adduser'
      }
      {
        name: 'List Groups'
        url: '#useradmin/listgroups'
      }
      {
        name: 'Add Group'
        url: '#useradmin/addgroup'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data

    make_main_content: ->
      @make_sidebar()

    list_users: ->
      @make_sidebar()
      userlist = AppBus.reqres.request 'get-users'
      response = userlist.fetch()
      response.done =>
        view = new Views.UserListView
          collection: userlist
        MainBus.vent.trigger 'appregion:content:show', view

    add_user: ->
      @make_sidebar()
      console.log "add_user called on controller"
      view = new Views.NewUserFormView
      MainBus.vent.trigger 'appregion:content:show', view
      
    list_groups: ->
      @make_sidebar()
      console.log "list_groups called on controller"

      grouplist = AppBus.reqres.request 'get-groups'
      response = grouplist.fetch()
      response.done =>
        view = new Views.GroupListView
          collection: grouplist
        MainBus.vent.trigger 'appregion:content:show', view
        

    add_group: ->
      @make_sidebar()
      console.log "add_group called on controller"
      #@set_header 'add group'
      
      view = new Views.NewGroupFormView
      MainBus.vent.trigger 'appregion:content:show', view

    view_user: (user_id) ->
      @make_sidebar()
      console.log "view_user called on controller"
      #@set_header 'view user'

      users = AppBus.reqres.request 'get-users'
      
      view = new Views.ViewUserView
        model: users.get user_id
      MainBus.vent.trigger 'appregion:content:show', view
      
    start: ->
      MainBus.vent.trigger 'appregion:content:empty', ''
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'wiki started'

  module.exports = Controller
  
