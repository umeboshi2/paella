define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  CommonTemplates = require 'common/templates'
  FormView = require 'common/views/formview'
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
  PageableView = require 'common/views/pageable'
  NameContentFormView = require 'common/views/namecontentform'
  
  { navigate_to_url } = require 'common/util'

  FDTemplates = require 'frontdoor/templates'
  
  Templates = require 'machines/templates'
  AppBus = require 'machines/msgbus'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends BaseSideBarView

  class SimpleMachineEntryView extends Backbone.Marionette.ItemView
    template: Templates.machine_name_entry

  class SimpleMachineListView extends PageableView
    childView: SimpleMachineEntryView
    childViewContainer: '.listview-list'
    itemSelector: '.machine'
    template: Templates.simple_machine_list
    ui: () ->
      super
        container: @childViewContainer

  class BasicMachineView extends Backbone.Marionette.ItemView
    template: Templates.view_machine
    
  class EditRecipeView extends BaseEditPageView
    template: Templates.edit_recipe

  class NewRecipeView extends NameContentFormView
    template: Templates.new_recipe_form
    collection: AppBus.reqres.request 'recipe:collection'

    createModel: ->
      new Backbone.Model
      
      
  class NewRaidRecipeView extends NameContentFormView
    template: Templates.new_raid_recipe_form
    collection: AppBus.reqres.request 'raid_recipe:collection'

    createModel: ->
      new Backbone.Model
      
      
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    SimpleMachineListView: SimpleMachineListView
    BasicMachineView: BasicMachineView
    EditRecipeView: EditRecipeView
    NewRecipeView: NewRecipeView
    NewRaidRecipeView: NewRaidRecipeView
    
