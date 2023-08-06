var moveQueen = function(index, dangerTest) {
    var drop = '';
    
    drop += moveRook(index, dangerTest);
	drop += moveBishop(index, dangerTest);
    
    return drop;
}