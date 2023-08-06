Ext.define('Ux.locale.override.extjs.Button', {
    override : 'Ext.button.Button',

    requires : [
        'Ux.locale.override.extjs.Component'
    ],

    setLocale : function(locale) {        
        var me          = this,
            locales     = me.locales,
            text        = locales.text,
            tooltip        = locales.tooltip,
            manager     = me.locale,
            defaultText = '';
            defaultTooltip = '';
        
        if (text) {            
            if (Ext.isObject(text)) {
                defaultText = text.defaultText;
                text        = text.key;
            }

            text = manager.get(text, defaultText);

            if (Ext.isString(text)) {
                me.setText(text);
            }
        }

        if (tooltip) {                     
            if (Ext.isObject(tooltip)) {
                defaultText = tooltip.defaultText;
                tooltip     = tooltip.key;
            }

            tooltip = manager.get(tooltip, defaultText);

            if (Ext.isString(tooltip)) {                
                me.setTooltip(tooltip);
            }
        }

        me.callOverridden(arguments);
    }
});