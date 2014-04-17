# modular template loading
define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  teacup = require 'teacup'

  renderable = teacup.renderable

  div = teacup.div
  # I use "icon" for font-awesome
  icon = teacup.i
  strong = teacup.strong
  span = teacup.span
  label = teacup.label
  input = teacup.input

  text = teacup.text
  img = teacup.img
  # Main Templates must use teacup.
  # The template must be a teacup.renderable, 
  # and accept a layout model as an argument.

  # Tagnames to be used in the template.
  {div, span, link, text, strong, label, input, 
  button, a, nav, form, p,
  ul, li, b,
  h1, h2, h3,
  subtitle, section, hr
  } = teacup
            
    
  ########################################
  # Templates
  ########################################
  rss_feed_entry = renderable (feed) ->
    div '.listview-list-entry', ->
      span '.btn-default.btn-xs', ->
        a href:'#simplerss/editfeed/' + feed.id,
        style:'color:black', ->
          icon '.edit-feed.fa.fa-pencil'
      text "    "
      a href:'#simplerss/showfeed/' + feed.id, feed.name
        

  rss_feed_list = renderable (header) ->
    div '.listview-header', "RSS Feeds"
    div '.rss-feedlist.listview-list'

  rss_feed_form = renderable (feed, btntxt) ->
    div '.form-group', ->
      label '.control-label', for:'input_name', 'Feed Name'
      input '#input_name.form-control',
      name:'name', 'data-validation':'name',
      placeholder:feed.name, value:feed.name
    div '.form-group', ->
      label '.control-label', for:'input_url', 'Url'
      input '#input_url.form-control',
      name:'url', 'data-validation':'url',
      placeholder:feed.url, value:feed.url
    input '.btn.btn-default.btn-xs', type:'submit', value:btntxt
    
  new_rss_feed = (feed) ->
    rss_feed_form(feed, 'Submit New Feed')

  edit_rss_feed = (feed) ->
    rss_feed_form(feed, 'Update Rss Feed')
    
        
  viewfeed = renderable (data) ->
    div '.listview-header', ->
      text data.feed.title
    div '.listview-list', ->
      for entry in data.entries
        div '.listview-list-entry', ->
          div ->
            a '.rssviewer-viewfeed-entry-link',
            href:entry.link, entry.title
          div ->
            teacup.raw entry.summary
            
  ##################################################################
  # ##########################
  ##################################################################    
          
  module.exports =
    rss_feed_entry: rss_feed_entry
    rss_feed_list: rss_feed_list
    new_rss_feed: new_rss_feed
    edit_rss_feed: edit_rss_feed
    viewfeed: viewfeed
    
    
