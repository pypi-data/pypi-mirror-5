Ext.override(Ext.selection.Model, {
    storeHasSelected: function(record) {
        var store = this.store,
            records,
            len, id, i, m;

        if (record.hasId()) {
            return store.getById(record.getId());
        } else {
            if (store.buffered) {
                records = [];
                for (m in store.data.map) {
                    records = records.concat(store.data.map[m].value);
                }
            } else {
                records = store.data.items;
            }
            len = records.length;
            id = record.internalId;

            for (i = 0; i < len; ++i) {
                if (id === records[i].internalId) {
                    return true;
                }
            }
        }
        return false;
    }
});