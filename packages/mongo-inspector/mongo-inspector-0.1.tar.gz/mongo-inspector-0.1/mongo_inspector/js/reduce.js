
function reduce(key, values) {

    var unique = function (array) {
        var index, item,
            set = {};

        for (index in array) {
            item = array[index];
            set[item] = null;
        }

        return Object.keys(set);
    };

    var types = values.map(function(v) { return v.types[0]; });
    return {types: unique(types)};
}
