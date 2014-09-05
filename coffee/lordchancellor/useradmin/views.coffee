define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  Models = require 'models'

  Templates = require 'useradmin/templates'
  AppBus = require 'useradmin/msgbus'
  
  FormView = require 'common/views/formview'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: Templates.frontdoor_main

  class SideBarView extends BaseSideBarView
    
  class SimpleUserEntryView extends Backbone.Marionette.ItemView
    template: Templates.simple_user_entry

  class UserListView extends Backbone.Marionette.CompositeView
    template: Templates.simple_user_list
    itemView: SimpleUserEntryView
    className: 'listview-list'

  class SimpleGroupEntryView extends Backbone.Marionette.ItemView
    template: Templates.simple_group_entry

  class GroupListView extends Backbone.Marionette.CompositeView
    template: Templates.simple_group_list
    itemView: SimpleGroupEntryView
    className: 'listview-list'
    
  class NewUserFormView extends FormView
    ui:
      name: '[name="name"]'
      password: '[name="password"]'
      confirm: '[name="confirm"]'
      
    template: Templates.new_user_form

    createModel: ->
      new Models.User

    updateModel: ->
      @model.set
        name: @ui.name.val()
        password: @ui.password.val()
        confirm: @ui.confirm.val()
      users = MSGBUS.reqres.request 'useradmin:userlist'
      users.add @model

    onSuccess: (model) ->
      MSGBUS.events.trigger 'useradmin:event:user_added'
      
      
        
      
  class NewGroupFormView extends FormView
    template: Templates.new_group_form

    createModel: ->
      new Models.Group
      
  class ViewUserView extends Backbone.Marionette.ItemView
    events:
      'click .delete-user-button': 'delete_user_pressed'
      'click .confirm-delete-button': 'confirm_delete_pressed'
      
    template: Templates.view_user_page

    delete_user_pressed: ->
      console.log 'delete_user_pressed'
      button = $ '.delete-user-button'
      button.removeClass 'delete-user-button'
      button.addClass 'confirm-delete-button'
      button.text 'Confirm'

    confirm_delete_pressed: ->
      console.log 'confirm_delete_pressed'
      button = $ '.confirm-delete-button'
      @model.destroy()
      MSGBUS.events.trigger 'rcontent:close'
      
      

      
      
      
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    SimpleUserEntryView: SimpleUserEntryView
    UserListView: UserListView
    SimpleGroupEntryView: SimpleGroupEntryView
    GroupListView: GroupListView
    NewUserFormView: NewUserFormView
    NewGroupFormView: NewGroupFormView
    ViewUserView: ViewUserView
    