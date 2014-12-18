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

  class SimpleRecipeEntryView extends Backbone.Marionette.ItemView
    template: Templates.recipe_name_entry
    
  class SimpleRecipeListView extends PageableView
    childView: SimpleRecipeEntryView
    childViewContainer: '.listview-list'
    itemSelector: '.recipe'
    template: Templates.simple_recipe_list
    ui: () ->
      super
        container: @childViewContainer

  class SimpleRaidRecipeEntryView extends Backbone.Marionette.ItemView
    template: Templates.raid_recipe_name_entry

  class SimpleRaidRecipeListView extends PageableView
    childView: SimpleRaidRecipeEntryView
    childViewContainer: '.listview-list'
    itemSelector: '.recipe'
    template: Templates.simple_raid_recipe_list
    ui: () ->
      super
        container: @childViewContainer

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
    SimpleRecipeListView: SimpleRecipeListView
    SimpleRaidRecipeListView: SimpleRaidRecipeListView
    EditRecipeView: EditRecipeView
    NewRecipeView: NewRecipeView
    NewRaidRecipeView: NewRaidRecipeView
    
