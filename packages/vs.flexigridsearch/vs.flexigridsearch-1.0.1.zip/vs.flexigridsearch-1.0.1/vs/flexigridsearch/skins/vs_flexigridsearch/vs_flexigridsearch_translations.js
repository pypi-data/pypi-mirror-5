KNOWN_LANGUAGES = ['en', 'de'];

T = new Array();

T['en'] = new Array()
T['en']['results'] = 'Results';      
T['en']['title'] = 'Title';      
T['en']['description'] = 'Description';
T['en']['creator'] = 'Creator';
T['en']['created'] = 'Created';
T['en']['modified'] = 'Modified';
T['en']['expires'] = 'Expires';
T['en']['effective'] = 'Effective';
T['en']['location'] = 'Location';
T['en']['start'] = 'Start'; 
T['en']['end'] = 'End';
T['en']['getId'] = 'Shortname';
T['en']['subject'] = 'Subject';
T['en']['portal_type'] = 'Type';
T['en']['getObjSize'] = 'Size';
T['en']['review_state'] = 'Status';
T['en']['page'] = 'Page';
T['en']['outof'] = 'of';
T['en']['display_from_to'] = 'Displaying {from} to {to} of {total} items';

T['de'] = new Array()
T['de']['results'] = 'Ergebnis der Suchanfrage';      
T['de']['title'] = 'Titel';      
T['de']['description'] = 'Beschreibung';
T['de']['creator'] = 'Ersteller';
T['de']['created'] = 'angelegt';
T['de']['modified'] = 'geändert';
T['de']['expires'] = 'Verfallsdatum';
T['de']['effective'] = 'Fälligkeitsdatum';
T['de']['location'] = 'Ort';
T['de']['start'] = 'Starttermin'; 
T['de']['end'] = 'Endtermin';
T['de']['getId'] = 'Kurzname';
T['de']['subject'] = 'Schlüsselworte';
T['de']['portal_type'] = 'Typ';
T['de']['getObjSize'] = 'Größe';
T['de']['review_state'] = 'Status';
T['de']['page'] = 'Seite';
T['de']['outof'] = 'von';
T['de']['display_from_to'] = '{from} bis {to} von {total} Treffern';

function vs_translate(language, key) {
    console.log(language, key);
    if (language == 'en' || KNOWN_LANGUAGES.indexOf(language) == -1) 
        return key;
    return T[language][key];
}

