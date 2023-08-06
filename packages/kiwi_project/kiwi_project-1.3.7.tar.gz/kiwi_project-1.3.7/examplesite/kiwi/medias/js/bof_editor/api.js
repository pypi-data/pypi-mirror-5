/*
BOF Editor
Initially based on the code of the jQuery plugin : fullTextArea
Developed and designed by Thenon David
www.sveetch.biz

BOF API 0.9.6

This script is part of BOF Editor. 

Requires :

    * jQuery library >= 1.3.2

Le BOF editor est à utiliser de la façon suivante :

  $('#montextarea').BOF_Editor(options);

L'argument 'options' est facultatif, si il est spécifié ce doit être un hash {} (ou objet 
anonyme) contenant les options par défaut à écraser selon vos besoins :

* root_padding: détermine l'espacement intérieur du bloc principale de 
  l'éditeur, 10px par défaut. Cette valeur est à spécifier en option comme un nombre et 
  toujours utilisée en interne avec une unité de pixel.

* mode: Si "focus" l'éditeur s'ouvrira dès le clic dans le textarea; Si mode "button", 
  un bouton lien sera ajouté juste en dessous le textarea, son 
  clic ouvrira l'éditeur. Si vous passez directement un objet jQuery dans cette 
  option, le clic sur cet objet sera utilisé comme évènement déclencheur. Par défaut 
  le mode 'focus' est utilisé.

* background_scroll_autorestore: Active la restauration de la position verticale de 
  l'ascenceur avant que l'éditeur ne s'ouvre. Cette option est activée par défaut. En 
  théorie il n'est pas utile de se préoccuper de cette option mais dans certains cas 
  particuliers d'intégration, elle peut gêner avec d'autres composants, dans ce cas il 
  faudra la désactiver et la récupération du scroll sera à votre charge (par exemple dans 
  le callback d'alerte)

* with_wikibar: insère une wikibar sur le champs de l'éditeur. Désactivé par défaut.

* wikibar_options: Permet de forcer des options de la wikibar (et écraser celle par 
  défaut de l'éditeur), voyez l'API de la wikibar pour plus de détails sur les options 
  disponibles.

* syntax_help: Attends un URL vers la page d'aide qui sera inséré dans l'éditeur comme 
  référence d'aide de la syntaxe disponible de l'éditeur. Option désactivée par défaut, 
  donc aucun lien d'aide n'est affiché.

* url_preview: si 'false', pas de preview et pas de menu d'onglets; si il est 
  renseigné ce doit être une chaine de caractère contenant un lien auquel 
  envoyer le contenu à prévisualiser. L'envoi se fait via un POST, le contenu 
  est dans un attribut "source" et l'éditeur attend en retour une réponse html 
  contenant directement le rendu de la prévisualisation. Option désactivée par défaut.

* with_alert: si true, un message automatique sera affiché au dessous du champs 
  ciblé lorsque l'utilisateur accepte le contenu modifié dans l'éditeur. Si false 
  ne fait rien. La valeure de cette option peut aussi etre une fonction qui sera 
  appelée au moment à l'acceptation. Pour plus de détails sur cette fonction 
  regardez "jQuery.fn.BOF_Editor.create_alert"

* alert_position: dans le cas de with_alert=true, permet de choisir si le 
  message sera affiché au dessus ('top') ou bien alors en 
  dessous ('bottom'). Par défaut l'option contient 'top'.

* unique_id: Chaîne de texte unique à l'instance de l'éditeur qui est rajoutée en 
  suffixe des attributs "id" de certains éléments de l'éditeur. Ceci afin de gérer de 
  multiples instances de l'éditeur dans un même document. Par défaut cette option est 
  remplie automatiquement par un timestamp, donc en général il est inutile de s'en 
  préoccuper.

* csrf_token: Chaîne de texte du nom de cookie à lire pour y récupérer la chaîne unique 
  "csrf_token" utilisé par Django >= 1.2.x pour sécuriser les requêtes POST. Ce n'est 
  utilisé que dans le cas de la prévisualisation donc de même désactivé par défaut, mais 
  il est en général obligatoire si vous activez la prévisualisation dans le cadre d'une 
  webapp Django.

Toute les autres options commencant par "i18_" sont des chaines de textes que 
vous pouver modifier pour changer les textes ou les traduires dans une autre 
langue.
*/
jQuery.fn.BOF_Editor = function(options) {
    
    // Options par défauts
    var defaults = {
        'root_padding': 10,
        'mode': 'focus',
        'background_scroll_autorestore': true,
        'with_wikibar': false,
        'syntax_help': false,
        'wikibar_options': {},
        'url_preview': false,
        'with_alert': false,
        'alert_position': "top",
        'unique_id': +new Date,
        'url_preview': false,
        'csrf_token': false,
        // Chaines de texte
        'i18n_alert_message': "Ce texte a été modifié, n'oubliez pas de sauvegarder vos modifications.",
        'i18n_opener_button': "Ouvrir l'éditeur",
        'i18n_tab_form': "Formulaire",
        'i18n_tab_preview': "Prévisualisation",
        'i18n_button_accept': "Accepter",
        'i18n_button_cancel': "Annuler",
        'i18n_button_close': "Fermer",
        'i18n_syntax_help': "Aide sur la syntaxe wiki"
    };
    // Gestion des options envoyés
    var opts = jQuery.extend(defaults, options);

    // Ouverture de la scène avec le focus sur l'input ciblé
    if(opts.mode == 'focus') {
        return this.each(function(){
            jQuery(this).focus(Main);
        });
    // Ouverture avec le clic sur un bouton automatiquement généré
    } else if(opts.mode == 'button') {
        return this.each(function(){
            var obj = this;
            jQuery.fn.BOF_Editor.create_opener_button(this, opts.i18n_opener_button).click(function() {
                Main(null, obj);
                return false;
            });
        });
    // Ouverture avec le clic sur l'objet jQuery donné directement
    } else {
        return this.each(function(){
            var obj = this;
            opts.mode.click(function() {
                Main(null, obj);
                return false;
            });
        });
    }
    
    /*
    ** Créé une nouvelle scène en avant avec un fond opaque de séparation 
    ** visuelle
    **
    ** @e : evenement donné par jQuery avec un appel du genre focus(), 
    ** mettre null si il est appelé directement
    ** @elem: qu'on appele la méthode directement (et non via un evenement 
    ** comme focus/click/etc..) on doit donner l'objet ciblé
    */
    function Main(e, elem) {
        var obj;
        var overlay;
        var scene;
        var root_container;
        var form_container;
        var preview_container;
        var textarea;
        var textarea_height;
        var fixed_visible_element_height = 0;
        var fixed_hidable_element_height = 0;
        var save;
        var cancel;
        var undefined;
        if (elem == undefined){
            obj = this;
        } else {
            obj = elem;
        }
        
        // On vérifie que l'éditeur n'est pas déja ouvert, par sécurité et pour 
        // contrer un bug Safari
        if( DoesExists() ) {
            return;
        }
        
        // Gestion du redimensionnement de l'éditeur lors du redimensionnement de la 
        // fenêtre du navigateur
        jQuery(window).bind('resize', resize);

        // Enregistre la position de l'ascenceur vertical
        if(opts.background_scroll_autorestore == true){
            save_scroll_position('window_scroll_position');
        }
        
        // Empeche le scroll en dehors de la scène
        jQuery("body","html").css({'height':"100%", 'width':"100%"});
        jQuery("html").css('overflow',"hidden");
        
        // Fond opaque de séparation des scènes 
        overlay = jQuery('<div>').css({
            'position':"absolute",
            'z-index':200,
            'left':0,
            'top':jQuery(window).scrollTop(),
            'width': jQuery(window).width(),
            'height': jQuery(window).height(),
            'background-color': "black",
            'opacity': '0.7',
            'display': "none"
        });
        jQuery("body").append(overlay);
        
        // La scène de l'éditeur
        scene = jQuery('<div>').css({
            'position': "absolute",
            'z-index': 202,
            'left': 0,
            'top': jQuery(window).scrollTop(),
            'width': jQuery(window).width(),
            'height': jQuery(window).height(),
            'background-color': "transparent"
        }).attr('id', "ui_EEditor_scene");
        // Contrôle de la touche ESC pour fermer l'éditeur
        jQuery(scene).keydown( function(e){
            if(e.keyCode == '27'){
                close_scene();
                return false;
            }
            return true;
        });
        // Ajoute la scène dans le html à la fin du <body/>
        jQuery("body").append(scene);
        
        // Conteneur principal des éléménts de la scène
        root_container = jQuery('<div>').css({
            'position': "absolute",
            'z-index': 204,
            'width': (jQuery(window).width()*0.9)-(opts.root_padding*2),
            'height': jQuery(window).height()*0.93,
            'left': jQuery(window).width()*0.05,
            'top': jQuery(window).height()*0.02,
            'padding': opts.root_padding+'px'
        }).attr('id', "ui_EEditor_root_container");
        jQuery(scene).append(root_container);
        // Hauteur de base disponible au textarea
        textarea_height = root_container.outerHeight();
        
        // Contenu du textarea qui remplit toute la scène moins la place pour 
        // le ou les outils de l'interfaces
        form_container = jQuery('<div>').attr('id', "ui_EEditor_form").css({'display': "block"});
        root_container.append(form_container);

        // Menu d'onglet si la preview est activée
        if (opts.url_preview){
            get_tabs();
        }
        // Le champs de texte et ses boutons
        get_editor();
        // La wikibar optionnelle
        if (opts.with_wikibar){
            get_wikibar();
        }
        
        // Protection de la scène
        protect_scene();
        
        // Une petite animation d'opacité pour le fond semi-opaque de la scène
        overlay.fadeIn("fast");
        
        
        /*
        / Vérifie que l'éditeur est bien ouvert
        */
        function DoesExists() {
            if( jQuery("#ui_EEditor_scene").length > 0 ) {
                return true;
            }
            return false;
        };
        /*
        / Insère un menu d'onglets pour la preview
        */
        function get_tabs() {
            // Cadre du bouton pour fermer l'éditeur
            var closebutton_container = jQuery('<div id="ui_EEditor_closebutton_layer">'+
                '<a id="ui_EEditor_closebutton_link" title="'+ opts.i18n_button_close +'" href="#"><span>'+ opts.i18n_button_close +'</span></a>'+
            '</div>').css({
                'position': "absolute",
                'z-index': 205,
                'top': jQuery(window).height()*0.02,
                'right': opts.root_padding
            });
            var closebutton_layer = root_container.prepend(closebutton_container);
            jQuery("#ui_EEditor_closebutton_link").click(function() {
                close_scene();
                return false;
            });
            // Mise à jour de la hauteur de base disponible au textarea
            textarea_height += -jQuery('#ui_EEditor_closebutton_layer').outerHeight();
            fixed_visible_element_height += -jQuery('#ui_EEditor_closebutton_layer').outerHeight();
            
            // Cadre du menu d'onglets
            var menu_tab = root_container.prepend('<div id="ui_EEditor_tabs"><ul>'+
                '<li id="ui_EEditor_tab_form" class="active"><span>'+ opts.i18n_tab_form +'</span></li>'+
                '<li id="ui_EEditor_tab_preview"><span>'+ opts.i18n_tab_preview +'</span></li>'+
            '</ul><div class="cale"></div></div>');
            // Mise à jour de la hauteur de base disponible au textarea
            textarea_height += -jQuery('#ui_EEditor_tabs').outerHeight();
            fixed_visible_element_height += -jQuery('#ui_EEditor_tabs').outerHeight();
            
            // Contenu de la preview, caché et vide par défaut
            preview_container = jQuery('<div>').css({
                'width': (jQuery(window).width()*0.9)-(opts.root_padding*3),
                'height': textarea_height-(opts.root_padding*3),
                'overflow': "auto",
                'display': "none",
                'padding': (opts.root_padding/2)+'px'
            }).attr('id', "ui_EEditor_preview").hide();
            root_container.append(preview_container);
            
            // Clic sur l'onglet du formulaire de l'éditeur
            jQuery("#ui_EEditor_tab_form span").click(function() {
                if( jQuery(this).parent().hasClass('active') ){
                    return false;
                }
                jQuery("#ui_EEditor_preview").hide();
                jQuery("#ui_EEditor_tab_preview").removeClass("active");
                jQuery("#ui_EEditor_form").show();
                jQuery("#ui_EEditor_tab_form").addClass("active");
                jQuery("#ui_EEditor_preview div.wiki2xhtml").remove();
                restore_scroll_position('textarea_scroll_position', jQuery('#ui_EEditor_textarea'), jQuery('#ui_EEditor_scene'));
            });
            // Clic sur l'onglet de prévisualisation
            jQuery("#ui_EEditor_tab_preview span").click(function() {
                if( jQuery(this).parent().hasClass('active') ){
                    return false;
                }
                save_scroll_position('textarea_scroll_position', jQuery('#ui_EEditor_textarea'), jQuery('#ui_EEditor_scene'));
                jQuery("#ui_EEditor_form").hide();
                jQuery("#ui_EEditor_tab_form").removeClass("active");
                jQuery("#ui_EEditor_preview").show();
                jQuery("#ui_EEditor_tab_preview").addClass("active");
                jQuery("#ui_EEditor_preview div.wiki2xhtml").remove();
                // Requête AJAX pour récuper la preview html du texte
                request_headers = {};
                if(opts.csrf_token) {
                    request_headers["X-CSRFToken"] = getCookie(opts.csrf_token);
                };
                jQuery.ajax({
                    type: "POST",
                    global: false,
                    dataType: "html",
                    url: opts.url_preview,
                    headers: request_headers,
                    data: {
                        "nocache": (new Date()).getTime(),
                        "source": textarea.val()
                    },
                    success: function( htmlNode ){
                        jQuery('#ui_EEditor_preview').append(
                            jQuery('<div>').attr('class', "wiki2xhtml").append(htmlNode)
                        );
                        jQuery("#ui_EEditor_preview div.wiki2xhtml a").click(function(){
                            try { window.open(jQuery(this).attr('href')) } catch (e) { } return false;
                        });
                    }
                });
            });
        };
        
        /*
        / Clone le textarea original et l'introduit avec les bonnes dimensions 
        / dans le container dédié
        */
        function get_editor() {
            // Bouton de confirmation et annulation
            var buttons_container = jQuery('<div>').attr({ 'class': "buttons" });
            form_container.append(buttons_container);
            save = jQuery('<input>').attr({
                'type': "button",
                'value': opts.i18n_button_accept
            }).css({'width':"45%", 'margin-right':"9%"}).addClass("button_save");
            buttons_container.append(save);
            cancel = jQuery('<input>').attr({
                'type': "button",
                'value': opts.i18n_button_cancel
            }).css({'width':"45%"}).addClass("button_cancel");
            buttons_container.append(cancel);
            
            // Pour les paddins amassés le long du parcours
            textarea_height += -(opts.root_padding*3);
            textarea_height += -opts.root_padding;
            textarea_height += -buttons_container.outerHeight();
            fixed_hidable_element_height += -jQuery('#ui_EEditor_form div.buttons').outerHeight();
            // Clone du textarea de base avec des dimensions qui remplissent 
            // tout le vide de la scène, on change seulement l'id pour qu'il 
            // n'y ait pas de conflit
            textarea = jQuery(obj).clone().css({
                'width': (root_container.width()*1.0)-(opts.root_padding*2),
                'height': textarea_height
            }).attr('id', 'ui_EEditor_textarea').val( jQuery(obj).val() );
            // On le rajoute AVANT les boutons
            buttons_container.before( textarea );
            // Déplace le focus sur le clone
            jQuery(textarea).focus();
            
            // Evènements sur les boutons
            jQuery(cancel).click(function() {
                // Vire la scène sans rien modifier de l'original
                close_scene();
                return false;
            });   
            jQuery(save).click(function() {
                var original = jQuery(obj).val();
                var edited = jQuery(textarea).val();
                // Met à jour l'original avec le contenu modifié et vire la 
                // scène
                jQuery(obj).val(edited);
                close_scene();
                // Témoin de modification
                if(opts.with_alert == true) {
                    jQuery.fn.BOF_Editor.create_alert(obj, opts, original, edited);
                } else if ( jQuery.isFunction( opts.with_alert ) ) {
                    opts.with_alert(obj, opts, original, edited);
                }
                return false;
            });
        };
        
        /*
        / Insère la wikibar et recalcul la hauteur du textarea
        / TODO: Utiliser l'option du lien d'aide de syntaxe pour mettre le lien 
        / directement si la wikibar n'est pas activée
        */
        function get_wikibar() {
            if (opts.syntax_help) {
                opts.wikibar_options['with_help_syntax'] = [opts.i18n_syntax_help, opts.syntax_help];
            }
            jQuery('#ui_EEditor_textarea').Wikibar(false, opts.wikibar_options);
            textarea.css({'height': textarea.height()-jQuery('#ui_wikitoolbar').outerHeight()});
            fixed_hidable_element_height += -jQuery('#ui_wikitoolbar').outerHeight();
        };
        
        /*
        / Protège la scène de l'éditeur des évènements de la scène de fond
        */
        function protect_scene() {
            //"ua-sniffing" hack on IE6
            if(/MSIE 6/i.test(navigator.userAgent)){
                jQuery('select').css({'visibility':"hidden"});
            }
            // S'assure que le scroll ne déplace pas la scène de fond
            jQuery(window).bind('scroll', protect_background_scroll);
        };
        function protect_background_scroll() { 
            jQuery(overlay).css({
                'top':jQuery(window).scrollTop(),
                'height':jQuery(window).height()
            });
        };
        
        /*
        / Ferme la scène et revient à l'état initial de la page
        */
        function close_scene() {
            // Vire la scène
            jQuery(overlay).remove();
            jQuery(textarea).remove();
            jQuery(scene).remove();
            // Retire le hack anti-scroll
            jQuery("body","html").css({'height':"", 'width':""});
            jQuery("html").css('overflow', "auto");
            // Retire le hack sur les <select/> pour IE
            if(/MSIE 6/i.test(navigator.userAgent)){
                jQuery('select').css({visibility:'visible'});
            }
            // Désactivation des évènements utilisés
            jQuery(window).unbind('scroll', protect_background_scroll);
            jQuery(window).unbind('resize', resize);
            // Remet la position verticale initiale de la page
            if(opts.background_scroll_autorestore == true){
                restore_scroll_position('window_scroll_position');
            }
        };
        /*
        / Sert à désactiver tout évènement sur un élément html
        */
        function disable() {
            if(this !== textarea && this !== save && this !== cancel ){
                return false;
            }
        };
        
        /*
        / Recalcul de toute les dimensions de l'éditeur
        */
        function resize() {
            var window_elem = jQuery(window);
            overlay.css({
                'top':window_elem.scrollTop(),
                'width': window_elem.width(),
                'height': window_elem.height(),
            });
            scene.css({
                'top': window_elem.scrollTop(),
                'width': window_elem.width(),
                'height': window_elem.height(),
            });
            root_container.css({
                'width': (window_elem.width()*0.9)-(opts.root_padding*2),
                'height': window_elem.height()*0.93,
                'left': window_elem.width()*0.05,
                'top': window_elem.height()*0.02,
            });
            // Hauteur de base disponible au textarea
            var new_textarea_height = root_container.outerHeight();
            var new_preview_height = new_textarea_height-(opts.root_padding*3)+fixed_visible_element_height;
            new_textarea_height += -(opts.root_padding*4)+fixed_visible_element_height+fixed_hidable_element_height;
            textarea.css({
                'width': (root_container.width()*1.0)-(opts.root_padding*2),
                'height': new_textarea_height
            });
            preview_container.css({
                'width': (window_elem.width()*0.9)-(opts.root_padding*3),
                'height': new_preview_height,
            });
        };
        
        /*
        / Sauvegarde une la position verticale d'une référence
        / La valeur est stockée sous le nom 'BOF_'+key dans le container 
        / spécifié (si non spécifié, sur le <body/> par défaut)
        */
        function save_scroll_position(key, referer, elem_container) {
            if(referer == undefined){
                var elem_referer = jQuery(window);
            } else {
                var elem_referer = referer;
            }
            if(elem_container == undefined) {
                elem_container = jQuery('body');
            }
            var elem_container = jQuery(elem_container);
            elem_container.data('BOF_'+key, elem_referer.scrollTop());
        };
        
        /*
        / Restauration de la position verticale enregistrée d'un élément (referer)
        */
        function restore_scroll_position(key, referer, elem_container) {
            if(referer == undefined){
                var elem_referer = jQuery(window);
            } else {
                var elem_referer = referer;
            }
            if(elem_container == undefined) {
                elem_container = jQuery('body');
            }
            var pos_data = elem_container.data('BOF_'+key);
            if(pos_data){
                elem_referer.scrollTop(pos_data);
                elem_container.removeData('BOF_'+key);
            }
        };
        /*
        * Pour lire les cookies
        */
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

};

/*
* Créé un message d'alerte en haut ou en bas de l'objet ciblé
*/
jQuery.fn.BOF_Editor.create_alert = function(obj, opts, original, edited) {
    // Empeche d'afficher plusieurs fois le meme message et empeche d'afficher 
    // le message si rien à été changé.
    if( jQuery("#ui_EEditor_alert_"+ opts.unique_id).length > 0 || original == edited) {
        return;
    }
    
    var alertObj = jQuery('<p>').attr('id', 'ui_EEditor_alert_'+opts.unique_id).css({'display': "none"}).addClass('ui_EEditor_alert').text(opts.i18n_alert_message);
    // Positionne l'alerte au dessus ou en dessous le champs de texte original
    if(opts.alert_position == "top") {
        jQuery(obj).before(alertObj);
    } else {
        jQuery(obj).after(alertObj);
    }
    alertObj.slideDown("slow");
    
    return alertObj;
};

/*
* Créé un bouton, l'ajoute au dessous du l'objet ciblé et le renvoi pour qu'il 
* puisse être réutilisé
*/
jQuery.fn.BOF_Editor.create_opener_button = function(obj, label) {
    var button = jQuery('<a>').attr({
        'title': label,
        'href': "#"
    }).addClass('ui_EEditor_opener_button').text(label);
    jQuery(obj).after(button);
    return button;
};
