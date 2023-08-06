/*
PyWiki2Xhtml Javascript Wikibar
Developed and designed by Thenon David
www.sveetch.biz

Wikibar API 2.3

This script is part of PyWiki2Xhtml. 
It requires jQuery library >= 1.2.6

Plugin qui rajoute la barre de boutons de raccourcis wiki
au dessus du textarea et pose la capture d'évènement de clic sur
ces boutons.

La wikibar est placée avant l'objet ciblé, par défaut cet objet est considéré 
comme un textarea.

* "target_element_id": (string) Indique un id de textarea autre que l'id de l'objet
  ciblé dans l'init de la class. A faire si l'id de base n'est pas celui d'un 
  textarea. (Utile si on veut placer la wikibar avant que le textarea soit 
  placé/modifié dans le DOM);
* "options": (object) Les options modifiables du plugin.

Un élément de la syntaxe qui contient un attribut "item_list" est considéré comme un 
élément de séléction, auquel sera ajouté une liste de séléction juste avant le bouton.

Par défaut la syntaxe utilisée est celle de PyWiki2Xhtml.
*/

jQuery.fn.Wikibar = function(target_element_id, options) {
    
    // Options par défauts
    var defaults = {
        'with_wikiword_option': true, // Active l'élément de syntaxe pour les mots Wiki
        'with_flv_option': false, // Active l'élément de syntaxe pour ajouter des urls FLV
        'with_access_keys': true, // Active l'utilisation des raccourcis clavier
        'with_attachment': false, // Active le menu d'attachement
        //'with_help_syntax': ["Aide sur la syntaxe wiki", '/wiki/syntax/help/'],
        'with_help_syntax': false, // Array de deux éléments: le texte du lien d'aide puis son URL
        'excluded': [], // Liste de clé d'élément de syntaxe à ne pas utiliser
        'syntax_schema': {} // Emplacement destiné au schéma
    };
    // Éléments de la syntaxe par défaut
    var syntax_schema = {
        'heading1': {
            'label':"Entête de niveau 1", // Titre à afficher (texte alternatif, bulle d'aide)
            'access_key':"1", // Touche de raccourci clavier (généralement avec le combo SHIFT+ALT+RACCOURCI)
            'enclosure': ["!!! ", "\n"], // Séquence d'ouverture et fermeture
            'control_activation': false // Fonction custom de controle et manipulation de la valeur
        },
        'heading2': {
            'label':"Entête de niveau 2",
            'access_key':"2",
            'enclosure': ["!! ", "\n"],
            'control_activation': false
        },
        'heading3': {
            'label':"Entête de niveau 3",
            'access_key':"3",
            'enclosure': ["! ", "\n"],
            'control_activation': false
        },
        'strong': {
            'label':"Gras",
            'access_key':"b",
            'enclosure': ["__", "__"],
            'control_activation': false
        },
        'em': {
            'label':"Emphase",
            'access_key':"i",
            'enclosure': ["''", "''"],
            'control_activation': false
        },
        'code': {
            'label':"Code",
            'access_key':"c",
            'enclosure': ["@@", "@@"],
            'control_activation': false
        },
        'del': {
            'label':"Surligné",
            'access_key':"s",
            'enclosure': ["--", "--"],
            'control_activation': false
        },
        'add': {
            'label':"Souligné",
            'access_key':"u",
            'enclosure': ["++", "++"],
            'control_activation': false
        },
        'wikiword': {
            'label':"Mot wiki",
            'access_key':"w",
            'enclosure': ["¶¶¶", "¶¶¶"],
            'control_activation': 'with_wikiword_option'
        },
        'link': {
            'label':"Lien",
            'access_key':"a",
            'enclosure': ["[", "]", "Entrez une url", jQuery.fn.Wikibar.promptForUrl],
            'control_activation': false
        },
        'image': {
            'label':"Insérer une image",
            'access_key':"p",
            'enclosure': ["((", "))", "Entrez un lien vers une image", jQuery.fn.Wikibar.promptForImage],
            'control_activation': false
        },
        'flv': {
            'label':"Insérer le code d'une vidéo Flash",
            'access_key':"m",
            'enclosure': ["«««", "»»»", "Entrez le code html fourni", jQuery.fn.Wikibar.promptForFlvCode],
            'control_activation': 'with_flv_option'
        },
        'attachment': {
            'label':"Insérer un lien vers le fichier séléctionné",
            'access_key':"f",
            'enclosure': ["[", "]", "Séléctionnez un fichier", jQuery.fn.Wikibar.putAttachItem],
            'control_activation': 'with_attachment',
            'item_list': []
        }
    };
    // Gestion des options envoyés
    var opts = jQuery.extend(defaults, options);
    // Met à jour la syntaxe par défaut par des éléments de syntaxe spécifiés si il y 
    // en a
    var scheme = jQuery.extend(syntax_schema, opts.syntax_schema);
    opts.syntax_schema = scheme;
    
    // Il est pas vraiment prévu d'utiliser ce plugin avec plusieurs éléments 
    // d'un coup, mais on laisse le support vu que ça mange pas de pain
    return this.each(function(){
        // Si il n'est pas spécifié en argument, l'id du textarea ciblé devient 
        // celui de l'objet donné à l'instanciation
        if( !target_element_id ) {
            target_element_id = jQuery(this).attr('id');
        }
        // Lance la méthode principale
        Main(false, this, target_element_id);
    });

    /*
    * Lance tout le processus
    */
    function Main(e, elem, target_element_id) {
        var undefined;
        var obj;
        obj = elem;
        var target = target_element_id;
        
        // Crée le div principal de la wikibar et l'ajoute avant l'objet ciblé
        var toolbar_body_Html = jQuery('<div>').attr({
            'id': "ui_wikitoolbar",
            'class': "wikitoolbar"
        });
        // Ajoute tout les boutons qui sont activés
        $.each( opts.syntax_schema, function(key, val){
//             console.log(key + " inArray => " + );
            if(jQuery.inArray(key, opts.excluded)==-1 && (val.control_activation == false || (val.control_activation != false && opts[val.control_activation]))) {
                if( !val.item_list ){
                    toolbar_body_Html.append( 
                        add_button(key, val.label, val.access_key, function() {
                            jQuery.fn.Wikibar.enclose(target, val.enclosure[0], val.enclosure[1], val.enclosure[2], val.enclosure[3]);
                        })
                    );
                } else {
                    toolbar_body_Html.append( 
                        add_select_input(key, val, function() {
                            jQuery.fn.Wikibar.enclose(target, val.enclosure[0], val.enclosure[1], val.enclosure[2], val.enclosure[3]);
                        })
                    );
                }
            }
        });
        
        // Lien d'aide optionel
        if(opts.with_help_syntax) {
            var help_link = jQuery('<a>').attr({
                'title': opts.with_help_syntax[0],
                'href': opts.with_help_syntax[1],
                'id': "wikibarButton_help"
            }).text(opts.with_help_syntax[0]);
            if(opts.with_access_keys) help_link.attr({'accesskey': "h"});
            // Gestion du clic
            help_link.click(function(){
                try { window.open(opts.with_help_syntax[1], "Wikibar_help_syntax") } catch (e) { } return false
            });
            // Ajout au DOM de la toolbar
            toolbar_body_Html.append(help_link);
        }
        
        // Termine en ajoutant une cale à la fin du div et le rajoute au document
        jQuery(toolbar_body_Html).append('<div class="cale"></div>');
        jQuery(obj).before(toolbar_body_Html);
    };

    /*
    * Méthode d'ajout d'un bouton à la Wikibar
    */
    function add_button(id, label, key, fn) {
        var html = jQuery('<a>').attr({
            'title': label,
            'href': "#",
            'id': "wikibarButton_"+id
        });
        // Access key optionelle
        if(opts.with_access_keys) html.attr({'accesskey': key});
        // Gestion du clic
        html.click(function(){
            try { fn() } catch (e) { } return false
        });
        
        // Renvoi l'objet créé prêt à insérer
        return html;
    };

    /*
    * Création d'une liste de séléction
    */
    function add_select_input(id, params, fn) {
        if( params.item_list.length > 0 ) {
            var options = '<option value="">'+params.enclosure[2]+'</option>';
            $.each( params.item_list, function(key, val){
                options += '<option value="'+val[0]+'">'+val[1]+'</option>';
            });
            
            var html = jQuery('<span class="select_container"><select name="'+id+'" size="1" id="wikibarSelect_'+id+'">'+options+'</select></span>');
            html.append( add_button(id, params.label, params.access_key, fn) );
            
            // Renvoi l'objet créé prêt à insérer
            return html;
        }
        return '';
    };
};

