var Shape = function(name, color) {
    this.name = name;
    this.color = color;
    this.img = function() {
        if(this.color == null) {
            return null;
        }
        var color = this.color == WHITE ? 'white' : 'black';
        var shape = eval('typeof this').lowercase()
        return color + '/' + shape;
    }
}