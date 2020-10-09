
import $ from "jquery";
import i18next from 'i18next';
import jqueryI18next from 'jquery-i18next';
import HttpApi from 'i18next-http-backend';


export default () => {
    var language = 'en'

    if (getCookie("_lang") !== '') {
        language = getCookie("_lang")
    }

    i18next
        .use(HttpApi)
        .init({
            debug: true,
            lng: language,
            fallbackLng: 'en',
            backend: {
                loadPath: '/themes/core/static/locales/{{ lng }}/translation.json',
            },
        }, function () {
            jqueryI18next.init(i18next, $);
            $('html').localize();
        }
        );

    i18next.on('languageChanged', () => {
        jqueryI18next.init(i18next, $);
        $('html').localize();
    });

    $("#en-switch").click(function () {
        switchLanguage('en');
    });

    $("#sl-switch").click(function () {
        switchLanguage('sl');
    });

    function switchLanguage(newLang) {
        var cookie = '_lang=' + newLang + ';'
        document.cookie = cookie
        i18next.changeLanguage(newLang, (err, t) => {
            if (err) {
                console.log('something went wrong loading translations', err);
                return null;
            }
            t('key');
        });
    }

    function getCookie(cname) {
        var name = cname + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    }
};