/*
* Enferme une séléction entre un @prefix et @suffix, en dernier argument cette 
* méthode peut recevoir une fonction supplémentaire qui se chargera du formatage
*/
jQuery.fn.Wikibar.enclose = function(target_id, prefix, suffix, label, extFn) {
    var textarea = jQuery("#"+target_id)[0];
    textarea.focus();
    
    // Récupère la séléction en cours si y'en a une et ses paramètres de position
    var start, end, sel, scrollPos, subst, undefined;
    if (typeof(document["selection"]) != "undefined") {
        sel = document.selection.createRange().text;
    } else if (textarea["setSelectionRange"] != undefined) {
        start = textarea.selectionStart;
        end = textarea.selectionEnd;
        scrollPos = textarea.scrollTop;
        sel = textarea.value.substring(start, end);
    }
    // Rajoute un espace en fin pour éviter qu'il se fasse bouffer
    if (sel.match(/ $/)) {
        sel = sel.substring(0, sel.length - 1);
        suffix = suffix + " ";
    }
    
    // Si la balise a une fonction dédicacée pour le formatage, on l'utilise, 
    // sinon on utilise "l'enclosure" de la balise
    if(extFn){
        subst = extFn(sel, label, prefix, suffix);
    } else {
        subst = prefix + sel + suffix;
    }
    if (document["selection"] != undefined) {
        var range = document.selection.createRange().text = subst;
        textarea.caretPos -= suffix.length;
    } else if (textarea["setSelectionRange"] != undefined) {
        textarea.value = textarea.value.substring(0, start) + subst +
                        textarea.value.substring(end);
        if (sel) {
            textarea.setSelectionRange(start + subst.length, start + subst.length);
        } else {
            textarea.setSelectionRange(start + prefix.length, start + prefix.length);
        }
        textarea.scrollTop = scrollPos;
    }
};

