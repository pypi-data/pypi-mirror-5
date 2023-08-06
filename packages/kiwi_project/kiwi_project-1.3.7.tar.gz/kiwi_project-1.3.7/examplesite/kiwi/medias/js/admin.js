/*
* Surclasse du 'putAttachItem' original de Wikibar pour lui ajouter la syntaxe de la 
* macro 'attach' de PyWiki2xhtml
*/
jQuery.fn.Wikibar.putAttachMacro = function(s, label, prefix, suffix) {
    var selected_opt = $("#wikibarSelect_attachment :selected");
    
    if(selected_opt.attr("value").length > 0) {
        if(s.length==0) {
            s = selected_opt.text();
        }
        return "{% attach "+selected_opt.attr("value")+" %}" + s + "{% endattach %}";
    }
    
    return s;
};
