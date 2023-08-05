var astream_language_en = { 
    "comment"			: "comment",
    "save"				: "save",
    "view_all"			: "view all",
    "last_activity"		: "Last activity:"
}
var astream_language_de = { 
    "comment"			: "Kommentieren",
    "save"				: "Speichern",
    "view_all"			: "Alle anzeigen",
    "last_activity"		: "Letzte Aktivität am"
}

$(document).ready(				
    function () {
        // --- initialize i18n
        
        i18n_language = $('html').attr("lang").slice(0,2);
    }
);
