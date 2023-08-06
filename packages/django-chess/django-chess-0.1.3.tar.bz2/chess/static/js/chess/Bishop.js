var moveBishop = function(index, dangerTest) {
    var obj = playarea[index];
    var xy = toXY(index);
    var drop = '';
    var toIndex = null;

    var a = (obj.color == WHITE) ? WHITE : BLACK;
    var b = (obj.color == WHITE) ? BLACK : WHITE;
    var x = xy[X];
    var y = xy[Y];
    
    function bishopMethod(dTest) {
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
        
        if(playarea[toIndex].color != null && playarea[index].color != playarea[toIndex].color && dTest && (playarea[toIndex].name == BISHOP || playarea[toIndex].name == QUEEN)) {
            danger = true;
        }
        
        return danger;
    }
    
    while(true) {
        if(x == 7 || y == 0) {
            break;
        }
        
        toIndex = fromXY(x + 1, y - 1);

        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(bishopMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x ++;
        y --;
    }
    
    x = xy[X];
    y = xy[Y];
    
    while(true) {
        if (x == 7 || y == 7) {
            break;
        }
        
        toIndex = fromXY(x + 1, y + 1);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(bishopMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x ++;
        y ++;
    }
    
    x = xy[X];
    y = xy[Y];
        
    while(true) {
        
        if(x == 0 || y == 7) {
            break;
        }
        
        toIndex = fromXY(x - 1, y + 1);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(bishopMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x --;
        y ++;
    }
    
    x = xy[X];
    y = xy[Y];
    
    while(true) {
        
        if(x == 0 || y == 0) {
            break;
        }
        toIndex = fromXY(x - 1, y - 1);
        
        if(playarea[toIndex].color == a) {
            break;
        }
        
        if(bishopMethod(dangerTest)) {
            return true;
        }
        
        if(playarea[toIndex].color == b) {
            break;
        }
        
        x = x - 1;
        y = y - 1;
    }
    
    return drop
}