Ext.Loader.setConfig({
    enabled : true,
    paths   : {
        Ux : '/static/sencha_touch/Ux'
    }
});

Ext.require([
    'Ext.Container',
    'Ext.TitleBar',
    'Ext.field.Select',
    'Ext.field.DatePicker',
    'Ext.tab.Panel',
    'Ext.navigation.View',

    'Ux.locale.Manager',
    'Ux.locale.override.st.Component',
    'Ux.locale.override.st.Button',
    'Ux.locale.override.st.Container',
    'Ux.locale.override.st.TitleBar',
    'Ux.locale.override.st.field.Field',
    'Ux.locale.override.st.field.DatePicker',
    'Ux.locale.override.st.picker.Picker',
    'Ux.locale.override.st.picker.Date',
    'Ux.locale.override.st.navigation.View',
    'Ux.locale.override.st.navigation.Bar'
], function() {
    Ux.locale.Manager.setConfig({
        ajaxConfig : {
            method : 'GET'
        },
        language   : 'it',
        tpl        : '/static/subscribe_touch/app/locales/{locale}.json',
        type       : 'ajax'
    });
});