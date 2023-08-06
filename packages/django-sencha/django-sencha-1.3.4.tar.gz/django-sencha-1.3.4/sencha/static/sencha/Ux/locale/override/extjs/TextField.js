Ext.define('Ux.locale.override.extjs.TextField', {
    override : 'Ext.form.TextField',

    requires : [
        'Ux.locale.override.extjs.Component'
    ],

    setLocale : function(locale) {
        var me          = this,
            locales     = me.locales,
            text        = locales.emptyText,
            manager     = me.locale,
            defaultText = '';
             
        if (text) {
            if (Ext.isObject(text)) {
                defaultText = text.defaultText;
                text        = text.key;
            }

            text = manager.get(text, defaultText);

            if (Ext.isString(text)) {                
                me.emptyText = text;                
                me.applyEmptyText();
            }
        }

        me.callOverridden(arguments);
    },

    
});