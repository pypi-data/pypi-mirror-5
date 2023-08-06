
Ext.apply(Ext.MessageBox, {
    YES: {text: 'Si', itemId: 'yes', ui: 'action'},
    NO: {text: 'No', itemId: 'no'}
});

Ext.apply(Ext.MessageBox, {
    YESNO: [Ext.MessageBox.NO, Ext.MessageBox.YES]
});