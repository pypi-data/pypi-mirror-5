var movePawn = function(index, dangerTest) {
    var obj = playarea[index];
    var xy = toXY(index);
    var drop = '';
    var toIndex = null;
    
    function pawnMethod1(dTest) {
        var danger = false;
        
        if(playarea[toIndex].color == null && !dTest) {
            if(!validate(index, toIndex)) {
                drop += '.block_' + toIndex + ', ';
                dropEnabled.push(toIndex);
                
                if(help) {
                    previousHelpCSS.push(new Array(toIndex, $('.block_' + toIndex).css('background-color')));
                }
            }
        }
        
        return danger;
    }
    
    function pawnMethod2(dTest) {
        var danger = false;
        
        if(playarea[toIndex].color != null && playarea[index].color != playarea[toIndex].color && !dTest) {
            if(!validate(index, toIndex)) {
                drop += '.block_' + toIndex + ', ';
                dropEnabled.push(toIndex);
                
                if(help) {
                    previousHelpCSS.push(new Array(toIndex, $('.block_' + toIndex).css('background-color')));
                }
            }
        }
        
        if(playarea[toIndex].color != null  && playarea[index].color != playarea[toIndex].color && dTest && playarea[toIndex].name == PAWN) {
            danger = true;
        }
        
        return danger;
    }
    
    if(obj.color == WHITE) {
        if(xy[Y] == 6) {
            toIndex = fromXY(xy[X], xy[Y] - 2);
            if(pawnMethod1(dangerTest)) {
                return true;
            }
        }
        
        if(xy[Y] != 0) {
            toIndex = fromXY(xy[X], xy[Y] - 1);
            if(pawnMethod1(dangerTest)) {
                return true;
            }
        }
        
        if(xy[X] != 0 && xy[Y] != 0) {
            toIndex = fromXY(xy[X] - 1, xy[Y] - 1);
            if(pawnMethod2(dangerTest)) {
                return true;
            }
        }
        
        if(xy[X] != 7 && xy[Y] != 0) {
            toIndex = fromXY(xy[X] + 1, xy[Y] - 1);
            if(pawnMethod2(dangerTest)) {
                return true;
            }
        }
    } else {
        if(xy[Y] == 1) {
            toIndex = fromXY(xy[X], xy[Y] + 2);
            if(pawnMethod1(dangerTest)) {
                return true;
            }
        }
        
        if(xy[Y] != 7) {
            toIndex = fromXY(xy[X], xy[Y] + 1);
            if(pawnMethod1(dangerTest)) {
                return true;
            }
        }
        
        if(xy[X] != 0 && xy[Y] != 7) {
            toIndex = fromXY(xy[X] - 1, xy[Y] + 1);
            if(pawnMethod2(dangerTest)) {
                return true;
            }
        }
        
        if(xy[X] != 7 && xy[Y] != 7) {
            toIndex = fromXY(xy[X] + 1, xy[Y] + 1);
            if(pawnMethod2(dangerTest)) {
                return true;
            }
        }
    }
    return drop
}