/*
* Affiche un prompt pour renseigner les options d'un lien standard
*/
jQuery.fn.Wikibar.promptForUrl = function(s, label, prefix, suffix) {
    var url = prompt(label, 'http://');
    if (url) {
        if(s.length==0) {
            return prefix + url + suffix;
        }
        return prefix + s +'|'+ url + suffix;
    }
    return s;
};

/*
* Affiche un prompt pour renseigner les options d'une image
*/
jQuery.fn.Wikibar.promptForImage = function(s, label, prefix, suffix) {
    var url = prompt(label, 'http://');
    if (url) {
        if(s.length==0) {
            return prefix + url + suffix;
        }
        return prefix + url + '|'+ s + suffix;
    }
    return s;
};

/*
* Ajoute un lien vers un fichier de la liste d'attachements
*/
jQuery.fn.Wikibar.putAttachItem = function(s, label, prefix, suffix) {
    var selected_opt = $("#wikibarSelect_attachment :selected");
    
    if(selected_opt.attr("value").length > 0) {
        if(s.length==0) {
            s = selected_opt.text();
        }
        return prefix + s + '|'+ selected_opt.attr("value") + suffix;
    }
    
    return s;
};

/*
* Affiche un prompt pour renseigner les options d'une vidéo Flash
* Prévu pour parser un code <embed/> donné par dailymotion/youtube/yahoo/..
*/
jQuery.fn.Wikibar.promptForFlvCode = function(s, label, prefix, suffix) {
    var code = prompt(label, '');
    // Si on a bien un morceau de code
    if (code) {
        // Recherche d'un @src
        var url = "";
        var url_res = code.match(/src="[^"]*"/);
        var url_res2 = code.match(/src='[^']*'/);
        // On a une url
        if (url_res || url_res2) {
            if(url_res) {
                url = url_res[0].match(/src="(.*)"/)[1];
            } else {
                url = url_res2[0].match(/src='(.*)'/)[1];
            }
            // Recherche d'un @flashvars
            var flvars_res = code.match(/flashvars="[^"]*"/i);
            var flvars_res2 = code.match(/flashvars='[^']*'/i);
            if(flvars_res) {
                url = url +'|'+ flvars_res[0].match(/flashvars="(.*)"/i)[1];
            } else if(flvars_res2) {
                url = url +'|'+ flvars_res2[0].match(/flashvars='(.*)'/i)[1];
            }
            // Renvoi l'url et le flashvars optionnel
            return s + prefix + url + suffix;
        }
    }
    return s;
};

/*
* Schémas de syntaxes
*/
// Syntaxe PyWiki2Xhtml par défaut courte
var Wikibar_default_short_syntax = {
    'strong': {
        'label':"Gras",
        'access_key':"b",
        'enclosure': ["__", "__"],
        'control_activation': false
    },
    'em': {
        'label':"Emphase",
        'access_key':"i",
        'enclosure': ["''", "''"],
        'control_activation': false
    },
    'code': {
        'label':"Code",
        'access_key':"c",
        'enclosure': ["@@", "@@"],
        'control_activation': false
    },
    'del': {
        'label':"Surligné",
        'access_key':"s",
        'enclosure': ["--", "--"],
        'control_activation': false
    },
    'add': {
        'label':"Souligné",
        'access_key':"u",
        'enclosure': ["++", "++"],
        'control_activation': false
    },
    'link': {
        'label':"Lien",
        'access_key':"a",
        'enclosure': ["[", "]", "Entrez une url", jQuery.fn.Wikibar.promptForUrl],
        'control_activation': false
    },
};
// Syntaxe PyWiki2Xhtml 'améliorée' courte
var Wikibar_new_short_syntax = {
    'strong': {
        'label':"Gras",
        'access_key':"b",
        'enclosure': ["**", "**"],
        'control_activation': false
    },
    'em': {
        'label':"Emphase",
        'access_key':"i",
        'enclosure': ["''", "''"],
        'control_activation': false
    },
    'code': {
        'label':"Code",
        'access_key':"c",
        'enclosure': ["@@", "@@"],
        'control_activation': false
    },
    'del': {
        'label':"Surligné",
        'access_key':"s",
        'enclosure': ["--", "--"],
        'control_activation': false
    },
    'add': {
        'label':"Souligné",
        'access_key':"u",
        'enclosure': ["__", "__"],
        'control_activation': false
    },
    'link': {
        'label':"Lien",
        'access_key':"a",
        'enclosure': ["[", "]", "Entrez une url", jQuery.fn.Wikibar.promptForUrl],
        'control_activation': false
    },
};
