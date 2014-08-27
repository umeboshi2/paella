define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'views/templates'

  FDTemplates = require 'frontdoor/templates'
  FormView = require 'common/form_view'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/editview'
  BaseSideBarView = require 'common/sidebarview'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends BaseSideBarView
    
  class PageListEntryView extends Backbone.Marionette.ItemView
    template: FDTemplates.page_list_entry
    
  class PageListView extends Backbone.Marionette.CompositeView
    template: FDTemplates.page_list
    childView: PageListEntryView
    childViewContainer: '.listview-list'
    # handle new page button click
    events:
      'click #add-new-page-button': 'add_new_page_pressed'
      
    add_new_page_pressed: () ->
      console.log 'add_new_page_pressed called'
      navigate_to_url '#wiki/addpage'
      
  class ShowPageView extends Backbone.Marionette.ItemView
    template: FDTemplates.show_page_view


  class EditPageView extends BaseEditPageView
    template: FDTemplates.edit_page
    
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    PageListView: PageListView
    ShowPageView: ShowPageView
    EditPageView: EditPageView
    
    