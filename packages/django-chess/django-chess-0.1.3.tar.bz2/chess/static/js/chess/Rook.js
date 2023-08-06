var moveRook = function(index, dangerTest) {
    var obj = playarea[index];
    var xy = toXY(index);
    var drop = '';
    var toIndex = null;
    
    var a = (obj.color == WHITE) ? WHITE : BLACK;
    var b = (obj.color == WHITE) ? BLACK : WHITE;
    var x = xy[X];
    var y = xy[Y];

    function rookMethod(dTest) {
        var danger = false;
        
        if((playarea[toIndex].color == null  || playarea[index].color != playarea[toIndex].color) && !dTest) {
            if(!validate(index, toIndex)) {
                drop += '.block_' + toIndex + ', ';
                dropEnabled.push(toIndex);
                
                if(help) {
                    previousHelpCSS.push(new Array(toIndex, $('.block_' + toIndex).css('background-color')));
                }
            }
        }
        
        if(playarea[toIndex].color != null  && playarea[index].color != playarea[toIndex].color && dTest && (playarea[toIndex].name == ROOK || playarea[toIndex].name == QUEEN)) {
            danger = true;
        }
        
        return danger;
    }
    
    while(x != 7) {
        toIndex = fromXY(x + 1, xy[Y]);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(rookMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x ++;
    }
    
    x = xy[X];
		
    while(x != 0) {
        toIndex = fromXY(x - 1, xy[Y]);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(rookMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x --;
    }
    
    x = xy[X];
    while(y != 7) {
        toIndex = fromXY(xy[X], y + 1);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(rookMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        y ++;
    }
    
    y = xy[Y];
    
    while(y != 0) {
        toIndex = fromXY(xy[X], y - 1);
        
        if(playarea[toIndex].color == a) {
            break;
        }
       
        if(rookMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        y --;
    }
    
    return drop;
}