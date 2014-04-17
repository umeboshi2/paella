define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'simplerss/templates'

  Models = require 'models'

  FormView = require 'common/form_view'
  
  
  class FeedEntryView extends Backbone.Marionette.ItemView
    template: Templates.rss_feed_entry

  class FeedListView extends Backbone.Marionette.CollectionView
    template: Templates.rss_feed_list
    itemView: FeedEntryView

  class FeedDataView extends Backbone.Marionette.ItemView
    template: Templates.viewfeed

  class BaseFeedView extends FormView
    ui:
      name: '[name="name"]'
      url: '[name="url"]'
      
    updateModel: ->
      @model.set
        name: @ui.name.val()
        url: @ui.url.val()
      #@model.save()
      
  class NewFeedView extends BaseFeedView
    template: Templates.new_rss_feed
      
    createModel: ->
      new Models.RssFeed

    onSuccess: (model) ->
      MSGBUS.commands.execute 'rssfeed:create', model
      
  class EditFeedView extends BaseFeedView
    template: Templates.edit_rss_feed

    createModel: ->
      @model
      
    onSuccess: (model) ->
      MSGBUS.commands.execute 'rssfeed:update', model
      
      
  module.exports =
    FeedEntryView: FeedEntryView
    FeedListView: FeedListView
    FeedDataView: FeedDataView
    NewFeedView: NewFeedView
    EditFeedView: EditFeedView
    
    
  
    