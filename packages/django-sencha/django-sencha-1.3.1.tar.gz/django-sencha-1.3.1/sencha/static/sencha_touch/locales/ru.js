
Ext.apply(Ext.MessageBox, {
    YES: { text: 'да', itemId: 'yes', ui: 'action' },
    NO: { text: 'нет', itemId: 'no' }
});

Ext.apply(Ext.MessageBox, {
    YESNO: [Ext.MessageBox.NO, Ext.MessageBox.YES]
});