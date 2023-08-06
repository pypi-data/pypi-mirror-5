var moveKnight = function(index, dangerTest) {
    var obj = playarea[index];
    var xy = toXY(index);
    var drop = '';
    var toIndex = null;
    
    var a = (obj.color == WHITE) ? WHITE : BLACK;
    var x = xy[X] - 2;
    var y = xy[Y] - 1;
    
    function knightMethod(dTest) {
        var danger = false;
        
        if((playarea[toIndex].color == null || playarea[index].color != playarea[toIndex].color) && !dTest) {
            if(!validate(index, toIndex)) {
                drop += '.block_' + toIndex + ', ';
                dropEnabled.push(toIndex);
                
                if(help) {
                    previousHelpCSS.push(new Array(toIndex, $('.block_' + toIndex).css('background-color')));
                }
            }
        }
        
        if(playarea[toIndex].color != null  && playarea[index].color != playarea[toIndex].color && dTest && playarea[toIndex].name == KNIGHT) {
            danger = true;
        }
        
        return danger;
    }
    
    if(x >= 0 && y >= 0) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }

    x = xy[X] - 1;
    y = xy[Y] - 2;
		
	if(x >= 0 && y >= 0) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
    x = xy[X] + 1;
    y = xy[Y] - 2;

    if(x <= 7 && y >= 0) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
	x = xy[X] + 2;
	y = xy[Y] - 1;

    if(x <= 7 && y >= 0) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
    x = xy[X] + 2;
    y = xy[Y] + 1;
		
    if(x <= 7 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
    x = xy[X] + 1;
    y = xy[Y] + 2;

    if(x <= 7 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
    x = xy[X] - 1;
    y = xy[Y] + 2;

    if(x >= 0 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
    x = xy[X] - 2;
    y = xy[Y] + 1;

	if(x >= 0 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(knightMethod(dangerTest)) {
            return true;
        }
    }	
		
	return drop;
}