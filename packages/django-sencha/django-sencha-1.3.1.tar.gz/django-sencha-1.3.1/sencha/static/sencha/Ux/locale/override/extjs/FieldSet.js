Ext.define('Ux.locale.override.extjs.FieldSet', {
    override : 'Ext.form.FieldSet',

    requires : [
        'Ux.locale.override.extjs.Component'
    ],

    setLocale : function(locale) {
        var me          = this,
            locales     = me.locales,
            text        = locales.title,
            manager     = me.locale,
            defaultText = '';

        if (text) {
            if (Ext.isObject(text)) {
                defaultText = text.defaultText;
                text        = text.key;
            }

            text = manager.get(text, defaultText);

            if (Ext.isString(text)) {
                me.setTitle(text);
            }
        }

        me.callOverridden(arguments);
    },

});