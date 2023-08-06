Ext.define('Ux.locale.override.extjs.ChartAxis', {
    override : 'Ext.chart.Chart',

    requires : [
        'Ux.locale.override.extjs.Component'
    ],

    setLocale : function(locale) {        
        var me                  = this,
            locales             = me.locales,
            titleBottom         = locales.titleBottom,
            titleLeft           = locales.titleLeft,
            manager             = me.locale,
            defaultTitleLeft    = '',
            defaultTitleBottom  = '';
        
        if (titleLeft) {                                    
            text = manager.get(titleLeft, defaultTitleLeft);

            if (Ext.isString(text)) {
                me.axes.get('left').setTitle(text);
            }
        }

        if (titleBottom) {                        
            text = manager.get(titleBottom, defaultTitleBottom);

            if (Ext.isString(text)) {               
                me.axes.get('bottom').setTitle(text);
            }
        }

        me.callOverridden(arguments);
    }
});