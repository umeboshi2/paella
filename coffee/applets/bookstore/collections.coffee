define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  AppBus = require 'bookstore/msgbus'
  
  { Book } = require 'bookstore/models'
  
      

  ########################################
  # Collections
  ########################################

  class BookCollection extends Backbone.Collection
    model: Book
    url: '/'
    initialize: () ->
      #console.log "BOOKS INIT"
      AppBus.vent.on 'search:term', (term) =>
        @search term
      AppBus.vent.on 'search:more', () =>
        @moreBooks()
      # the number of books we fetch each time
      @maxResults = 40

      # the results "page" we last fetched
      @page = 0

      # flags whether the collection is currently in the
      # process of fetching
      # more results from the API (to avoid
      # multiple simultaneous calls
      @loading = false

      # remember the previous search
      @previousSearch = null

      # the maximum number of results for the previous search
      @totalItems = null

    search: (searchTerm) ->
      #console.log "BOOKS: Search"
      @page = 0
      @previousSearch = searchTerm

      @fetchBooks searchTerm, (books) =>
        if books.length < 1
          AppBus.vent.trigger 'search:noResults'
        else
          # a new search will reset/empty any existing items
          # in your collection
          @reset books

    moreBooks: () ->
      # if we've loaded all the books for this search,
      # there are no more to load !
      return true  if @length >= @totalItems
      @fetchBooks @previousSearch, (books) =>
        #add will append more items to our collection of books
        @add books

    fetchBooks: (searchTerm, callback) ->
      return true  if @loading
      @loading = true
      AppBus.vent.trigger "search:start"
      query = "#{encodeURIComponent(searchTerm)}&maxResults=#{@maxResults}&startIndex=#{(@page * @maxResults)}&fields=totalItems,items(id,volumeInfo/title,volumeInfo/subtitle,volumeInfo/authors,volumeInfo/publishedDate,volumeInfo/description,volumeInfo/imageLinks)"
      $.ajax
        url: "https://www.googleapis.com/books/v1/volumes"
        dataType: "jsonp"
        data: "q=#{query}" #"q=" + query
        success: (res) =>
          # success callback, don't forget to use
          # CoffeeScript FAT ARROW =>
          AppBus.vent.trigger "search:stop"
          if res.totalItems is 0
            callback []
            return []
          if res.items
            @page++
            @totalItems = res.totalItems
            searchResults = []
            _.each res.items, (item) ->
              thumbnail = null
              thumbnail = item.volumeInfo.imageLinks.thumbnail  if item.volumeInfo and item.volumeInfo.imageLinks and item.volumeInfo.imageLinks.thumbnail
              searchResults[searchResults.length] = new Book
                thumbnail: thumbnail
                title: item.volumeInfo.title
                subtitle: item.volumeInfo.subtitle
                description: item.volumeInfo.description
                googleId: item.id
            callback searchResults
            @loading = false
            searchResults  # returns searchresults
          else
            AppBus.vent.trigger "search:error"
            @loading = false
        error: =>
          #    again CS fat arrow so @loading refers to
          # proper this context (the collection)
          AppBus.vent.trigger "search:error"
          @loading = false

  # handle any "book:entities" requests
  AppBus.reqres.setHandler 'book:entities', ->
    new BookCollection
      
  module.exports =
    BookCollection: BookCollection
    
    
