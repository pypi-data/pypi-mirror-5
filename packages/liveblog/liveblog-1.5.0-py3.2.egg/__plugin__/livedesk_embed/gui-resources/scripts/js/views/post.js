define([
	'jquery',
	'gizmo/superdesk',
	'jquery/tmpl',
	'jquery/utils',
	'utils/encode_url',
	'tmpl!theme/item/base',
	'tmpl!theme/item/item',
	'tmpl!theme/item/annotated',
	'tmpl!theme/item/social-share',
	'tmpl!theme/item/posttype/normal',
	'tmpl!theme/item/posttype/image',
	'tmpl!theme/item/posttype/wrapup',
	'tmpl!theme/item/posttype/quote',
	'tmpl!theme/item/posttype/link',
	'tmpl!theme/item/posttype/advertisement',	
	'tmpl!theme/item/source/advertisement',	
	'tmpl!theme/item/source/google',
	'tmpl!theme/item/source/twitter',
	'tmpl!theme/item/source/facebook',
	'tmpl!theme/item/source/youtube',
	'tmpl!theme/item/source/flickr',
	'tmpl!theme/item/source/comments',
	'tmpl!theme/item/source/soundcloud',
	'tmpl!theme/item/source/instagram',
	'tmpl!theme/item/source/sms'
], function( $, Gizmo ) {
	return Gizmo.View.extend ({
		init: function()
		{
					var self = this;
					self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName';
					self.model
							.on('read update', function(evt, data){
									/**
									 * Quickfix.
									 * @TODO: make the isCollectionDelete check in gizmo before triggering the update.
									 */
					   				if( self._parent.model.get('PostPublished').isCollectionDeleted(self.model) )
										return;
									//console.log('this.data: ',$.extend({},this.data), ' is only:' ,isOnly(this.data, ['CId','Order']));
									/*if(isOnly(this.data, ['CId','Order']) || isOnly(data, ['CId','Order'])) {
											console.log('this.data: ',$.extend({},this.data));
											console.log('data: ',$.extend({}, data));
											console.log('force');
											self.model.xfilter(self.xfilter).sync({force: true});
									}
									else*/
									{
										self.render(evt, data);
									}
							})
							.on('delete', self.remove, self)
							.xfilter(self.xfilter)
							.sync();
		},
		remove: function(evt)
		{
			var self = this;
			self._parent.removeOne(self);
			self.el.remove();
			self.model.off('read update delete');
			return self;			
		},
		toggleWrap: function(e, forceToggle) {
			if (typeof forceToggle != 'boolean' ) {
				forceToggle = false;
			}
			this._toggleWrap($(e).closest('li').first(), forceToggle);
		},
		_toggleWrap: function(item, forceToggle) {
			if (typeof forceToggle != 'boolean' ) {
				forceToggle = false;
			}
			if (item.hasClass('open')) {
				var collapse = true;
				if ( collapse ) {
					item.removeClass('open').addClass('closed');
					item.nextUntil('.wrapup,#loading-more').hide();
				} else {
					//don't collapse wrap'
				}
			} else {
				item.removeClass('closed').addClass('open');
				item.nextUntil('.wrapup,#loading-more').show();
			}
		},		
		render: function(evt, data)
		{
			var self = this, 
				data = self.model.feed(),
				order = parseFloat(self.model.get('Order')),
				regexHash, newHash, createdOn;
			if ( !isNaN(self.order) && (order != self.order)) {
				self._parent.orderOne(self);
			}
			data.HashIdentifier = self._parent.hashIdentifier;
			if(data.Meta) {
				data.Meta = JSON.parse(data.Meta);
			}
			if(data.Meta && data.Meta.annotation) {
				if(data.Meta.annotation[1] === null) {
					data.Meta.annotation = data.Meta.annotation[0];
					data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
				}
				if ( typeof data.Meta.annotation !== 'string') {
					if(data.Meta.annotation[0]) {
						var aux = data.Meta.annotation;
						data.Meta.annotation = {
							'before': $.trimTag(['<br>', '<br />'], aux[0]), 
							'after': $.trimTag(['<br>', '<br />'], aux[1])
						}
					} else {
						data.Meta.annotation = {
							'before': $.trimTag(['<br>', '<br />'], data.Meta.annotation.before), 
							'after': $.trimTag(['<br>', '<br />'], data.Meta.annotation.after)
						}					
					}
				} else {
					data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
				}
			}
			newHash = self._parent.hashIdentifier + data.Order;
			if(self._parent.location.indexOf('?') === -1) {
				data.permalink = self._parent.location + '?' + newHash ;
			} else if(self._parent.location.indexOf(self._parent.hashIdentifier) !== -1) {
				regexHash = new RegExp(self._parent.hashIdentifier+'[^&]*');
				data.permalink = self._parent.location.replace(regexHash,newHash);
			} else {
				data.permalink = self._parent.location + '&' + newHash;
			}
			if(data.Author.Source.IsModifiable ===  'True' || data.Author.Source.Name === 'internal') {
				data.item = "posttype/"+data.Type.Key;
			}
			else if(data.Type)
				data.item = "source/"+data.Author.Source.Name;
			if(data.CreatedOn) {
				createdOn = new Date(Date.parse(data.CreatedOn));
				data.CreatedOn = createdOn.format(_('mm/dd/yyyy HH:MM o'));
				data.CreatedOnISO = createdOn.getTime();
			}
			if(data.PublishedOn) {
				publishedOn = new Date(Date.parse(data.PublishedOn));
				data.PublishedOn = publishedOn.format(_('mm/dd/yyyy HH:MM o'));
				data.PublishedOnISO = publishedOn.getTime();
			}
			if(data.Content) {
				data.Content = data.Content.replace(livedesk.server(),livedesk.FrontendServer);
			}
			if( (data.item === "source/comments") && data.Meta && data.Meta.AuthorName ) {
				var cleanName = data.Meta.AuthorName.replace('commentator','');
				data.Meta.AuthorName = _('%(full_name)s commentator').format({"full_name": cleanName});
			}
			//console.log(data);
			$.tmpl('theme/item/item',data, function(e, o){
				if(!e) {
					self.setElement(o);
					var input = $('input[data-type="permalink"]',self.el);
					$('a[rel="bookmark"]', self.el).on(self.getEvent('click'), function(evt) {
						evt.preventDefault();
						if(input.css('visibility') === 'visible') {
							input.css('visibility', 'hidden' );
						} else {
							input.css('visibility', 'visible' );
							input.trigger(self.getEvent('focus'));
							$('.result-header .share-box', self.el).fadeOut('fast');
						}
						
					});
					input.on(self.getEvent('focus')+' '+self.getEvent('click'), function() {
						$(this).select();
					});
					$('.big-toggle', self.el).off( self.getEvent('click') ).on(self.getEvent('click'), function(){
						self.toggleWrap(this, true);
					});

					var li = $('.result-header', self.el).parent();
					li.hover(function(){
						//hover in
					}, function(){
						$(this).find('.share-box').fadeOut(100);
						$('input[data-type="permalink"]', self.el).css('visibility', 'hidden');
					});

					var sharelink = $('.sf-share', self.el);
					sharelink.on(self.getEvent('click'), function(evt){
					    evt.preventDefault();
						var share = $(this);
						var added = share.attr('data-added');
						if ( added != 'yes') {
							var blogTitle = encodeURL(self._parent.model.get('Title'));
							var myPerm = encodeURL(data.permalink);
							var imgSrc = $('.result-content img:first', self.el).attr('src');
							var mediaSrc = '';
							var showPin = false;
							if ( imgSrc ) {
								var imgObj = new Image();
								imgObj.src = imgSrc;
								if ( imgObj.width >= 100 && imgObj.height >= 200 ) {
									mediaSrc = imgSrc;
									showPin = true;
								}
							}
							if ( !showPin ) {
								var ifrSrc = $('iframe', self.el).attr('src');
								if ( ifrSrc ) {
									ifrSrc = ifrSrc.toString();
									if ( ifrSrc.indexOf("youtube") != -1) {
										mediaSrc = data.Meta.thumbnail.hqDefault;
										showPin = true;
									}	
								}
							}
							var summary = encodeURL($('.result-content .result-text:last', self.el).text());
							var pinurl = "http://pinterest.com/pin/create/button/?url=" + myPerm + "&media=" + mediaSrc + "&description=" + blogTitle;
							var gglurl = "https://plus.google.com/share?url=" + myPerm + "&t=";
							var emailurl = "mailto:?to=&subject=" + _('Check out this Live Blog') + "&body=" + myPerm;
							var fburl = "http://www.facebook.com/sharer.php?s=100";
							fburl += '&p[title]=' + blogTitle;
							fburl += '&p[summary]=' + summary;
							fburl += '&p[url]=' + myPerm;
							var i = 0;
							$('.result-content img', self.el).each(function(){
								var src = $(this).attr('src');
								fburl += '&p[images][' + i + ']=' + src;
								i ++;
							});
							

							var socialParams = {
								'fbclick': "$.socialShareWindow('" + fburl + "',400,570); return false;",
								'twtclick': "$.socialShareWindow('http://twitter.com/home?status=" + _('Now reading ') + blogTitle + ": " + myPerm + "',400,570); return false;",
								'linclick': "$.socialShareWindow('http://www.linkedin.com/shareArticle?mini=true&url=" + myPerm + "&title=" +  blogTitle + "&summary=" + summary + "', 400, 570); return false;",
								'pinclick': "$.socialShareWindow('" + pinurl + "', 400, 700); return false;",
								'gglclick': "$.socialShareWindow('" + gglurl + "', 400, 570); return false;",
								'emailclick': "$.socialShareWindow('" + emailurl + "', 1024, 768); return false;",
								'emailurl': emailurl,
								'showPin': showPin
							}
							$.tmpl('theme/item/social-share', socialParams, function(e, o){
								share.after(o);
								share.attr('data-added', 'yes');	
							});
						}
						$('input[data-type="permalink"]', self.el).css('visibility', 'hidden');
						$(this).next('.share-box').toggle();
					})
				} else {
					console.error(e);
				}
			});
			setTimeout(function(){
				/*
				$.tmpl('theme/item/social-share', {'permalink': data.permalink}, function(e, o){
					$('.sf-share[data-shared!="yes"]').on('click', function(){
						var share = $(this);
						var added = share.attr('data-added');
						if ( added != 'yes') {
							var url = share.attr('data-added');
							share.after(o);
							share.attr('data-added', 'yes');
						}
						$(this).next('.share-box').toggle();
					});
				});	
				*/
			});
					
		}
	});
});