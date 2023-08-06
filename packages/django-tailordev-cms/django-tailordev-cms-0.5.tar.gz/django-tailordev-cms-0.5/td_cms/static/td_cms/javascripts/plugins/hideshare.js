/*

  2013, Nov. 3

  TailorDev fork of the hideshare original plugin to make it compatible
  with zurb foundation basements.
  */

/*! hideshare - v0.1.0 - 2013-09-11
* https://github.com/arnonate/jQuery-FASS-Widget
* Copyright (c) 2013 Nate Arnold; Licensed MIT */
/* ========================================================================
 * HIDESHARE v1.0.0
 * https://github.com/arnonate/hideshare
 * ========================================================================

  Copyright (c) 2013 Nate Arnold

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation
  files (the "Software"), to deal in the Software without
  restriction, including without limitation the rights to use,
  copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.
  */

;(function(window, $) {

    "use strict";

    // HIDESHARE PUBLIC CLASS DEFINITION
    // =================================

    var Hideshare = function (elem, options) {
      this.elem = elem;
      this.$elem = $(elem);
      this.options = options;
    };

    Hideshare.prototype = {
        defaults: {
            link: document.URL,
            title: document.title,
            media: null,
            facebook: true,
            twitter: true,
            pinterest: true,
            googleplus: true,
            linkedin: true,
        },

        init: function() {
            this.config = $.extend({}, this.defaults, this.options);
            this.wrapHideshare();
            return this;
        },

        wrapHideshare: function() {
            var output = output,
            width = this.$elem.outerWidth(),
            height = this.$elem.outerHeight(),
            shareTitle = this.config.title,
            shareLink = this.config.link,
            shareMedia = this.config.media,
            facebookTemplate = '<li><a class="hideshare-facebook" href="#"><i class="social sfoundicon-facebook"></i><span>Facebook</span></a></li>',
            twitterTemplate = '<li><a class="hideshare-twitter" href="#"><i class="social sfoundicon-twitter"></i><span>Twitter</span></a></li>',
            pinterestTemplate = '<li><a class="hideshare-pinterest" href="#" data-pin-do="buttonPin" data-pin-config="above"><i class="social sfoundicon-pinterest"></i><span>Pinterest</span></a></li>',
            googleplusTemplate = '<li><a class="hideshare-google-plus" href="#"><i class="social sfoundicon-google-plus"></i><span>Google Plus</span></a></li>',
            linkedinTemplate = '<li><a class="hideshare-linkedin" href="#"><i class="social sfoundicon-linkedin"></i><span>Linked In</span></a></li>';

            output = "";

            if (this.config.facebook) {
                output += facebookTemplate;
            }
            if (this.config.twitter) {
                output += twitterTemplate;
            }
            if (this.config.pinterest) {
                output += pinterestTemplate;
            }
            if (this.config.googleplus) {
                output += googleplusTemplate;
            }
            if (this.config.linkedin) {
                output += linkedinTemplate;
            }

            // Construct sharing list
            var hideshareList = '<ul id="hideshare-list">' + output + '</ul>';

            // Wrap button
            this.$elem.addClass("hideshare-btn").wrap("<div class='hideshare-wrap' />");

            // Insert sharing button list
            $(hideshareList).insertAfter(this.$elem);

            // SHARING FUNCTIONS
            var shareFacebook = function() {
                window.open('//www.facebook.com/share.php?u=' + encodeURIComponent(shareLink),'Facebook','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
            };
            var shareTwitter = function() {
                window.open('//twitter.com/home?status=' + encodeURIComponent(shareTitle) + '+' + encodeURIComponent(shareLink),'Twitter','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
            };
            var sharePinterest = function() {
                window.open('//pinterest.com/pin/create/button/?url=' + encodeURIComponent(shareLink) + '&media=' + encodeURIComponent(shareMedia) + '&description=' + encodeURIComponent(shareTitle),'Pinterest','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
            };
            var shareGooglePlus = function() {
                window.open('//plus.google.com/share?url=' + encodeURIComponent(shareLink),'GooglePlus','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
            };
            var shareLinkedIn = function() {
                window.open('//www.linkedin.com/shareArticle?mini=true&url=' + encodeURIComponent(shareLink) + '&title=' + encodeURIComponent(shareTitle) + '&source=' + encodeURIComponent(shareLink),'LinkedIn','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
            };

            $(".hideshare-facebook").click(function() {
                shareFacebook();
                return false;
            });

            $(".hideshare-twitter").click(function() {
                shareTwitter();
                return false;
            });

            $(".hideshare-pinterest").click(function() {
                sharePinterest();
                return false;
            });

            $(".hideshare-google-plus").click(function() {
                shareGooglePlus();
                return false;
            });

            $(".hideshare-linkedin").click(function() {
                shareLinkedIn();
                return false;
            });
        }
    };

    Hideshare.defaults = Hideshare.prototype.defaults;

    $.fn.hideshare = function(options) {
        return this.each(function() {
            new Hideshare(this, options).init();
      });
    };

    window.Hideshare = Hideshare;

})(window, jQuery);
