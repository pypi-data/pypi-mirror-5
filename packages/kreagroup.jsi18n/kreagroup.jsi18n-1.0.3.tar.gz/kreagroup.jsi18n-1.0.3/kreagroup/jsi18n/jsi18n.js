/*
   @see jarn/jsi18n/jsi18n.js
        (jarn.jsi18n-1.0-py2.7.egg)
 */

/*global $:false, window:false, portal_url:false, jarn:false, jQuery:false, localStorage:false, */

(function (jarn, $) {

    jarn.i18n = {

        storage: null,
        catalogs: {},
        currentLanguage: null,
        ttl: 24 * 3600 * 1000,

        init: function () {
            // @added
            // Internet Explorer 8 does not know Date.now() which is used in
            // e.g. loadCatalog, so we "define" it here...
            if (!Date.now) {
                Date.now = function() {
                    return new Date().valueOf();
                }
            }

            jarn.i18n.currentLanguage = $('html').attr('lang');
            try {
                if ('localStorage' in window && window.localStorage !== null && 'JSON' in window && window.JSON !== null) {
                    jarn.i18n.storage = localStorage;
                }
            } catch (e) {}
        },

        setTTL: function (millis) {
            jarn.i18n.ttl = millis;
        },

        _setCatalog: function (domain, language, catalog) {
            if (domain in jarn.i18n.catalogs) {
                jarn.i18n.catalogs[domain][language] = catalog;
            } else {
                jarn.i18n.catalogs[domain] = {};
                jarn.i18n.catalogs[domain][language] = catalog;
            }
        },

        _storeCatalog: function (domain, language, catalog) {
            var key = domain + '-' + language;
            if (jarn.i18n.storage !== null &&
                catalog !== null) {
                jarn.i18n.storage.setItem(key, JSON.stringify(catalog));
                jarn.i18n.storage.setItem(key + '-updated', Date.now());
            }
        },

        loadCatalog: function (domain, language) {
            if (typeof (language) === 'undefined') {
                language = jarn.i18n.currentLanguage;
            }
            if (jarn.i18n.storage !== null) {
                var key = domain + '-' + language;
                if (key in jarn.i18n.storage) {
                    if ((Date.now() - parseInt(jarn.i18n.storage.getItem(key + '-updated'), 10)) < jarn.i18n.ttl) {
                        var catalog = JSON.parse(jarn.i18n.storage.getItem(key));
                        jarn.i18n._setCatalog(domain, language, catalog);
                        return;
                    }
                }
            }
            /*
             @changed load catalog synchronous, because otherwise, the first
                      time a page loads which uses jarn.jsi18n, there is a big
                      chance the i18n does not work, although the second page
                      (and next ones) of the same plone site do work. If you do
                      e.g.:

                          jarn.i18n.loadCatalog('plone', 'es');
                          _es = jarn.i18n.MessageFactory('plone', 'es');
                          _es('Contributor');

                      It is possible the loadCatalog is still downloading the
                      catalog via the asynchronous getJSON, while the
                      _es('Contributor') is already executed, and therefor,
                      'Contributor' is not translated...

             @remark Synchronous loading of data is NOT a good solution, but it
                     makes i18n work in every use case...
             */

            // @added
            $.ajax({url: portal_url + '/jsi18n?' +
                'domain=' + domain + '&language=' + language,
                async: false,
                datatype: 'json',
                success: function (catalog) {
                    if (catalog === null) {
                        return;
                    }
                    jarn.i18n._setCatalog(domain, language, catalog);
                    jarn.i18n._storeCatalog(domain, language, catalog);
                }});
            /* @removed
            $.getJSON(portal_url + '/jsi18n?' +
                'domain=' + domain + '&language=' + language,
                function (catalog) {
                    if (catalog === null) {
                        return;
                    }
                    jarn.i18n._setCatalog(domain, language, catalog);
                    jarn.i18n._storeCatalog(domain, language, catalog);
                });
            */
        },

        MessageFactory: function (domain, language) {
            language = language || jarn.i18n.currentLanguage;

            return function translate (msgid, keywords) {
                var msgstr;
                if ((domain in jarn.i18n.catalogs) && (language in jarn.i18n.catalogs[domain]) && (msgid in jarn.i18n.catalogs[domain][language])) {
                    msgstr = jarn.i18n.catalogs[domain][language][msgid];
                } else {
                    msgstr = msgid;
                }
                if (keywords) {
                    var regexp, keyword;
                    for (keyword in keywords) {
                        if (keywords.hasOwnProperty(keyword)) {
                            regexp = RegExp("\\$\\{" + keyword + '\\}', 'g');
                            msgstr = msgstr.replace(regexp, keywords[keyword]);
                        }
                    }
                }
                return msgstr;
            };
        }
    };

    jarn.i18n.init();

})(window.jarn = window.jarn || {}, jQuery);
