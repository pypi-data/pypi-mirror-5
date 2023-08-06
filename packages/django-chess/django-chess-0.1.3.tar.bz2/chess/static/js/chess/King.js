var moveKing = function (index, dangerTest) {
    var obj = playarea[index];
    var xy = toXY(index);
    var drop = '';
    var toIndex = null;

    var a = (obj.color == WHITE) ? WHITE : BLACK;
    var x = xy[X];
    var y = xy[Y] - 1;
    
    function kingMethod(dTest) {
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
        
        if(playarea[toIndex].color != null  && playarea[index].color != playarea[toIndex].color && dTest && playarea[toIndex].name == KING) {
            danger = true;
        }
        
        return danger;
    }
    
    if(y >= 0) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }

    x = xy[X] - 1;
    y = xy[Y] - 1;

    if(x >= 0 && y >= 0) {
        toIndex = fromXY(x, y);
       
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X] - 1;
    y = xy[Y];

    if(x >= 0) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X] - 1;
    y = xy[Y] + 1;
    
    if(x >= 0 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X];
    y = xy[Y] + 1;

    if(y <= 7) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X] + 1;
    y = xy[Y] + 1;

    if(x <= 7 && y <= 7) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X] + 1;
    y = xy[Y];

    if(x <= 7) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    x = xy[X] + 1;
    y = xy[Y] - 1;

    if(x <= 7 && y >= 0) {
        toIndex = fromXY(x, y);
        
        if(kingMethod(dangerTest)) {
            return true;
        }
    }
    
    return drop;
}